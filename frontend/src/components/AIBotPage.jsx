import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import axiosClient from "../api/axiosClient";
import SystemReadinessGate from "./SystemReadinessGate.jsx";
import { useRefreshSubscription } from "../contexts/UiActionsContext.jsx";

const DEFAULT_MESSAGE = "ping";

const toStatusLabel = (status) => {
  if (!status || typeof status !== "object") return "unknown";
  if (typeof status.status === "string") return status.status;
  if (status.ok === true) return "ok";
  if (status.ok === false) return "error";
  return "unknown";
};

const formatTime = (value) => {
  if (!value) return "never";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "unknown";
  return date.toLocaleString();
};

const getErrorMessage = (error, fallback) => {
  return (
    error?.normalized?.detail ||
    error?.response?.data?.detail ||
    error?.response?.data?.error ||
    error?.message ||
    fallback
  );
};

const parseContext = (raw) => {
  const trimmed = String(raw || "").trim();
  if (!trimmed) return { value: {} };
  try {
    const parsed = JSON.parse(trimmed);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return { error: "Context must be a JSON object." };
    }
    return { value: parsed };
  } catch (err) {
    return { error: "Context must be valid JSON." };
  }
};

export default function AIBotPage({
  botKey,
  title,
  description,
  defaultMessage = "",
  relatedLinks = [],
  metaSource = "ui",
  mode = "active",
  preview = false,
}) {
  const [statusData, setStatusData] = useState(null);
  const [configData, setConfigData] = useState(null);
  const [statusError, setStatusError] = useState("");
  const [configError, setConfigError] = useState("");
  const [loadingStatus, setLoadingStatus] = useState(false);
  const [loadingConfig, setLoadingConfig] = useState(false);

  const [message, setMessage] = useState(defaultMessage || "");
  const [contextText, setContextText] = useState("{}");
  const [contextError, setContextError] = useState("");
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState(null);
  const [runError, setRunError] = useState("");
  const [lastRunTime, setLastRunTime] = useState(null);

  const botLabel = title || botKey;
  const isPreview = preview || mode === "preview";

  const loadStatus = useCallback(async () => {
    if (isPreview) return;
    if (!botKey) return;
    setLoadingStatus(true);
    setStatusError("");
    try {
      const res = await axiosClient.get(
        `/api/v1/ai/bots/available/${encodeURIComponent(botKey)}/status`
      );
      setStatusData(res?.data || null);
    } catch (error) {
      setStatusError(getErrorMessage(error, "Failed to load status."));
      setStatusData(null);
    } finally {
      setLoadingStatus(false);
    }
  }, [botKey]);

  const loadConfig = useCallback(async () => {
    if (isPreview) return;
    if (!botKey) return;
    setLoadingConfig(true);
    setConfigError("");
    try {
      const res = await axiosClient.get(
        `/api/v1/ai/bots/available/${encodeURIComponent(botKey)}/config`
      );
      setConfigData(res?.data || null);
    } catch (error) {
      setConfigError(getErrorMessage(error, "Config is not available."));
      setConfigData(null);
    } finally {
      setLoadingConfig(false);
    }
  }, [botKey]);

  const refreshAll = useCallback(() => {
    if (isPreview) return;
    loadStatus();
    loadConfig();
  }, [isPreview, loadStatus, loadConfig]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  useRefreshSubscription(refreshAll);

  const runBot = async () => {
    if (isPreview) return;
    if (!botKey) return;
    const parsed = parseContext(contextText);
    if (parsed.error) {
      setContextError(parsed.error);
      return;
    }
    setContextError("");
    setRunError("");
    setRunning(true);
    setRunResult(null);

    try {
      const payload = {
        message: message?.trim() || DEFAULT_MESSAGE,
        context: parsed.value || {},
        meta: { source: metaSource },
      };
      const res = await axiosClient.post(
        `/api/v1/ai/bots/available/${encodeURIComponent(botKey)}/run`,
        payload
      );
      setRunResult(res?.data || null);
      setLastRunTime(res?.data?.ts || null);
    } catch (error) {
      setRunError(getErrorMessage(error, "Failed to run the bot."));
    } finally {
      setRunning(false);
    }
  };

  const statusLabel = useMemo(
    () => toStatusLabel(statusData?.status),
    [statusData]
  );

  return (
    <SystemReadinessGate>
      <div className="space-y-6">
        {isPreview ? (
          <div className="rounded-2xl border border-amber-400/30 bg-amber-500/10 px-4 py-3 text-xs text-amber-100">
            <div className="font-semibold text-white">Intelligence Mode</div>
            <div className="mt-1 text-amber-100/80">
              Backend execution is not active yet. You can review metadata and
              use the unified control view.
            </div>
          </div>
        ) : null}
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-2xl font-semibold text-white">
              {botLabel || "AI Bot"}
            </div>
            {description ? (
              <div className="mt-1 text-sm text-slate-300">{description}</div>
            ) : null}
          </div>
          {botKey ? (
            <div className="rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-200">
              {botKey}
            </div>
          ) : null}
        </div>

        <div className="grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
          <div className="rounded-2xl border border-white/10 bg-white/10 p-5 shadow-lg shadow-black/40 backdrop-blur">
            <div className="text-sm font-semibold text-white">Run bot</div>
            <div className="mt-3 space-y-3">
              <textarea
                rows={3}
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                placeholder="Message to send to the bot"
                className="w-full rounded-lg border border-white/10 bg-slate-950/60 px-3 py-2 text-sm text-white placeholder:text-slate-500"
              />
              <details className="rounded-lg border border-white/10 bg-slate-950/40 p-3">
                <summary className="cursor-pointer text-xs font-semibold text-slate-200">
                  Advanced context (JSON)
                </summary>
                <textarea
                  rows={4}
                  value={contextText}
                  onChange={(event) => setContextText(event.target.value)}
                  className="mt-3 w-full rounded-lg border border-white/10 bg-slate-950/60 px-3 py-2 text-xs text-white placeholder:text-slate-500"
                />
                {contextError ? (
                  <div className="mt-2 text-xs text-rose-200">{contextError}</div>
                ) : null}
              </details>
              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={runBot}
                  disabled={running || isPreview}
                  className="rounded-lg bg-sky-500/80 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isPreview ? "Preview mode" : running ? "Running..." : "Run bot"}
                </button>
                <button
                  type="button"
                  onClick={refreshAll}
                  className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold text-slate-200 transition hover:bg-white/10"
                >
                  Refresh status
                </button>
              </div>
              {runError ? (
                <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-100">
                  {runError}
                </div>
              ) : null}
              {lastRunTime ? (
                <div className="text-xs text-slate-400">
                  Last run: {formatTime(lastRunTime)}
                </div>
              ) : null}
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-2xl border border-white/10 bg-white/10 p-5 shadow-lg shadow-black/40 backdrop-blur">
              <div className="text-sm font-semibold text-white">Status</div>
              {loadingStatus ? (
                <div className="mt-3 text-xs text-slate-400">Loading status...</div>
              ) : statusError ? (
                <div className="mt-3 text-xs text-slate-300">
                  <p className="text-rose-300">{statusError}</p>
                </div>
              ) : (
                <div className="mt-3 space-y-2 text-xs text-slate-200">
                  <div className="flex items-center justify-between">
                    <span>Status</span>
                    <span className="font-semibold text-white">{statusLabel}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Timestamp</span>
                    <span>{formatTime(statusData?.ts)}</span>
                  </div>
                </div>
              )}
              {statusData?.status ? (
                <details className="mt-3 rounded-lg border border-white/10 bg-slate-950/40 p-3">
                  <summary className="cursor-pointer text-xs font-semibold text-slate-200">
                    View status payload
                  </summary>
                  <pre className="mt-2 max-h-40 overflow-auto text-[11px] text-slate-300">
                    {JSON.stringify(statusData.status, null, 2)}
                  </pre>
                </details>
              ) : null}
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/10 p-5 shadow-lg shadow-black/40 backdrop-blur">
              <div className="text-sm font-semibold text-white">Config</div>
              {loadingConfig ? (
                <div className="mt-3 text-xs text-slate-400">Loading config...</div>
              ) : configError ? (
                <p className="mt-3 text-xs text-slate-300">{configError}</p>
              ) : configData?.config ? (
                <pre className="mt-3 max-h-40 overflow-auto rounded-lg border border-white/10 bg-slate-950/40 p-3 text-[11px] text-slate-300">
                  {JSON.stringify(configData.config, null, 2)}
                </pre>
              ) : (
                <div className="mt-3 text-xs text-slate-400">No config data.</div>
              )}
            </div>
          </div>
        </div>

        {runResult ? (
          <div className="rounded-2xl border border-white/10 bg-white/10 p-5 shadow-lg shadow-black/40 backdrop-blur">
            <div className="text-sm font-semibold text-white">Latest run result</div>
            <pre className="mt-3 max-h-80 overflow-auto rounded-lg border border-white/10 bg-slate-950/40 p-3 text-[11px] text-slate-300">
              {JSON.stringify(runResult, null, 2)}
            </pre>
          </div>
        ) : null}

        {relatedLinks.length ? (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-xs text-slate-200">
            <div className="font-semibold text-white">Related tools</div>
            <div className="mt-2 flex flex-wrap gap-2">
              {relatedLinks.map((link) => (
                <Link
                  key={link.href}
                  to={link.href}
                  className="rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs font-semibold text-slate-200 hover:bg-white/20"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </SystemReadinessGate>
  );
}
