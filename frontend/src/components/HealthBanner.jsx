function HealthBanner({ health, loading, error }) {
  if (loading) {
    return <div className="banner banner-neutral">Checking backend health and auth readiness...</div>;
  }

  if (error) {
    return <div className="banner banner-error">{error}</div>;
  }

  if (!health) {
    return null;
  }

  return (
    <div className="banner banner-success">
      Backend: {health.risk_engine} | Database: {health.database} | Auth: {health.auth_system} |
      Latency: {health.api_latency_ms} ms
    </div>
  );
}

export default HealthBanner;
