// frontend/src/config/env.ts
const DEFAULT_API_BASE_URL =
  typeof window !== "undefined" && window.location.origin
    ? window.location.origin
    : "";
const DEFAULT_WS_PATH = "/api/v1/ws";
const DEFAULT_WS_URL =
  typeof window !== "undefined" && window.location.host
    ? `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}${DEFAULT_WS_PATH}`
    : "";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  DEFAULT_API_BASE_URL;

const deriveWsBaseFromUrl = (value?: string): string | null => {
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
  typeof window !== "undefined" && window.location.host
    ? `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}${DEFAULT_WS_PATH}`
    : null;

export const WS_BASE_URL =
  import.meta.env.VITE_WS_BASE_URL ||
  import.meta.env.VITE_WS_URL ||
  import.meta.env.VITE_WEBSOCKET_URL ||
  wsFromApi ||
  browserWs ||
  DEFAULT_WS_URL;

export const FRONTEND_BASE_URL =
  import.meta.env.VITE_FRONTEND_BASE_URL ||
  (typeof window !== "undefined" && window.location.origin
    ? window.location.origin
    : "");
