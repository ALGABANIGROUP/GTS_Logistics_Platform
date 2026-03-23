import React from "react";
import { Link } from "react-router-dom";

const cards = [
  {
    title: "Safety Incident Log",
    description: "Record, review, and resolve operational incidents from one controlled workspace.",
    to: "/ai-bots/safety/incidents",
  },
  {
    title: "Driver Monitor",
    description: "Track driver status, readiness, and compliance follow-up tasks.",
    to: "/ai-bots/safety/drivers/monitor",
  },
  {
    title: "Vehicle Sensors",
    description: "Review telemetry and sensor-oriented signals that affect operational safety.",
    to: "/ai-bots/safety/vehicles/sensors",
  },
];

export default function SafetyDashboardWorkspace() {
  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="overflow-hidden rounded-[32px] border border-orange-400/10 bg-[radial-gradient(circle_at_top,_rgba(249,115,22,0.16),_rgba(2,6,23,0.96)_42%)] p-6 shadow-[0_24px_80px_rgba(2,6,23,0.45)]">
        <div className="max-w-3xl">
          <div className="mb-3 inline-flex rounded-full border border-orange-400/20 bg-orange-400/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-orange-200">Safety Operations</div>
          <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">Safety Manager Workspace</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
            Dedicated space for incident oversight, compliance-oriented monitoring, and safety visibility across fleet operations.
          </p>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        {cards.map((card) => (
          <Link
            key={card.to}
            to={card.to}
            className="rounded-[30px] border border-white/10 bg-white/[0.04] p-6 transition hover:bg-white/[0.06]"
          >
            <div className="text-xs uppercase tracking-[0.24em] text-slate-400">Safety Module</div>
            <div className="mt-3 text-xl font-semibold text-white">{card.title}</div>
            <div className="mt-3 text-sm leading-6 text-slate-300">{card.description}</div>
            <div className="mt-6 text-sm font-medium text-orange-200">Open module</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
