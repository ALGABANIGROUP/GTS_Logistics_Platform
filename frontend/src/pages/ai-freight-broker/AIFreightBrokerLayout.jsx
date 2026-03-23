import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, Package, MapPinned, Truck, Users, Link2 } from "lucide-react";
import "./AIFreightBrokerLayout.css";

const navItems = [
    { label: "Dashboard", to: "/ai-bots/freight_broker", icon: LayoutDashboard },
    { label: "Shipments", to: "/ai-bots/freight_broker/shipments", icon: Package },
    { label: "Map", to: "/ai-bots/freight_broker/map", icon: MapPinned },
    { label: "Live Map", to: "/ai-bots/freight_broker/live-map", icon: MapPinned },
    { label: "Vehicles", to: "/ai-bots/freight_broker/vehicles", icon: Truck },
    { label: "Drivers", to: "/ai-bots/freight_broker/drivers", icon: Users },
    { label: "Assignments", to: "/ai-bots/freight_broker/assignments", icon: Link2 },
];

const navLinkBase =
    "group flex w-full items-center gap-3 rounded-2xl px-3 py-3 transition glass-panel border border-white/10";

const AIFreightBrokerLayout = () => {
    return (
        <div className="ai-freight-broker-layout">
            <aside className="ai-freight-broker-panel glass-panel border border-white/10 text-slate-100">
                <div className="ai-freight-panel-header">
                    <p className="text-[12px] uppercase tracking-[0.08em] text-slate-300/80 mb-1">AI Control Suite</p>
                    <h3 className="text-lg font-semibold leading-tight text-white">AI Freight Broker</h3>
                    <p className="text-[12px] text-slate-300/80 leading-tight">Broker intelligence, shipments, fleet control, and live map.</p>
                </div>
                <nav className="ai-freight-nav">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        return (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                end={item.to === "/ai-bots/freight_broker"}
                                title={item.label}
                                className={({ isActive }) =>
                                    [
                                        navLinkBase,
                                        isActive
                                            ? "text-white ring-1 ring-blue-400/40 shadow-lg shadow-blue-900/30 bg-gradient-to-r from-blue-600/30 to-cyan-500/20"
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
};

export default AIFreightBrokerLayout;
