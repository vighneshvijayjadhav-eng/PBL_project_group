import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Insurance Claim Processing & Risk Profiling System"
    api_prefix: str = "/api"
    database_url: str = Field(
        default=os.getenv("DATABASE_URL", "sqlite:///./test.db"),
        env="DATABASE_URL",
    )
    secret_key: str = Field(default=os.getenv("SECRET_KEY", "change-me"), env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(
        default=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        env="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    refresh_token_expire_days: int = Field(
        default=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
        env="REFRESH_TOKEN_EXPIRE_DAYS",
    )
    rate_limit_window_seconds: int = Field(
        default=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")),
        env="RATE_LIMIT_WINDOW_SECONDS",
    )
    rate_limit_max_requests: int = Field(
        default=int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "120")),
        env="RATE_LIMIT_MAX_REQUESTS",
    )
    risk_engine_url: str = Field(default=os.getenv("RISK_ENGINE_URL", "http://localhost:8001"), env="RISK_ENGINE_URL")
    ml_model_path: str = Field(
        default=os.getenv("ML_MODEL_PATH", "risk_engine/artifacts/best_model.pkl"),
        env="ML_MODEL_PATH",
    )
    scaler_path: str = Field(
        default=os.getenv("SCALER_PATH", "risk_engine/artifacts/scaler.pkl"),
        env="SCALER_PATH",
    )
    encoders_path: str = Field(
        default=os.getenv("ENCODERS_PATH", "risk_engine/artifacts/encoders.pkl"),
        env="ENCODERS_PATH",
    )
    feature_order_path: str = Field(
        default=os.getenv("FEATURE_ORDER_PATH", "risk_engine/artifacts/feature_order.json"),
        env="FEATURE_ORDER_PATH",
    )
    risk_weight_ml: float = Field(default=float(os.getenv("RISK_WEIGHT_ML", "0.6")), env="RISK_WEIGHT_ML")
    risk_weight_rb: float = Field(default=float(os.getenv("RISK_WEIGHT_RB", "0.4")), env="RISK_WEIGHT_RB")
    max_upload_size_mb: int = Field(default=int(os.getenv("MAX_UPLOAD_SIZE_MB", "10")), env="MAX_UPLOAD_SIZE_MB")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
