import React, { useEffect, useState } from "react";
import axiosClient from "../../api/axiosClient";

const STATUS_STYLES = {
  completed: "bg-emerald-500/15 text-emerald-200",
  running: "bg-sky-500/15 text-sky-200",
  failed: "bg-rose-500/15 text-rose-200",
  skipped: "bg-amber-500/15 text-amber-200",
};

const formatTime = (value) => {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return "—";
  }
};

export default function ExecutionHistory({ refreshKey }) {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        setLoading(true);
        const res = await axiosClient.get("/api/v1/bots/history", {
          params: { limit: 50 },
        });
        const list = res?.data?.runs || [];
        if (active) setRuns(Array.isArray(list) ? list : []);
      } catch {
        if (active) setRuns([]);
      } finally {
        if (active) setLoading(false);
      }
    };

    load();
    return () => {
      active = false;
    };
  }, [refreshKey]);

  return (
    <div className="glass-panel rounded-2xl p-5 shadow-lg shadow-black/30">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-lg font-semibold text-white">Execution History</div>
          <div className="text-sm text-slate-300">
            Recent automated and human-triggered runs.
          </div>
        </div>
      </div>

      {loading ? (
        <div className="mt-4 text-sm text-slate-300">Loading history...</div>
      ) : runs.length === 0 ? (
        <div className="mt-4 text-sm text-slate-300">No runs recorded.</div>
      ) : (
        <div className="mt-4 space-y-3">
          {runs.map((run) => {
            const status = run.status || "completed";
            const badgeClass = STATUS_STYLES[status] || STATUS_STYLES.completed;
            return (
              <div
                key={run.id}
                className="rounded-xl border border-white/10 bg-white/5 p-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="text-sm font-semibold text-white">
                    {run.bot_name} · {run.task_type || "run"}
                  </div>
                  <span className={`rounded-full px-2 py-1 text-xs ${badgeClass}`}>
                    {status.toUpperCase()}
                  </span>
                </div>
                <div className="mt-2 grid gap-2 text-xs text-slate-300 sm:grid-cols-2">
                  <div>
                    <span className="text-slate-400">Started:</span>{" "}
                    {formatTime(run.started_at)}
                  </div>
                  <div>
                    <span className="text-slate-400">Finished:</span>{" "}
                    {formatTime(run.finished_at)}
                  </div>
                </div>
                {run.error ? (
                  <div className="mt-2 text-xs text-rose-200">
                    Error: {run.error}
                  </div>
                ) : null}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
