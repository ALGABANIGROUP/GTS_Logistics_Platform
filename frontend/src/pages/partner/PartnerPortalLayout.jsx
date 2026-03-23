// frontend/src/pages/partner/PartnerPortalLayout.jsx

import React from "react";
import { NavLink, Outlet } from "react-router-dom";

const navLinkClass =
    "px-3 py-2 rounded-md text-sm font-medium inline-flex items-center gap-1";
const navLinkActive =
    "bg-blue-50 text-blue-700 border border-blue-100";
const navLinkInactive =
    "text-gray-600 hover:text-gray-900 hover:bg-gray-50";

const PartnerPortalLayout = ({ children }) => {
    // If used inside a <Route>, Outlet will render nested routes.
    // If children is passed directly, it will render children instead.
    return (
        <div className="min-h-[calc(100vh-6rem)] bg-gray-50 -m-4 p-4">
            <div className="max-w-6xl mx-auto space-y-4">
                <header className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                        <h1 className="text-2xl font-semibold text-gray-900">
                            Partner Portal
                        </h1>
                        <p className="text-sm text-gray-500">
                            Access your clients, orders, revenue and payouts.
                        </p>
                    </div>
                </header>

                <nav className="flex flex-wrap gap-2 bg-white rounded-lg shadow-sm border px-3 py-2">
                    <NavLink
                        to="/partner-portal"
                        end
                        className={({ isActive }) =>
                            `${navLinkClass} ${isActive ? navLinkActive : navLinkInactive
                            }`
                        }
                    >
                        Overview
                    </NavLink>
                    <NavLink
                        to="/partner-portal/clients"
                        className={({ isActive }) =>
                            `${navLinkClass} ${isActive ? navLinkActive : navLinkInactive
                            }`
                        }
                    >
                        Clients
                    </NavLink>
                    <NavLink
                        to="/partner-portal/orders"
                        className={({ isActive }) =>
                            `${navLinkClass} ${isActive ? navLinkActive : navLinkInactive
                            }`
                        }
                    >
                        Orders
                    </NavLink>
                    <NavLink
                        to="/partner-portal/revenue"
                        className={({ isActive }) =>
                            `${navLinkClass} ${isActive ? navLinkActive : navLinkInactive
                            }`
                        }
                    >
                        Revenue
                    </NavLink>
                    <NavLink
                        to="/partner-portal/payouts"
                        className={({ isActive }) =>
                            `${navLinkClass} ${isActive ? navLinkActive : navLinkInactive
                            }`
                        }
                    >
                        Payouts
                    </NavLink>
                    <NavLink
                        to="/partner-portal/settings"
                        className={({ isActive }) =>
                            `${navLinkClass} ${isActive ? navLinkActive : navLinkInactive
                            }`
                        }
                    >
                        Settings
                    </NavLink>
                </nav>

                <main>
                    {children || <Outlet />}
                </main>
            </div>
        </div>
    );
};

export default PartnerPortalLayout;
