import React, { useEffect, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";
import RequireAuth from "../../components/RequireAuth.jsx";

export default function OperationsManager() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <OperationsManagerContent />
    </RequireAuth>
  );
}

function OperationsManagerContent() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [shipments, setShipments] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [performance, setPerformance] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError("");
    try {
      const [shipmentsRes, metricsRes, performanceRes] = await Promise.all([
        axiosClient.get("/api/v1/admin/shipments/analytics"),
        axiosClient.get("/api/v1/admin/metrics"),
        axiosClient.get("/api/v1/admin/performance"),
      ]);
      setShipments(shipmentsRes.data?.shipments || null);
      setMetrics(metricsRes.data?.metrics || null);
      setPerformance(performanceRes.data?.performance || null);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to load operations data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const cards = useMemo(() => {
    const today = shipments?.today || {};
    const ops = performance?.operations_stats || {};
    return [
      { label: "Shipments Today", value: today.total ?? 0 },
      { label: "In Transit", value: today.in_transit ?? 0 },
      { label: "Completed Ops", value: ops.completed_operations ?? 0 },
      { label: "Pending Ops", value: ops.pending_operations ?? 0 },
    ];
  }, [shipments, performance]);

  const bottleneck = performance?.system_efficiency?.bottleneck_identified || "No bottleneck reported.";
  const recommendations = performance?.system_efficiency?.recommended_optimizations || [];
  const botPerformance = performance?.bots_performance || {};
  const apiPerformance = metrics?.api_performance || {};
  const systemResources = metrics?.system_resources || {};

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Operations Manager</h1>
          <p className="text-sm text-slate-400">Live operations snapshot across shipments, bots, and platform throughput.</p>
        </div>
        <button
          onClick={loadData}
          className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500"
        >
          Refresh
        </button>
      </div>

      {error ? (
        <div className="rounded-lg border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-100">{error}</div>
      ) : null}

      {loading ? (
        <div className="text-sm text-slate-400">Loading operations data...</div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {cards.map((card) => (
              <div key={card.label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="text-xs uppercase tracking-wide text-slate-400">{card.label}</div>
                <div className="mt-2 text-2xl font-bold text-slate-100">{card.value}</div>
              </div>
            ))}
          </div>

          <div className="grid gap-4 xl:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 xl:col-span-2">
              <h2 className="text-sm font-semibold text-slate-100">Shipment Analytics</h2>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <div className="rounded-xl border border-white/10 bg-slate-950/30 p-3">
                  <div className="text-xs text-slate-400">Today</div>
                  <div className="mt-2 space-y-1 text-sm text-slate-200">
                    <div>Total: {shipments?.today?.total ?? 0}</div>
                    <div>Completed: {shipments?.today?.completed ?? 0}</div>
                    <div>Failed: {shipments?.today?.failed ?? 0}</div>
                  </div>
                </div>
                <div className="rounded-xl border border-white/10 bg-slate-950/30 p-3">
                  <div className="text-xs text-slate-400">This Month</div>
                  <div className="mt-2 space-y-1 text-sm text-slate-200">
                    <div>Total: {shipments?.this_month?.total ?? 0}</div>
                    <div>Completed: {shipments?.this_month?.completed ?? 0}</div>
                    <div>Avg Completion: {shipments?.this_month?.avg_completion_time ?? "-"}</div>
                  </div>
                </div>
              </div>
              <div className="mt-4 text-sm text-slate-400">{shipments?.message || "No shipment advisory available."}</div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <h2 className="text-sm font-semibold text-slate-100">System Efficiency</h2>
              <div className="mt-3 text-sm text-slate-300">
                <div>Score: {performance?.system_efficiency?.overall_efficiency_score ?? "-"}</div>
                <div className="mt-2">Bottleneck: {bottleneck}</div>
              </div>
              <ul className="mt-3 space-y-2 text-sm text-slate-400">
                {recommendations.length ? (
                  recommendations.map((item) => <li key={item}>• {item}</li>)
                ) : (
                  <li>• No recommendations returned.</li>
                )}
              </ul>
            </div>
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <h2 className="text-sm font-semibold text-slate-100">Bot Performance</h2>
              <div className="mt-3 space-y-3">
                {Object.entries(botPerformance).map(([name, info]) => (
                  <div key={name} className="rounded-xl border border-white/10 bg-slate-950/30 p-3 text-sm text-slate-200">
                    <div className="font-medium text-slate-100">{name}</div>
                    <div className="mt-1 text-slate-400">
                      Ops: {info.operations_completed} | Success: {info.success_rate_percent}% | Utilization: {info.utilization_percent}%
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <h2 className="text-sm font-semibold text-slate-100">Platform Throughput</h2>
              <div className="mt-3 grid gap-3 sm:grid-cols-2 text-sm text-slate-200">
                <div className="rounded-xl border border-white/10 bg-slate-950/30 p-3">
                  <div className="text-xs text-slate-400">API</div>
                  <div className="mt-2">Avg Response: {apiPerformance.avg_response_time_ms ?? "-"} ms</div>
                  <div>Requests/min: {apiPerformance.requests_per_minute ?? "-"}</div>
                </div>
                <div className="rounded-xl border border-white/10 bg-slate-950/30 p-3">
                  <div className="text-xs text-slate-400">Resources</div>
                  <div className="mt-2">CPU: {systemResources.cpu_usage_percent ?? "-"}%</div>
                  <div>Memory: {systemResources.memory_usage_percent ?? "-"}%</div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
