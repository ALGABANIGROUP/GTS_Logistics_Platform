import React from "react";
import { NavLink, Outlet } from "react-router-dom";

const navLinkBaseClasses =
    "block rounded-md px-3 py-2 text-sm font-medium transition-colors";
const navLinkActive =
    "bg-sky-600 text-white";
const navLinkInactive =
    "text-slate-700 hover:bg-slate-100 hover:text-slate-900";

const PartnerPortalLayout: React.FC = () => {
    return (
        <div className="min-h-screen flex bg-slate-50">
            <aside className="w-64 bg-white border-r border-slate-200 px-3 py-4 flex flex-col">
                <div className="px-2 py-3 border-b border-slate-200 mb-3">
                    <h1 className="text-lg font-semibold text-slate-900">Partner Portal</h1>
                    <p className="text-xs text-slate-500">
                        Manage your clients, orders, and earnings.
                    </p>
                </div>
                <nav className="flex-1 space-y-1">
                    <NavLink
                        to="/partner-portal"
                        end
                        className={({ isActive }) =>
                            `${navLinkBaseClasses} ${isActive ? navLinkActive : navLinkInactive
                            }`
                        }
                    >
                        Dashboard
                    </NavLink>
                    <NavLink
                        to="/partner-portal/clients"
                        className={({ isActive }) =>
                            `${navLinkBaseClasses} ${isActive ? navLinkActive : navLinkInactive
                            }`
                        }
                    >
                        Clients
                    </NavLink>
                    <NavLink
                        to="/partner-portal/orders"
                        className={({ isActive }) =>
                            `${navLinkBaseClasses} ${isActive ? navLinkActive : navLinkInactive
                            }`
                        }
                    >
                        Orders
                    </NavLink>
                    <NavLink
                        to="/partner-portal/revenue"
                        className={({ isActive }) =>
                            `${navLinkBaseClasses} ${isActive ? navLinkActive : navLinkInactive
                            }`
                        }
                    >
                        Revenue
                    </NavLink>
                    <NavLink
                        to="/partner-portal/payouts"
                        className={({ isActive }) =>
                            `${navLinkBaseClasses} ${isActive ? navLinkActive : navLinkInactive
                            }`
                        }
                    >
                        Payouts
                    </NavLink>
                    <NavLink
                        to="/partner-portal/settings"
                        className={({ isActive }) =>
                            `${navLinkBaseClasses} ${isActive ? navLinkActive : navLinkInactive
                            }`
                        }
                    >
                        Settings
                    </NavLink>
                </nav>
            </aside>
            <main className="flex-1 px-6 py-6">
                <Outlet />
            </main>
        </div>
    );
};

export default PartnerPortalLayout;
