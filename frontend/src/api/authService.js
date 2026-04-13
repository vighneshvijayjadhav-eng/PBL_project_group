import { apiClient } from "./client";

export async function loginUser(credentials) {
  const response = await apiClient.post("/api/auth/login", credentials);
  return response.data;
}

export async function refreshUserToken(refreshToken) {
  const response = await apiClient.post(
    "/api/auth/refresh",
    { refresh_token: refreshToken },
    { skipAuthRefresh: true },
  );
  return response.data;
}

export async function logoutUser(refreshToken) {
  const response = await apiClient.post(
    "/api/auth/logout",
    { refresh_token: refreshToken },
    { skipAuthRefresh: true },
  );
  return response.data;
}
