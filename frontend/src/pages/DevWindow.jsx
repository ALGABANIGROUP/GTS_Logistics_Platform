// frontend/src/pages/DevWindow.jsx
import React, { useEffect, useRef, useState } from "react";

/** ===========================
 * /** ===========================
 *  Config
 *  =========================== */
// Use VITE_API_BASE_URL when provided; fallback to Vite proxy when empty.
const API_BASE =
  (typeof import.meta !== "undefined" &&
    import.meta?.env?.VITE_API_BASE_URL) ||
  ""; // if empty, Vite proxy may be used

const api = (path) => `${API_BASE}${path}`;


/** ===========================
 *  Tiny UI (no shadcn/ui)
 *  =========================== */
function Card({ className = "", children, ...rest }) {
  return (
    <div className={`rounded-2xl border bg-white ${className}`} {...rest}>
      {children}
    </div>
  );
}
function CardContent({ className = "", children }) {
  return <div className={`p-4 ${className}`}>{children}</div>;
}
function Button({ children, className = "", variant = "primary", size = "md", ...props }) {
  const base = "inline-flex items-center justify-center rounded-xl font-medium transition active:scale-[.98]";
  const sizes = { sm: "h-8 px-3 text-sm", md: "h-9 px-4 text-sm", lg: "h-10 px-5" };
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-slate-100 text-slate-900 hover:bg-slate-200",
    outline: "border bg-transparent hover:bg-slate-50",
    ghost: "hover:bg-slate-100",
  };
  return (
    <button className={`${base} ${sizes[size]} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}
function Badge({ children, className = "" }) {
  return <span className={`inline-flex items-center rounded-lg px-2 py-0.5 text-xs ${className}`}>{children}</span>;
}
function Input(props) {
  return (
    <input
      {...props}
      className={`h-9 px-3 rounded-xl border bg-white outline-none focus:ring-2 focus:ring-blue-200 ${props.className || ""}`}
    />
  );
}
function Select({ value, onChange, children, className = "" }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
      className={`h-9 px-3 rounded-xl border bg-white text-sm outline-none focus:ring-2 focus:ring-blue-200 ${className}`}
    >
      {children}
    </select>
  );
}
function Textarea(props) {
  return (
    <textarea
      {...props}
      className={`rounded-xl border bg-white outline-none focus:ring-2 focus:ring-blue-200 px-3 py-2 text-sm ${props.className || ""}`}
    />
  );
}

/** ===========================
 *  Utils
 *  =========================== */
function fmtDate(s) {
  if (!s) return "--";
  try {
    const d = new Date(s);
    return d.toLocaleString();
  } catch {
    return s;
  }
}
function PriorityBadge({ value }) {
  const v = Number.isFinite(+value) ? +value : 9999;
  const label = isFinite(v) ? `P${v}` : "P?";
  const color = v <= 1 ? "bg-green-100 text-green-700" : v <= 2 ? "bg-yellow-100 text-yellow-800" : "bg-gray-100 text-gray-800";
  return <Badge className={`${color} font-medium`}>{label}</Badge>;
}
function StatusBadge({ status }) {
  const s = (status || "").toLowerCase();
  const map = {
    open: { text: "To-Do", cls: "bg-slate-100 text-slate-700" },
    in_progress: { text: "In Progress", cls: "bg-blue-100 text-blue-700" },
    done: { text: "Done", cls: "bg-emerald-100 text-emerald-700" },
  };
  const obj = map[s] || { text: status || "?", cls: "bg-zinc-100 text-zinc-700" };
  return <Badge className={obj.cls}>{obj.text}</Badge>;
}
function ErrorBanner({ error, onRetry }) {
  if (!error) return null;
  return (
    <div className="flex items-center gap-3 p-3 rounded-xl border bg-amber-50 text-amber-900">
      <span>[warn]</span>
      <div className="text-sm flex-1 truncate" title={String(error?.message || error)}>
        {String(error?.message || error)}
      </div>
      {onRetry && (
        <Button size="sm" variant="secondary" onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  );
}

/** ===========================
 *  Data hooks (fetch)
 *  =========================== */
function useBoard({ category, order, includeEta }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const qs = new URLSearchParams();
      if (category) qs.set("category", category);
      if (order) qs.set("order", order);
      if (includeEta != null) qs.set("include_eta", String(includeEta));
      const res = await fetch(api(`/vizion/board?${qs.toString()}`), { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const j = await res.json();
      setData(j);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    load();
    const t = setInterval(load, 30000);
    return () => clearInterval(t);
  }, [category, order, includeEta]);
  return { data, loading, error, reload: load };
}
function useSummary() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(api(`/vizion/summary`), { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const j = await res.json();
      setSummary(j.summary || j);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    load();
    const t = setInterval(load, 60000);
    return () => clearInterval(t);
  }, []);
  return { summary, loading, error, reload: load };
}
function useEvents(limit = 50) {
  const [events, setEvents] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const qs = new URLSearchParams({ limit: String(limit) });
      const res = await fetch(api(`/vizion/events?${qs.toString()}`), { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const j = await res.json();
      setEvents(j?.events || j || []);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    load();
    const t = setInterval(load, 30000);
    return () => clearInterval(t);
  }, [limit]);
  return { events, loading, error, reload: load };
}

/** ===========================
 *  Actions
 *  =========================== */
async function startTask(id) {
  const r = await fetch(api(`/vizion/tasks/${id}/start`), { method: "POST" });
  if (!r.ok) throw new Error("start failed");
}
async function stopTask(id, { keepalive = false } = {}) {
  const r = await fetch(api(`/vizion/tasks/${id}/stop`), { method: "POST", keepalive });
  if (!r.ok) throw new Error("stop failed");
}
async function completeTask(id) {
  let r = await fetch(api(`/vizion/tasks/${id}/done`), { method: "POST" });
  if (r.status === 404 || r.status === 405) {
    r = await fetch(api(`/vizion/tasks/${id}/complete`), { method: "POST" });
  }
  if (!r.ok) throw new Error("complete failed");
}
async function reopenTask(id) {
  const r = await fetch(api(`/vizion/tasks/${id}/reopen`), { method: "POST" });
  if (!r.ok) throw new Error("reopen failed");
}
async function createTask(payload) {
  const r = await fetch(api(`/vizion/tasks`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error("create failed");
  return r.json();
}
async function addNote(taskId, text) {
  const r = await fetch(api(`/vizion/tasks/${taskId}/notes`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!r.ok) throw new Error("add note failed");
  return r.json();
}

/** ===========================
 *  UI pieces
 *  =========================== */
function TaskCard({ t, onChanged, onOpen }) {
  const [busy, setBusy] = useState(false);
  const wrap = (fn) => async (e) => {
    e?.stopPropagation?.();
    try {
      setBusy(true);
      await fn();
      onChanged?.();
    } catch (e2) {
      alert(String(e2?.message || e2));
    } finally {
      setBusy(false);
    }
  };
  const onStart = wrap(() => startTask(t.id));
  const onStop = wrap(() => stopTask(t.id));
  const onComplete = wrap(() => completeTask(t.id));
  const onReopen = wrap(() => reopenTask(t.id));

  return (
    <Card className="flex flex-col cursor-pointer hover:bg-slate-50 transition" onClick={() => onOpen?.(t)}>
      <CardContent className="flex flex-col gap-3">
        <div className="flex items-center justify-between gap-3">
          <div className="font-semibold leading-tight truncate" title={t.title}>
            {t.title}
          </div>
          <PriorityBadge value={t.priority} />
        </div>
        <div className="flex items-center gap-2 text-xs">
          <StatusBadge status={t.status} />
          {t.category && <Badge className="border">{t.category}</Badge>}
          {t.eta_min != null && <span className="inline-flex items-center gap-1 text-slate-500">ETA {Math.round(t.eta_min)}m</span>}
          {t.spent_min > 0 && <span className="inline-flex items-center gap-1 text-slate-500">Spent {Math.round(t.spent_min)}m</span>}
        </div>
        <div className="grid grid-cols-2 gap-3 text-xs text-slate-500">
          <div>
            <div className="text-[11px]">Updated</div>
            {fmtDate(t.updated_at)}
          </div>
          <div>
            <div className="text-[11px]">Due</div>
            {fmtDate(t.due_ts)}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" size="sm" onClick={onStart} disabled={busy}>
            Start
          </Button>
          <Button variant="secondary" size="sm" onClick={onStop} disabled={busy}>
            Stop
          </Button>
          {String(t.status).toLowerCase() !== "done" ? (
            <Button size="sm" onClick={onComplete} disabled={busy}>
              Complete
            </Button>
          ) : (
            <Button variant="outline" size="sm" onClick={onReopen} disabled={busy}>
              Reopen
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function Column({ title, items, onChanged, onOpen }) {
  return (
    <div className="flex flex-col gap-3 min-h-[200px]">
      <div className="text-sm font-semibold opacity-70">
        {title} <span className="opacity-60">({items?.length || 0})</span>
      </div>
      {items?.length ? (
        items.map((t) => <TaskCard key={t.id} t={t} onChanged={onChanged} onOpen={onOpen} />)
      ) : (
        <div className="text-xs text-slate-500 border rounded-xl py-6 text-center">No items</div>
      )}
    </div>
  );
}

function Field({ label, children, className = "" }) {
  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <div className="text-xs text-slate-500">{label}</div>
      {children}
    </div>
  );
}

function NewTask({ onCreated }) {
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("");
  const [priority, setPriority] = useState("2");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    setLoading(true);
    try {
      await createTask({ title, category, priority: Number(priority) });
      setTitle("");
      setCategory("");
      setPriority("2");
      onCreated?.();
    } catch (e2) {
      alert(String(e2?.message || e2));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="flex flex-wrap gap-3 items-end">
      <Field label="Title" className="min-w-[240px]">
        <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Task title" />
      </Field>
      <Field label="Category">
        <Input value={category} onChange={(e) => setCategory(e.target.value)} placeholder="e.g. feature" />
      </Field>
      <Field label="Priority">
        <Select value={priority} onChange={setPriority} className="w-[120px]">
          <option value="1">P1</option>
          <option value="2">P2</option>
          <option value="3">P3</option>
          <option value="4">P4</option>
        </Select>
      </Field>
      <Button type="submit" disabled={loading}>
        {loading ? "..." : "Add Task"}
      </Button>
    </form>
  );
}

/** ===========================
 *  Focus Panel (Auto Start/Stop)
 *  =========================== */
function FocusPanel({ task, onClose, onChanged }) {
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [sec, setSec] = useState(0);
  const autoStartedRef = useRef(false);
  const tickRef = useRef(null);

  // Auto-start when opening if task is open
  useEffect(() => {
    (async () => {
      if (!task) return;
      if (String(task.status).toLowerCase() === "open") {
        try {
          await startTask(task.id);
          autoStartedRef.current = true;
          onChanged?.();
        } catch {
          /* ignore */
        }
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [task?.id]);

  // Simple timer while focused
  useEffect(() => {
    tickRef.current = setInterval(() => setSec((s) => s + 1), 1000);
    return () => clearInterval(tickRef.current);
  }, []);

  // Helper to stop (optionally with keepalive)
  const stopIfNeeded = async ({ keepalive = false } = {}) => {
    if (autoStartedRef.current && task) {
      try {
        await stopTask(task.id, { keepalive });
      } catch {
        /* ignore */
      }
      autoStartedRef.current = false;
      onChanged?.();
    }
  };

  // Stop if tab/window is closing (beforeunload + unload)
  useEffect(() => {
    const handler = () => {
      if (autoStartedRef.current && task) {
        try {
          // try keepalive fetch first
          fetch(api(`/vizion/tasks/${task.id}/stop`), { method: "POST", keepalive: true }).catch(() => { });
          // best-effort beacon fallback
          navigator.sendBeacon?.(api(`/vizion/tasks/${task.id}/stop`), new Blob([]));
        } catch {
          /* ignore */
        }
      }
    };
    window.addEventListener("beforeunload", handler);
    window.addEventListener("unload", handler);
    return () => {
      window.removeEventListener("beforeunload", handler);
      window.removeEventListener("unload", handler);
    };
  }, [task?.id]);

  // Stop if page becomes hidden
  useEffect(() => {
    const onVis = () => {
      if (document.visibilityState === "hidden" && autoStartedRef.current && task) {
        fetch(api(`/vizion/tasks/${task.id}/stop`), { method: "POST", keepalive: true }).catch(() => { });
      }
    };
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, [task?.id]);

  const doAddNote = async () => {
    if (!note.trim()) return;
    setBusy(true);
    try {
      await addNote(task.id, note.trim());
      setNote("");
      onChanged?.();
    } finally {
      setBusy(false);
    }
  };

  const doComplete = async () => {
    setBusy(true);
    try {
      await stopIfNeeded({ keepalive: true });
      await completeTask(task.id);
      onChanged?.();
      onClose?.();
    } finally {
      setBusy(false);
    }
  };

  const doClose = async () => {
    setBusy(true);
    try {
      await stopIfNeeded({ keepalive: true });
      onClose?.();
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/30" onClick={doClose} />
      <div className="absolute right-0 top-0 h-full w-full md:w-[440px] bg-white shadow-xl p-5 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div className="min-w-0">
            <div className="font-semibold truncate" title={task.title}>
              {task.title}
            </div>
            <div className="text-xs text-slate-500 mt-0.5">Focused | {sec}s</div>
          </div>
          <div className="flex items-center gap-2">
            <PriorityBadge value={task.priority} />
            <StatusBadge status={task.status} />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 text-xs text-slate-500">
          <Field label="Category">
            <div>{task.category || "--"}</div>
          </Field>
          <Field label="ETA">
            <div>{task.eta_min != null ? `${Math.round(task.eta_min)}m` : "--"}</div>
          </Field>
          <Field label="Updated">
            <div>{fmtDate(task.updated_at)}</div>
          </Field>
          <Field label="Due">
            <div>{fmtDate(task.due_ts)}</div>
          </Field>
        </div>

        <div className="flex flex-col gap-2">
          <Field label="Add note">
            <div className="flex gap-2">
              <Textarea rows={3} value={note} onChange={(e) => setNote(e.target.value)} placeholder="Type a note..." />
              <Button onClick={doAddNote} disabled={busy || !note.trim()}>
                Add
              </Button>
            </div>
          </Field>
        </div>

        <div className="mt-auto flex flex-wrap gap-2">
          <Button variant="secondary" onClick={doClose} disabled={busy}>
            Close (auto-stop)
          </Button>
          <Button onClick={doComplete} disabled={busy}>
            {busy ? "..." : "Complete"}
          </Button>
        </div>
      </div>
    </div>
  );
}

/** ===========================
 *  Page
 *  =========================== */
export default function DevWindow({ title = "Developer Window" }) {
  const [category, setCategory] = useState("");
  const [order, setOrder] = useState("priority");
  const [includeEta, setIncludeEta] = useState(true);

  const { data: boardRes, loading: loadingBoard, error: errBoard, reload: reloadBoard } = useBoard({
    category,
    order,
    includeEta,
  });
  const { summary, loading: loadingSummary, error: errSummary, reload: reloadSummary } = useSummary();
  const { events, loading: loadingEvents, error: errEvents, reload: reloadEvents } = useEvents(50);

  const counts = boardRes?.counts || summary || {};
  const cols = boardRes?.board || { todo: [], in_progress: [], done: [] };

  const [openedTask, setOpenedTask] = useState(null);

  const reloadAll = () => {
    reloadBoard();
    reloadSummary();
    reloadEvents();
  };

  // Auto-close the FocusPanel when the opened task becomes "done"
  useEffect(() => {
    if (!openedTask || !boardRes?.board) return;
    const findById = (arr) => arr?.find?.((x) => x.id === openedTask.id);
    const latest =
      findById(boardRes.board.in_progress) || findById(boardRes.board.todo) || findById(boardRes.board.done);
    if (latest && String(latest.status).toLowerCase() === "done") {
      setOpenedTask(null);
    }
  }, [boardRes?.generated_at, openedTask?.id, boardRes?.board, openedTask]);

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" onClick={reloadAll}>
            Refresh
          </Button>
        </div>
      </div>

      {/* Errors */}
      <div className="flex flex-col gap-2 mb-4">
        <ErrorBanner error={errBoard} onRetry={reloadBoard} />
        <ErrorBanner error={errSummary} onRetry={reloadSummary} />
        <ErrorBanner error={errEvents} onRetry={reloadEvents} />
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <Card>
          <CardContent>
            <div className="text-xs text-slate-500">Open</div>
            <div className="text-2xl font-semibold">
              {counts.open ?? (loadingSummary || loadingBoard ? "..." : "--")}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <div className="text-xs text-slate-500">In Progress</div>
            <div className="text-2xl font-semibold">
              {counts.in_progress ?? (loadingSummary || loadingBoard ? "..." : "--")}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <div className="text-xs text-slate-500">Done</div>
            <div className="text-2xl font-semibold">
              {counts.done ?? (loadingSummary || loadingBoard ? "..." : "--")}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <div className="text-xs text-slate-500">Spent (min)</div>
            <div className="text-2xl font-semibold">
              {counts.spent_minutes != null
                ? Math.round((counts.spent_minutes || 0) * 10) / 10
                : loadingSummary || loadingBoard
                  ? "..."
                  : "--"}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters & New task */}
      <div className="rounded-2xl border p-4 mb-6">
        <div className="flex flex-wrap items-end gap-3">
          <Field label="Filter by Category">
            <Input value={category} onChange={(e) => setCategory(e.target.value)} placeholder="feature | ops | ..." />
          </Field>
          <Field label="Order">
            <Select value={order} onChange={setOrder} className="w-[180px]">
              <option value="priority">Priority</option>
              <option value="updated">Last Updated</option>
              <option value="due">Due Date</option>
            </Select>
          </Field>
          <div className="flex items-center gap-2 text-sm">
            <input
              id="eta"
              type="checkbox"
              className="size-4"
              checked={includeEta}
              onChange={(e) => setIncludeEta(e.target.checked)}
            />
            <label htmlFor="eta" className="text-sm">
              Include ETA
            </label>
          </div>
        </div>
        <div className="mt-4">
          <NewTask onCreated={reloadAll} />
        </div>
      </div>

      {/* Board */}
      <div className="grid md:grid-cols-3 gap-4">
        <div className="rounded-2xl border p-4">
          <Column title="To-Do" items={cols.todo} onChanged={reloadAll} onOpen={setOpenedTask} />
        </div>
        <div className="rounded-2xl border p-4">
          <Column title="In Progress" items={cols.in_progress} onChanged={reloadAll} onOpen={setOpenedTask} />
        </div>
        <div className="rounded-2xl border p-4">
          <Column title="Done" items={cols.done} onChanged={reloadAll} onOpen={setOpenedTask} />
        </div>
      </div>

      {/* Events Timeline */}
      <div className="rounded-2xl border p-4 mt-6">
        <div className="flex items-center justify-between mb-3">
          <div className="text-sm font-semibold">Events (latest)</div>
          {loadingEvents && <span className="text-sm text-slate-500">loading...</span>}
        </div>
        {!events?.length ? (
          <div className="text-xs text-slate-500 border rounded-xl py-6 text-center">No events</div>
        ) : (
          <div className="divide-y">
            {events.map((e, idx) => (
              <div key={idx} className="py-2 text-sm flex flex-wrap gap-x-4 gap-y-1">
                <div className="font-mono text-xs opacity-70">{fmtDate(e.created_at || e.ts)}</div>
                <div className="font-medium">{e.event || e.type}</div>
                {e.message && <div className="opacity-80">- {e.message}</div>}
                {e.meta && (
                  <div className="text-xs text-slate-500 w-full truncate">
                    {typeof e.meta === "string" ? e.meta : JSON.stringify(e.meta)}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="text-xs text-slate-500 mt-6">
        Generated at: {boardRes?.generated_at ? fmtDate(boardRes.generated_at) : "--"}
      </div>

      {/* Focus side panel with auto start/stop */}
      {openedTask && <FocusPanel task={openedTask} onClose={() => setOpenedTask(null)} onChanged={reloadAll} />}
    </div>
  );
}
