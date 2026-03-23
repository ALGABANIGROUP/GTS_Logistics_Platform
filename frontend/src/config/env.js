// E:\GTS Logistics\frontend\src\config\env.js
const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const DEFAULT_WS_PATH = "/api/v1/ws";
const DEFAULT_WS_URL = `ws://127.0.0.1:8000${DEFAULT_WS_PATH}`;

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  DEFAULT_API_BASE_URL;

const deriveWsBaseFromUrl = (value) => {
  if (!value) return null;
  try {
    const parsed = new URL(value);
    const prefix = parsed.protocol === "https:" ? "wss" : "ws";
    return `${prefix}://${parsed.host}${DEFAULT_WS_PATH}`;
  } catch {
    return null;
  }
};

const wsFromApi = deriveWsBaseFromUrl(API_BASE_URL);
const browserWs =
  typeof window !== "undefined" && window.location && window.location.host
    ? `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}${DEFAULT_WS_PATH}`
    : null;

export const WS_BASE_URL =
  import.meta.env.VITE_WS_BASE_URL ||
  import.meta.env.VITE_WS_URL ||
  import.meta.env.VITE_WEBSOCKET_URL ||
  wsFromApi ||
  browserWs ||
  DEFAULT_WS_URL;

const parseBool = (value) =>
  ["1", "true", "yes", "on"].includes(String(value || "").toLowerCase());

export const HCAPTCHA_DISABLED = parseBool(
  import.meta.env.VITE_HCAPTCHA_DISABLED
);

export const HCAPTCHA_SITEKEY =
  HCAPTCHA_DISABLED ? "" : import.meta.env.VITE_HCAPTCHA_SITEKEY || "";
