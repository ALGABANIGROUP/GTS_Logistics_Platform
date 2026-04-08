import { settings } from "../config/settings";
import {
    clearAuthCache,
    readAuthToken,
    writeAuthToken,
    writeRefreshToken,
} from "../utils/authStorage";
import axiosClient from "./axiosClient";

export function storeAccessToken(token) {
    writeAuthToken(token);
}

export function readAccessToken() {
    return readAuthToken();
}

export function clearAccessToken() {
    clearAuthCache();
}

export const authApi = {
    login: async ({ email, password }) => {
        const res = await axiosClient.post(settings.ENDPOINTS.AUTH.LOGIN, {
            email,
            password,
        }, {
            headers: { "Content-Type": "application/json" },
        });

        const token = res?.data?.access_token;
        const refreshToken = res?.data?.refresh_token;
        if (token) storeAccessToken(token);
        if (refreshToken) writeRefreshToken(refreshToken);
        return res;
    },

    me: async () => {
        const token = readAccessToken();
        if (!token) {
            throw new Error("No authentication token found");
        }

        return axiosClient.get("/api/v1/auth/me", {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
    },

    refresh: async (refreshToken) => {
        if (!refreshToken) {
            throw new Error("refresh_token is required");
        }

        const res = await axiosClient.post("/api/v1/auth/refresh", {
            refresh_token: refreshToken,
        });

        const token = res?.data?.access_token;
        const nextRefreshToken = res?.data?.refresh_token;
        if (token) storeAccessToken(token);
        if (nextRefreshToken) writeRefreshToken(nextRefreshToken);
        return res;
    },

    userMe: () => axiosClient.get("/api/v1/users/me"),
};
