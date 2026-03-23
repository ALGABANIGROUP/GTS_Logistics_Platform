import React, { useEffect, useMemo, useRef, useState } from "react";
import axiosClient from "../../api/axiosClient";
import { WS_BASE_URL } from "../../config/env";
import { appendTokenToWsUrl, isSocketUnauthorized, notifySocketUnauthorized } from "../../utils/wsHelpers";
import BotStatusPanel from "../../components/bos/BotStatusPanel.jsx";
import CommandGateway from "../../components/bos/CommandGateway.jsx";
import ExecutionHistory from "../../components/bos/ExecutionHistory.jsx";

const StatCard = ({ label, value }) => (
  <div className="glass-panel rounded-2xl p-4 text-sm text-slate-200">
    <div className="text-xs uppercase tracking-wide text-slate-400">{label}</div>
    <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
  </div>
);

export default function AutomaticDashboard() {
  const [stats, setStats] = useState(null);
  const [live, setLive] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const wsRef = useRef(null);

  const refresh = () => setRefreshKey((value) => value + 1);

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        const res = await axiosClient.get("/api/v1/bots/stats");
        if (active) setStats(res?.data || null);
      } catch {
        if (active) setStats(null);
      }
    };

    load();
    return () => {
      active = false;
    };
  }, [refreshKey]);

  useEffect(() => {
    const url = appendTokenToWsUrl(`${WS_BASE_URL}/live`);
    if (!url) {
      setLive(false);
      return;
    }

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setLive(true);
      try {
        ws.send(JSON.stringify({ type: "subscribe", channel: "bots.*" }));
        ws.send(JSON.stringify({ type: "subscribe", channel: "commands.*" }));
      } catch {
        // ignore
      }
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (!msg || !msg.channel) return;
        if (msg.channel.startsWith("bots.") || msg.channel.startsWith("commands.")) {
          refresh();
        }
      } catch {
        // ignore
      }
    };

    ws.onclose = (event) => {
      setLive(false);
      if (isSocketUnauthorized(event)) {
        notifySocketUnauthorized(event);
      }
    };

    ws.onerror = () => {
      setLive(false);
    };

    return () => {
      try {
        ws.close(1000, "unmount");
      } catch {
        // ignore
      }
    };
  }, []);

  const statValues = useMemo(() => {
    return {
      totalRuns: stats?.total_runs ?? "—",
      totalCommands: stats?.human_commands ?? "—",
      running: stats?.by_status?.running ?? 0,
      failed: stats?.by_status?.failed ?? 0,
    };
  }, [stats]);

  return (
    <div className="glass-page p-4 md:p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="text-2xl font-semibold text-white">Bot Operating System</div>
          <div className="text-sm text-slate-300">
            Scheduler, human commands, and automation telemetry.
          </div>
        </div>
        <div className="text-xs text-slate-300">
          WS:{" "}
          <span className={live ? "text-emerald-300" : "text-rose-300"}>
            {live ? "connected" : "offline"}
          </span>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Runs" value={statValues.totalRuns} />
        <StatCard label="Human Commands" value={statValues.totalCommands} />
        <StatCard label="Running" value={statValues.running} />
        <StatCard label="Failed" value={statValues.failed} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <BotStatusPanel refreshKey={refreshKey} />
        <CommandGateway onExecuted={refresh} />
      </div>

      <ExecutionHistory refreshKey={refreshKey} />
    </div>
  );
}
