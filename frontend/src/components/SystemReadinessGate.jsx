import React, { useEffect, useRef, useState } from "react";
import { useRefreshSubscription } from "../contexts/UiActionsContext.jsx";
import { useSystemReadiness } from "../contexts/SystemReadinessContext.jsx";

const formatDetails = (checks) => {
  if (!checks || typeof checks !== "object") return [];
  return Object.entries(checks).map(([key, value]) => {
    if (!value || typeof value !== "object") {
      return { key, ok: false, detail: "Unavailable" };
    }
    if (value.ok === true) {
      return { key, ok: true, detail: "Ready" };
    }
    if (value.missing && Array.isArray(value.missing)) {
      return { key, ok: false, detail: `Missing: ${value.missing.join(", ")}` };
    }
    return { key, ok: false, detail: value.error || "Unavailable" };
  });
};

const SystemReadinessGate = ({
  children,
  title = "System checks pending",
  description = "Services are starting or temporarily unavailable. You can keep using the app.",
  showDetails = true,
}) => {
  const { state, refresh } = useSystemReadiness();
  const [showBanner, setShowBanner] = useState(false);
  const bannerTimerRef = useRef(null);

  useEffect(() => {
    if (state.ready) {
      if (bannerTimerRef.current) {
        clearTimeout(bannerTimerRef.current);
        bannerTimerRef.current = null;
      }
      setShowBanner(false);
      return;
    }
    if (bannerTimerRef.current) {
      clearTimeout(bannerTimerRef.current);
    }
    bannerTimerRef.current = window.setTimeout(() => {
      setShowBanner(true);
    }, 2500);
    return () => {
      if (bannerTimerRef.current) {
        clearTimeout(bannerTimerRef.current);
        bannerTimerRef.current = null;
      }
    };
  }, [state.ready, state.error, state.loading]);

  useRefreshSubscription(() => {
    refresh(true);
  });

  const detailRows = formatDetails(state.checks);
  const headline = state.error ? "Backend not reachable" : title;
  const subline = state.error ? state.error : description;

  return (
    <>
      {showBanner ? (
        <div className="mb-4 rounded-2xl border border-amber-400/30 bg-amber-500/10 p-4 text-sm text-amber-100 space-y-3">
          <div>
            <div className="text-sm font-semibold text-white">{headline}</div>
            <div className="text-xs text-amber-100/80">{subline}</div>
          </div>

          {state.loading ? (
            <div className="text-[11px] text-amber-100/70">
              Checking system readiness...
            </div>
          ) : null}

          {showDetails && detailRows.length ? (
            <div className="grid gap-2 text-xs">
              {detailRows.map((row) => (
                <div
                  key={row.key}
                  className="flex items-center justify-between rounded-lg border border-white/10 bg-white/5 px-3 py-2"
                >
                  <span className="font-semibold uppercase tracking-wide text-[10px] text-amber-100/70">
                    {row.key}
                  </span>
                  <span
                    className={`text-[11px] ${
                      row.ok ? "text-emerald-200" : "text-amber-200"
                    }`}
                  >
                    {row.detail}
                  </span>
                </div>
              ))}
            </div>
          ) : null}

          <button
            type="button"
            onClick={() => refresh(true)}
            className="inline-flex items-center justify-center rounded-lg border border-amber-400/40 bg-amber-500/20 px-3 py-2 text-xs font-semibold text-amber-100 hover:bg-amber-500/30"
          >
            Retry readiness check
          </button>
        </div>
      ) : null}
      {children}
    </>
  );
};

export default SystemReadinessGate;
