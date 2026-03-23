import React from "react";

export default function SafetyDriverMonitorPage() {
  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="rounded-[32px] border border-white/10 bg-white/[0.04] p-6">
        <div className="mb-3 inline-flex rounded-full border border-orange-400/20 bg-orange-400/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-orange-200">Safety Monitor</div>
        <h1 className="text-3xl font-semibold tracking-tight text-white">Driver Safety Monitor</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
          This workspace is reserved for driver monitoring, compliance follow-up, fatigue flags, and safety-driven coaching workflows.
        </p>
      </div>
    </div>
  );
}
