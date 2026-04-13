import logging
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.database import Base, engine
from app.dependencies import AppException, build_response
from app.routers import auth, claims, policies, system, users
from app.services.rate_limiter import is_rate_limited

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.request_id = str(uuid4())
        start_time = time.perf_counter()
        client_host = request.client.host if request.client else "unknown"
        rate_limit_key = f"{client_host}:{request.url.path}"

        if is_rate_limited(
            rate_limit_key,
            limit=settings.rate_limit_max_requests,
            window_seconds=settings.rate_limit_window_seconds,
        ):
            logger.warning(
                "rate_limit_exceeded request_id=%s method=%s path=%s client=%s",
                request.state.request_id,
                request.method,
                request.url.path,
                client_host,
            )
            return build_response(
                request,
                success=False,
                data=None,
                error={"code": "RATE_LIMITED", "message": "Too many requests", "details": {}},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request_failed request_id=%s method=%s path=%s client=%s",
                request.state.request_id,
                request.method,
                request.url.path,
                client_host,
            )
            raise

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "request_completed request_id=%s method=%s path=%s status=%s duration_ms=%s client=%s",
            request.state.request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            client_host,
        )
        response.headers["X-Request-Id"] = request.state.request_id
        return response


app = FastAPI(title="Insurance Claim Processing & Risk Profiling System")
app.add_middleware(RequestContextMiddleware)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Database connected")
    logger.info("Risk engine ready")


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.error(
        "app_exception request_id=%s path=%s status=%s code=%s details=%s",
        getattr(request.state, "request_id", "unknown"),
        request.url.path,
        exc.status_code,
        exc.code,
        exc.details,
    )
    return build_response(
        request,
        success=False,
        data=None,
        error={"code": exc.code, "message": exc.message, "details": exc.details},
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning(
        "validation_error request_id=%s path=%s errors=%s",
        getattr(request.state, "request_id", "unknown"),
        request.url.path,
        exc.errors(),
    )
    return build_response(
        request,
        success=False,
        data=None,
        error={"code": "VALIDATION_ERROR", "message": "Request validation failed", "details": {"errors": exc.errors()}},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code = "AUTH_INVALID" if exc.status_code == status.HTTP_401_UNAUTHORIZED else "ACCESS_DENIED"
    logger.warning(
        "http_exception request_id=%s path=%s status=%s detail=%s",
        getattr(request.state, "request_id", "unknown"),
        request.url.path,
        exc.status_code,
        exc.detail,
    )
    return build_response(
        request,
        success=False,
        data=None,
        error={"code": code, "message": str(exc.detail), "details": {}},
        status_code=exc.status_code,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "unhandled_exception request_id=%s path=%s",
        getattr(request.state, "request_id", "unknown"),
        request.url.path,
    )
    return build_response(
        request,
        success=False,
        data=None,
        error={"code": "INTERNAL_ERROR", "message": "Internal server error", "details": {}},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(policies.router)
app.include_router(claims.router)
app.include_router(system.router)
