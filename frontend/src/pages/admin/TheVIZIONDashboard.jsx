import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import "./TheVIZIONDashboard.css";

const emptyState = {
  loading: true,
  error: "",
  summary: null,
  board: null,
  events: [],
};

const formatDateTime = (value) => {
  if (!value) return "Not available";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString();
};

const toneClass = (value, positiveThreshold = 1) => {
  if (typeof value !== "number") return "muted";
  if (value >= positiveThreshold) return "ok";
  return "muted";
};

export default function TheVIZIONDashboard() {
  const [state, setState] = useState(emptyState);

  useEffect(() => {
    let active = true;

    const load = async () => {
      setState((prev) => ({ ...prev, loading: true, error: "" }));

      const [summaryRes, boardRes, eventsRes] = await Promise.allSettled([
        fetch("/vizion/summary", { cache: "no-store" }),
        fetch("/vizion/board?include_eta=true", { cache: "no-store" }),
        fetch("/vizion/events?limit=10", { cache: "no-store" }),
      ]);

      if (!active) return;

      const parseJson = async (result) => {
        if (result.status !== "fulfilled") throw result.reason;
        if (!result.value.ok) {
          throw new Error(`HTTP ${result.value.status}`);
        }
        return result.value.json();
      };

      try {
        const [summary, board, events] = await Promise.all([
          parseJson(summaryRes),
          parseJson(boardRes),
          parseJson(eventsRes),
        ]);

        if (!active) return;

        setState({
          loading: false,
          error: "",
          summary: summary.summary || null,
          board: board || null,
          events: events.events || [],
        });
      } catch (error) {
        if (!active) return;
        setState({
          loading: false,
          error: error?.message || "Failed to load TheVIZION telemetry.",
          summary: null,
          board: null,
          events: [],
        });
      }
    };

    load();
    return () => {
      active = false;
    };
  }, []);

  const counters = useMemo(() => {
    const summary = state.summary || {};
    const board = state.board?.board || {};
    return {
      open: summary.open ?? board.todo?.length ?? 0,
      inProgress: summary.in_progress ?? board.in_progress?.length ?? 0,
      done: summary.done ?? board.done?.length ?? 0,
      spent: summary.spent_minutes ?? 0,
      total:
        (summary.open ?? board.todo?.length ?? 0) +
        (summary.in_progress ?? board.in_progress?.length ?? 0) +
        (summary.done ?? board.done?.length ?? 0),
    };
  }, [state.summary, state.board]);

  const latestTask = useMemo(() => {
    const board = state.board?.board || {};
    const all = [...(board.in_progress || []), ...(board.todo || []), ...(board.done || [])];
    if (!all.length) return null;
    return all.toSorted((a, b) => String(b.updated_at || "").localeCompare(String(a.updated_at || "")))[0];
  }, [state.board]);

  const capabilityCards = [
    {
      title: "Task Manager",
      status: "Live",
      description:
        "Manual task creation, priority queueing, session tracking, completion flow, and event logging are available now.",
      to: "/admin/TheVIZION/task-manager",
      cta: "Open Task Manager",
    },
    {
      title: "Events Stream",
      status: "Live",
      description:
        "Recent VIZION events are available through /vizion/events and power the operational timeline for task actions.",
      to: "/admin/TheVIZION/task-manager",
      cta: "Review activity",
    },
    {
      title: "Observability Core",
      status: "Live",
      description:
        "Board and summary endpoints expose the current task state, time spent, and active work in progress.",
      to: "/admin/TheVIZION/task-manager",
      cta: "Inspect queue",
    },
    {
      title: "Performance / Publish Logs",
      status: "Planned UI",
      description:
        "Tables exist in the backend model, but the /vizion frontend endpoints for these signals are not exposed yet.",
      to: null,
      cta: "Backend wiring pending",
    },
  ];

  return (
    <div className="vizion-dashboard">
      <section className="vizion-hero">
        <div className="vizion-hero-copy">
          <div className="vizion-eyebrow">Admin / TheVIZION</div>
          <h1>TheVIZION Observability Hub</h1>
          <p>
            TheVIZION is the platform eye for GTS. It tracks operational events, task execution,
            work sessions, and system visibility without coupling that telemetry to the core admin
            workflows.
          </p>
          <div className="vizion-actions">
            <Link to="/admin/TheVIZION/task-manager" className="vizion-primary-action">
              Open Task Manager
            </Link>
            <Link to="/dev-window" className="vizion-secondary-action">
              Open Developer Window
            </Link>
          </div>
        </div>

        <div className="vizion-hero-panel">
          <div className="vizion-signal-label">Live signal</div>
          <div className="vizion-signal-value">{state.loading ? "Loading..." : `${counters.total} tasks tracked`}</div>
          <div className="vizion-signal-meta">
            {latestTask
              ? `Latest task: ${latestTask.title} | updated ${formatDateTime(latestTask.updated_at)}`
              : "No tracked tasks yet."}
          </div>
        </div>
      </section>

      {state.error ? (
        <div className="vizion-banner vizion-banner-warn">
          TheVIZION live data is partially unavailable: {state.error}
        </div>
      ) : null}

      <section className="vizion-section">
        <div className="vizion-section-header">
          <h2>Operational Snapshot</h2>
          <p>Current state exposed by `/vizion/summary` and `/vizion/board`.</p>
        </div>

        <div className="vizion-stats-grid">
          <article className="vizion-stat-card">
            <span>Open queue</span>
            <strong className={`vizion-stat-value vizion-stat-${toneClass(counters.open)}`}>{counters.open}</strong>
            <small>Pending manual or reopened tasks.</small>
          </article>
          <article className="vizion-stat-card">
            <span>In progress</span>
            <strong className={`vizion-stat-value vizion-stat-${toneClass(counters.inProgress)}`}>{counters.inProgress}</strong>
            <small>Tasks with an active running session.</small>
          </article>
          <article className="vizion-stat-card">
            <span>Completed</span>
            <strong className={`vizion-stat-value vizion-stat-${toneClass(counters.done)}`}>{counters.done}</strong>
            <small>Closed work tracked through VIZION.</small>
          </article>
          <article className="vizion-stat-card">
            <span>Spent minutes</span>
            <strong className="vizion-stat-value">{counters.spent}</strong>
            <small>Total recorded work across sessions.</small>
          </article>
        </div>
      </section>

      <section className="vizion-section">
        <div className="vizion-section-header">
          <h2>What Is Live Now</h2>
          <p>The page reflects backend capabilities already exposed in the current project.</p>
        </div>

        <div className="vizion-capability-grid">
          {capabilityCards.map((card) => (
            <article key={card.title} className="vizion-capability-card">
              <div className="vizion-capability-head">
                <h3>{card.title}</h3>
                <span className={`vizion-pill vizion-pill-${card.status === "Live" ? "ok" : "planned"}`}>
                  {card.status}
                </span>
              </div>
              <p>{card.description}</p>
              {card.to ? (
                <Link to={card.to} className="vizion-inline-link">
                  {card.cta}
                </Link>
              ) : (
                <span className="vizion-inline-link vizion-inline-link-muted">{card.cta}</span>
              )}
            </article>
          ))}
        </div>
      </section>

      <section className="vizion-section vizion-two-column">
        <article className="vizion-panel">
          <div className="vizion-section-header">
            <h2>Architecture Intent</h2>
            <p>How TheVIZION fits the platform today.</p>
          </div>
          <ul className="vizion-list">
            <li>Observability layer for tasks, events, and execution sessions.</li>
            <li>Non-blocking admin support system for monitoring work and platform behavior.</li>
            <li>SQLite fallback and VIZION EYE toggles exist in backend configuration.</li>
            <li>Task Manager is one module inside TheVIZION, not the whole section.</li>
          </ul>
        </article>

        <article className="vizion-panel">
          <div className="vizion-section-header">
            <h2>Current Gaps</h2>
            <p>Items implied by the data model but not surfaced yet in the current UI/API.</p>
          </div>
          <ul className="vizion-list">
            <li>Dedicated frontend endpoints for performance logs.</li>
            <li>Dedicated frontend endpoints for publish logs.</li>
            <li>Persisted automation rules and cron-driven scheduled tasks.</li>
            <li>User assignment workflow and richer task metadata fields.</li>
          </ul>
        </article>
      </section>

      <section className="vizion-section">
        <div className="vizion-section-header">
          <h2>Recent Event Stream</h2>
          <p>Latest items emitted through `/vizion/events`.</p>
        </div>

        <div className="vizion-event-list">
          {state.events.length ? (
            state.events.map((event, index) => (
              <article key={`${event.ts}-${event.event}-${index}`} className="vizion-event-card">
                <div className="vizion-event-meta">
                  <span className="vizion-event-type">{event.event}</span>
                  <span>{formatDateTime(event.ts)}</span>
                </div>
                <div className="vizion-event-message">{event.message || "No event message provided."}</div>
                {event.meta && Object.keys(event.meta).length ? (
                  <pre className="vizion-event-payload">{JSON.stringify(event.meta, null, 2)}</pre>
                ) : null}
              </article>
            ))
          ) : (
            <div className="vizion-empty-state">No VIZION events have been recorded yet.</div>
          )}
        </div>
      </section>
    </div>
  );
}
