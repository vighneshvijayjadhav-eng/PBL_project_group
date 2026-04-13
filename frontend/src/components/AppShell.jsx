import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

function AppShell() {
  const { logout, role, userEmail } = useAuth();
  const { showToast } = useToast();
  const [loggingOut, setLoggingOut] = useState(false);

  async function handleLogout() {
    setLoggingOut(true);
    await logout();
    showToast({
      title: "Signed out",
      message: "Your session has been cleared safely.",
      tone: "info",
    });
    setLoggingOut(false);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Insurance Claim Processing System</p>
          <h1 className="sidebar-title">Fraud-Aware Claims Portal</h1>
          <p className="sidebar-copy">
            Submit claims, monitor fraud risk scoring, and track decision status from one place.
          </p>
        </div>

        <nav className="nav-links">
          <NavLink to="/claims/new" className="nav-link">
            Submit Claim
          </NavLink>
          <NavLink to="/claims/dashboard" className="nav-link">
            Status Dashboard
          </NavLink>
          {role === "admin" ? (
            <NavLink to="/admin/dashboard" className="nav-link">
              Admin Dashboard
            </NavLink>
          ) : null}
        </nav>

        <div className="sidebar-footer">
          <span className="user-chip">{userEmail || "Authenticated User"}</span>
          {role ? <span className="role-chip">{role}</span> : null}
          <button type="button" className="secondary-button" onClick={handleLogout} disabled={loggingOut}>
            {loggingOut ? "Signing Out..." : "Sign Out"}
          </button>
        </div>
      </aside>

      <main className="page-content">
        <Outlet />
      </main>
    </div>
  );
}

export default AppShell;
