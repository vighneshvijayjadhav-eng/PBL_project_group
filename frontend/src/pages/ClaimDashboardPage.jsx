import { useEffect, useState } from "react";

import { fetchClaimById, fetchClaimSummary, fetchSystemHealth } from "../api/claimService";
import ClaimCard from "../components/ClaimCard";
import HealthBanner from "../components/HealthBanner";
import LoadingSkeleton from "../components/LoadingSkeleton";
import { useToast } from "../context/ToastContext";
import { useClaimHistory } from "../hooks/useClaimHistory";

function ClaimDashboardPage() {
  const { claimIds } = useClaimHistory();
  const { showToast } = useToast();
  const [claims, setClaims] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [health, setHealth] = useState(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [healthError, setHealthError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const claimResponses = await Promise.all(
          claimIds.map(async (claimId) => {
            const response = await fetchClaimById(claimId);
            return response.data;
          }),
        );
        const summaryResponse = await fetchClaimSummary();
        setClaims(claimResponses);
        setSummary(summaryResponse.data);
      } catch (requestError) {
        setError(requestError.message);
        showToast({
          title: "Dashboard unavailable",
          message: requestError.message,
          tone: "error",
        });
      } finally {
        setLoading(false);
      }
    }

    async function loadHealth() {
      try {
        const response = await fetchSystemHealth();
        setHealth(response.data);
      } catch (requestError) {
        setHealthError(requestError.message);
        showToast({
          title: "Health check failed",
          message: requestError.message,
          tone: "error",
        });
      } finally {
        setHealthLoading(false);
      }
    }

    loadDashboard();
    loadHealth();
  }, [claimIds, showToast]);

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <p className="eyebrow">Claim Dashboard</p>
          <h2>Track submitted claims and fraud scoring</h2>
        </div>
      </div>

      <HealthBanner health={health} loading={healthLoading} error={healthError} />

      <div className="stats-grid">
        {loading ? (
          <LoadingSkeleton lines={3} />
        ) : (
          <>
            <div className="stat-card">
              <span>Total Claims</span>
              <strong>{summary?.total_claims ?? 0}</strong>
            </div>
            <div className="stat-card">
              <span>Average Risk Score</span>
              <strong>{summary?.avg_risk_score ?? "0.0000"}</strong>
            </div>
            <div className="stat-card">
              <span>High-Risk Percentage</span>
              <strong>{summary?.high_risk_percentage ?? "0.00"}%</strong>
            </div>
          </>
        )}
      </div>

      {loading ? <LoadingSkeleton lines={4} /> : null}
      {error ? <p className="form-error">{error}</p> : null}

      {!loading && !error && claims.length === 0 ? (
        <div className="empty-state">
          <h3>No claims yet</h3>
          <p>Submit a claim to populate the dashboard. Submitted claim IDs are tracked locally.</p>
        </div>
      ) : null}

      <div className="claim-list">
        {claims.map((claim) => (
          <ClaimCard key={claim.claim_id} claim={claim} />
        ))}
      </div>
    </section>
  );
}

export default ClaimDashboardPage;
