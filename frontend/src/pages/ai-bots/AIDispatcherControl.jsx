import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Bot,
  Copy,
  RefreshCcw,
  Save,
  Terminal,
  Clock,
  ShieldAlert,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import axiosClient from "../../api/axiosClient";
import SystemReadinessGate from "../../components/SystemReadinessGate.jsx";
import { useRefreshSubscription } from "../../contexts/UiActionsContext.jsx";
import "./AIDispatcherControl.css";

const DEFAULT_MESSAGE = "Analyze driver distribution for peak hours.";

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

const getStatusTone = ({ label, error }) => {
  const text = `${label || ""} ${error || ""}`.toLowerCase();
  if (text.includes("forbidden") || text.includes("403")) return "forbidden";
  if (text.includes("ok") || text.includes("online") || text.includes("ready")) return "online";
  if (text.includes("error") || text.includes("down") || text.includes("offline")) return "offline";
  return "unknown";
};

export default function AIDispatcherControl({ botKey: botKeyProp = "ai_dispatcher" }) {
  const [searchParams] = useSearchParams();
  const queryBot = (searchParams.get("bot") || "").trim();
  const botKey = queryBot || botKeyProp;

  const [statusData, setStatusData] = useState(null);
  const [configData, setConfigData] = useState(null);
  const [statusError, setStatusError] = useState("");
  const [configError, setConfigError] = useState("");
  const [loadingStatus, setLoadingStatus] = useState(false);
  const [loadingConfig, setLoadingConfig] = useState(false);

  const [message, setMessage] = useState(DEFAULT_MESSAGE);
  const [contextText, setContextText] = useState(
    JSON.stringify(
      {
        timeframe: "24h",
        priority: "optimization",
        region: "all",
        include_metrics: true,
        simulation_mode: false,
      },
      null,
      2
    )
  );
  const [contextError, setContextError] = useState("");
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState(null);
  const [runError, setRunError] = useState("");
  const [lastRunTime, setLastRunTime] = useState(null);
  const [expanded, setExpanded] = useState(false);

  const loadStatus = useCallback(async () => {
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
    loadStatus();
    loadConfig();
  }, [loadStatus, loadConfig]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  useRefreshSubscription(refreshAll);

  const runBot = async () => {
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
        meta: { source: "ui" },
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

  const statusTone = useMemo(
    () => getStatusTone({ label: statusLabel, error: statusError }),
    [statusLabel, statusError]
  );

  const configEntries = useMemo(() => {
    const config = configData?.config;
    if (!config || typeof config !== "object") return [];
    return Object.entries(config).slice(0, 6);
  }, [configData]);

  const handleCopy = async () => {
    if (!runResult) return;
    const text = JSON.stringify(runResult, null, 2);
    await navigator.clipboard.writeText(text);
  };

  const handleSave = () => {
    if (!runResult) return;
    const blob = new Blob([JSON.stringify(runResult, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ai_dispatcher_response_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const clearAll = () => {
    setMessage("");
    setContextText("{}");
    setRunResult(null);
    setRunError("");
  };

  return (
    <SystemReadinessGate>
      <div className="aid-control">
        <header className="aid-control-header">
          <div>
            <p className="aid-control-kicker">AI Bot Control</p>
            <h1>AID - AI Dispatcher</h1>
            <p className="aid-control-subtitle">
              Run and inspect the dispatcher bot with real-time telemetry.
            </p>
          </div>
          <div className="aid-control-meta">
            <div className={`aid-control-status ${statusTone}`}>
              {statusTone === "online" ? <ShieldCheck size={16} /> : <ShieldAlert size={16} />}
              <span>{statusTone === "online" ? "Online" : statusTone === "forbidden" ? "Forbidden" : "Offline"}</span>
            </div>
            <div className="aid-control-time">
              <Clock size={16} />
              <span>{new Date().toLocaleTimeString("en-US")}</span>
            </div>
          </div>
        </header>

        <section className="aid-control-grid">
          <div className="aid-control-card aid-control-info">
            <div className="aid-control-icon">
              <Bot size={26} />
            </div>
            <div>
              <h2>AI Dispatcher Bot</h2>
              <p>Smart dispatch and logistics optimization AI.</p>
            </div>
            <span className="aid-control-botid">{botKey}</span>
          </div>

          <div className="aid-control-statuscard">
            <div className="aid-control-card-header">
              <h3>Status</h3>
              <span className={`aid-control-badge ${statusTone}`}>{statusTone}</span>
            </div>
            {loadingStatus ? (
              <p className="aid-control-muted">Loading status...</p>
            ) : statusError ? (
              <p className="aid-control-error">{statusError}</p>
            ) : (
              <div className="aid-control-list">
                <div>
                  <span>Status</span>
                  <strong>{statusLabel}</strong>
                </div>
                <div>
                  <span>Last Active</span>
                  <strong>{formatTime(statusData?.ts)}</strong>
                </div>
                <div>
                  <span>Endpoint</span>
                  <strong>/api/v1/ai/bots/available/{botKey}</strong>
                </div>
              </div>
            )}
          </div>

          <div className="aid-control-configcard">
            <div className="aid-control-card-header">
              <h3>Configuration</h3>
              <button type="button" className="aid-control-light-btn" onClick={loadConfig}>
                <RefreshCcw size={16} /> Refresh
              </button>
            </div>
            {loadingConfig ? (
              <p className="aid-control-muted">Loading config...</p>
            ) : configError ? (
              <p className="aid-control-muted">{configError}</p>
            ) : configEntries.length ? (
              <div className="aid-control-config">
                {configEntries.map(([key, value]) => (
                  <div key={key}>
                    <span>{key}</span>
                    <strong>{String(value)}</strong>
                  </div>
                ))}
              </div>
            ) : (
              <p className="aid-control-muted">No config data.</p>
            )}
          </div>
        </section>

        <section className="aid-control-panel">
          <div className="aid-control-card-header">
            <h3>
              <Terminal size={18} /> Bot Control Panel
            </h3>
          </div>

          <label className="aid-control-label" htmlFor="bot-message">
            Message to send to the bot
          </label>
          <textarea
            id="bot-message"
            rows={3}
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Enter your message or command for the AI dispatcher..."
          />

          <button
            type="button"
            className="aid-control-context-toggle"
            onClick={() => setExpanded((prev) => !prev)}
          >
            Advanced context (JSON)
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          {expanded ? (
            <>
              <textarea
                className="aid-control-json"
                rows={6}
                value={contextText}
                onChange={(event) => setContextText(event.target.value)}
              />
              {contextError ? <p className="aid-control-error">{contextError}</p> : null}
            </>
          ) : null}

          <div className="aid-control-actions">
            <button type="button" className="aid-control-primary" onClick={runBot} disabled={running}>
              {running ? "Running..." : "Run Bot"}
            </button>
            <button type="button" className="aid-control-secondary" onClick={refreshAll}>
              Refresh Status
            </button>
            <button type="button" className="aid-control-ghost" onClick={clearAll}>
              Clear
            </button>
          </div>

          {runError ? <p className="aid-control-error">{runError}</p> : null}
          {lastRunTime ? (
            <p className="aid-control-muted">Last run: {formatTime(lastRunTime)}</p>
          ) : null}
        </section>

        <section className="aid-control-response">
          <div className="aid-control-card-header">
            <h3>Bot Response</h3>
            <div className="aid-control-response-actions">
              <button type="button" onClick={handleCopy} className="aid-control-icon-btn">
                <Copy size={16} />
              </button>
              <button type="button" onClick={handleSave} className="aid-control-icon-btn">
                <Save size={16} />
              </button>
            </div>
          </div>
          <div className="aid-control-response-body">
            {runResult ? (
              <pre>{JSON.stringify(runResult, null, 2)}</pre>
            ) : (
              <div className="aid-control-empty">
                <Bot size={32} />
                <p>Bot response will appear here after execution.</p>
              </div>
            )}
          </div>
        </section>
      </div>
    </SystemReadinessGate>
  );
}
