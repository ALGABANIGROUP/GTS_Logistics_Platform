import axios from "axios";
import {
  clearAuthCache,
  readAuthToken,
  readRefreshToken,
  writeAuthToken,
  writeRefreshToken,
} from "../utils/authStorage";

// ---- Resolve API base URL (strict, no silent fallback) ----
const resolveBaseURL = () => {
  const envURL =
    typeof import.meta !== "undefined" &&
    import.meta.env &&
    import.meta.env.VITE_API_BASE_URL;

  if (!envURL) {
    throw new Error(
      "[GTS] VITE_API_BASE_URL is not defined. " +
      "Make sure it exists in frontend/.env and restart Vite."
    );
  }

  // Normalize: remove trailing slash
  const normalized = envURL.replace(/\/+$/, "");
  console.log("Using API URL from env:", normalized);
  return normalized;
};

const BASE_URL = resolveBaseURL();
const authTrace = (message, data) => {
  if (typeof console === "undefined") return;
  const stamp = new Date().toISOString();
  if (typeof data === "undefined") {
    console.log(`[AxiosAuth ${stamp}] ${message}`);
    return;
  }
  console.log(`[AxiosAuth ${stamp}] ${message}`, data);
};

// ---- Token helpers ----
const TOKEN_KEYS = ["access_token", "token", "authToken", "jwt"];

const isAuthDebugEnabled = () => {
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

const isVerboseAxiosDebugEnabled = () => {
  try {
    return (
      typeof window !== "undefined" &&
      window.localStorage &&
      window.localStorage.getItem("gts_debug_network") === "1"
    );
  } catch {
    return false;
  }
};

const readTokenSafe = () => {
  try {
    const t = readAuthToken?.();
    if (t) return t;
  } catch { }

  const ls = typeof window !== "undefined" ? window.localStorage : null;
  const ss = typeof window !== "undefined" ? window.sessionStorage : null;

  // Try primary key first
  if (ls?.getItem("access_token")) return ls.getItem("access_token");
  if (ss?.getItem("access_token")) return ss.getItem("access_token");

  // Fallback to other keys
  for (const key of TOKEN_KEYS.slice(1)) {
    if (ls?.getItem(key)) return ls.getItem(key);
    if (ss?.getItem(key)) return ss.getItem(key);
  }
  return null;
};

const normalizeBaseUrlForRequest = (config) => {
  const url = config?.url || "";
  const base = config?.baseURL || BASE_URL;

  if (!base || !url) return config;

  if (base.endsWith("/api/v1") && url.startsWith("/api/v1/")) {
    config.baseURL = base.replace(/\/api\/v1\/?$/, "");
  }

  return config;
};

const refreshClient = axios.create({
  baseURL: BASE_URL,
  timeout: 120000,
  headers: {
    Accept: "application/json",
  },
});

let refreshPromise = null;

const refreshAccessToken = async () => {
  if (refreshPromise) return refreshPromise;

  const refreshToken = readRefreshToken();
  authTrace("refreshAccessToken invoked", {
    hasRefreshToken: Boolean(refreshToken),
    refreshTokenPreview: refreshToken ? `${refreshToken.slice(0, 10)}...` : null,
  });
  if (!refreshToken) return null;

  refreshPromise = refreshClient
    .post("/api/v1/auth/refresh", { refresh_token: refreshToken })
    .then((res) => {
      const data = res?.data || {};
      if (data?.ok === false) {
        throw new Error(data?.error || "Token refresh failed");
      }
      authTrace("/api/v1/auth/refresh response", {
        status: res?.status,
        ok: data?.ok,
        hasAccessToken: Boolean(data.access_token || data.token),
        hasRefreshToken: Boolean(data.refresh_token),
        error: data?.error || null,
      });
      const newAccess = data.access_token || data.token || null;
      const newRefresh = data.refresh_token || null;
      if (!newAccess) {
        throw new Error("Refresh response did not include an access token");
      }
      if (newAccess) writeAuthToken(newAccess);
      if (newRefresh) writeRefreshToken(newRefresh);
      return newAccess;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
};

const isHardAuthFailure = ({ status, url, detail, hadToken }) => {
  if (status !== 401 || !hadToken) {
    return false;
  }

  const normalizedUrl = String(url || "").toLowerCase();

  if (
    normalizedUrl.includes("/api/v1/auth/me") ||
    normalizedUrl.includes("/api/v1/auth/refresh") ||
    normalizedUrl.includes("/api/v1/auth/me/quick") ||
    normalizedUrl.includes("/auth/me") ||
    normalizedUrl.includes("/auth/refresh")
  ) {
    return true;
  }

  return false;
};

/**
 * Axios instance for API communication
 * - BASE_URL should NOT include /api/v1
 * - All requests should use /api/v1/endpoint format
 * - Tokens are automatically injected by request interceptor
 */
const axiosClient = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

// ---- Diagnostic logging on initialization ----
if (isVerboseAxiosDebugEnabled()) {
  console.group("Axios Client Configuration");
  console.log("Base URL:", BASE_URL);
  console.log("Timeout:", axiosClient.defaults.timeout, "ms");
  console.log("Endpoint reachable at:", `${BASE_URL}/health`);
  console.log("Expected backend:", BASE_URL.includes("127.0.0.1") ? "localhost (127.0.0.1)" : "remote");
  console.log("Current page origin:", window.location?.origin);
  console.log("Environment:", process.env.NODE_ENV);
  console.groupEnd();
}

// Quick connectivity test with detailed diagnostics
if (typeof window !== "undefined" && isVerboseAxiosDebugEnabled()) {
  setTimeout(() => {
    const testURL = `${BASE_URL}/api/v1/system/health`;
    console.log(`Testing connectivity to: ${testURL}`);

    fetch(testURL, {
      method: "GET",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
      }
    })
      .then(res => {
        console.log(`Backend responded with status ${res.status}`);
        return res.json();
      })
      .then(data => console.log("Backend data:", data))
      .catch(err => {
        console.error("Backend connectivity check failed");
        console.error("Error type:", err.name);
        console.error("Error message:", err.message);
        console.error("Attempted URL:", testURL);
        console.error("Verify backend is running at:", BASE_URL);
      });
  }, 1000);
}

// ---- Request interceptor ----
axiosClient.interceptors.request.use(
  (config) => {
    normalizeBaseUrlForRequest(config);
    const token = readTokenSafe();
    if (isAuthDebugEnabled()) {
      console.log("[GTS][axiosClient] Auth token present:", Boolean(token));
    }
    const hasAuthHeader =
      config?.headers?.Authorization || config?.headers?.authorization;

    if (token && !hasAuthHeader) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ---- Response interceptor ----
axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const isCanceled =
      error?.code === "ERR_CANCELED" ||
      error?.message === "canceled" ||
      error?.message?.toLowerCase?.() === "canceled" ||
      error?.name === "CanceledError";

    const status = error?.response?.status;
    const data = error?.response?.data;
    const url = error?.config?.url || "";
    const originalRequest = error?.config || {};
    const hadToken = Boolean(readTokenSafe());
    const isAuthEndpoint =
      url.includes("/api/v1/auth/token") || url.includes("/api/v1/auth/refresh");

    if (status === 401 || status === 403) {
      authTrace(`HTTP ${status} on ${url}`, {
        data,
        hadToken,
        isAuthEndpoint,
      });
    }

    // Suppress logging for expected development errors (endpoints not yet implemented)
    const isSalesIntelligenceEndpoint = url?.includes("/sales_intelligence");
    const isAdminEndpoint = url?.includes("/api/v1/admin") || url?.includes("/data-sources/");
    const isFinanceEndpoint = url?.includes("/finance/");
    const isPlatformEndpoint = url?.includes("/platform/expenses");
    const isMaintenanceEndpoint =
      url?.includes("/maintenance/") ||
      url?.includes("/dev_maintenance/");
    const isExpectedDevError =
      (status === 404 ||
        status === 401 ||
        error?.message === "Network Error") &&
      (isSalesIntelligenceEndpoint ||
        isAdminEndpoint ||
        isFinanceEndpoint ||
        isPlatformEndpoint ||
        isMaintenanceEndpoint);

    // Enhanced network error diagnostics
    if (error.code === "ERR_NETWORK" && !isCanceled && isVerboseAxiosDebugEnabled()) {
      console.group("NETWORK ERROR DETECTED");
      console.error("Backend Not Responding");
      console.table({
        "Attempted URL": originalRequest.url,
        "Base URL": originalRequest.baseURL,
        "Full URL": `${originalRequest.baseURL}${originalRequest.url}`,
        "Method": originalRequest.method?.toUpperCase() || "GET",
        "Timeout (ms)": originalRequest.timeout,
        "Time": new Date().toLocaleTimeString(),
      });

      // Log full error details
      console.error("Full Error Object:", {
        code: error.code,
        message: error.message,
        errno: error.errno,
        syscall: error.syscall,
        isAxiosError: error.isAxiosError,
        config: {
          method: error.config?.method,
          url: error.config?.url,
          baseURL: error.config?.baseURL,
          timeout: error.config?.timeout,
        },
      });

      console.error("Troubleshooting Steps:");
      console.error("   1. Is backend running? Check terminal for 'Uvicorn running'");
      console.error("   2. Backend port 8000 check: http://127.0.0.1:8000/api/v1/system/health");
      console.error("   3. Verify VITE_API_BASE_URL in frontend/.env = http://127.0.0.1:8000");
      console.error("   4. Restart Vite in frontend");
      console.groupEnd();
    }

    if (
      process.env.NODE_ENV !== "production" &&
      !isCanceled &&
      !isExpectedDevError &&
      !isAuthEndpoint &&
      isVerboseAxiosDebugEnabled()
    ) {
      if (error.code !== "ERR_NETWORK") {  // Already logged above
        console.error("[Axios Error]", {
          status,
          url,
          message: error?.message,
          code: error?.code,
          data: error?.response?.data,
        });
      }
    }

    // ---- Normalize error to always be a string or safe object ----
    const normalizeErrorData = (errorData) => {
      if (!errorData) return "Request failed.";

      // If it's already a string
      if (typeof errorData === "string") {
        return errorData;
      }

      // If it's Pydantic validation errors (array of objects)
      if (Array.isArray(errorData)) {
        return errorData
          .map((err) => {
            if (typeof err === "string") return err;
            if (err.msg) return err.msg;
            if (err.message) return err.message;
            return JSON.stringify(err);
          })
          .filter(Boolean)
          .join("; ");
      }

      // If it's an object with common error fields
      if (typeof errorData === "object") {
        if (errorData.detail) {
          // If detail is an array, join them
          if (Array.isArray(errorData.detail)) {
            return errorData.detail
              .map((d) => {
                if (typeof d === "string") return d;
                if (typeof d === "object") return d.msg || JSON.stringify(d);
                return String(d);
              })
              .filter(Boolean)
              .join("; ");
          }
          // If detail is a string or object
          return typeof errorData.detail === "string"
            ? errorData.detail
            : normalizeErrorData(errorData.detail);
        }

        if (errorData.message) return errorData.message;
        if (errorData.msg) return errorData.msg;
        if (errorData.error) return errorData.error;

        // Try to find any string value
        for (const [key, value] of Object.entries(errorData)) {
          if (typeof value === "string" && value.trim()) {
            return value;
          }
        }

        // Last resort: stringify (but only log, don't show to user)
        return "Request processing error";
      }

      return "Request failed.";
    };

    error.normalized = {
      status,
      detail: normalizeErrorData(data) || error?.message || "Request failed.",
    };

    if (status === 401 && !isAuthEndpoint) {
      if (!originalRequest._retry) {
        originalRequest._retry = true;
        try {
          const newToken = await refreshAccessToken();
          if (newToken) {
            originalRequest.headers = originalRequest.headers || {};
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return axiosClient(originalRequest);
          }
        } catch {
          // ignore and fall through to clearAuthCache
        }
      }

      if (isHardAuthFailure({ status, url, detail: error?.normalized?.detail, hadToken })) {
        authTrace("Hard auth failure detected", {
          status,
          url,
          detail: error?.normalized?.detail,
        });
        clearAuthCache();

        const now = Date.now();
        if (!window.__gtsAuthExpiredAt || now - window.__gtsAuthExpiredAt > 1000) {
          window.__gtsAuthExpiredAt = now;
          try {
            window.dispatchEvent(
              new CustomEvent("auth:expired", { detail: { status, url } })
            );
          } catch { }
        }
      }
    }

    if (status === 422 && isAuthDebugEnabled()) {
      console.warn("[GTS][axiosClient] Validation error:", error?.normalized?.detail);
    }

    return Promise.reject(error);
  }
);

export default axiosClient;
