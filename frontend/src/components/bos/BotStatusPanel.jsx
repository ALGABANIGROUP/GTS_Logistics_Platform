import React, { useEffect, useState } from "react";
import axiosClient from "../../api/axiosClient";

const STATUS_STYLES = {
  idle: "bg-slate-500/20 text-slate-200",
  running: "bg-sky-500/20 text-sky-200",
  error: "bg-rose-500/20 text-rose-200",
  paused: "bg-amber-500/20 text-amber-200",
  disabled: "bg-slate-700/30 text-slate-300",
};

const formatTime = (value) => {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return "—";
  }
};

export default function BotStatusPanel({ refreshKey }) {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        setLoading(true);
        const res = await axiosClient.get("/api/v1/bots");
        const list = res?.data?.bots || [];
        if (active) setBots(Array.isArray(list) ? list : []);
      } catch {
        if (active) setBots([]);
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
          <div className="text-lg font-semibold text-white">Bot Status</div>
          <div className="text-sm text-slate-300">
            Live automation and scheduling overview.
          </div>
        </div>
      </div>

      {loading ? (
        <div className="mt-4 text-sm text-slate-300">Loading bots...</div>
      ) : bots.length === 0 ? (
        <div className="mt-4 text-sm text-slate-300">No bots available.</div>
      ) : (
        <div className="mt-4 space-y-3">
          {bots.map((bot) => {
            const status = bot.status || "idle";
            const badgeClass = STATUS_STYLES[status] || STATUS_STYLES.idle;
            return (
              <div
                key={bot.bot_name}
                className="flex flex-col gap-2 rounded-xl border border-white/10 bg-white/5 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="text-sm font-semibold text-white">
                    {bot.bot_name}
                  </div>
                  <span className={`rounded-full px-2 py-1 text-xs ${badgeClass}`}>
                    {status.toUpperCase()}
                  </span>
                </div>
                <div className="grid gap-2 text-xs text-slate-300 sm:grid-cols-2 lg:grid-cols-3">
                  <div>
                    <span className="text-slate-400">Automation:</span>{" "}
                    {bot.automation_level || "auto"}
                  </div>
                  <div>
                    <span className="text-slate-400">Schedule:</span>{" "}
                    {bot.schedule_cron || "manual"}
                  </div>
                  <div>
                    <span className="text-slate-400">Next run:</span>{" "}
                    {formatTime(bot.next_run)}
                  </div>
                  <div>
                    <span className="text-slate-400">Last status:</span>{" "}
                    {bot.last_run?.status || "—"}
                  </div>
                  <div>
                    <span className="text-slate-400">Last run:</span>{" "}
                    {formatTime(bot.last_run?.started_at)}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
