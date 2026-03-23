import axiosClient from "../api/axiosClient";
import { readAuthToken, readRefreshToken } from "./authStorage";

const decodeJwtPayload = (token) => {
  if (!token || typeof token !== "string") return null;
  const parts = token.split(".");
  if (parts.length < 2) return null;
  try {
    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = payload.padEnd(Math.ceil(payload.length / 4) * 4, "=");
    const json = atob(padded);
    const parsed = JSON.parse(json);
    return parsed && typeof parsed === "object" ? parsed : null;
  } catch {
    return null;
  }
};

export const isAuthDebugEnabled = () => {
  try {
    return (
      typeof window !== "undefined" &&
      window.localStorage &&
      window.localStorage.getItem("gts_debug_auth") === "1"
    );
  } catch {
    return false;
  }
};

export const discoverTokenIssue = () => {
  const token = readAuthToken();
  if (!token) {
    console.warn("[Auth] No token found in storage.");
    return { status: "missing" };
  }

  const payload = decodeJwtPayload(token);
  if (!payload) {
    console.warn("[Auth] Token exists but could not be decoded as JWT.");
    return { status: "unreadable" };
  }

  const exp = Number(payload.exp || 0);
  const now = Math.floor(Date.now() / 1000);
  if (exp && exp < now) {
    console.warn(
      `[Auth] Token expired at ${new Date(exp * 1000).toISOString()}.`
    );
    return { status: "expired", exp };
  }

  console.log(
    `[Auth] Token is valid${exp ? ` until ${new Date(exp * 1000).toISOString()}` : ""}.`
  );
  return { status: "valid", exp };
};

export const checkAPIConnection = async (endpoint = "/api/v1/auth/me") => {
  try {
    const response = await axiosClient.get(endpoint);
    console.log("[Auth] API request successful:", response?.data);
    return { ok: true, data: response?.data };
  } catch (error) {
    const status = error?.response?.status;
    console.error("[Auth] API request failed:", error);
    if (status === 401) {
      console.warn("[Auth] Token is invalid or session expired.");
    } else if (status === 422) {
      console.warn("[Auth] Validation error from API.");
    }
    return { ok: false, status, error };
  }
};

export const attachAuthDebugTools = () => {
  if (typeof window === "undefined") return;
  window.GTS_AUTH = window.GTS_AUTH || {};
  window.GTS_AUTH.discoverTokenIssue = discoverTokenIssue;
  window.GTS_AUTH.checkAPIConnection = checkAPIConnection;
};

export const getTokenSnapshot = () => {
  const token = readAuthToken();
  const refreshToken = readRefreshToken();
  const payload = decodeJwtPayload(token);
  const exp = payload && typeof payload.exp === "number" ? payload.exp : null;
  return {
    hasAccessToken: Boolean(token),
    hasRefreshToken: Boolean(refreshToken),
    exp,
  };
};
