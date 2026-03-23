import { WS_BASE_URL } from "../config/env";
import { appendTokenToWsUrl, isSocketUnauthorized, notifySocketUnauthorized } from "./wsHelpers";

let singleton = null;

function normalizeBase(base) {
  return String(base || "").replace(/\/+$/, "");
}

function buildWsUrl(path) {
  const base = normalizeBase(WS_BASE_URL);
  const p = String(path || "").startsWith("/") ? path : `/${path}`;
  return `${base}${p}`;
}

function buildAuthWsUrl(path) {
  return appendTokenToWsUrl(buildWsUrl(path));
}

class WSClient {
  constructor() {
    this.url = null;
    this.ws = null;
    this.subscriptions = new Set();
    this.handlers = new Set();
    this.closedByUser = false;
    this._reconnectTimer = null;
    this._retryCount = 0;
    this._maxRetries = 5;
    this._retryDelay = 3000;
  }

  connect() {
    if (this.ws) return;

    const url = buildAuthWsUrl("/live");
    if (!url) {
      // Silently skip if no token
      return;
    }

    // Stop retrying after max retries
    if (this._retryCount >= this._maxRetries) {
      if (this._retryCount === this._maxRetries) {
        console.warn(`[WS] Max retries (${this._maxRetries}) reached. WebSocket disabled.`);
        this._retryCount++; // Increment to prevent showing this message again
      }
      return;
    }

    this.closedByUser = false;
    this.url = url;

    try {
      this.ws = new WebSocket(this.url);
    } catch (err) {
      console.error("[WS] Failed to create WebSocket:", err.message);
      this._scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      this._retryCount = 0; // Reset retry count on successful connection
      for (const ch of this.subscriptions) {
        this.send({ type: "subscribe", channel: ch });
      }
    };

    this.ws.onmessage = (e) => {
      let data = e.data;
      try {
        data = JSON.parse(e.data);
      } catch { }
      for (const fn of this.handlers) fn(data);
    };

    this.ws.onclose = (event) => {
      this.ws = null;

      if (this._reconnectTimer) {
        clearTimeout(this._reconnectTimer);
        this._reconnectTimer = null;
      }

      if (isSocketUnauthorized(event)) {
        notifySocketUnauthorized(event);
        return;
      }

      if (!this.closedByUser && this.subscriptions.size > 0) {
        this._scheduleReconnect();
      }
    };

    this.ws.onerror = (err) => {
      // Silently handle error - onclose will trigger reconnect
    };
  }

  _scheduleReconnect() {
    if (this._reconnectTimer) {
      clearTimeout(this._reconnectTimer);
    }

    this._retryCount++;

    if (this._retryCount >= this._maxRetries) {
      return;
    }

    const delay = Math.min(this._retryDelay * this._retryCount, 30000);
    this._reconnectTimer = setTimeout(() => this.connect(), delay);
  }

  disconnect() {
    this.closedByUser = true;

    if (this._reconnectTimer) {
      clearTimeout(this._reconnectTimer);
      this._reconnectTimer = null;
    }

    if (this.ws) {
      try {
        this.ws.close();
      } catch { }
      this.ws = null;
    }
  }

  send(msg) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(msg));
    }
  }

  subscribe(channel) {
    const ch = String(channel || "").trim();
    if (!ch) return;

    this.subscriptions.add(ch);
    this.connect();

    // If already open, subscribe immediately; otherwise onopen will do it.
    this.send({ type: "subscribe", channel: ch });
  }

  onMessage(fn) {
    if (typeof fn !== "function") return () => { };
    this.handlers.add(fn);
    return () => this.handlers.delete(fn);
  }
}

export function getWSClient() {
  if (!singleton) {
    singleton = new WSClient();
  }
  return singleton;
}
