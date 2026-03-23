import React from "react";
import { useNavigate } from "react-router-dom";
import GlassCard from "../components/ui/GlassCard.jsx";
import gabaniLogo from "../assets/gabani_logo.png";
import { registrationStatus } from "../config/registration";
import "./PortalLanding.css";

export default function PortalLanding() {
  React.useEffect(() => {
    document.body.classList.add("portal");
    return () => document.body.classList.remove("portal");
  }, []);

  const navigate = useNavigate();
  const { disabled: registrationClosed, notice, reopenLabel, contactEmail } =
    registrationStatus;

  return (
    <div className="portal-landing min-h-screen h-screen overflow-hidden">
      <div className="portal-overlay" />

      <div className="portal-content max-h-screen overflow-hidden">
        <header className="portal-header">
          <div className="portal-brand">
            <img
              src={gabaniLogo}
              alt="Gabani Transport Solutions"
              className="portal-logo"
            />
            <div className="portal-company">Gabani Transport Solutions (GTS)</div>
          </div>
          <h1 className="portal-title text-lg md:text-xl">
            Logistics Command &amp; Control
          </h1>
          <p className="portal-subtitle">
            Unified Platform for Comprehensive Transportation Management and
            Intelligent Load Matching Across Business Networks
          </p>
        </header>

        <main className="portal-cards">
          <GlassCard className="portal-card backdrop-blur-none bg-[#0f0f0f]/85 border-white/15 shadow-[0_20px_50px_rgba(0,0,0,0.45)]">
            <div className="portal-card-icon" aria-hidden="true">
              →
            </div>
            <h2 className="portal-card-title">Sign In</h2>
            <p className="portal-card-desc">
              Continue to the unified login for TMS, LoadBoard, and
              <br />
              admin dashboards.
            </p>
            <button
              className="portal-btn h-12 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/60 focus-visible:ring-offset-2 focus-visible:ring-offset-black/30"
              onClick={() => navigate("/login")}
            >
              Continue
            </button>
          </GlassCard>

          <GlassCard className="portal-card backdrop-blur-none bg-[#0f0f0f]/85 border-white/15 shadow-[0_20px_50px_rgba(0,0,0,0.45)]">
            <div className="portal-card-icon" aria-hidden="true">
              U
            </div>
            <h2 className="portal-card-title">Request Access</h2>
            <p className="portal-card-desc">
              {registrationClosed ? (
                <>
                  {notice}
                  <br />
                  {reopenLabel
                    ? `Expected to reopen on ${reopenLabel}.`
                    : "Registration is paused for now."}
                </>
              ) : (
                <>
                  Register your company details, choose a system, and
                  <br />
                  assign a role.
                </>
              )}
            </p>
            {registrationClosed ? (
              <div className="mt-2 space-y-1 text-center text-[13px] text-white/70">
                {reopenLabel && (
                  <p className="text-xs text-white/80">
                    Reopening on {reopenLabel}.
                  </p>
                )}
                <p className="text-xs text-white/60">
                  Contact{" "}
                  <a
                    href={`mailto:${contactEmail}`}
                    className="text-white underline"
                  >
                    {contactEmail}
                  </a>{" "}
                  for expedited approval.
                </p>
              </div>
            ) : (
              <button
                className="portal-btn h-12 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/60 focus-visible:ring-offset-2 focus-visible:ring-offset-black/30"
                onClick={() => navigate("/register")}
              >
                Continue
              </button>
            )}
          </GlassCard>

        </main>

        <footer className="portal-footer">
          <div>© 2026 Gabani Transport Solutions (GTS)</div>
          <div className="portal-footer-sub">
            Secure workspace. Authorization is required. {" • "}
            <button
              onClick={() => navigate("/terms-and-conditions")}
              style={{
                background: "none",
                border: "none",
                color: "inherit",
                textDecoration: "underline",
                cursor: "pointer",
                padding: 0,
                font: "inherit",
              }}
            >
              Terms & Conditions
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}
