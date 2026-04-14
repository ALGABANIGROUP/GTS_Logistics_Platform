import { startTransition, useDeferredValue, useEffect, useMemo, useState } from "react";
import "./TaskManager.css";

const INITIAL_FORM = {
  title: "",
  description: "",
  category: "",
  priority: "2",
  expected: "",
  due_ts: "",
};

const FILTERS = [
  { key: "all", label: "All Tasks" },
  { key: "pending", label: "Pending" },
  { key: "in_progress", label: "In Progress" },
  { key: "today", label: "Today" },
  { key: "done", label: "Done" },
  { key: "rules", label: "Auto Rules" },
  { key: "scheduled", label: "Scheduled" },
];

const fetchJson = async (url, init) => {
  const response = await fetch(url, {
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  if (response.status === 204) return null;
  return response.json();
};

const formatDateTime = (value) => {
  if (!value) return "Not scheduled";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString();
};

const isToday = (value) => {
  if (!value) return false;
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return false;
  const now = new Date();
  return (
    parsed.getFullYear() === now.getFullYear() &&
    parsed.getMonth() === now.getMonth() &&
    parsed.getDate() === now.getDate()
  );
};

const getPriorityMeta = (value) => {
  const numeric = Number(value);
  if (numeric <= 1) return { label: "Urgent", cls: "urgent" };
  if (numeric === 2) return { label: "High", cls: "high" };
  if (numeric === 3) return { label: "Medium", cls: "medium" };
  return { label: "Low", cls: "low" };
};

const getStatusMeta = (status) => {
  switch (status) {
    case "in_progress":
      return { label: "In Progress", cls: "active" };
    case "done":
      return { label: "Completed", cls: "done" };
    default:
      return { label: "Pending", cls: "pending" };
  }
};

const sortTasks = (tasks, order) => {
  const list = [...tasks];
  if (order === "updated") {
    return list.toSorted((a, b) => String(b.updated_at || "").localeCompare(String(a.updated_at || "")));
  }
  if (order === "due") {
    return list.toSorted((a, b) => {
      if (!a.due_ts && !b.due_ts) return 0;
      if (!a.due_ts) return 1;
      if (!b.due_ts) return -1;
      return String(a.due_ts).localeCompare(String(b.due_ts));
    });
  }
  return list.toSorted((a, b) => {
    const priorityDiff = Number(a.priority || 99) - Number(b.priority || 99);
    if (priorityDiff !== 0) return priorityDiff;
    return String(b.updated_at || "").localeCompare(String(a.updated_at || ""));
  });
};

const flattenBoard = (board) => [
  ...(board?.todo || []),
  ...(board?.in_progress || []),
  ...(board?.done || []),
];

const taskMatchesFilter = (task, activeTab) => {
  switch (activeTab) {
    case "pending":
      return task.status === "open";
    case "in_progress":
      return task.status === "in_progress";
    case "done":
      return task.status === "done";
    case "today":
      return isToday(task.due_ts);
    default:
      return true;
  }
};

export default function TaskManager() {
  const [boardData, setBoardData] = useState(null);
  const [summary, setSummary] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  const [order, setOrder] = useState("priority");
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(INITIAL_FORM);

  const deferredSearch = useDeferredValue(search.trim().toLowerCase());

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [boardRes, summaryRes, eventsRes] = await Promise.all([
        fetchJson(`/vizion/board?order=${order}&include_eta=true`),
        fetchJson("/vizion/summary"),
        fetchJson("/vizion/events?limit=12"),
      ]);

      setBoardData(boardRes);
      setSummary(summaryRes.summary || null);
      setEvents(eventsRes.events || []);
    } catch (nextError) {
      setError(nextError?.message || "Failed to load task telemetry.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const timer = setInterval(load, 30000);
    return () => clearInterval(timer);
  }, [order]);

  const tasks = useMemo(() => {
    const base = sortTasks(flattenBoard(boardData?.board), order);
    return base.filter((task) => {
      if (!taskMatchesFilter(task, activeTab)) return false;
      if (categoryFilter && task.category !== categoryFilter) return false;
      if (!deferredSearch) return true;
      const haystack = [task.title, task.category, task.status].join(" ").toLowerCase();
      return haystack.includes(deferredSearch);
    });
  }, [activeTab, boardData, categoryFilter, deferredSearch, order]);

  const categories = useMemo(() => {
    const values = new Set(flattenBoard(boardData?.board).map((task) => task.category).filter(Boolean));
    return [...values].toSorted((a, b) => a.localeCompare(b));
  }, [boardData]);

  const counts = useMemo(() => {
    const source = summary || {};
    return {
      open: source.open ?? boardData?.board?.todo?.length ?? 0,
      in_progress: source.in_progress ?? boardData?.board?.in_progress?.length ?? 0,
      done: source.done ?? boardData?.board?.done?.length ?? 0,
      spent_minutes: source.spent_minutes ?? 0,
    };
  }, [boardData, summary]);

  const queueCards = [
    {
      title: "Manual queue",
      value: counts.open + counts.in_progress + counts.done,
      description: "Persisted VIZION tasks available through the current backend.",
    },
    {
      title: "Automatic rules",
      value: "Planned",
      description: "UI lane reserved. Backend rule endpoints are not exposed yet.",
    },
    {
      title: "Scheduled tasks",
      value: "Planned",
      description: "Cron-backed recurring jobs are part of the target design, not wired yet.",
    },
  ];

  const mutateTask = async (taskId, action) => {
    const endpointMap = {
      start: `/vizion/tasks/${taskId}/start`,
      stop: `/vizion/tasks/${taskId}/stop`,
      complete: `/vizion/tasks/${taskId}/complete`,
      reopen: `/vizion/tasks/${taskId}/reopen`,
    };
    await fetchJson(endpointMap[action], { method: "POST" });
    await load();
  };

  const createTask = async (event) => {
    event.preventDefault();
    if (!form.title.trim()) return;

    setSaving(true);
    setError("");
    try {
      await fetchJson("/vizion/tasks", {
        method: "POST",
        body: JSON.stringify({
          title: form.title.trim(),
          description: form.description.trim(),
          category: form.category.trim(),
          priority: Number(form.priority),
          expected: form.expected ? Number(form.expected) : null,
          due_ts: form.due_ts || null,
        }),
      });

      setForm(INITIAL_FORM);
      setShowCreate(false);
      await load();
    } catch (nextError) {
      setError(nextError?.message || "Failed to create task.");
    } finally {
      setSaving(false);
    }
  };

  const switchTab = (key) => {
    startTransition(() => setActiveTab(key));
  };

  const showRealTasks = activeTab !== "rules" && activeTab !== "scheduled";

  return (
    <div className="vizion-task-page">
      <section className="task-shell">
        <div className="task-hero">
          <div>
            <div className="task-breadcrumb">Admin / TheVIZION / Task Manager</div>
            <h1>Task Manager</h1>
            <p>
              Manual task operations are live today. Automatic rules and recurring schedules are
              represented in the UI so the section matches the target architecture without masking
              what is still pending in the backend.
            </p>
          </div>

          <div className="task-hero-actions">
            <button type="button" className="task-primary-btn" onClick={() => setShowCreate(true)}>
              + New Task
            </button>
            <button type="button" className="task-secondary-btn" onClick={load}>
              Refresh
            </button>
          </div>
        </div>

        {error ? <div className="task-banner task-banner-warn">{error}</div> : null}
        {loading ? <div className="task-banner">Loading TheVIZION task signals...</div> : null}

        <div className="task-stats-grid">
          <article className="task-stat-card">
            <span>Pending</span>
            <strong>{counts.open}</strong>
            <small>Ready to start.</small>
          </article>
          <article className="task-stat-card">
            <span>In Progress</span>
            <strong>{counts.in_progress}</strong>
            <small>Tracked with active work sessions.</small>
          </article>
          <article className="task-stat-card">
            <span>Done</span>
            <strong>{counts.done}</strong>
            <small>Completed and logged in VIZION.</small>
          </article>
          <article className="task-stat-card">
            <span>Spent Minutes</span>
            <strong>{counts.spent_minutes}</strong>
            <small>Total time recorded across all sessions.</small>
          </article>
        </div>

        <div className="task-workspace">
          <div className="task-main-panel">
            <div className="task-tab-strip">
              {FILTERS.map((filter) => (
                <button
                  key={filter.key}
                  type="button"
                  className={filter.key === activeTab ? "task-tab active" : "task-tab"}
                  onClick={() => switchTab(filter.key)}
                >
                  {filter.label}
                </button>
              ))}
            </div>

            <div className="task-toolbar">
              <input
                type="text"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                className="task-input"
                placeholder="Search by title, category, or status"
              />

              <select
                value={categoryFilter}
                onChange={(event) => setCategoryFilter(event.target.value)}
                className="task-select"
                disabled={!showRealTasks}
              >
                <option value="">All categories</option>
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>

              <select value={order} onChange={(event) => setOrder(event.target.value)} className="task-select">
                <option value="priority">Priority</option>
                <option value="updated">Last updated</option>
                <option value="due">Due date</option>
              </select>
            </div>

            {showRealTasks ? (
              <div className="task-list">
                {tasks.length ? (
                  tasks.map((task) => {
                    const priority = getPriorityMeta(task.priority);
                    const status = getStatusMeta(task.status);

                    return (
                      <article key={task.id} className="task-card">
                        <div className="task-card-head">
                          <div className="task-card-title-group">
                            <span className={`task-priority task-priority-${priority.cls}`}>{priority.label}</span>
                            <h3>{task.title}</h3>
                          </div>
                          <span className={`task-status task-status-${status.cls}`}>{status.label}</span>
                        </div>

                        <div className="task-card-meta">
                          <span>{task.category || "general"}</span>
                          <span>ETA {task.eta_min != null ? `${Math.round(task.eta_min)} min` : "n/a"}</span>
                          <span>Spent {task.spent_min != null ? `${Math.round(task.spent_min)} min` : "0 min"}</span>
                          <span>Due {formatDateTime(task.due_ts)}</span>
                        </div>

                        <div className="task-card-footer">
                          <div className="task-card-update">Updated {formatDateTime(task.updated_at)}</div>
                          <div className="task-card-actions">
                            {task.status === "open" ? (
                              <button type="button" className="task-action-btn" onClick={() => mutateTask(task.id, "start")}>
                                Start
                              </button>
                            ) : null}

                            {task.status === "in_progress" ? (
                              <>
                                <button type="button" className="task-action-btn ghost" onClick={() => mutateTask(task.id, "stop")}>
                                  Stop
                                </button>
                                <button type="button" className="task-action-btn" onClick={() => mutateTask(task.id, "complete")}>
                                  Complete
                                </button>
                              </>
                            ) : null}

                            {task.status === "done" ? (
                              <button type="button" className="task-action-btn ghost" onClick={() => mutateTask(task.id, "reopen")}>
                                Reopen
                              </button>
                            ) : null}
                          </div>
                        </div>
                      </article>
                    );
                  })
                ) : (
                  <div className="task-empty-state">No tasks match the current filter set.</div>
                )}
              </div>
            ) : (
              <div className="task-planned-panel">
                <h3>{activeTab === "rules" ? "Automatic Task Rules" : "Scheduled Task Queue"}</h3>
                <p>
                  This lane is part of the TheVIZION target design, but the current backend only
                  exposes manual task operations through `/vizion/tasks`, `/vizion/board`,
                  `/vizion/summary`, and `/vizion/events`.
                </p>
                <ul>
                  <li>Recommended backend endpoint family: `/api/v1/tasks/rules`.</li>
                  <li>Persist rule conditions, event triggers, and actions in a dedicated table.</li>
                  <li>Wire cron-backed recurring tasks once scheduler ownership is defined.</li>
                </ul>
              </div>
            )}
          </div>

          <aside className="task-side-panel">
            <section className="task-side-card">
              <h2>Queue Design</h2>
              <div className="task-queue-grid">
                {queueCards.map((card) => (
                  <article key={card.title} className="task-mini-card">
                    <span>{card.title}</span>
                    <strong>{card.value}</strong>
                    <small>{card.description}</small>
                  </article>
                ))}
              </div>
            </section>

            <section className="task-side-card">
              <h2>Recent Activity</h2>
              <div className="task-event-list">
                {events.length ? (
                  events.map((event, index) => (
                    <article key={`${event.ts}-${event.event}-${index}`} className="task-event-item">
                      <div className="task-event-head">
                        <span>{event.event}</span>
                        <time>{formatDateTime(event.ts)}</time>
                      </div>
                      <p>{event.message || "No event message."}</p>
                    </article>
                  ))
                ) : (
                  <div className="task-empty-inline">No recent task events.</div>
                )}
              </div>
            </section>

            <section className="task-side-card">
              <h2>Target Automation Examples</h2>
              <ul className="task-guidance-list">
                <li>Shipment created -&gt; dispatch follow-up task.</li>
                <li>Invoice overdue -&gt; collections task.</li>
                <li>Document expiry -&gt; compliance review task.</li>
                <li>08:00 daily -&gt; operational summary task.</li>
              </ul>
            </section>
          </aside>
        </div>
      </section>

      {showCreate ? (
        <div className="task-modal-backdrop" onClick={() => setShowCreate(false)}>
          <div className="task-modal" onClick={(event) => event.stopPropagation()}>
            <div className="task-modal-head">
              <div>
                <h2>Create Manual Task</h2>
                <p>Persist a task into the live TheVIZION board.</p>
              </div>
              <button type="button" className="task-close-btn" onClick={() => setShowCreate(false)}>
                x
              </button>
            </div>

            <form className="task-form" onSubmit={createTask}>
              <label>
                <span>Title</span>
                <input
                  type="text"
                  className="task-input"
                  value={form.title}
                  onChange={(event) => setForm((prev) => ({ ...prev, title: event.target.value }))}
                  placeholder="Shipment dispatch follow-up"
                  required
                />
              </label>

              <label>
                <span>Description</span>
                <textarea
                  className="task-textarea"
                  value={form.description}
                  onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
                  placeholder="Optional execution context"
                  rows={4}
                />
              </label>

              <div className="task-form-grid">
                <label>
                  <span>Category</span>
                  <input
                    type="text"
                    className="task-input"
                    value={form.category}
                    onChange={(event) => setForm((prev) => ({ ...prev, category: event.target.value }))}
                    placeholder="shipment"
                  />
                </label>

                <label>
                  <span>Priority</span>
                  <select
                    className="task-select"
                    value={form.priority}
                    onChange={(event) => setForm((prev) => ({ ...prev, priority: event.target.value }))}
                  >
                    <option value="1">Urgent</option>
                    <option value="2">High</option>
                    <option value="3">Medium</option>
                    <option value="4">Low</option>
                  </select>
                </label>

                <label>
                  <span>Expected minutes</span>
                  <input
                    type="number"
                    min="0"
                    className="task-input"
                    value={form.expected}
                    onChange={(event) => setForm((prev) => ({ ...prev, expected: event.target.value }))}
                    placeholder="45"
                  />
                </label>

                <label>
                  <span>Due date</span>
                  <input
                    type="datetime-local"
                    className="task-input"
                    value={form.due_ts}
                    onChange={(event) => setForm((prev) => ({ ...prev, due_ts: event.target.value }))}
                  />
                </label>
              </div>

              <div className="task-form-actions">
                <button type="button" className="task-secondary-btn" onClick={() => setShowCreate(false)}>
                  Cancel
                </button>
                <button type="submit" className="task-primary-btn" disabled={saving}>
                  {saving ? "Saving..." : "Create task"}
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </div>
  );
}
