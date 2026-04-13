import { createContext, useContext, useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";

import { logoutUser } from "../api/authService";
import { clearAuthTokens, getAccessToken, getRefreshToken, setAuthTokens } from "../api/tokenStorage";

const AuthContext = createContext(null);

function decodeAccessToken(token) {
  if (!token) {
    return null;
  }

  try {
    const payload = jwtDecode(token);
    return {
      userId: payload.user_id,
      email: payload.email,
      role: payload.role,
      exp: payload.exp,
    };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(() => getAccessToken());
  const [refreshToken, setRefreshToken] = useState(() => getRefreshToken());
  const [user, setUser] = useState(() => decodeAccessToken(getAccessToken()));

  useEffect(() => {
    function syncAuthState() {
      const nextAccessToken = getAccessToken();
      const nextRefreshToken = getRefreshToken();
      setAccessToken(nextAccessToken);
      setRefreshToken(nextRefreshToken);
      setUser(decodeAccessToken(nextAccessToken));
    }

    window.addEventListener("auth:changed", syncAuthState);
    window.addEventListener("storage", syncAuthState);

    return () => {
      window.removeEventListener("auth:changed", syncAuthState);
      window.removeEventListener("storage", syncAuthState);
    };
  }, []);

  const value = {
    accessToken,
    refreshToken,
    user,
    role: user?.role ?? null,
    userEmail: user?.email ?? null,
    isAuthenticated: Boolean(accessToken && refreshToken && user),
    login: ({ accessToken: nextAccessToken, refreshToken: nextRefreshToken }) => {
      setAuthTokens({
        accessToken: nextAccessToken,
        refreshToken: nextRefreshToken,
      });
    },
    logout: async () => {
      const currentRefreshToken = getRefreshToken();
      if (currentRefreshToken && getAccessToken()) {
        try {
          await logoutUser(currentRefreshToken);
        } catch {
          // Best effort logout. Local cleanup still happens.
        }
      }
      clearAuthTokens();
      localStorage.removeItem("submitted_claim_ids");
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
