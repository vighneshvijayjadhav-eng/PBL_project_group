function FiltersBar({ filters, onChange, onReset, disabled }) {
  return (
    <section className="filters-bar">
      <label className="field">
        <span>Status</span>
        <select
          value={filters.status}
          onChange={(event) => onChange("status", event.target.value)}
          disabled={disabled}
        >
          <option value="">All</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="pending">Pending</option>
        </select>
      </label>

      <label className="field">
        <span>Risk Level</span>
        <select
          value={filters.risk_level}
          onChange={(event) => onChange("risk_level", event.target.value)}
          disabled={disabled}
        >
          <option value="">All</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </label>

      <label className="field">
        <span>Min Risk Score</span>
        <input
          type="number"
          min="0"
          max="1"
          step="0.0001"
          value={filters.min_risk_score}
          onChange={(event) => onChange("min_risk_score", event.target.value)}
          disabled={disabled}
          placeholder="0.0000"
        />
      </label>

      <label className="field">
        <span>Max Risk Score</span>
        <input
          type="number"
          min="0"
          max="1"
          step="0.0001"
          value={filters.max_risk_score}
          onChange={(event) => onChange("max_risk_score", event.target.value)}
          disabled={disabled}
          placeholder="1.0000"
        />
      </label>

      <div className="filters-actions">
        <button type="button" className="secondary-button" onClick={onReset} disabled={disabled}>
          Reset Filters
        </button>
      </div>
    </section>
  );
}

export default FiltersBar;
