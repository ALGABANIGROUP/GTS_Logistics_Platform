import { readAuthToken } from "./authStorage";

const AUTH_CLOSE_CODES = new Set([4001, 4011, 4401]);

export function appendTokenToWsUrl(baseUrl, overrideToken) {
  if (!baseUrl) {
    return null;
  }

  const token = overrideToken || readAuthToken();
  if (!token) {
    return null;
  }

  const encoded = encodeURIComponent(token);
  try {
    const url = new URL(baseUrl);
    url.searchParams.set("token", token);
    return url.toString();
  } catch {
    const delimiter = baseUrl.includes("?") ? "&" : "?";
    return `${baseUrl}${delimiter}token=${encoded}`;
  }
}

export function isSocketUnauthorized(eventOrCode) {
  const code =
    typeof eventOrCode === "number"
      ? eventOrCode
      : eventOrCode?.code ?? eventOrCode?.target?.code;
  return AUTH_CLOSE_CODES.has(Number(code));
}

export function notifySocketUnauthorized(eventOrCode) {
  const code =
    typeof eventOrCode === "number"
      ? eventOrCode
      : eventOrCode?.code ?? eventOrCode?.target?.code;

  if (typeof window === "undefined") {
    return;
  }

  try {
    window.dispatchEvent(
      new CustomEvent("auth:socket-unauthorized", {
        detail: { code: Number(code) || null },
      })
    );
  } catch {
    // ignore
  }
}
