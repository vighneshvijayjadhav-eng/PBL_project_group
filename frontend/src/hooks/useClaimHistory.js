import { useCallback, useState } from "react";

const STORAGE_KEY = "submitted_claim_ids";

function readStoredIds() {
  try {
    const rawValue = localStorage.getItem(STORAGE_KEY);
    return rawValue ? JSON.parse(rawValue) : [];
  } catch {
    return [];
  }
}

export function useClaimHistory() {
  const [claimIds, setClaimIds] = useState(readStoredIds);

  const saveClaimId = useCallback((claimId) => {
    setClaimIds((currentIds) => {
      const nextIds = Array.from(new Set([claimId, ...currentIds]));
      localStorage.setItem(STORAGE_KEY, JSON.stringify(nextIds));
      return nextIds;
    });
  }, []);

  return { claimIds, saveClaimId };
}
