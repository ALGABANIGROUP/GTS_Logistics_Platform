import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, ShieldAlert, Users, Cpu } from "lucide-react";
import "../ai-freight-broker/AIFreightBrokerLayout.css";

const navItems = [
  { label: "Dashboard", to: "/ai-bots/safety/dashboard", icon: LayoutDashboard },
  { label: "Incidents", to: "/ai-bots/safety/incidents", icon: ShieldAlert },
  { label: "Driver Monitor", to: "/ai-bots/safety/drivers/monitor", icon: Users },
  { label: "Vehicle Sensors", to: "/ai-bots/safety/vehicles/sensors", icon: Cpu },
];

const navLinkBase =
  "group flex w-full items-center gap-3 rounded-2xl px-3 py-3 transition border border-white/10 bg-white/[0.03]";

export default function SafetyWorkspaceLayout() {
  return (
    <div className="ai-freight-broker-layout">
      <aside className="ai-freight-broker-panel border border-white/10 bg-white/[0.04] text-slate-100 backdrop-blur-xl">
        <div className="ai-freight-panel-header">
          <p className="mb-1 text-[12px] uppercase tracking-[0.08em] text-slate-300/80">AI Control Suite</p>
          <h3 className="text-lg font-semibold leading-tight text-white">AI Safety Manager</h3>
          <p className="text-[12px] leading-tight text-slate-300/80">Safety oversight, incident response, driver monitoring, and fleet telemetry controls.</p>
        </div>
        <nav className="ai-freight-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  [
                    navLinkBase,
                    isActive
                      ? "bg-gradient-to-r from-orange-600/30 to-amber-500/20 text-white ring-1 ring-orange-400/40 shadow-lg shadow-orange-900/20"
                      : "text-slate-200 hover:bg-white/10 hover:text-white hover:ring-white/15",
                  ].join(" ")
                }
              >
                <span className="grid h-10 w-10 place-items-center rounded-2xl bg-white/10 ring-1 ring-white/15 transition group-hover:bg-white/15 group-hover:ring-white/20">
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </span>
                <span className="text-[14px] leading-none">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </aside>
      <main className="ai-freight-broker-content">
        <Outlet />
      </main>
    </div>
  );
}
