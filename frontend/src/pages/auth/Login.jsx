import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext.jsx";
import truckBg from "../../assets/bg_login.png";

export default function Login() {
  // Set body class for background exception
  React.useEffect(() => {
    document.body.classList.add('login');
    return () => document.body.classList.remove('login');
  }, []);
  const { login, initTwoFactorSetup, verifyTwoFactorLogin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const emailRef = useRef(null);
  const passwordRef = useRef(null);

  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [step, setStep] = useState("login");
  const [otpCode, setOtpCode] = useState("");
  const [backupCode, setBackupCode] = useState("");
  const [setupData, setSetupData] = useState(null);
  const [pendingCreds, setPendingCreds] = useState(null);

  const resolveNextPath = () => {
    const params = new URLSearchParams(location.search);
    const nextRaw = params.get("next");
    const stateNext = location.state?.from?.pathname;
    let candidate = stateNext || "/dashboard";

    if (nextRaw) {
      try {
        candidate = decodeURIComponent(nextRaw);
      } catch {
        candidate = nextRaw;
      }
    }

    if (!candidate || !candidate.startsWith("/") || candidate.startsWith("//")) {
      return "/dashboard";
    }
    if (candidate.startsWith("/login") || candidate.startsWith("/register")) {
      return "/dashboard";
    }

    return candidate;
  };

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const reason = params.get("reason");
    if (reason === "expired") {
      setError("Session expired. Please login again.");
    }
  }, [location.search]);

  const handlePostLogin = (result) => {
    const nextUser = result?.user || {};
    const rawStatus = nextUser.user_status ?? nextUser.userStatus ?? null;
    let accountStatus = rawStatus ? String(rawStatus).trim().toLowerCase() : null;
    if (accountStatus === "inactive") accountStatus = "pending";
    if (!accountStatus) accountStatus = nextUser.is_active === false ? "pending" : "active";

    const nextPath = resolveNextPath();

    if (accountStatus !== "active") {
      navigate("/account-inactive", { replace: true });
    } else {
      navigate(nextPath, { replace: true });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const email = (emailRef.current?.value || "").trim();
      const password = passwordRef.current?.value || "";

      if (step === "login") {
        const result = await login({ email, password, remember: rememberMe });
        handlePostLogin(result);
        return;
      }

      if (!pendingCreds?.email || !pendingCreds?.password) {
        throw new Error("Missing credentials for two-factor verification.");
      }

      const result = await verifyTwoFactorLogin({
        email: pendingCreds.email,
        password: pendingCreds.password,
        token: otpCode.trim(),
        backupCode: backupCode.trim(),
      });
      handlePostLogin(result);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      const setupRequired = Boolean(detail?.setup_required);
      const twoFactorRequired = Boolean(detail?.two_factor_required);

      if (step === "login" && (setupRequired || twoFactorRequired)) {
        const email = (emailRef.current?.value || "").trim();
        const password = passwordRef.current?.value || "";
        setPendingCreds({ email, password });

        if (setupRequired) {
          const setup = await initTwoFactorSetup({ email, password });
          setSetupData(setup || null);
          setStep("setup");
          setError("");
          return;
        }

        if (twoFactorRequired) {
          setStep("verify");
          setError("Two-factor authentication required.");
          return;
        }
      }

      const msg =
        err?.normalized?.detail ||
        detail ||
        err?.message ||
        "Login failed";
      setError(typeof msg === "string" ? msg : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100vw",
        backgroundImage: `url(${truckBg})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        position: "relative",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
      }}
    >
      {/* Dark overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          width: "100vw",
          height: "100vh",
          background: "rgba(0,0,0,0.35)",
          zIndex: 1,
        }}
      />

      <div
        style={{
          position: "relative",
          zIndex: 2,
          width: "100vw",
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
        }}
      >
        <form
          onSubmit={handleSubmit}
          style={{
            width: "100%",
            maxWidth: 420,
            minWidth: 0,
            boxSizing: "border-box",
            padding: "28px 20px",
            borderRadius: "16px",
            background: "rgba(20, 20, 20, 0.55)",
            backdropFilter: "blur(14px)",
            border: "1px solid rgba(255,255,255,0.12)",
            color: "white",
            boxShadow: "0 4px 32px 0 rgba(0,0,0,0.18)",
            margin: "0 12px",
          }}
        >
          <h2 style={{ margin: 0, marginBottom: 14 }}>Sign In</h2>

          {error ? (
            <div
              style={{
                background: "rgba(255,0,0,0.12)",
                border: "1px solid rgba(255,0,0,0.25)",
                padding: 10,
                borderRadius: 10,
                marginBottom: 12,
                fontSize: 14,
              }}
            >
              {error}
            </div>
          ) : null}

          {step === "login" ? (
            <>
              <label style={{ display: "block", fontSize: 13, opacity: 0.9 }}>
                Email
              </label>
              <input
                ref={emailRef}
                type="email"
                autoComplete="username"
                defaultValue=""
                required
                style={{
                  width: "100%",
                  padding: "12px 12px",
                  borderRadius: 10,
                  border: "1px solid rgba(255,255,255,0.18)",
                  background: "rgba(0,0,0,0.25)",
                  color: "white",
                  marginTop: 6,
                  marginBottom: 12,
                  outline: "none",
                }}
              />
            </>
          ) : (
            <div
              style={{
                background: "rgba(255,255,255,0.06)",
                border: "1px solid rgba(255,255,255,0.12)",
                padding: 10,
                borderRadius: 10,
                marginBottom: 12,
                fontSize: 13,
              }}
            >
              Two-factor authentication for <strong>{pendingCreds?.email}</strong>
            </div>
          )}

          {step === "login" && (
            <>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: 8,
                  fontSize: 13,
                  opacity: 0.9,
                }}
              >
                <label>Password</label>
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  style={{
                    background: "transparent",
                    border: "none",
                    color: "#9fd3ff",
                    cursor: "pointer",
                    padding: 0,
                    fontSize: 12,
                  }}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
              <input
                ref={passwordRef}
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                required
                style={{
                  width: "100%",
                  padding: "12px 12px",
                  borderRadius: 10,
                  border: "1px solid rgba(255,255,255,0.18)",
                  background: "rgba(0,0,0,0.25)",
                  color: "white",
                  marginTop: 6,
                  marginBottom: 12,
                  outline: "none",
                }}
              />
            </>
          )}

          {step === "setup" && setupData?.qr_code && (
            <div
              style={{
                background: "rgba(0,0,0,0.25)",
                border: "1px solid rgba(255,255,255,0.12)",
                padding: 12,
                borderRadius: 10,
                marginBottom: 12,
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: 13, marginBottom: 8 }}>Scan this QR code in your authenticator app</div>
              <img
                src={setupData.qr_code}
                alt="2FA QR Code"
                style={{ width: 180, height: 180, borderRadius: 8 }}
              />
              {Array.isArray(setupData.backup_codes) && setupData.backup_codes.length > 0 && (
                <div style={{ marginTop: 12, textAlign: "left", fontSize: 12 }}>
                  <div style={{ marginBottom: 6 }}>Backup Codes (store securely):</div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                    {setupData.backup_codes.map((code) => (
                      <span
                        key={code}
                        style={{
                          background: "rgba(255,255,255,0.08)",
                          border: "1px solid rgba(255,255,255,0.12)",
                          padding: "4px 6px",
                          borderRadius: 6,
                        }}
                      >
                        {code}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {(step === "setup" || step === "verify") && (
            <>
              <label style={{ display: "block", fontSize: 13, opacity: 0.9 }}>
                Authenticator Code
              </label>
              <input
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value)}
                type="text"
                inputMode="numeric"
                placeholder="123456"
                style={{
                  width: "100%",
                  padding: "12px 12px",
                  borderRadius: 10,
                  border: "1px solid rgba(255,255,255,0.18)",
                  background: "rgba(0,0,0,0.25)",
                  color: "white",
                  marginTop: 6,
                  marginBottom: 12,
                  outline: "none",
                }}
              />

              <label style={{ display: "block", fontSize: 13, opacity: 0.9 }}>
                Backup Code (optional)
              </label>
              <input
                value={backupCode}
                onChange={(e) => setBackupCode(e.target.value)}
                type="text"
                placeholder="XXXX-XXXX"
                style={{
                  width: "100%",
                  padding: "12px 12px",
                  borderRadius: 10,
                  border: "1px solid rgba(255,255,255,0.18)",
                  background: "rgba(0,0,0,0.25)",
                  color: "white",
                  marginTop: 6,
                  marginBottom: 12,
                  outline: "none",
                }}
              />
            </>
          )}

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 12,
              marginBottom: 12,
              fontSize: 13,
            }}
          >
            <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              Remember me
            </label>

            <Link to="/forgot-password" style={{ color: "#9fd3ff" }}>
              Forgot password?
            </Link>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px 14px",
              borderRadius: 12,
              border: "none",
              cursor: loading ? "not-allowed" : "pointer",
              background: loading ? "rgba(255,255,255,0.25)" : "rgba(255,255,255,0.18)",
              color: "white",
              fontWeight: 600,
            }}
          >
            {loading ? "Signing in..." : "Continue"}
          </button>

          <div style={{ marginTop: 14, fontSize: 13, opacity: 0.95 }}>
            <Link to="/terms-and-conditions" style={{ color: "#9fd3ff" }}>
              Terms & Conditions
            </Link>
          </div>

          <button
            type="button"
            onClick={() => navigate("/")}
            style={{
              width: "100%",
              marginTop: 12,
              padding: "12px 14px",
              borderRadius: 12,
              border: "1px solid rgba(255,255,255,0.2)",
              background: "rgba(255,255,255,0.12)",
              color: "white",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            Back to Portal
          </button>
        </form>
      </div>
    </div >
  );
}
