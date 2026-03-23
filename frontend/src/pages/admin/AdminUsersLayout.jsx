import React from "react";
import RequireAuth from '../../components/RequireAuth.jsx';
import { NavLink, Outlet } from "react-router-dom";

const tabClass = ({ isActive }) =>
    `px-3 py-2 rounded-lg text-sm font-semibold ${isActive ? "bg-sky-600 text-white" : "border border-slate-300 text-slate-700 hover:bg-slate-50"
    }`;

return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
        <div className="p-6 space-y-6">
            <div>
                <h1 className="text-2xl font-bold">Users Management</h1>
                <div className="text-sm text-slate-500">/admin</div>
            </div>

            {/* Internal sub-menu (not MAIN menu) */}
            <div className="flex flex-wrap gap-2">
                <NavLink to="/admin/users" className={tabClass}>
                    Users & Roles
                </NavLink>
                <NavLink to="/admin/portal-requests" className={tabClass}>
                    Portal Requests
                </NavLink>
            </div>

            <Outlet />
        </div>
    </RequireAuth>
);
}
