function Pagination({ pagination, pageSize, onPageChange, onPageSizeChange, disabled }) {
  const hasPagination = Boolean(pagination);

  return (
    <div className="pagination-bar">
      <div className="pagination-copy">
        {hasPagination ? (
          <span>
            Page {pagination.page} of {pagination.pages} | Total Claims: {pagination.total}
          </span>
        ) : (
          <span>Pagination unavailable</span>
        )}
      </div>

      <div className="pagination-controls">
        <label className="field field-inline">
          <span>Page Size</span>
          <select value={pageSize} onChange={(event) => onPageSizeChange(Number(event.target.value))} disabled={disabled}>
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        </label>

        <button
          type="button"
          className="secondary-button"
          onClick={() => onPageChange((pagination?.page || 1) - 1)}
          disabled={disabled || !hasPagination || pagination.page <= 1}
        >
          Previous
        </button>
        <button
          type="button"
          className="secondary-button"
          onClick={() => onPageChange((pagination?.page || 1) + 1)}
          disabled={disabled || !hasPagination || pagination.page >= pagination.pages}
        >
          Next
        </button>
      </div>
    </div>
  );
}

export default Pagination;
