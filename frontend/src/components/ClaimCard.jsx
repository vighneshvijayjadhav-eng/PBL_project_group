function formatStatus(status) {
  if (status === "approved") {
    return "Approved";
  }
  if (status === "denied") {
    return "Rejected";
  }
  return "Pending";
}

function ClaimCard({ claim }) {
  const riskScore = claim.final_risk_score ?? claim.rule_score ?? claim.ml_score ?? "N/A";

  return (
    <article className="claim-card">
      <div className="claim-card-header">
        <div>
          <p className="claim-label">Claim #{claim.claim_id}</p>
          <h3>{claim.claim_type}</h3>
        </div>
        <span className={`status-badge status-${formatStatus(claim.claim_status).toLowerCase()}`}>
          {formatStatus(claim.claim_status)}
        </span>
      </div>

      <dl className="claim-grid">
        <div>
          <dt>Claim Amount</dt>
          <dd>{claim.claim_amount}</dd>
        </div>
        <div>
          <dt>Fraud Risk Score</dt>
          <dd>{riskScore}</dd>
        </div>
        <div>
          <dt>Fraud Risk Level</dt>
          <dd>{claim.risk_level}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{claim.claim_status}</dd>
        </div>
      </dl>

      <p className="claim-description">{claim.description}</p>
    </article>
  );
}

export default ClaimCard;
