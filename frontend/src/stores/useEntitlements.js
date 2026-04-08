import { create } from "zustand";
import { readAuthToken } from "../utils/authStorage";
import { getUserRole, isSuperAdminRole } from "../utils/userRole";

const readSessionJson = (key) => {
    if (typeof window === "undefined") {
        return null;
    }
    try {
        const raw = window.sessionStorage.getItem(key);
        return raw ? JSON.parse(raw) : null;
    } catch {
        return null;
    }
};

const decodeJwtPayload = (token) => {
    try {
        const base64Url = String(token || "").split(".")[1];
        if (!base64Url) return null;
        const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
        const jsonPayload = decodeURIComponent(
            atob(base64)
                .split("")
                .map((char) => `%${(`00${char.charCodeAt(0).toString(16)}`).slice(-2)}`)
                .join("")
        );
        return JSON.parse(jsonPayload);
    } catch {
        return null;
    }
};

export const useEntitlements = create((set, get) => ({
    loaded: false,
    role_key: null,
    permissions: [],
    features: [],
    modules: null,
    plan: null,
    subscription: null,
    init: async () => {
        const token = readAuthToken();
        if (!token) {
            set({
                loaded: false,
                role_key: null,
                permissions: [],
                features: [],
                modules: null,
                plan: null,
                subscription: null,
            });
            return;
        }

        const meta = readSessionJson("auth_context");
        const user = readSessionJson("user");

        const ent = meta?.entitlements || null;
        const roleFromEnt = ent?.role_key;
        const roleFromUser = getUserRole(user);
        const roleFromMeta = getUserRole(meta?.user);
        const roleFromToken = getUserRole(decodeJwtPayload(token));
        const finalRole = roleFromEnt || roleFromUser || roleFromMeta || roleFromToken || null;
        const effectivePermissions = ent?.permissions || meta?.permissions || [];

        set({
            loaded: true,
            role_key: finalRole,
            permissions: effectivePermissions,
            features: ent?.features || meta?.features || [],
            modules: ent?.modules || meta?.modules || null,
            plan: ent?.plan || meta?.plan || null,
            subscription: ent?.subscription || meta?.subscription || null,
        });
    },

    isSuperAdmin: () => {
        const r = get().role_key;
        return isSuperAdminRole(r);
    },

    hasFeature: (f) => get().features?.includes(f),
    hasPermission: (p) => {
        const role = get().role_key;
        const permissions = get().permissions || [];
        if (!p) return true;
        if (isSuperAdminRole(role)) return true;
        if (permissions.includes("*")) return true;
        return permissions.includes(p);
    },
    hasPlan: (p) => {
        const current = (get().plan || "").toLowerCase();
        return !p || current === String(p).toLowerCase();
    },
    hasSubscription: (s) => {
        const current = (get().subscription || "").toLowerCase();
        return !s || current === String(s).toLowerCase();
    },
    hasModule: (m) => {
        const modules = get().modules;
        if (!modules) return true;
        if (Array.isArray(modules)) return modules.includes(m);
        const keys = Object.keys(modules);
        if (keys.length === 0) return true;
        return Boolean(modules[m]);
    },
}));
