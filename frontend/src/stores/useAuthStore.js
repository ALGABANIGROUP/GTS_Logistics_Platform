import { useAuth } from "../contexts/AuthContext";

export const useAuthStore = (selector) => {
    const auth = useAuth();
    const permissions = auth.permissions || [];
    const features = auth.features || [];
    const role = String(auth.user?.role_key || auth.user?.role || "").toLowerCase();
    const isAdminLike = role === "super_admin" || role === "admin" || role === "owner";

    const state = {
        user: auth.user,
        token: auth.token,
        isLoading: auth.loading,
        error: auth.error,
        permissions,
        entitlements: features,
        isAuthenticated: () => Boolean(auth.isAuthenticated),
        userRole: () => auth.user?.role_key || auth.user?.role || null,
        hasPermission: (permission) => {
            if (!permission) return true;
            if (isAdminLike) return true;
            if (permissions.includes("*")) return true;
            return permissions.includes(permission);
        },
        hasEntitlement: (entitlement) => features.includes(entitlement),
        login: auth.login,
        logout: auth.logout,
        checkAuth: async () => Boolean(auth.isAuthenticated),
    };

    return typeof selector === "function" ? selector(state) : state;
};
