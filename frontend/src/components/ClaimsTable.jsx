import LoadingSkeleton from "./LoadingSkeleton";

function riskBadgeClass(riskLevel) {
  if (riskLevel === "high") {
    return "risk-badge risk-high";
  }
  if (riskLevel === "medium") {
    return "risk-badge risk-medium";
  }
  return "risk-badge risk-low";
}

function statusBadgeClass(status) {
  if (status === "approved") {
    return "status-badge status-approved";
  }
  if (status === "rejected") {
    return "status-badge status-rejected";
  }
  return "status-badge status-pending";
}

function ClaimsTable({ claims, loading }) {
  if (loading) {
    return <LoadingSkeleton variant="table" />;
  }

  if (!claims.length) {
    return (
      <div className="empty-state">
        <h3>No data found</h3>
        <p>Try adjusting the filters to broaden the claim search.</p>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="claims-table">
        <thead>
          <tr>
            <th>Claim ID</th>
            <th>User ID</th>
            <th>Claim Amount</th>
            <th>Fraud Score</th>
            <th>Risk Level</th>
            <th>Status</th>
            <th>Created Date</th>
          </tr>
        </thead>
        <tbody>
          {claims.map((claim) => (
            <tr key={claim.claim_id}>
              <td>#{claim.claim_id}</td>
              <td>{claim.claimant_id}</td>
              <td>{claim.claim_amount}</td>
              <td>{claim.fraud_score}</td>
              <td>
                <span className={riskBadgeClass(claim.risk_level)}>{claim.risk_level}</span>
              </td>
              <td>
                <span className={statusBadgeClass(claim.status)}>{claim.status}</span>
              </td>
              <td>{new Date(claim.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ClaimsTable;
