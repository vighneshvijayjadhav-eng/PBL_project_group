function LoadingSkeleton({ variant = "block", lines = 1 }) {
  if (variant === "table") {
    return (
      <div className="table-wrapper">
        <div className="skeleton-table">
          {Array.from({ length: 6 }).map((_, rowIndex) => (
            <div key={rowIndex} className="skeleton-row">
              {Array.from({ length: 7 }).map((__, cellIndex) => (
                <span key={cellIndex} className="skeleton-line" />
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="skeleton-group">
      {Array.from({ length: lines }).map((_, index) => (
        <span key={index} className="skeleton-line" />
      ))}
    </div>
  );
}

export default LoadingSkeleton;
