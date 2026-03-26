import React, {
    createContext,
    useContext,
    useEffect,
    useMemo,
    useState,
} from "react";
import axios from "axios";
import {
    clearAuthCache,
    readAuthToken,
    writeAuthToken,
    writeRefreshToken,
} from "../utils/authStorage";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const AuthContext = createContext();

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
                    const response = await axios.get(`${API_URL}/api/v1/auth/me`, {
                        headers: { Authorization: `Bearer ${currentToken}` },
                    });
                    if (!cancelled) {
                        setToken(currentToken);
                        setUser(response.data);
                    }
                }
            } catch (error) {
                console.error("Auth init error:", error);
                clearAuthCache();
                if (!cancelled) {
                    setToken("");
                    setUser(null);
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

    const login = async (email, password, remember = false) => {
        try {
            const formData = new URLSearchParams();
            formData.append("username", email);
            formData.append("password", password);

            const response = await axios.post(`${API_URL}/api/v1/auth/token`, formData, {
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
            });

            const { access_token, refresh_token } = response.data || {};
            if (!access_token) {
                throw new Error("No access token received");
            }

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

            const userResponse = await axios.get(`${API_URL}/api/v1/auth/me`, {
                headers: { Authorization: `Bearer ${access_token}` },
            });

            setToken(access_token);
            setUser(userResponse.data);

            return { success: true, user: userResponse.data };
        } catch (error) {
            console.error("Login error:", error);
            throw new Error(error.response?.data?.detail || "Invalid email or password");
        }
    };

    const register = async (userData) => {
        try {
            const response = await axios.post(`${API_URL}/api/v1/auth/register`, userData);
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.detail || "Registration failed");
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
            register,
            logout,
            isAuthenticated: Boolean(user && token),
            accountStatus: user?.status || user?.account_status || "active",
            permissions: Array.isArray(user?.permissions) ? user.permissions : [],
        }),
        [authReady, loading, token, user]
    );

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
