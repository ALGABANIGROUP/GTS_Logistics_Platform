import React, {
    createContext,
    useContext,
    useEffect,
    useMemo,
    useState,
} from "react";
import axios from "axios";
import axiosClient from "../api/axiosClient";
import {
    clearAuthCache,
    readAuthToken,
    writeAuthToken,
    writeRefreshToken,
} from "../utils/authStorage";
import { API_BASE_URL } from "../config/env";

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

const getApiErrorDetail = (error) => error?.response?.data?.detail;

const getFieldErrors = (detail) => {
    if (!detail) {
        return {};
    }

    if (Array.isArray(detail)) {
        return detail.reduce((acc, item) => {
            const field = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : null;
            const message = item?.msg;
            if (field && message) {
                acc[field] = message;
            }
            return acc;
        }, {});
    }

    if (typeof detail === "object") {
        if (detail.field && detail.message) {
            return { [detail.field]: detail.message };
        }

        return Object.entries(detail).reduce((acc, [key, value]) => {
            if (typeof value === "string") {
                acc[key] = value;
            }
            return acc;
        }, {});
    }

    return {};
};

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

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [authReady, setAuthReady] = useState(false);
    const [token, setToken] = useState(() => readAuthToken());

    useEffect(() => {
        let cancelled = false;

        const initAuth = async () => {
            setLoading(true);

            const currentToken = readAuthToken();
            if (!currentToken) {
                if (!cancelled) {
                    setToken("");
                    setUser(null);
                    setLoading(false);
                    setAuthReady(true);
                }
                return;
            }

            try {
                const decoded = decodeToken(currentToken);
                if (!decoded || decoded.exp * 1000 <= Date.now()) {
                    clearAuthCache();
                    if (!cancelled) {
                        setToken("");
                        setUser(null);
                    }
                } else {
                    const response = await axiosClient.get(`/api/v1/auth/me`, {
                        headers: { Authorization: `Bearer ${currentToken}` },
                    });
                    if (!cancelled) {
                        setToken(currentToken);
                        setUser(normalizeAuthPayload(response.data));
                    }
                }
            } catch (error) {
                console.error("Auth init error:", error);
                const status = error?.response?.status;
                if (!cancelled) {
                    // Do not clear auth state on transient 401 here.
                    // axiosClient interceptor handles refresh and emits auth:expired for hard failures.
                    if (status !== 401 && status !== 403) {
                        clearAuthCache();
                        setToken("");
                        setUser(null);
                    }
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                    setAuthReady(true);
                }
            }
        };

        initAuth();
        return () => {
            cancelled = true;
        };
    }, [token]);

    useEffect(() => {
        if (typeof window === "undefined") {
            return undefined;
        }

        const handleAuthExpired = () => {
            clearAuthCache();
            setToken("");
            setUser(null);
            setLoading(false);
            setAuthReady(true);
        };

        window.addEventListener("auth:expired", handleAuthExpired);
        return () => {
            window.removeEventListener("auth:expired", handleAuthExpired);
        };
    }, []);

    const login = async (email, password, remember = false) => {
        try {
            const formData = new URLSearchParams();
            formData.append("username", email);
            formData.append("password", password);

            const response = await axiosClient.post(`/api/v1/auth/token`, formData, {
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
            });

            const { access_token, refresh_token } = response.data || {};
            if (!access_token) {
                throw new Error("No access token received");
            }

            clearAuthCache();
            writeAuthToken(access_token);
            if (refresh_token) {
                writeRefreshToken(refresh_token);
            }

            if (remember) {
                try {
                    window.localStorage.setItem("gts_saved_email", email);
                } catch {
                    // ignore storage errors
                }
            }

            let userPayload = normalizeAuthPayload(response.data);
            try {
                const userResponse = await axiosClient.get(`/api/v1/auth/me`, {
                    headers: { Authorization: `Bearer ${access_token}` },
                });
                userPayload = normalizeAuthPayload(userResponse.data) || userPayload;
            } catch (meError) {
                console.warn("Auth /me fallback triggered:", meError);
            }

            if (!userPayload) {
                throw new Error("Unable to load user profile after login");
            }

            setToken(access_token);
            setUser(userPayload);

            return { success: true, user: userPayload };
        } catch (error) {
            console.error("Login error:", error);
            const detail = getApiErrorDetail(error);
            const status = error?.response?.status || 0;
            let message = getApiErrorMessage(error, "Invalid email or password");

            if (status === 401) {
                message = "Invalid email or password";
            } else if (
                (status === 400 || status === 403) &&
                String(message).toLowerCase() === "account is not active"
            ) {
                message = "Account is disabled";
            } else if (status === 422 && !message) {
                message = "Email and password are required";
            }

            return {
                success: false,
                status,
                detail,
                fieldErrors: getFieldErrors(detail),
                message,
            };
        }
    };

    const forgotPassword = async (email) => {
        setLoading(true);
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
            setLoading(false);
        }
    };

    const resetPassword = async (resetToken, newPassword) => {
        setLoading(true);
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
            setLoading(false);
        }
    };

    const register = async (userData) => {
        try {
            const response = await axios.post(`${API_URL}/api/v1/auth/register`, userData);
            return response.data;
        } catch (error) {
            const wrapped = new Error(getApiErrorMessage(error, "Registration failed"));
            wrapped.detail = error?.response?.data?.detail;
            throw wrapped;
        }
    };

    const logout = () => {
        clearAuthCache();
        setToken("");
        setUser(null);
    };

    const value = useMemo(
        () => ({
            user,
            setUser,
            updateUser: setUser,
            token,
            loading,
            authReady,
            login,
            forgotPassword,
            resetPassword,
            register,
            logout,
            isAuthenticated: Boolean(user && token),
            role: user?.effective_role || user?.role || "",
            features: Array.isArray(user?.features) ? user.features : [],
            modules: user?.modules && typeof user.modules === "object" ? user.modules : {},
            authMeta: user?.authMeta || null,
            accountStatus: user?.status || user?.account_status || "active",
            permissions: Array.isArray(user?.permissions) ? user.permissions : [],
        }),
        [authReady, loading, token, user]
    );

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
