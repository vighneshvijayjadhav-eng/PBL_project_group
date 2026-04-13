import { useEffect, useState } from "react";

import { fetchSystemHealth, submitClaim } from "../api/claimService";
import HealthBanner from "../components/HealthBanner";
import { useToast } from "../context/ToastContext";
import { useClaimHistory } from "../hooks/useClaimHistory";

const initialFormState = {
  policy_id: "",
  claim_type: "accident",
  claim_amount: "",
  description: "",
  claimant_age: "",
  claimant_gender: "male",
  claimant_location: "",
  policy_tenure_months: "",
  premium_to_claim_ratio: "",
  previous_claims_count: "0",
  previous_fraud_flag: false,
  incident_severity: "medium",
  hospitalization_required: false,
  police_report_filed: true,
  document_count: "1",
  claim_submission_delay_days: "0",
  incident_date: "",
};

function ClaimSubmissionPage() {
  const { saveClaimId } = useClaimHistory();
  const { showToast } = useToast();
  const [formData, setFormData] = useState(initialFormState);
  const [health, setHealth] = useState(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [healthError, setHealthError] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    async function loadHealth() {
      try {
        const response = await fetchSystemHealth();
        setHealth(response.data);
      } catch (requestError) {
        setHealthError(requestError.message);
      } finally {
        setHealthLoading(false);
      }
    }

    loadHealth();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const payload = {
        ...formData,
        policy_id: Number(formData.policy_id),
        claim_amount: formData.claim_amount,
        claimant_age: Number(formData.claimant_age),
        policy_tenure_months: Number(formData.policy_tenure_months),
        premium_to_claim_ratio: formData.premium_to_claim_ratio,
        previous_claims_count: Number(formData.previous_claims_count),
        document_count: Number(formData.document_count),
        claim_submission_delay_days: Number(formData.claim_submission_delay_days),
      };

      const response = await submitClaim(payload);
      saveClaimId(response.data.claim_id);
      setSuccess(`Claim #${response.data.claim_id} submitted successfully.`);
      showToast({
        title: "Claim submitted",
        message: `Claim #${response.data.claim_id} has been queued for scoring.`,
        tone: "success",
      });
      setFormData(initialFormState);
    } catch (requestError) {
      setError(requestError.message);
      showToast({
        title: "Submission failed",
        message: requestError.message,
        tone: "error",
      });
    } finally {
      setLoading(false);
    }
  }

  function updateField(fieldName, value) {
    setFormData((current) => ({ ...current, [fieldName]: value }));
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <p className="eyebrow">Claim Submission</p>
          <h2>Submit a new insurance claim</h2>
        </div>
      </div>

      <HealthBanner health={health} loading={healthLoading} error={healthError} />

      <form className="claim-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Policy ID</span>
          <input
            type="number"
            value={formData.policy_id}
            onChange={(event) => updateField("policy_id", event.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Claim Type</span>
          <select value={formData.claim_type} onChange={(event) => updateField("claim_type", event.target.value)}>
            <option value="accident">Accident</option>
            <option value="theft">Theft</option>
            <option value="fire">Fire</option>
            <option value="other">Other</option>
          </select>
        </label>

        <label className="field">
          <span>Claim Amount</span>
          <input
            type="number"
            min="0"
            step="0.01"
            value={formData.claim_amount}
            onChange={(event) => updateField("claim_amount", event.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Incident Date</span>
          <input
            type="datetime-local"
            value={formData.incident_date}
            onChange={(event) => updateField("incident_date", event.target.value)}
            required
          />
        </label>

        <label className="field field-wide">
          <span>Description</span>
          <textarea
            rows="4"
            value={formData.description}
            onChange={(event) => updateField("description", event.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Claimant Age</span>
          <input
            type="number"
            min="0"
            value={formData.claimant_age}
            onChange={(event) => updateField("claimant_age", event.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Claimant Gender</span>
          <select
            value={formData.claimant_gender}
            onChange={(event) => updateField("claimant_gender", event.target.value)}
          >
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </label>

        <label className="field">
          <span>Location</span>
          <input
            type="text"
            value={formData.claimant_location}
            onChange={(event) => updateField("claimant_location", event.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Policy Tenure (Months)</span>
          <input
            type="number"
            min="0"
            value={formData.policy_tenure_months}
            onChange={(event) => updateField("policy_tenure_months", event.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Premium to Claim Ratio</span>
          <input
            type="number"
            min="0"
            step="0.01"
            value={formData.premium_to_claim_ratio}
            onChange={(event) => updateField("premium_to_claim_ratio", event.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Previous Claims Count</span>
          <input
            type="number"
            min="0"
            value={formData.previous_claims_count}
            onChange={(event) => updateField("previous_claims_count", event.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Incident Severity</span>
          <select
            value={formData.incident_severity}
            onChange={(event) => updateField("incident_severity", event.target.value)}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>

        <label className="field">
          <span>Document Count</span>
          <input
            type="number"
            min="0"
            value={formData.document_count}
            onChange={(event) => updateField("document_count", event.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Submission Delay (Days)</span>
          <input
            type="number"
            min="0"
            value={formData.claim_submission_delay_days}
            onChange={(event) => updateField("claim_submission_delay_days", event.target.value)}
            required
          />
        </label>

        <label className="checkbox-field">
          <input
            type="checkbox"
            checked={formData.previous_fraud_flag}
            onChange={(event) => updateField("previous_fraud_flag", event.target.checked)}
          />
          <span>Previous fraud flag</span>
        </label>

        <label className="checkbox-field">
          <input
            type="checkbox"
            checked={formData.hospitalization_required}
            onChange={(event) => updateField("hospitalization_required", event.target.checked)}
          />
          <span>Hospitalization required</span>
        </label>

        <label className="checkbox-field">
          <input
            type="checkbox"
            checked={formData.police_report_filed}
            onChange={(event) => updateField("police_report_filed", event.target.checked)}
          />
          <span>Police report filed</span>
        </label>

        {error ? <p className="form-error field-wide">{error}</p> : null}
        {success ? <p className="form-success field-wide">{success}</p> : null}

        <button type="submit" className="primary-button field-wide" disabled={loading}>
          {loading ? "Submitting..." : "Submit Claim"}
        </button>
      </form>
    </section>
  );
}

export default ClaimSubmissionPage;
