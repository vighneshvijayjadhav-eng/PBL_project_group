import { apiClient } from "./client";

export async function submitClaim(payload) {
  const response = await apiClient.post("/claims/", payload);
  return response.data;
}

export async function fetchClaimById(claimId) {
  const response = await apiClient.get(`/claims/${claimId}`);
  return response.data;
}

export async function fetchClaimSummary() {
  const response = await apiClient.get("/claims/summary");
  return response.data;
}

export async function fetchSystemHealth() {
  const response = await apiClient.get("/system/health");
  return response.data;
}

export async function fetchAdminClaims(params) {
  const response = await apiClient.get("/admin/claims", { params });
  return response.data;
}
