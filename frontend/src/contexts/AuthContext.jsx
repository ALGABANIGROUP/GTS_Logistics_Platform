/* eslint-disable react/prop-types */

// frontend/src/contexts/AuthContext.jsx
import axios from "axios";
import {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useState,
} from "react";
import axiosClient from "../api/axiosClient";
import { API_BASE_URL } from "../config/env";
import {
    clearAuthCache,
    readAuthToken,
    writeAuthToken,
    writeRefreshToken,
} from "../utils/authStorage";

const API_URL = String(API_BASE_URL || "").replace(/\/+$/, "");

const AuthContext = createContext();

const normalizeAuthPayload = (payload) => {
    if (!payload) {
        return null;
    }

    const rawUser =
        payload.user && typeof payload.user === "object" ? payload.user : payload;
    if (!rawUser || typeof rawUser !== "object") {
        return null;
    }

    const entitlements =
        payload.entitlements && typeof payload.entitlements === "object"
            ? payload.entitlements
            : {};
    const planModules =
        payload.plan && payload.plan.modules && typeof payload.plan.modules === "object"
            ? payload.plan.modules
            : {};
    const moduleKeys = Array.isArray(entitlements.modules) ? entitlements.modules : [];
    const modules = { ...planModules };
    for (const key of moduleKeys) {
        if (key) {
            modules[key] = true;
        }
    }

    const features = Array.isArray(entitlements.features)
        ? entitlements.features
        : Array.isArray(rawUser.features)
            ? rawUser.features
            : [];

    const bots = Array.isArray(entitlements.bots)
        ? entitlements.bots
        : Array.isArray(rawUser.assigned_bots)
            ? rawUser.assigned_bots
            : [];

    return {
        ...rawUser,
        permissions: Array.isArray(rawUser.permissions) ? rawUser.permissions : [],
        features,
        modules,
        assigned_bots: Array.isArray(rawUser.assigned_bots) ? rawUser.assigned_bots : bots,
        authMeta: {
            entitlements,
            tenant: payload.tenant || null,
            plan: payload.plan || null,
            system: payload.system || null,
            bots,
        },
    };
};

const getApiErrorMessage = (error, fallbackMessage) =>
    (typeof error?.response?.data?.detail === "object"
        ? error?.response?.data?.detail?.message
        : error?.response?.data?.detail) ||
    error?.response?.data?.message ||
    error?.message ||
    fallbackMessage;

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within AuthProvider");
    }
    return context;
};

const decodeToken = (token) => {
    try {
        const base64Url = token.split(".")[1];
        const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
        const jsonPayload = decodeURIComponent(
            atob(base64)
                .split("")
                .map((char) => `%${(`00${char.charCodeAt(0).toString(16)}`).slice(-2)}`)
                .join("")
        );
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error("Token decode error:", error);
        return null;
    }
};

const mergeTokenClaims = (normalizedUser, token) => {
    if (!normalizedUser) {
        return null;
    }

    const claims = token ? decodeToken(token) : null;
    if (!claims || typeof claims !== "object") {
        return {
            ...normalizedUser,
            effective_role:
                normalizedUser.effective_role ||
                normalizedUser.role ||
                normalizedUser.db_role ||
                normalizedUser.token_role ||
                null,
        };
    }

    return {
        ...normalizedUser,
        id: normalizedUser.id ?? claims.user_id ?? claims.id ?? claims.sub ?? null,
        email: normalizedUser.email || claims.email || null,
        role: normalizedUser.role || claims.role || null,
        token_role: normalizedUser.token_role || claims.role || null,
        effective_role:
            normalizedUser.effective_role ||
            normalizedUser.role ||
            normalizedUser.db_role ||
            normalizedUser.token_role ||
            claims.role ||
            null,
    };
};

const readStoredUser = (token) => {
    if (typeof window === "undefined") {
        return null;
    }

    for (const storage of [window.sessionStorage, window.localStorage]) {
        try {
            const raw = storage.getItem("user");
            if (!raw) {
                continue;
            }
            const parsed = JSON.parse(raw);
            const normalized = mergeTokenClaims(normalizeAuthPayload(parsed), token);
            if (normalized) {
                return normalized;
            }
        } catch (error) {
            console.warn("Failed to restore stored user:", error);
        }
    }

    return null;
};

const persistAuthContext = (payload, token = null) => {
    if (typeof window === "undefined" || !payload) {
        return;
    }

    const normalized = mergeTokenClaims(normalizeAuthPayload(payload), token);
    if (!normalized) {
        return;
    }

    const authContext = {
        user: normalized,
        permissions: Array.isArray(normalized.permissions) ? normalized.permissions : [],
        features: Array.isArray(normalized.features) ? normalized.features : [],
        modules: normalized.modules && typeof normalized.modules === "object" ? normalized.modules : {},
        entitlements: {
            role_key:
                normalized.effective_role ||
                normalized.role_key ||
                normalized.role ||
                normalized.db_role ||
                normalized.token_role ||
                null,
            permissions: Array.isArray(normalized.permissions) ? normalized.permissions : [],
            features: Array.isArray(normalized.features) ? normalized.features : [],
            modules: normalized.modules && typeof normalized.modules === "object" ? normalized.modules : {},
            plan: normalized.authMeta?.plan || null,
            subscription: normalized.authMeta?.tenant?.plan_key || null,
        },
    };

    try {
        window.sessionStorage.setItem("user", JSON.stringify(normalized));
        window.sessionStorage.setItem("auth_context", JSON.stringify(authContext));
        window.localStorage.setItem("user", JSON.stringify(normalized));
        window.localStorage.setItem("auth_context", JSON.stringify(authContext));
    } catch (error) {
        console.warn("Failed to persist auth context:", error);
    }
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const checkAuth = useCallback(async () => {
    const token = readAuthToken();

    if (!token) {
      clearAuthCache();
      setIsAuthenticated(false);
      setUser(null);
      setIsLoading(false);
      return;
    }

    const restoredUser = readStoredUser(token);
    if (restoredUser) {
      setUser(restoredUser);
      setIsAuthenticated(true);
    }

    try {
      const response = await axiosClient.get('/api/v1/auth/me');
      const normalizedUser = mergeTokenClaims(normalizeAuthPayload(response.data), token);

      if (!normalizedUser) {
        throw new Error("Unable to normalize authenticated user");
      }

      persistAuthContext(response.data, token);
      setUser(normalizedUser);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Auth check failed:', error);
      clearAuthCache();
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

    const login = useCallback(async (email, password) => {
        try {
            const response = await axiosClient.post('/api/v1/auth/login', { email, password });
            const { access_token, refresh_token } = response.data;
            const normalizedUser = mergeTokenClaims(
                normalizeAuthPayload(response.data),
                access_token
            );

            writeAuthToken(access_token);
            if (refresh_token) {
                writeRefreshToken(refresh_token);
            }

            persistAuthContext(response.data, access_token);
            setUser(normalizedUser);
            setIsAuthenticated(true);
            return { success: true, user: normalizedUser };
        } catch (error) {
            console.error('Login failed:', error);
            return { success: false, error: error.response?.data?.detail || 'Login failed' };
        }
    }, []);

    const forgotPassword = useCallback(async (email) => {
        setIsLoading(true);
        try {
            const response = await axios.post(`${API_URL}/api/v1/auth/forgot-password`, {
                email,
            });
            return {
                success: true,
                ...(response.data || {}),
            };
        } catch (error) {
            console.error("Forgot password error:", error);
            throw new Error(
                getApiErrorMessage(
                    error,
                    "Unable to send reset instructions right now"
                )
            );
        } finally {
            setIsLoading(false);
        }
    }, []);

    const resetPassword = useCallback(async (resetToken, newPassword) => {
        setIsLoading(true);
        try {
            const response = await axios.post(`${API_URL}/api/v1/auth/reset-password`, {
                token: resetToken,
                new_password: newPassword,
            });
            return {
                success: true,
                ...(response.data || {}),
            };
        } catch (error) {
            console.error("Reset password error:", error);
            throw new Error(
                getApiErrorMessage(error, "Failed to reset password")
            );
        } finally {
            setIsLoading(false);
        }
    }, []);

    const register = useCallback(async (userData) => {
        try {
            // CHANGED: backend expects full_name (not name)
            const payload = {
                email: userData.email,
                password: userData.password,
                full_name: userData.full_name || userData.name || "",
                company: userData.company,
            };

            const response = await axios.post(`${API_URL}/api/v1/auth/register`, payload);
            return response.data;
        } catch (error) {
            const wrapped = new Error(getApiErrorMessage(error, "Registration failed"));
            wrapped.detail = error?.response?.data?.detail;
            throw wrapped;
        }
    }, []);

    const changePassword = useCallback(async (currentPassword, newPassword) => {
        const response = await axiosClient.post("/api/v1/auth/change-password", {
            current_password: currentPassword,
            new_password: newPassword,
        });
        return response.data;
    }, []);

    const updateUser = useCallback((updater) => {
        setUser((prev) => {
            const nextUser =
                typeof updater === "function"
                    ? updater(prev)
                    : { ...(prev || {}), ...(updater || {}) };

            if (nextUser) {
                persistAuthContext({ user: nextUser }, readAuthToken());
            }

            return nextUser;
        });
    }, []);

    const logout = useCallback(() => {
        clearAuthCache();
        setUser(null);
        setIsAuthenticated(false);
    }, []);

    const resolvedRole = useMemo(
        () =>
            user?.effective_role ||
            user?.role ||
            user?.db_role ||
            user?.token_role ||
            null,
        [user]
    );
    const permissions = useMemo(
        () => (Array.isArray(user?.permissions) ? user.permissions : []),
        [user]
    );
    const features = useMemo(
        () => (Array.isArray(user?.features) ? user.features : []),
        [user]
    );
    const modules = useMemo(
        () => (user?.modules && typeof user.modules === "object" ? user.modules : {}),
        [user]
    );
    const authMeta = useMemo(() => user?.authMeta || {}, [user]);
    const token = readAuthToken();
    const authReady = !isLoading;
    const accountStatus =
        user?.account_status ||
        (user?.is_active === false ? "inactive" : user ? "active" : null);

    const value = useMemo(() => ({
        user,
        setUser: updateUser,
        updateUser,
        role: resolvedRole,
        token,
        loading: isLoading,
        isLoading,
        authReady,
        isAuthenticated,
        accountStatus,
        permissions,
        features,
        modules,
        authMeta,
        plan: authMeta?.plan || null,
        system: authMeta?.system || user?.system || user?.system_type || null,
        login,
        register,
        forgotPassword,
        resetPassword,
        changePassword,
        logout,
        checkAuth
    }), [
        user,
        updateUser,
        resolvedRole,
        token,
        isLoading,
        authReady,
        isAuthenticated,
        accountStatus,
        permissions,
        features,
        modules,
        authMeta,
        login,
        register,
        forgotPassword,
        resetPassword,
        changePassword,
        logout,
        checkAuth,
    ]);

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
