import { useNavigate } from "react-router-dom";
import portalBg from "../assets/bg_login.png";
import gabaniLogo from "../assets/gabani_logo.png";
import { registrationStatus } from "../config/registration";

// ✅ Update the logo filename based on your assets

export default function Portal() {
  const navigate = useNavigate();
  const { disabled: registrationClosed, notice, reopenLabel, contactEmail } =
    registrationStatus;

  return (
    <div
      className="min-h-screen w-full bg-cover bg-center bg-no-repeat relative"
      style={{ backgroundImage: `url(${portalBg})` }}
    >
      {/* ✅ Cinematic overlay (instead of bg-black/45) */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/35 to-black/10" />

      {/* ✅ Top-left fixed brand */}
      <div className="fixed top-5 left-5 z-20 flex items-center gap-4">
        <img
          src={gabaniLogo}
          alt="Gabani Transport Solutions"
          className="h-[7.2rem] w-[7.2rem] md:h-[8.4rem] md:w-[8.4rem] rounded-3xl object-contain ring-1 ring-white/20 bg-white/5 p-2"
        />
        <div className="text-white leading-tight">
          <div className="text-base md:text-lg font-semibold">
            Gabani Transport Solutions (GTS)
          </div>
          <div className="text-sm md:text-base text-white/75">
            Logistics Command &amp; Control
          </div>
        </div>
      </div>

      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4">
        {/* Title */}
        <div className="text-center mb-10">
          <h1 className="text-white text-4xl md:text-5xl font-bold tracking-tight">
            Gabani Transport Solutions (GTS)
          </h1>
          <p className="text-white/80 mt-2">Logistics Command &amp; Control</p>
        </div>

        {/* Cards */}
        <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* ✅ Card style: removed glass effect (no backdrop-blur) */}
          {/* Sign In */}
          <div className="rounded-2xl border border-white/15 bg-black/35 shadow-2xl p-7 text-center">
            <h3 className="text-white text-xl font-semibold">Sign In</h3>
            <p className="text-white/70 text-sm mt-2 mb-6">
              Access your dashboard and internal tools.
            </p>
            <button
              onClick={() => navigate("/login")}
              className="w-full rounded-xl bg-white/15 hover:bg-white/25 text-white font-semibold py-3 border border-white/20 transition"
            >
              Continue
            </button>
          </div>

          {/* TMS */}
          <div className="rounded-2xl border border-white/15 bg-black/35 shadow-2xl p-7 text-center">
            <h3 className="text-white text-xl font-semibold">TMS System</h3>
            <p className="text-white/70 text-sm mt-2 mb-6">
              Transport Management System for verified companies.
            </p>
            <button
              onClick={() => navigate("/login")}
              className="w-full rounded-xl bg-white/15 hover:bg-white/25 text-white font-semibold py-3 border border-white/20 transition"
            >
              Access TMS
            </button>
          </div>

          {/* Request Access */}
          <div className="rounded-2xl border border-white/15 bg-black/35 shadow-2xl p-7 text-center">
            <h3 className="text-white text-xl font-semibold">Request Access</h3>
            <p className="text-white/70 text-sm mt-2 mb-6">
              {registrationClosed
                ? notice
                : "Submit your details for portal access review."}
            </p>
            {registrationClosed ? (
              <div className="space-y-1 text-[13px] text-white/70">
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
                onClick={() => navigate("/register")}
                className="w-full rounded-xl bg-white/15 hover:bg-white/25 text-white font-semibold py-3 border border-white/20 transition"
              >
                Continue
              </button>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-10 text-center text-white/60 text-xs">
          Secure workspace. Authorization is required.
        </div>
      </div>
    </div>
  );
}
