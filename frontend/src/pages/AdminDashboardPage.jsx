import { startTransition, useDeferredValue, useEffect, useState } from "react";

import { fetchAdminClaims, fetchSystemHealth } from "../api/claimService";
import ClaimsTable from "../components/ClaimsTable";
import FiltersBar from "../components/FiltersBar";
import HealthBanner from "../components/HealthBanner";
import Pagination from "../components/Pagination";
import RiskChart from "../components/RiskChart";
import StatusChart from "../components/StatusChart";
import { useToast } from "../context/ToastContext";

const initialFilters = {
  status: "",
  risk_level: "",
  min_risk_score: "",
  max_risk_score: "",
};

function AdminDashboardPage() {
  const { showToast } = useToast();
  const [filters, setFilters] = useState(initialFilters);
  const [claims, setClaims] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [health, setHealth] = useState(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [healthError, setHealthError] = useState("");
  const deferredFilters = useDeferredValue(filters);

  useEffect(() => {
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

    loadHealth();
  }, [showToast]);

  useEffect(() => {
    async function loadClaims() {
      setLoading(true);
      setError("");

      try {
        const params = {
          page,
          limit,
          ...(deferredFilters.status ? { status: deferredFilters.status } : {}),
          ...(deferredFilters.risk_level ? { risk_level: deferredFilters.risk_level } : {}),
          ...(deferredFilters.min_risk_score ? { min_risk_score: deferredFilters.min_risk_score } : {}),
          ...(deferredFilters.max_risk_score ? { max_risk_score: deferredFilters.max_risk_score } : {}),
        };

        const response = await fetchAdminClaims(params);
        setClaims(response.data.claims);
        setPagination(response.meta.pagination);
      } catch (requestError) {
        setError(requestError.message);
        showToast({
          title: "Claim feed failed",
          message: requestError.message,
          tone: "error",
        });
      } finally {
        setLoading(false);
      }
    }

    loadClaims();
  }, [deferredFilters, page, limit, showToast]);

  function handleFilterChange(fieldName, value) {
    startTransition(() => {
      setPage(1);
      setFilters((current) => ({ ...current, [fieldName]: value }));
    });
  }

  function handleReset() {
    startTransition(() => {
      setPage(1);
      setFilters(initialFilters);
    });
  }

  function handlePageSizeChange(nextLimit) {
    setLimit(nextLimit);
    setPage(1);
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <p className="eyebrow">Admin Dashboard</p>
          <h2>Claims monitoring and fraud analysis</h2>
          <p className="muted-copy">
            Example API call: <code>GET /admin/claims?status=approved&risk_level=high&page=1&limit=20</code>
          </p>
        </div>
      </div>

      <HealthBanner health={health} loading={healthLoading} error={healthError} />

      <FiltersBar filters={filters} onChange={handleFilterChange} onReset={handleReset} disabled={loading} />

      {error ? <p className="form-error dashboard-error">{error}</p> : null}

      <div className="charts-grid">
        <RiskChart claims={claims} />
        <StatusChart claims={claims} />
      </div>

      <ClaimsTable claims={claims} loading={loading} />

      <Pagination
        pagination={pagination}
        pageSize={limit}
        onPageChange={setPage}
        onPageSizeChange={handlePageSizeChange}
        disabled={loading}
      />
    </section>
  );
}

export default AdminDashboardPage;
