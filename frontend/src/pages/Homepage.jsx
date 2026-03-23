// frontend/src/pages/Homepage.jsx
import React from "react";
import { Link } from "react-router-dom";
import AuthLayout from "@/components/AuthLayout";
import { registrationStatus } from "../config/registration";

const Homepage = () => {
  const {
    disabled: registrationClosed,
    notice,
    reopenLabel,
    contactEmail,
  } = registrationStatus;
  return (
    <AuthLayout
      title="Logistics Command & Control"
      subtitle="AI-powered command center for dispatch, freight brokerage, and fleet operations."
      footer="Enterprise accounts are provisioned and activated by the GTS operations team. Client and partner portals are provided as whitelabel experiences under your corporate brand."
    >
      <div className="space-y-5">
        {/* Primary actions */}
        <div className="space-y-3">
          <button className="w-full">
            <Link
              to="/login"
              className="flex w-full items-center justify-center rounded-lg bg-sky-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-sky-500/40 transition hover:bg-sky-600"
            >
              Login to your GTS account
            </Link>
          </button>

          {registrationClosed ? (
            <div className="rounded-lg border border-slate-700/70 bg-slate-900/40 px-4 py-3 text-center text-xs text-slate-300">
              <p className="text-slate-100 font-semibold">Private mode</p>
              <p className="mt-1">{notice}</p>
              {reopenLabel && (
                <p className="mt-1 text-[11px] text-slate-400">
                  Expected to reopen on {reopenLabel}.
                </p>
              )}
              <p className="mt-1 text-[11px] text-slate-400">
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
            <button className="w-full">
              <Link
                to="/register"
                className="flex w-full items-center justify-center rounded-lg border border-sky-400/70 bg-slate-900/40 px-4 py-2.5 text-sm font-semibold text-sky-100 shadow-md shadow-sky-500/20 transition hover:bg-sky-500/10"
              >
                Request enterprise access
              </Link>
            </button>
          )}

          <p className="text-[11px] text-slate-300/90">
            New enterprise accounts are created in a{" "}
            <span className="font-semibold text-amber-300">
              pending approval
            </span>{" "}
            state. A GTS administrator must review and activate the account
            before production access is granted.
          </p>
        </div>

        {/* Editions section */}
        <div className="mt-4 grid gap-3 rounded-xl border border-slate-700/70 bg-slate-900/40 p-3 sm:grid-cols-2">
          <div className="rounded-lg bg-slate-900/60 p-3 border border-sky-500/30">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-sky-300 mb-1">
              GTS Enterprise Edition
            </p>
            <p className="text-xs text-slate-200 mb-2">
              Full Gabani Transport Solutions (GTS) Command Center for internal operations and
              dispatch teams.
            </p>
            <p className="text-[10px] text-slate-400">
              Includes AI dispatch, freight brokerage, finance insights,
              compliance, and documents automation.
            </p>
          </div>

          <div className="rounded-lg bg-slate-900/60 p-3 border border-emerald-400/30">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-300 mb-1">
              Client / Partner Portal
            </p>
            <p className="text-xs text-slate-200 mb-2">
              Dedicated portal for shippers, customers, and partners under your
              own brand.
            </p>
            <p className="text-[10px] text-slate-400">
              Designed for whitelabel deployment with separate login, access
              policies, and branding.
            </p>
          </div>
        </div>

        {/* Small links row */}
        <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1">
          <Link to="/login" className="hover:text-sky-200 text-sky-300">
            Already have access? Login
          </Link>
          <span className="text-slate-500">
            GTS Dispatcher • Enterprise Edition
          </span>
        </div>
      </div>

      {/* Footer is coming from AuthLayout, but we add legal line here too if needed */}
      {/* Example (optional): 
      <p className="mt-4 text-[10px] text-center text-slate-500">
        © {new Date().getFullYear()} GABANI TRANSPORT SOLUTIONS (GTS) CORP. All rights reserved.
      </p>
      */}
    </AuthLayout>
  );
};

export default Homepage;
