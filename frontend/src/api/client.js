import axios from "axios";

import { clearAuthTokens, getAccessToken, getRefreshToken, setAuthTokens } from "./tokenStorage";

const API_BASE_URL = "http://127.0.0.1:8000";
const AUTH_PATHS = ["/api/auth/login", "/api/auth/refresh"];

let refreshRequest = null;

function normalizeError(error) {
  const message =
    error.response?.data?.error?.message ||
    error.response?.data?.detail ||
    error.message ||
    "Something went wrong";

  const normalized = new Error(message);
  normalized.status = error.response?.status;
  normalized.code = error.response?.data?.error?.code;
  return normalized;
}

function redirectToLogin() {
  if (window.location.pathname !== "/login") {
    window.location.assign("/login");
  }
}

async function requestTokenRefresh() {
  if (!refreshRequest) {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      throw new Error("Missing refresh token");
    }

    refreshRequest = axios
      .post(`${API_BASE_URL}/api/auth/refresh`, { refresh_token: refreshToken })
      .then((response) => {
        const session = response.data?.data;
        if (!session?.access_token || !session?.refresh_token) {
          throw new Error("Refresh response is invalid");
        }

        setAuthTokens({
          accessToken: session.access_token,
          refreshToken: session.refresh_token,
        });
        return session.access_token;
      })
      .catch((error) => {
        clearAuthTokens();
        window.localStorage.removeItem("submitted_claim_ids");
        redirectToLogin();
        throw normalizeError(error);
      })
      .finally(() => {
        refreshRequest = null;
      });
  }

  return refreshRequest;
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const requestPath = originalRequest?.url || "";

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.skipAuthRefresh &&
      !AUTH_PATHS.some((path) => requestPath.includes(path))
    ) {
      originalRequest._retry = true;

      try {
        const nextAccessToken = await requestTokenRefresh();
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers.Authorization = `Bearer ${nextAccessToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(normalizeError(error));
  },
);
