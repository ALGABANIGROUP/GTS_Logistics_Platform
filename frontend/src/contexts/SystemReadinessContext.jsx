import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { API_BASE_URL } from "../config/env";

const READINESS_URL = `${String(API_BASE_URL || "").replace(/\/+$/, "")}/api/v1/system/readiness`;
const MAX_RETRY_ATTEMPTS = 3;
const RETRY_DELAY_MS = 4000;
const CACHE_TTL_MS = 90_000;

const SystemReadinessContext = createContext(null);

export const SystemReadinessProvider = ({ children }) => {
  const [state, setState] = useState({
    loading: false,
    error: null,
    ready: false,
    checks: null,
  });

  const attemptsRef = useRef(0);
  const retryTimerRef = useRef(null);
  const lastOkAtRef = useRef(0);
  const lastCheckedAtRef = useRef(0);
  const refreshRef = useRef(null);

  const scheduleRetry = useCallback(() => {
    if (attemptsRef.current >= MAX_RETRY_ATTEMPTS) return;
    attemptsRef.current += 1;
    if (retryTimerRef.current) {
      clearTimeout(retryTimerRef.current);
    }
    const delayMs = Math.min(RETRY_DELAY_MS * attemptsRef.current, 12_000);
    retryTimerRef.current = window.setTimeout(() => {
      if (refreshRef.current) {
        refreshRef.current(true);
      }
    }, delayMs);
  }, []);

  const refresh = useCallback(
    async (force = false) => {
      const now = Date.now();
      if (!force) {
        if (lastOkAtRef.current && now - lastOkAtRef.current < CACHE_TTL_MS) {
          return;
        }
        if (
          lastCheckedAtRef.current &&
          now - lastCheckedAtRef.current < CACHE_TTL_MS
        ) {
          return;
        }
      }

      lastCheckedAtRef.current = now;
      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        const controller = new AbortController();
        const timeoutId = window.setTimeout(() => controller.abort(), 5000);
        const res = await fetch(READINESS_URL, {
          method: "GET",
          signal: controller.signal,
        });
        clearTimeout(timeoutId);

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        const ok = Boolean(data?.ok);

        setState({
          loading: false,
          error: ok ? null : null,
          ready: ok,
          checks: data?.checks || null,
        });

        if (ok) {
          lastOkAtRef.current = Date.now();
          attemptsRef.current = 0;
        } else {
          scheduleRetry();
        }
      } catch (err) {
        const message =
          err?.name === "AbortError"
            ? "Readiness check timed out."
            : err?.message || "Backend not reachable.";
        setState({
          loading: false,
          error: message,
          ready: false,
          checks: null,
        });
        scheduleRetry();
      }
    },
    [scheduleRetry]
  );

  useEffect(() => {
    refreshRef.current = refresh;
  }, [refresh]);

  useEffect(() => {
    refresh(false);
    return () => {
      if (retryTimerRef.current) {
        clearTimeout(retryTimerRef.current);
      }
    };
  }, [refresh]);

  useEffect(() => {
    const onExpired = () => refresh(true);
    window.addEventListener("auth:expired", onExpired);
    return () => window.removeEventListener("auth:expired", onExpired);
  }, [refresh]);

  const value = useMemo(() => ({ state, refresh }), [state, refresh]);

  return (
    <SystemReadinessContext.Provider value={value}>
      {children}
    </SystemReadinessContext.Provider>
  );
};

export const useSystemReadiness = () => {
  const ctx = useContext(SystemReadinessContext);
  if (!ctx) {
    return {
      state: { loading: false, error: null, ready: true, checks: null },
      refresh: () => {},
    };
  }
  return ctx;
};
