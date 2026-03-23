import React, { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext.jsx";
import { getUserRole } from "../utils/userRole";

function formatRole(role) {
    const normalized = String(role || "").trim().toLowerCase();
    if (!normalized) return "USER";
    if (normalized === "super_admin") return "SUPER ADMIN";
    if (normalized === "system_admin") return "SYSTEM ADMIN";
    return normalized.replaceAll("_", " ").toUpperCase();
}

function getInitials(text) {
    const value = String(text || "").trim();
    if (!value) return "U";
    const parts = value.split(/\s+/).slice(0, 2);
    return parts.map((part) => part[0]?.toUpperCase()).join("") || "U";
}

export default function TopUserBar() {
    const { user, isAuthenticated, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const [currentTime, setCurrentTime] = useState(new Date());
    const [userTimezone] = useState(Intl.DateTimeFormat().resolvedOptions().timeZone);

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);

        return () => clearInterval(timer);
    }, []);

    const localTime = useMemo(() => {
        return currentTime.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            timeZone: userTimezone,
        });
    }, [currentTime, userTimezone]);

    const displayEmail = user?.email || user?.username || user?.name || "";
    const displaySub = useMemo(() => {
        const accountType =
            user?.user_type ||
            user?.broker_type ||
            user?.account_type ||
            user?.title;
        const region =
            user?.country && String(user.country).toUpperCase() !== "GLOBAL"
                ? user.country
                : user?.region;
        return [accountType, region].filter(Boolean).join(" • ");
    }, [user]);

    const role = formatRole(
        user?.effective_role ||
        user?.role ||
        user?.db_role ||
        user?.token_role ||
        getUserRole(user)
    );
    const initials = getInitials(displayEmail || user?.full_name || user?.fullName);

    const onSignIn = () => {
        const next =
            location?.pathname && location.pathname !== "/"
                ? location.pathname
                : "/dashboard";
        navigate(`/login?next=${encodeURIComponent(next)}`);
    };

    const onSignOut = async () => {
        try {
            await logout?.();
        } finally {
            navigate("/");
        }
    };

    return (
        <div className="w-full glass-panel border border-white/10 bg-slate-950/60 shadow-xl">
            <div className="mx-auto flex max-w-[1400px] items-center justify-between px-6 py-3">
                <div className="flex items-center gap-3">
                    <span className="glass-status-badge text-xs font-semibold">Online</span>

                    <div className="hidden sm:block text-xs text-slate-300">
                        <span className="font-semibold text-slate-200">{localTime}</span>
                        <span className="mx-2 text-slate-500">•</span>
                        <span className="text-slate-400">Secure logistics command center</span>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {!isAuthenticated ? (
                        <button
                            onClick={onSignIn}
                            className="glass-btn-primary glass-btn-sm rounded-full"
                        >
                            Sign In
                        </button>
                    ) : (
                        <div className="flex items-center gap-2">
                            <div className="hidden md:flex flex-col items-end">
                                <div className="text-sm font-semibold text-slate-100">
                                    {displayEmail}
                                </div>
                                {displaySub ? (
                                    <div className="text-xs text-slate-400">{displaySub}</div>
                                ) : null}
                            </div>

                            <span className="hidden sm:inline-flex items-center glass-badge glass-badge-draft text-[11px]">
                                {role}
                            </span>

                            <div className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-blue-500/25 text-sm font-bold text-blue-100 ring-1 ring-blue-300/30">
                                {initials}
                            </div>

                            <button
                                onClick={onSignOut}
                                className="hidden sm:inline-flex items-center glass-btn-secondary glass-btn-sm rounded-full"
                            >
                                Sign Out
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
