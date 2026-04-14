import { API_BASE_URL, WS_BASE_URL } from "../config/env.js";

const FETCH_PREFIXES = [
  "/api/",
  "/auth/",
  "/health",
  "/documents/",
  "/shipments/",
  "/reports/",
  "/ai/",
  "/vizion/",
  "/users/",
  "/emails/",
  "/notifications",
  "/safety",
  "/chatbot/",
  "/portal/",
  "/meta/",
  "/finance/",
  "/payment",
  "/payments/",
];

const WS_PREFIXES = [
  "/api/v1/ws",
  "/api/v1/transport/ws",
  "/api/v1/safety/ws",
  "/ws/",
];

const startsWithAny = (value, prefixes) =>
  prefixes.some((prefix) => value === prefix || value.startsWith(prefix));

const parseAbsoluteUrl = (value) => {
  try {
    return new URL(value);
  } catch {
    return null;
  }
};

const browserOrigin =
  typeof window !== "undefined" && window.location?.origin
    ? window.location.origin
    : null;
const apiTarget = parseAbsoluteUrl(API_BASE_URL);
const wsTarget = parseAbsoluteUrl(WS_BASE_URL);

const rewriteHttpUrl = (value) => {
  if (!value || !browserOrigin || !apiTarget) return value;

  let parsed;
  try {
    parsed = new URL(typeof value === "string" ? value : String(value), browserOrigin);
  } catch {
    return value;
  }

  const isRelative = typeof value === "string" && value.startsWith("/");
  const isFrontendOrigin = parsed.origin === browserOrigin;
  if (!(isRelative || isFrontendOrigin)) return value;
  if (!startsWithAny(parsed.pathname, FETCH_PREFIXES)) return value;

  parsed.protocol = apiTarget.protocol;
  parsed.host = apiTarget.host;
  return parsed.toString();
};

const rewriteWsUrl = (value) => {
  if (!value || !browserOrigin || !wsTarget) return value;

  let parsed;
  try {
    parsed = new URL(typeof value === "string" ? value : String(value), browserOrigin);
  } catch {
    return value;
  }

  const frontendWsOrigin =
    browserOrigin.replace(/^http:\/\//, "ws://").replace(/^https:\/\//, "wss://");
  const isRelative = typeof value === "string" && value.startsWith("/");
  const isFrontendOrigin =
    parsed.origin === browserOrigin || parsed.origin === frontendWsOrigin;
  if (!(isRelative || isFrontendOrigin)) return value;
  if (!startsWithAny(parsed.pathname, WS_PREFIXES)) return value;

  parsed.protocol = wsTarget.protocol;
  parsed.host = wsTarget.host;
  return parsed.toString();
};

export const installNetworkRuntime = () => {
  if (typeof window === "undefined" || window.__GTS_NETWORK_RUNTIME_INSTALLED__) {
    return;
  }

  const nativeFetch = window.fetch.bind(window);
  window.fetch = (input, init) => {
    if (typeof input === "string") {
      return nativeFetch(rewriteHttpUrl(input), init);
    }

    if (input instanceof URL) {
      return nativeFetch(rewriteHttpUrl(input.toString()), init);
    }

    if (input instanceof Request) {
      const rewrittenUrl = rewriteHttpUrl(input.url);
      if (rewrittenUrl !== input.url) {
        return nativeFetch(new Request(rewrittenUrl, input), init);
      }
    }

    return nativeFetch(input, init);
  };

  const NativeWebSocket = window.WebSocket;
  class RoutedWebSocket extends NativeWebSocket {
    static CONNECTING = NativeWebSocket.CONNECTING;
    static OPEN = NativeWebSocket.OPEN;
    static CLOSING = NativeWebSocket.CLOSING;
    static CLOSED = NativeWebSocket.CLOSED;

    constructor(url, protocols) {
      super(rewriteWsUrl(url), protocols);
    }
  }

  window.WebSocket = RoutedWebSocket;
  window.__GTS_NETWORK_RUNTIME_INSTALLED__ = true;
};
