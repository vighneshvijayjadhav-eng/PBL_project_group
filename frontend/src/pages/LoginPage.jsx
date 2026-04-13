import { useState } from "react";
import { jwtDecode } from "jwt-decode";
import { useLocation, useNavigate } from "react-router-dom";

import { loginUser } from "../api/authService";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const { showToast } = useToast();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const from = location.state?.from?.pathname;

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await loginUser(formData);
      login({
        accessToken: response.data.access_token,
        refreshToken: response.data.refresh_token,
      });

      const decodedToken = jwtDecode(response.data.access_token);
      const defaultPath = decodedToken.role === "admin" ? "/admin/dashboard" : "/claims/new";
      const nextPath = from || defaultPath;
      showToast({
        title: "Login successful",
        message: `Welcome back, ${decodedToken.email}.`,
        tone: "success",
      });
      navigate(nextPath, { replace: true });
    } catch (requestError) {
      setError(requestError.message);
      showToast({
        title: "Login failed",
        message: requestError.message,
        tone: "error",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <section className="auth-panel">
        <div>
          <p className="eyebrow">Secure Access</p>
          <h1>Sign in to the claims portal</h1>
          <p className="auth-copy">
            Use your registered email and password to manage claims and review fraud scoring.
          </p>
        </div>

        <form className="form-stack" onSubmit={handleSubmit}>
          <label className="field">
            <span>Email</span>
            <input
              type="email"
              value={formData.email}
              onChange={(event) =>
                setFormData((current) => ({ ...current, email: event.target.value }))
              }
              placeholder="name@example.com"
              required
            />
          </label>

          <label className="field">
            <span>Password</span>
            <input
              type="password"
              value={formData.password}
              onChange={(event) =>
                setFormData((current) => ({ ...current, password: event.target.value }))
              }
              placeholder="Enter your password"
              required
            />
          </label>

          {error ? <p className="form-error">{error}</p> : null}

          <button type="submit" className="primary-button" disabled={loading}>
            {loading ? "Signing in..." : "Login"}
          </button>
        </form>
      </section>
    </div>
  );
}

export default LoginPage;
