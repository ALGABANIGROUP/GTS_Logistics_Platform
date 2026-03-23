// frontend/src/pages/admin/AdminPanel.jsx
import React, { useEffect, useState } from "react";
import axiosClient from "@/api/axiosClient";
import { Link, useNavigate } from "react-router-dom";
import { useRefreshSubscription } from "../../contexts/UiActionsContext.jsx";
import SystemReadinessGate from "../../components/SystemReadinessGate.jsx";
import RequireAuth from '../../components/RequireAuth.jsx';
import { isAdminRole, isSuperAdminRole, normalizeUserRole } from "../../utils/userRole";

const decodeJwt = (token) => {
    if (!token) return null;
    try {
        const payloadPart = token.split(".")[1];
        if (!payloadPart) return null;
        const json = atob(payloadPart.replace(/-/g, "+").replace(/_/g, "/"));
        return JSON.parse(json);
    } catch {
        return null;
    }
};

const normalizeUsersPayload = (payload) => {
    if (Array.isArray(payload)) return payload;
    if (Array.isArray(payload?.users)) return payload.users;
    if (Array.isArray(payload?.data?.users)) return payload.data.users;
    return [];
};

const normalizeUserRecord = (payload) => {
    if (!payload || typeof payload !== "object") return null;
    return payload.data || payload.user || payload;
};

const generateTemporaryPassword = () =>
    `GTS!${Math.random().toString(36).slice(2, 8)}A9`;

const AdminPanel = () => {
    const navigate = useNavigate();
    const [cards, setCards] = useState({
        systemHealth: { loading: true, error: null, data: null },
        dbStats: { loading: true, error: null, data: null },
        metrics: { loading: true, error: null, data: null },
        botsStatus: { loading: true, error: null, data: null },
    });
    const [currentUser, setCurrentUser] = useState(null);
    const [userLoading, setUserLoading] = useState(true);
    const [error, setError] = useState(null);
    const [users, setUsers] = useState([]);
    const [roles, setRoles] = useState([]);
    const [rolesError, setRolesError] = useState(null);
    const [orgTree, setOrgTree] = useState([]);
    const [orgError, setOrgError] = useState(null);
    const [moveUserId, setMoveUserId] = useState("");
    const [moveManagerId, setMoveManagerId] = useState("");
    const [assistantPrompt, setAssistantPrompt] = useState("");
    const [assistantLoading, setAssistantLoading] = useState(false);
    const [assistantResponse, setAssistantResponse] = useState(null);
    const [infoMessage, setInfoMessage] = useState(null);
    const [userForm, setUserForm] = useState({
        email: "",
        full_name: "",
        role: "user",
        is_active: true,
    });

    const token =
        typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    const decoded = decodeJwt(token);

    const effectiveRole = normalizeUserRole(currentUser?.role || decoded?.role || "unknown");
    const isAdmin = isAdminRole(effectiveRole);
    const isSuperAdmin = isSuperAdminRole(effectiveRole);

    const prettyRole = (() => {
        switch (effectiveRole) {
            case "super_admin":
                return "Super Admin";
            case "admin":
                return "Administrator";
            case "manager":
                return "Manager";
            case "user":
                return "User";
            case "partner":
                return "Partner";
            default:
                return effectiveRole;
        }
    })();

    const quickActions = [
        {
            label: "ðŸ”§ System Admin Bot",
            to: "/ai-bots/system-admin",
            available: isSuperAdmin,
            reason: "Requires super admin role.",
        },
        {
            label: "Open AI Finance Bot",
            to: "/ai-bots/finance",
            available: isAdmin,
            reason: "Requires admin role.",
        },
        {
            label: "View all AI bots",
            to: "/ai-bots",
            available: isAdmin,
            reason: "Requires admin role.",
        },
        {
            label: "Review platform expenses",
            to: "/platform-expenses",
            available: isAdmin,
            reason: "Requires admin role.",
        },
        {
            label: "View email logs",
            to: "/emails/logs",
            available: isAdmin,
            reason: "Requires admin role.",
        },
    ];

    const updateCard = (key, patch) => {
        setCards((prev) => ({
            ...prev,
            [key]: { ...prev[key], ...patch },
        }));
    };

    const loadCard = async (key, requestFn) => {
        updateCard(key, { loading: true, error: null });
        try {
            const res = await requestFn();
            updateCard(key, { loading: false, data: res?.data || null });
        } catch (err) {
            const message =
                err?.response?.data?.detail ||
                err?.message ||
                "Failed to load card data.";
            updateCard(key, { loading: false, error: message });
        }
    };

    const loadCards = () => {
        loadCard("systemHealth", () => axiosClient.get("/api/v1/system/health"));
        loadCard("dbStats", () => axiosClient.get("/api/v1/system/database/stats"));
        loadCard("metrics", () => axiosClient.get("/api/v1/system/metrics"));
        loadCard("botsStatus", () => axiosClient.get("/api/v1/system/bots/status"));
    };

    const loadUserData = async () => {
        setUserLoading(true);
        setError(null);
        try {
            const [meRes, usersRes] = await Promise.allSettled([
                axiosClient.get("/users/me"),
                axiosClient.get("/api/v1/admin/users"),
            ]);

            if (meRes.status === "fulfilled") {
                setCurrentUser(meRes.value.data);
            } else {
                setError("Failed to load user profile.");
            }

            if (usersRes.status === "fulfilled") {
                setUsers(normalizeUsersPayload(usersRes.value.data));
            } else {
                setError("Failed to load users list.");
            }
        } catch (err) {
            console.error("[AdminPanel] loadUserData error:", err);
            const msg =
                err.response?.data?.detail ||
                err.message ||
                "Failed to load admin dashboard.";
            setError(msg);
        } finally {
            setUserLoading(false);
        }
    };

    const loadOrgTree = async () => {
        setOrgError(null);
        try {
            const res = await axiosClient.get("/api/v1/admin/org/tree");
            setOrgTree(res.data?.data?.tree || []);
        } catch (err) {
            setOrgError(err?.normalized?.detail || "Failed to load org chart.");
        }
    };

    const loadRoles = async () => {
        setRolesError(null);
        try {
            const res = await axiosClient.get("/api/v1/admin/roles");
            setRoles(res.data?.data?.roles || []);
        } catch (err) {
            setRolesError(err?.normalized?.detail || "Failed to load roles.");
        }
    };

    const moveUser = async () => {
        if (!moveUserId) return;
        try {
            await axiosClient.post(
                `/api/v1/admin/org/units/${moveUserId}/move`,
                null,
                { params: { parent_id: moveManagerId ? Number(moveManagerId) : null } }
            );
            setMoveUserId("");
            setMoveManagerId("");
            await loadOrgTree();
        } catch (err) {
            setOrgError(err?.normalized?.detail || "Failed to move user.");
        }
    };

    const loadData = () => {
        loadCards();
        loadUserData();
        loadOrgTree();
        loadRoles();
    };

    useRefreshSubscription(() => {
        loadData();
    });

    useEffect(() => {
        loadData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleUserCreate = async () => {
        if (!userForm.email) return;
        try {
            const temporaryPassword = generateTemporaryPassword();
            const payload = {
                email: userForm.email,
                full_name: userForm.full_name || userForm.email,
                role: userForm.role,
                is_active: userForm.is_active,
                password: temporaryPassword,
            };
            const res = await axiosClient.post("/api/v1/admin/users", payload);
            const created = normalizeUserRecord(res.data);
            if (created) {
                setUsers((prev) => [...prev, created]);
            }
            setUserForm({ email: "", full_name: "", role: "user", is_active: true });
            setInfoMessage(`User created with temporary password: ${temporaryPassword}`);
        } catch (err) {
            console.error("[AdminPanel] create user error:", err);
            setError("Failed to create user.");
        }
    };

    const handleUserRoleChange = async (userId, role) => {
        try {
            const res = await axiosClient.patch(`/api/v1/admin/users/${userId}`, { role });
            const updated = normalizeUserRecord(res.data);
            if (updated) {
                setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
            }
        } catch (err) {
            console.error("[AdminPanel] update role error:", err);
            setError("Failed to update user role.");
        }
    };

    const handleUserToggleActive = async (userId, isActive) => {
        try {
            const res = await axiosClient.patch(`/api/v1/admin/users/${userId}`, {
                is_active: !isActive,
            });
            const updated = normalizeUserRecord(res.data);
            if (updated) {
                setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
            }
        } catch (err) {
            console.error("[AdminPanel] update user status error:", err);
            setError("Failed to update user status.");
        }
    };

    const handleUserDelete = async (userId) => {
        try {
            await axiosClient.delete(`/api/v1/admin/users/${userId}`);
            setUsers((prev) => prev.filter((u) => u.id !== userId));
        } catch (err) {
            console.error("[AdminPanel] delete user error:", err);
            setError("Failed to delete user.");
        }
    };

    const handleUserBanToggle = async (userId, isBanned) => {
        try {
            const res = await axiosClient.patch(`/api/v1/admin/users/${userId}`, {
                is_banned: !isBanned,
                ban_reason: !isBanned ? "Banned from admin panel" : null,
                banned_until: null,
            });
            const updated = normalizeUserRecord(res.data);
            if (updated) {
                setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
            }
        } catch (err) {
            console.error("[AdminPanel] ban/unban error:", err);
            setError("Failed to update ban status.");
        }
    };

    const handleAssistantAsk = async () => {
        if (!assistantPrompt.trim()) return;
        setAssistantLoading(true);
        setAssistantResponse(null);
        try {
            const payload = {
                message: assistantPrompt.trim(),
                context: { action: "activity_summary", read_only: true },
                meta: { source: "admin_panel" },
            };
            const res = await axiosClient.post("/api/v1/ai/bots/available/system_admin/run", payload);
            setAssistantResponse(res.data?.result || res.data || {});
        } catch (err) {
            setAssistantResponse({
                ok: false,
                error: err?.normalized?.detail || err?.message || "Assistant request failed.",
            });
        } finally {
            setAssistantLoading(false);
        }
    };

    const renderUserNode = (node, depth = 0) => (
        <div key={node.id} className="space-y-1" style={{ marginLeft: depth * 16 }}>
            <div className="flex flex-wrap items-center gap-2 text-xs text-slate-200">
                <span className="font-semibold text-slate-100">
                    {node.name}
                </span>
                <span className="text-[10px] text-slate-400">{node.email}</span>
                <span className="rounded-full border border-white/10 px-2 py-0.5 text-[10px] uppercase text-slate-300">
                    {node.role}
                </span>
                {!node.is_active ? (
                    <span className="rounded-full border border-rose-400/40 px-2 py-0.5 text-[10px] text-rose-200">
                        Inactive
                    </span>
                ) : null}
                {node.is_banned ? (
                    <span className="rounded-full border border-amber-400/40 px-2 py-0.5 text-[10px] text-amber-200">
                        Banned
                    </span>
                ) : null}
            </div>
            {Array.isArray(node.children) &&
                node.children.map((child) => renderUserNode(child, depth + 1))}
        </div>
    );

    const renderCardState = (card, onRetry, renderContent, emptyMessage) => {
        if (card.loading) {
            return <p className="text-xs text-slate-500">Loading...</p>;
        }
        if (card.error) {
            return (
                <div className="flex items-center justify-between gap-2 text-xs text-rose-600">
                    <span>{card.error}</span>
                    <button
                        type="button"
                        onClick={onRetry}
                        className="px-2 py-1 rounded-md border border-rose-200 text-rose-700 hover:bg-rose-50"
                    >
                        Retry
                    </button>
                </div>
            );
        }
        if (!card.data) {
            return <p className="text-xs text-slate-500">{emptyMessage}</p>;
        }
        return renderContent(card.data);
    };

    const renderSystemHealth = () => {
        const card = cards.systemHealth;
        return renderCardState(
            card,
            () => loadCard("systemHealth", () => axiosClient.get("/api/v1/system/health")),
            (data) => {
                const ok =
                    data.ok === true ||
                    data.status === "ok" ||
                    data.status === "healthy";

                return (
                    <div>
                        <p
                            className={`text-sm font-semibold ${ok ? "text-emerald-600" : "text-rose-600"
                                }`}
                        >
                            {ok ? "Healthy" : "Issue detected"}
                        </p>
                        {data.details && (
                            <ul className="mt-2 list-disc list-inside text-xs text-slate-600 space-y-1">
                                {Array.isArray(data.details)
                                    ? data.details.map((d, idx) => (
                                        <li key={idx}>{String(d)}</li>
                                    ))
                                    : Object.entries(data.details).map(([k, v]) => (
                                        <li key={k}>
                                            <span className="font-semibold">{k}:</span>{" "}
                                            <span>{String(v)}</span>
                                        </li>
                                    ))}
                            </ul>
                        )}
                    </div>
                );
            },
            "No health data."
        );
    };

    const renderDbStats = () => {
        const card = cards.dbStats;
        return renderCardState(
            card,
            () => loadCard("dbStats", () => axiosClient.get("/api/v1/system/database/stats")),
            (data) => {
                const stats = data.stats || data;
                return (
                    <div className="space-y-1 text-xs text-slate-700">
                        {stats.engine && (
                            <p>
                                <span className="font-semibold">Engine:</span>{" "}
                                <span className="font-mono">{stats.engine}</span>
                            </p>
                        )}
                        {stats.url && (
                            <p>
                                <span className="font-semibold">URL:</span>{" "}
                                <span className="font-mono break-all text-[10px]">
                                    {stats.url}
                                </span>
                            </p>
                        )}
                        {typeof stats.total_tables === "number" && (
                            <p>
                                <span className="font-semibold">Tables:</span>{" "}
                                {stats.total_tables}
                            </p>
                        )}
                        {typeof stats.total_rows === "number" && (
                            <p>
                                <span className="font-semibold">Rows (approx):</span>{" "}
                                {stats.total_rows.toLocaleString()}
                            </p>
                        )}
                    </div>
                );
            },
            "No database stats."
        );
    };

    const renderMetrics = () => {
        const card = cards.metrics;
        return renderCardState(
            card,
            () => loadCard("metrics", () => axiosClient.get("/api/v1/system/metrics")),
            (data) => {
                const m = data.metrics || data;
                return (
                    <div className="grid grid-cols-2 gap-3 text-xs">
                        {Object.entries(m).map(([k, v]) => (
                            <div key={k} className="flex flex-col">
                                <span className="text-slate-500">{k}</span>
                                <span className="font-semibold text-slate-800">
                                    {typeof v === "number" ? v.toLocaleString() : String(v)}
                                </span>
                            </div>
                        ))}
                    </div>
                );
            },
            "No metrics available."
        );
    };

    const renderBotsStatus = () => {
        const card = cards.botsStatus;
        return renderCardState(
            card,
            () => loadCard("botsStatus", () => axiosClient.get("/api/v1/system/bots/status")),
            (data) => {
                const bots = data.bots || data;

                if (!bots || Object.keys(bots).length === 0) {
                    return <p className="text-xs text-slate-500">No bots registered.</p>;
                }

                return (
                    <ul className="space-y-1 text-xs text-slate-700">
                        {Object.entries(bots).map(([name, info]) => {
                            const status =
                                typeof info === "object" && info !== null
                                    ? info.status || info.role || "ok"
                                    : String(info);

                            const ok =
                                String(status).toLowerCase().includes("ok") ||
                                String(status).toLowerCase().includes("online");

                            return (
                                <li
                                    key={name}
                                    className="flex items-center justify-between border-b border-slate-100 last:border-none pb-1"
                                >
                                    <span className="font-mono text-[11px]">{name}</span>
                                    <span
                                        className={`px-2 py-0.5 rounded-full text-[10px] ${ok
                                            ? "bg-emerald-100 text-emerald-700 border border-emerald-300"
                                            : "bg-rose-100 text-rose-700 border border-rose-300"
                                            }`}
                                    >
                                        {String(status)}
                                    </span>
                                </li>
                            );
                        })}
                    </ul>
                );
            },
            "No bot status data."
        );
    };

    return (
        <RequireAuth roles={["admin", "owner", "super_admin"]}>
            <SystemReadinessGate>
                <div className="glass-page p-4 md:p-6 max-w-7xl mx-auto space-y-6 relative z-10" style={{
                    background: "rgba(18, 24, 38, 0.55)",
                    backgroundColor: "rgba(18, 24, 38, 0.8)", // Fallback for backdrop-filter
                    backdropFilter: "blur(12px)",
                    WebkitBackdropFilter: "blur(12px)" // Safari prefix
                }}>
                    {/* Header */}
                    <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-3">
                        <div>
                            <h1 className="text-xl md:text-2xl font-bold text-slate-900">
                                Admin Control Panel
                            </h1>
                            <p className="text-xs md:text-sm text-slate-600 mt-1">
                                Central dashboard for monitoring system health, database status, and
                                AI bots for Gabani Transport Solutions (GTS).
                            </p>
                        </div>

                        <div className="flex flex-col items-end gap-1 text-[11px] text-slate-600">
                            <div className="flex items-center gap-2">
                                <span className="font-semibold">User:</span>
                                <span className="px-2 py-0.5 rounded-full bg-slate-100 border border-slate-200">
                                    {currentUser?.email || decoded?.email || "unknown"}
                                </span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="font-semibold">Role:</span>
                                <span className="px-2 py-0.5 rounded-full bg-slate-100 border border-slate-200 flex items-center gap-2">
                                    <span>{prettyRole}</span>
                                    {isSuperAdmin && (
                                        <span className="px-1.5 py-0.5 rounded-full text-[9px] bg-indigo-100 text-indigo-700 border border-indigo-300 uppercase tracking-wide">
                                            Elevated
                                        </span>
                                    )}
                                </span>
                            </div>
                            <button
                                onClick={loadData}
                                className="mt-1 px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 transition"
                            >
                                Refresh
                            </button>
                        </div>
                    </div>

                    {/* Error banner */}
                    {error && (
                        <div className="text-xs text-rose-700 bg-rose-50 border border-rose-200 rounded-lg px-3 py-2">
                            {error}
                        </div>
                    )}

                    {infoMessage && (
                        <div className="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                            {infoMessage}
                        </div>
                    )}

                    {/* Loading banner */}
                    {userLoading && (
                        <div className="text-xs text-slate-600 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
                            Loading admin data...
                        </div>
                    )}

                    {/* Grid cards */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                        {/* System health */}
                        <div className="dashboard-card flex flex-col gap-2">
                            <div className="flex items-center justify-between">
                                <h2 className="text-sm font-semibold text-slate-900">
                                    System health
                                </h2>
                                <span className="text-[10px] text-slate-500">/api/v1/system/health</span>
                            </div>
                            {renderSystemHealth()}
                        </div>

                        {/* DB stats */}
                        <div className="dashboard-card flex flex-col gap-2">
                            <div className="flex items-center justify-between">
                                <h2 className="text-sm font-semibold text-slate-900">
                                    Database stats
                                </h2>
                                <span className="text-[10px] text-slate-500">
                                    /api/v1/system/database/stats
                                </span>
                            </div>
                            {renderDbStats()}
                        </div>

                        {/* Metrics */}
                        <div className="dashboard-card flex flex-col gap-2">
                            <div className="flex items-center justify-between">
                                <h2 className="text-sm font-semibold text-slate-900">
                                    System metrics
                                </h2>
                                <span className="text-[10px] text-slate-500">/api/v1/system/metrics</span>
                            </div>
                            {renderMetrics()}
                        </div>
                    </div>

                    {/* Second row: AI bots + links */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                        {/* AI bots status */}
                        <div className="dashboard-card flex flex-col gap-2 lg:col-span-2">
                            <div className="flex items-center justify-between">
                                <h2 className="text-sm font-semibold text-slate-900">
                                    AI bots status
                                </h2>
                                <span className="text-[10px] text-slate-500">
                                    /api/v1/system/bots/status
                                </span>
                            </div>
                            {renderBotsStatus()}
                        </div>

                        {/* Quick links */}
                        <div className="dashboard-card flex flex-col gap-3 text-xs">
                            <h2 className="text-sm font-semibold text-slate-900">
                                Quick admin actions
                            </h2>
                            <ul className="space-y-1.5">
                                {quickActions.map((action) => (
                                    <li key={action.to}>
                                        {action.available ? (
                                            <Link
                                                to={action.to}
                                                className="text-sky-700 hover:text-sky-900 underline underline-offset-4"
                                            >
                                                {action.label}
                                            </Link>
                                        ) : (
                                            <span
                                                className="text-slate-400 cursor-not-allowed"
                                                title={action.reason}
                                            >
                                                {action.label}
                                            </span>
                                        )}
                                    </li>
                                ))}
                            </ul>
                            <p className="text-[10px] text-slate-500 mt-1">
                                These actions require a valid admin or manager role on the backend
                                JWT.
                            </p>
                        </div>
                    </div>

                    {/* Super admin / owner section */}
                    {isSuperAdmin && (
                        <div className="dashboard-card border border-indigo-200 bg-indigo-50 flex flex-col gap-2 text-xs mt-4">
                            <div className="flex items-center justify-between">
                                <h2 className="text-sm font-semibold text-indigo-900">
                                    Role and permissions overview
                                </h2>
                                <span className="px-2 py-0.5 rounded-full text-[10px] bg-white border border-indigo-200 text-indigo-700">
                                    Super-level access
                                </span>
                            </div>
                            <p className="text-indigo-900">
                                You are signed in with an elevated role ({prettyRole}). This role is
                                intended for platform owners and top-level administrators.
                            </p>
                            <ul className="list-disc list-inside space-y-1 text-indigo-900">
                                <li>Full access to admin dashboards and monitoring tools.</li>
                                <li>
                                    Can be extended later to manage users, roles, and partner
                                    permissions.
                                </li>
                                <li>
                                    Recommended to keep this role limited to a small number of trusted
                                    accounts.
                                </li>
                            </ul>
                            <p className="text-[10px] text-indigo-700 mt-1">
                                User and role management tools are available below for this role.
                            </p>
                        </div>
                    )}

                    {/* User management */}
                    <div className="dashboard-card text-slate-100">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-semibold text-slate-100">
                                Users & Roles
                            </h2>
                            <span className="text-[10px] text-slate-400">/admin</span>
                        </div>

                        <div className="mt-4 grid gap-3 lg:grid-cols-[1fr_140px_140px_140px]">
                            <input
                                value={userForm.email}
                                onChange={(e) =>
                                    setUserForm((prev) => ({ ...prev, email: e.target.value }))
                                }
                                placeholder="user@company.com"
                                className="rounded-lg border border-white/10 bg-slate-950/40 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-400"
                            />
                            <input
                                value={userForm.full_name}
                                onChange={(e) =>
                                    setUserForm((prev) => ({ ...prev, full_name: e.target.value }))
                                }
                                placeholder="Full name"
                                className="rounded-lg border border-white/10 bg-slate-950/40 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-400"
                            />
                            <select
                                value={userForm.role}
                                onChange={(e) =>
                                    setUserForm((prev) => ({ ...prev, role: e.target.value }))
                                }
                                className="rounded-lg border border-white/10 bg-slate-950/40 px-3 py-2 text-sm text-slate-100"
                            >
                                <option value="super_admin">SUPER_ADMIN</option>
                                <option value="admin">ADMIN</option>
                                <option value="user">USER</option>
                            </select>
                            <button
                                onClick={handleUserCreate}
                                disabled={!isAdmin}
                                title={!isAdmin ? "Requires admin role." : undefined}
                                className="rounded-lg bg-sky-500 px-3 py-2 text-sm font-semibold text-white hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                Create
                            </button>
                        </div>

                        <div className="mt-4 divide-y divide-white/10">
                            {users.length === 0 ? (
                                <div className="text-xs text-slate-400 py-3">
                                    No users found.
                                </div>
                            ) : (
                                users.map((u) => (
                                    <div
                                        key={u.id}
                                        className="flex flex-wrap items-center justify-between gap-3 py-3 text-xs"
                                    >
                                        <div>
                                            <div className="text-sm font-semibold text-slate-100">
                                                {u.email}
                                            </div>
                                            <div className="text-[11px] text-slate-400">
                                                {u.full_name || "No name"}
                                            </div>
                                            {u.is_banned ? (
                                                <div className="mt-1 text-[10px] text-rose-200">
                                                    Banned
                                                </div>
                                            ) : null}
                                        </div>

                                        <div className="flex items-center gap-2">
                                            <select
                                                value={String(u.role || "user").toLowerCase()}
                                                onChange={(e) =>
                                                    handleUserRoleChange(u.id, e.target.value)
                                                }
                                                disabled={!isAdmin}
                                                title={!isAdmin ? "Requires admin role." : undefined}
                                                className="rounded-lg border border-white/10 bg-slate-950/40 px-2 py-1 text-[11px] text-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
                                            >
                                                <option value="super_admin">SUPER_ADMIN</option>
                                                <option value="admin">ADMIN</option>
                                                <option value="user">USER</option>
                                            </select>

                                            <button
                                                onClick={() => handleUserToggleActive(u.id, u.is_active)}
                                                disabled={!isAdmin}
                                                title={!isAdmin ? "Requires admin role." : undefined}
                                                className={`rounded-lg px-2 py-1 text-[11px] font-semibold ${u.is_active
                                                    ? "bg-emerald-500/20 text-emerald-200"
                                                    : "bg-rose-500/20 text-rose-200"
                                                    } disabled:cursor-not-allowed disabled:opacity-60`}
                                            >
                                                {u.is_active ? "Active" : "Disabled"}
                                            </button>

                                            <button
                                                onClick={() => handleUserBanToggle(u.id, u.is_banned)}
                                                disabled={!isAdmin}
                                                title={!isAdmin ? "Requires admin role." : undefined}
                                                className={`rounded-lg px-2 py-1 text-[11px] font-semibold ${u.is_banned
                                                    ? "bg-amber-500/20 text-amber-200"
                                                    : "bg-white/10 text-slate-200"
                                                    } disabled:cursor-not-allowed disabled:opacity-60`}
                                            >
                                                {u.is_banned ? "Unban" : "Ban"}
                                            </button>

                                            <button
                                                onClick={() => handleUserDelete(u.id)}
                                                disabled={!isAdmin}
                                                title={!isAdmin ? "Requires admin role." : undefined}
                                                className="rounded-lg px-2 py-1 text-[11px] text-rose-200 hover:bg-rose-500/20 disabled:cursor-not-allowed disabled:opacity-60"
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    <div className="dashboard-card text-slate-100">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-semibold text-slate-100">Org Chart</h2>
                            <span className="text-[10px] text-slate-400">/admin</span>
                        </div>

                        {orgError ? (
                            <div className="mt-3 rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-100">
                                {orgError}
                            </div>
                        ) : null}

                        <div className="mt-4 space-y-2">
                            {orgTree.length === 0 ? (
                                <div className="text-xs text-slate-400">No org chart data.</div>
                            ) : (
                                orgTree.map((node) => renderUserNode(node))
                            )}
                        </div>

                        <div className="mt-4 rounded-xl border border-white/10 bg-white/5 p-3">
                            <div className="text-xs font-semibold text-slate-200">Move User</div>
                            <div className="mt-2 flex flex-wrap gap-2">
                                <input
                                    className="w-32 rounded border border-white/20 bg-black/30 px-2 py-1 text-xs text-white"
                                    placeholder="User ID"
                                    value={moveUserId}
                                    onChange={(e) => setMoveUserId(e.target.value)}
                                />
                                <input
                                    className="w-36 rounded border border-white/20 bg-black/30 px-2 py-1 text-xs text-white"
                                    placeholder="Manager ID (optional)"
                                    value={moveManagerId}
                                    onChange={(e) => setMoveManagerId(e.target.value)}
                                />
                                <button
                                    className="rounded border border-white/20 px-3 py-1 text-xs text-white hover:bg-white/10"
                                    onClick={moveUser}
                                >
                                    Move
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="dashboard-card text-slate-100">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-semibold text-slate-100">Roles</h2>
                            <span className="text-[10px] text-slate-400">/admin</span>
                        </div>
                        {rolesError ? (
                            <div className="mt-3 rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-100">
                                {rolesError}
                            </div>
                        ) : null}
                        <div className="mt-4 divide-y divide-white/10">
                            {roles.length === 0 ? (
                                <div className="text-xs text-slate-400 py-3">No roles found.</div>
                            ) : (
                                roles.map((roleItem) => (
                                    <div key={roleItem.id} className="py-3 text-xs">
                                        <div className="text-sm font-semibold text-slate-100">
                                            {roleItem.name}
                                        </div>
                                        <div className="text-[11px] text-slate-400">
                                            {roleItem.description || "No description"}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    <div className="dashboard-card text-slate-100">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-semibold text-slate-100">Admin Assistant</h2>
                            <span className="text-[10px] text-slate-400">read-only</span>
                        </div>
                        <div className="mt-3 flex flex-col gap-3">
                            <textarea
                                value={assistantPrompt}
                                onChange={(e) => setAssistantPrompt(e.target.value)}
                                placeholder="Ask about access, roles, or recent activity..."
                                className="min-h-[80px] rounded-lg border border-white/10 bg-slate-950/40 p-3 text-sm text-slate-100 placeholder:text-slate-400"
                            />
                            <button
                                onClick={handleAssistantAsk}
                                disabled={!assistantPrompt.trim() || assistantLoading}
                                className="self-start rounded-lg bg-sky-500 px-3 py-2 text-xs font-semibold text-white hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                {assistantLoading ? "Working..." : "Ask Assistant"}
                            </button>
                            {assistantResponse ? (
                                <pre className="whitespace-pre-wrap rounded-lg border border-white/10 bg-black/30 p-3 text-[11px] text-slate-200">
                                    {JSON.stringify(assistantResponse, null, 2)}
                                </pre>
                            ) : null}
                        </div>
                    </div>
                </div>
            </SystemReadinessGate>
        </RequireAuth>
    );
};

export default AdminPanel;
