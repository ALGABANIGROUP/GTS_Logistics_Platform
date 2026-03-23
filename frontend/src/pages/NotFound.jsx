import React from "react";
import { Link } from "react-router-dom";

const NotFound = () => {
  return (
    <div className="min-h-[60vh] flex items-center justify-center px-6">
      <div className="max-w-md text-center space-y-3">
        <div className="mx-auto h-12 w-12 rounded-2xl bg-slate-900/70 text-slate-100 flex items-center justify-center">
          404
        </div>
        <h1 className="text-2xl font-semibold text-slate-100">Page unavailable</h1>
        <p className="text-sm text-slate-300">
          The destination you requested is not available. Check the link or return to a known page.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link
            to="/dashboard"
            className="px-4 py-2 rounded-lg bg-white/10 text-slate-100 text-sm hover:bg-white/20 transition"
          >
            Go to dashboard
          </Link>
          <Link
            to="/ai-bots"
            className="px-4 py-2 rounded-lg border border-white/10 text-slate-100 text-sm hover:bg-white/10 transition"
          >
            Open AI bots
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
