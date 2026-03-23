// File: src/contexts/AuthContext.jsx
import { createContext, useContext, useEffect, useState } from "react";
import PropTypes from "prop-types";
import axiosClient from "../api/axiosClient"; // <-- adjust this path to match your project
import { clearAuthCache, readAuthToken, writeAuthToken, writeRefreshToken } from "../utils/authStorage";
import {
    attachAuthDebugTools,
    discoverTokenIssue,
    isAuthDebugEnabled,
} from "../utils/authDiagnostics";
import { getUserRole } from "../utils/userRole";
import { useCurrencyStore } from "../stores/useCurrencyStore";

const computeModules = (rawModules = {}, features = []) => {
    const normalized = { ...rawModules };
    const hasAiFeature = features.some((key) => String(key || "").trim().toLowerCase().startsWith("ai."));
    if (!normalized.ai && (hasAiFeature || features.includes("ai.core"))) {
        normalized.ai = true;
    }
    return normalized;
};
const deriveAccountStatus = (nextUser) => {
    if (!nextUser) return null;
    const rawStatus = nextUser.user_status ?? nextUser.userStatus ?? null;
    if (rawStatus) {
        const normalized = String(rawStatus).trim().toLowerCase();
        if (normalized === "active") return "active";
        if (normalized === "pending") return "pending";
        if (normalized === "suspended") return "suspended";
        if (normalized === "inactive") return "pending";
        return normalized;
    }
    return nextUser.is_active === false ? "pending" : "active";
};

const buildNormalizedSessionUser = (primaryUser, authPayload = null) => {
    const flatAuthUser = authPayload && !authPayload.user ? authPayload : {};
    const mergedUser = {
        ...(primaryUser || {}),
        ...(authPayload?.user || {}),
        ...flatAuthUser,
    };
    const normalizedRole = getUserRole(mergedUser) || "user";
    return {
        ...mergedUser,
        role: normalizedRole,
        effective_role: mergedUser.effective_role || normalizedRole,
        db_role: mergedUser.db_role || null,
        token_role: mergedUser.token_role || null,
    };
};

const AuthContext = createContext(null);

const STORAGE_KEYS = {
    token: "access_token",
    user: "user",
    meta: "auth_context",
};
const BOOTSTRAP_TIMEOUT_MS = 7000;
const getSessionStorage = () =>
    (typeof window !== "undefined" ? window.sessionStorage : null);
const authTrace = (message, data) => {
    if (typeof console === "undefined") return;
    const stamp = new Date().toISOString();
    if (typeof data === "undefined") {
        console.log(`[Auth ${stamp}] ${message}`);
        return;
    }
    console.log(`[Auth ${stamp}] ${message}`, data);
};
const authTraceError = (message, error) => {
    if (typeof console === "undefined") return;
    const stamp = new Date().toISOString();
    console.error(`[Auth ERROR ${stamp}] ${message}`, error);
};

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(null);
    const [user, setUser] = useState(null);
    const [authMeta, setAuthMeta] = useState(null);
    const [entitlements, setEntitlements] = useState(null);
    const [entitlementsLoading, setEntitlementsLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true); // initial loading while reading localStorage
    const [authReady, setAuthReady] = useState(false);
    const [accountStatus, setAccountStatus] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        let cancelled = false;

        const bootstrap = async () => {
            setLoading(true);
            authTrace("Bootstrap started");
            if (isAuthDebugEnabled()) {
                attachAuthDebugTools();
                discoverTokenIssue();
            }
            const accessToken = readAuthToken();
            authTrace("Bootstrap token state", {
                hasAccessToken: Boolean(accessToken),
                accessTokenPreview: accessToken ? `${accessToken.slice(0, 12)}...` : null,
                hasSessionUser: Boolean(getSessionStorage()?.getItem(STORAGE_KEYS.user)),
            });
            if (!accessToken) {
                persistSession(null, null, null);
                if (!cancelled) {
                    setEntitlementsLoading(true);
                    setLoading(false);
                    setAuthReady(true);
                }
                return;
            }

            try {
                const authHeaders = { Authorization: `Bearer ${accessToken}` };
                const deadline = Date.now() + BOOTSTRAP_TIMEOUT_MS;
                const fetchWithTimeout = async (url) => {
                    const remaining = Math.max(0, deadline - Date.now());
                    if (!remaining) {
                        throw new Error("Auth bootstrap timeout");
                    }
                    const controller = new AbortController();
                    let timeoutId;
                    const timeoutPromise = new Promise((_, reject) => {
                        timeoutId = setTimeout(() => {
                            controller.abort();
                            reject(new Error("Auth bootstrap timeout"));
                        }, remaining);
                    });

                    try {
                        const requestPromise = axiosClient.get(url, {
                            headers: authHeaders,
                            signal: controller.signal,
                        });
                        return await Promise.race([requestPromise, timeoutPromise]);
                    } finally {
                        if (timeoutId) clearTimeout(timeoutId);
                    }
                };

                let authPayload = null;
                try {
                    console.log(
                        `[Auth] Fetching /api/v1/auth/me with token: ${accessToken?.substring(0, 10)}...`
                    );
                    authTrace("Fetching /api/v1/auth/me");
                    const meRes = await fetchWithTimeout("/api/v1/auth/me");
                    console.log("[Auth] /auth/me response status:", meRes?.status);
                    console.log("[Auth] /auth/me response data:", meRes?.data);
                    if (meRes?.status === 401) {
                        console.error("[Auth] Token rejected by backend");
                        clearAuthCache();
                        persistSession(null, null, null);
                        setEntitlementsLoading(true);
                        return;
                    }
                    authPayload = meRes?.data || null;
                    authTrace("/api/v1/auth/me response", {
                        status: meRes?.status,
                        ok: authPayload?.ok,
                        user: authPayload?.user
                            ? {
                                id: authPayload.user.id,
                                role: authPayload.user.role,
                                effective_role: authPayload.user.effective_role,
                                db_role: authPayload.user.db_role,
                                token_role: authPayload.user.token_role,
                            }
                            : null,
                    });
                } catch (err) {
                    console.error("[Auth] /auth/me failed:", err);
                    authTraceError("/api/v1/auth/me failed during bootstrap", {
                        hasAccessToken: Boolean(accessToken),
                    });
                    clearAuthCache();
                    persistSession(null, null, null);
                    setEntitlementsLoading(true);
                    return;
                }

                if (!authPayload) {
                    authTraceError("/api/v1/auth/me returned empty payload", authPayload);
                    clearAuthCache();
                    persistSession(null, null, null);
                    setEntitlementsLoading(true);
                    return;
                }

                const parsedUser = authPayload?.user || null;

                const sessionUser = parsedUser
                    ? {
                        ...buildNormalizedSessionUser(parsedUser, authPayload),
                        permissions: parsedUser.permissions || authPayload?.permissions || [],
                        source: parsedUser.source || "bootstrap",
                    }
                    : null;

                const sessionMeta = authPayload
                    ? {
                        tenant: authPayload.tenant || null,
                        plan: authPayload.plan || null,
                        modules: computeModules(authPayload.modules || {}, authPayload.entitlements?.features || []),
                        features: authPayload.entitlements?.features || [],
                        bots: authPayload.entitlements?.bots || [],
                        entitlements: authPayload.entitlements || null,
                        system: authPayload.system || null,
                        permissions: authPayload.user?.permissions || [],
                        role_key: sessionUser?.role || null,
                        user: sessionUser,
                    }
                    : null;

                const sessionEntitlements = authPayload?.entitlements || null;
                const latestToken = readAuthToken() || accessToken;

                if (sessionUser) {
                    authTrace("Persisting session from bootstrap", {
                        role: sessionUser.role,
                        effective_role: sessionUser.effective_role,
                        db_role: sessionUser.db_role,
                        token_role: sessionUser.token_role,
                    });
                    persistSession(latestToken, sessionUser, sessionMeta, sessionEntitlements);
                    setEntitlementsLoading(false);
                } else {
                    authTraceError("Bootstrap produced no session user", authPayload);
                    persistSession(null, null, null);
                    setEntitlementsLoading(true);
                }
            } catch {
                authTraceError("Bootstrap crashed", {});
                clearAuthCache();
                persistSession(null, null, null);
                setEntitlementsLoading(true);
            } finally {
                if (!cancelled) {
                    setLoading(false);
                    setAuthReady(true);
                }
            }
        };

        bootstrap();
        return () => {
            cancelled = true;
        };
    }, []);

    useEffect(() => {
        const handleExpired = () => {
            authTraceError("auth:expired event received", {
                path: typeof window !== "undefined" ? window.location.pathname : null,
            });
            clearAuthCache();
            persistSession(null, null, null);
            setError("Session expired. Please login again.");
            if (typeof window !== "undefined" && window.location.pathname !== "/login") {
                window.location.assign("/login?reason=expired");
            }
        };

        if (typeof window !== "undefined") {
            window.addEventListener("auth:expired", handleExpired);
            return () => window.removeEventListener("auth:expired", handleExpired);
        }
        return undefined;
    }, []);

    useEffect(() => {
        if (typeof window === "undefined") return undefined;

        const handleStorage = (e) => {
            if (!e) return;
            if (["access_token", "token", "gts_token", "user", "auth_context"].includes(e.key)) {
                refreshFromStorage();
            }
        };

        const handleVisibility = () => {
            if (!document.hidden) {
                refreshFromStorage();
                refreshAuthContext()?.catch(() => {
                    // Keep existing session when refresh endpoint is not reachable
                });
            }
        };

        window.addEventListener("storage", handleStorage);
        document.addEventListener("visibilitychange", handleVisibility);
        return () => {
            window.removeEventListener("storage", handleStorage);
            document.removeEventListener("visibilitychange", handleVisibility);
        };
    }, []);

    const persistSession = (nextToken, nextUser, nextMeta, nextEntitlements) => {
        authTrace("persistSession", {
            hasToken: Boolean(nextToken),
            userId: nextUser?.id || null,
            role: nextUser?.role || null,
            effective_role: nextUser?.effective_role || null,
        });
        setToken(nextToken || null);
        setUser(nextUser || null);
        setAuthMeta(nextMeta || null);
        setEntitlements(nextEntitlements || null);
        setIsAuthenticated(Boolean(nextToken && nextUser));
        setAccountStatus(deriveAccountStatus(nextUser));

        if (nextToken && nextUser) {
            writeAuthToken(nextToken);
            const sessionStorage = getSessionStorage();
            sessionStorage?.setItem(STORAGE_KEYS.user, JSON.stringify(nextUser));
            if (nextMeta) {
                sessionStorage?.setItem(STORAGE_KEYS.meta, JSON.stringify(nextMeta));
            } else {
                sessionStorage?.removeItem(STORAGE_KEYS.meta);
            }
        } else {
            const sessionStorage = getSessionStorage();
            sessionStorage?.removeItem(STORAGE_KEYS.token);
            sessionStorage?.removeItem(STORAGE_KEYS.user);
            sessionStorage?.removeItem(STORAGE_KEYS.meta);
        }
    };

    const finalizeLogin = async ({ accessToken, refreshToken, credentials, data }) => {
        authTrace("finalizeLogin started", {
            hasAccessToken: Boolean(accessToken),
            hasRefreshToken: Boolean(refreshToken),
        });
        let backendUser = data?.user || data?.profile || null;
        let authPayload = null;

        try {
            const authHeaders = {
                Authorization: `Bearer ${accessToken}`,
            };
            const meRes = await axiosClient.get("/api/v1/auth/me", {
                headers: authHeaders,
            });
            authPayload = meRes?.data || null;
        } catch {
            try {
                const authHeaders = {
                    Authorization: `Bearer ${accessToken}`,
                };
                const meRes = await axiosClient.get("/auth/me", {
                    headers: authHeaders,
                });
                authPayload = meRes?.data || null;
            } catch {
                authPayload = null;
            }
        }

        const authUser = authPayload?.user || null;
        const mergedUser = buildNormalizedSessionUser(
            {
                ...(backendUser || {}),
                ...(authUser || {}),
            },
            authPayload
        );

        if (!mergedUser || !mergedUser.email) {
            mergedUser.email = credentials?.email;
            mergedUser.full_name = data?.full_name || data?.name || "User";
            mergedUser.role = getUserRole(data) || data?.role || "user";
            mergedUser.user_type = data?.user_type || "Freight Broker";
            mergedUser.country = data?.country || "GLOBAL";
            mergedUser.source = "login-fallback";
        }

        const normalizedRole = getUserRole(mergedUser) || "user";
        const sessionUser = {
            ...mergedUser,
            role: normalizedRole,
            permissions: authUser?.permissions || mergedUser.permissions || [],
            loginAt: new Date().toISOString(),
            source: mergedUser.source || "web-ui",
        };

        const sessionMeta = authPayload
            ? {
                tenant: authPayload.tenant || null,
                plan: authPayload.plan || null,
                modules: computeModules(authPayload.modules || {}, authPayload.entitlements?.features || []),
                features: authPayload.entitlements?.features || [],
                bots: authPayload.entitlements?.bots || [],
                entitlements: authPayload.entitlements || null,
                system: authPayload.system || null,
                permissions: authUser?.permissions || [],
                role_key: normalizedRole,
                user: sessionUser,
            }
            : null;

        const sessionEntitlements = authPayload?.entitlements || null;

        await persistSession(accessToken, sessionUser, sessionMeta, sessionEntitlements);
        if (refreshToken) {
            writeRefreshToken(refreshToken);
        }

        // Initialize currency based on user's country
        const currencyStore = useCurrencyStore.getState();
        const userCountry = sessionUser?.country || "CA";
        currencyStore.initializeCurrencyFromUser(userCountry);

        setEntitlementsLoading(false);
        authTrace("finalizeLogin completed", {
            role: sessionUser?.role,
            effective_role: sessionUser?.effective_role,
            db_role: sessionUser?.db_role,
            token_role: sessionUser?.token_role,
        });

        return { token: accessToken, user: sessionUser, meta: sessionMeta };
    };

    const login = async (credentials) => {
        setLoading(true);
        setError(null);

        try {
            const identifier = (credentials.email || credentials.username || "").trim();
            const form = new URLSearchParams();
            form.set("grant_type", "password");
            form.set("username", identifier);
            form.set("password", credentials.password || "");

            const response = await axiosClient.post("/api/v1/auth/token", form, {
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
            });

            const data = response?.data || {};

            const accessToken = data.access_token || data.token || null;
            const refreshToken = data.refresh_token || data.refreshToken || null;

            if (!accessToken) {
                throw new Error("No access token returned from API.");
            }

            return await finalizeLogin({ accessToken, refreshToken, credentials, data });
        } catch (err) {
            console.error("AuthContext.login error:", err);
            setError(
                err?.response?.data?.detail ||
                err?.message ||
                "Login failed. Please check your credentials."
            );
            persistSession(null, null, null);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const initTwoFactorSetup = async ({ email, password }) => {
        const response = await axiosClient.post("/api/v1/auth/2fa/setup-init", {
            email,
            password,
        });
        return response?.data || null;
    };

    const verifyTwoFactorLogin = async ({ email, password, token: otp, backupCode }) => {
        setLoading(true);
        setError(null);

        try {
            const response = await axiosClient.post("/api/v1/auth/2fa/verify-login", {
                email,
                password,
                token: otp,
                backup_code: backupCode || null,
            });

            const data = response?.data || {};
            const accessToken = data.access_token || data.token || null;
            const refreshToken = data.refresh_token || data.refreshToken || null;

            if (!accessToken) {
                throw new Error("No access token returned from API.");
            }

            return await finalizeLogin({
                accessToken,
                refreshToken,
                credentials: { email },
                data,
            });
        } catch (err) {
            console.error("AuthContext.verifyTwoFactorLogin error:", err);
            setError(
                err?.response?.data?.detail ||
                err?.message ||
                "Two-factor verification failed."
            );
            persistSession(null, null, null);
            throw err;
        } finally {
            setLoading(false);
        }
    };


    const logout = () => {
        // Clear all auth data
        clearAuthCache();
        setToken(null);
        setUser(null);
        setAuthMeta(null);
        setEntitlements(null);
        setAccountStatus(null);
        setIsAuthenticated(false);
        setError(null);

        // Reset currency to default
        const currencyStore = useCurrencyStore.getState();
        currencyStore.setCurrency("CAD");
        currencyStore.setCountry("CA");

        // Redirect to login page
        window.location.href = '/login';
    };

    const refreshFromStorage = () => {
        try {
            const storedToken = readAuthToken();
            const sessionStorage = getSessionStorage();
            const storedUserRaw = sessionStorage?.getItem(STORAGE_KEYS.user);
            const storedMetaRaw = sessionStorage?.getItem(STORAGE_KEYS.meta);
            let parsedUser = null;

            if (storedUserRaw) {
                try {
                    parsedUser = JSON.parse(storedUserRaw);
                } catch {
                    parsedUser = null;
                }
            }

            if (parsedUser) {
                parsedUser = buildNormalizedSessionUser(parsedUser);
                sessionStorage?.setItem(STORAGE_KEYS.user, JSON.stringify(parsedUser));
            }

            let parsedMeta = null;
            if (storedMetaRaw) {
                try {
                    parsedMeta = JSON.parse(storedMetaRaw);
                } catch {
                    parsedMeta = null;
                }
            }

            if (storedToken && parsedUser) {
                setToken(storedToken);
                setUser(parsedUser);
                setAuthMeta(parsedMeta);
                setEntitlements(parsedMeta?.entitlements || null);
                setEntitlementsLoading(false);
                setIsAuthenticated(true);
                setAccountStatus(deriveAccountStatus(parsedUser));
            } else {
                setToken(null);
                setUser(null);
                setAuthMeta(null);
                setEntitlements(null);
                setEntitlementsLoading(true);
                setAccountStatus(null);
                setIsAuthenticated(false);
            }
        } catch {
            setToken(null);
            setUser(null);
            setAuthMeta(null);
            setEntitlements(null);
            setEntitlementsLoading(true);
            setAccountStatus(null);
            setIsAuthenticated(false);
        }
    };

    const refreshAuthContext = async () => {
        const accessToken = readAuthToken();
        if (!accessToken) {
            authTrace("refreshAuthContext skipped: no token");
            return null;
        }

        try {
            authTrace("refreshAuthContext started", {
                accessTokenPreview: `${accessToken.slice(0, 12)}...`,
            });
            const authHeaders = {
                Authorization: `Bearer ${accessToken}`,
            };
            const meRes = await axiosClient.get("/api/v1/auth/me", {
                headers: authHeaders,
            });
            const authPayload = meRes?.data || null;
            const authUser = authPayload?.user || {};
            const mergedUser = buildNormalizedSessionUser(
                {
                    ...(user || {}),
                    ...authUser,
                },
                authPayload
            );
            const normalizedRole = getUserRole(mergedUser) || "user";
            const sessionUser = {
                ...mergedUser,
                role: normalizedRole,
                permissions: authUser?.permissions || mergedUser.permissions || [],
            };
            const sessionMeta = authPayload
                ? {
                    tenant: authPayload.tenant || null,
                    plan: authPayload.plan || null,
                    modules: computeModules(authPayload.modules || {}, authPayload.entitlements?.features || []),
                    features: authPayload.entitlements?.features || [],
                    bots: authPayload.entitlements?.bots || [],
                    entitlements: authPayload.entitlements || null,
                    system: authPayload.system || null,
                    permissions: authUser?.permissions || [],
                }
                : null;

            const sessionEntitlements = authPayload?.entitlements || null;

            const latestToken = readAuthToken() || accessToken;
            persistSession(latestToken, sessionUser, sessionMeta, sessionEntitlements);
            setEntitlementsLoading(false);
            authTrace("refreshAuthContext completed", {
                role: sessionUser?.role,
                effective_role: sessionUser?.effective_role,
                db_role: sessionUser?.db_role,
                token_role: sessionUser?.token_role,
            });
            return sessionMeta;
        } catch (err) {
            authTraceError("refreshAuthContext failed", err);
            return null;
        }
    };

    const value = {
        token,
        user,
        setUser,
        authMeta,
        entitlements,
        entitlementsLoading,
        accountStatus,
        role: user?.role || null,
        modules: authMeta?.modules || {},
        features: authMeta?.features || [],
        permissions: authMeta?.permissions || user?.permissions || [],
        plan: authMeta?.plan || null,
        tenant: authMeta?.tenant || null,
        system: authMeta?.system || null,
        isAuthenticated,
        authReady,
        loading,
        error,
        login,
        initTwoFactorSetup,
        verifyTwoFactorLogin,
        logout,
        refreshFromStorage,
        refreshAuthContext,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

AuthProvider.propTypes = {
    children: PropTypes.node.isRequired,
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context) return context;

    return {
        token: null,
        user: null,
        setUser: () => { },
        authMeta: null,
        entitlements: null,
        entitlementsLoading: true,
        accountStatus: null,
        role: null,
        modules: {},
        features: [],
        permissions: [],
        plan: null,
        tenant: null,
        system: null,
        isAuthenticated: false,
        authReady: false,
        loading: false,
        error: null,
        login: async () => {
            throw new Error("Auth context is not ready.");
        },
        initTwoFactorSetup: async () => {
            throw new Error("Auth context is not ready.");
        },
        verifyTwoFactorLogin: async () => {
            throw new Error("Auth context is not ready.");
        },
        logout: () => { },
        refreshFromStorage: () => { },
        refreshAuthContext: async () => null,
    };
};
