import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useRefreshSubscription } from "../contexts/UiActionsContext.jsx";
import gabaniLogo from "../assets/gabani_logo.png";

const CardShell = ({ title, icon, children }) => (
  <div className="glass-15 rounded-2xl p-4 shadow-xl shadow-black/30 border border-[var(--navy-border-10)]">
    <div className="flex items-center justify-between mb-3">
      <p className="text-xs uppercase tracking-wide text-slate-300">{title}</p>
      <div className="h-10 w-10 rounded-xl glass-15 bg-[var(--navy-glass-15)] flex items-center justify-center text-xs font-semibold text-slate-200 border border-[var(--navy-border-10)]">
        {icon}
      </div>
    </div>
    {children}
  </div>
);

const StatCard = ({ title, value, helper, accent, icon, loading, error, onRetry }) => (
  <CardShell title={title} icon={icon}>
    {loading ? (
      <p className="mt-2 text-3xl font-bold text-slate-400">...</p>
    ) : error ? (
      <p className="mt-2 text-sm font-semibold text-rose-300">Unavailable</p>
    ) : (
      <p className={`mt-2 text-3xl font-bold ${accent}`}>{value}</p>
    )}
    {loading ? (
      <p className="text-xs text-slate-400">Loading card data...</p>
    ) : error ? (
      <div className="flex items-center justify-between text-xs text-rose-200">
        <span>{error}</span>
        <button
          type="button"
          onClick={onRetry}
          className="px-2 py-1 rounded-md border border-rose-400/40 text-rose-100 hover:bg-rose-500/10"
        >
          Retry
        </button>
      </div>
    ) : (
      <p className="text-xs text-slate-200">{helper}</p>
    )}
  </CardShell>
);

const Dashboard = () => {
  const navigate = useNavigate();
  const [cards, setCards] = useState({
    shipments: { loading: true, error: null, value: "0", helper: "Start by adding your first shipment." },
    documents: { loading: true, error: null, value: "0", helper: "No documents currently." },
    revenue: { loading: true, error: null, value: "$0", helper: "Will appear when operations start." },
  });

  const loadCard = async (key, loader) => {
    setCards((prev) => ({ ...prev, [key]: { ...prev[key], loading: true, error: null } }));
    try {
      const data = await loader();
      setCards((prev) => ({
        ...prev,
        [key]: { ...prev[key], loading: false, error: null, ...data },
      }));
    } catch (err) {
      setCards((prev) => ({
        ...prev,
        [key]: { ...prev[key], loading: false, error: err?.message || "Failed to load." },
      }));
    }
  };

  const loaders = useMemo(
    () => ({
      shipments: async () => ({ value: "0", helper: "Start by adding your first shipment." }),
      documents: async () => ({ value: "0", helper: "No documents currently." }),
      revenue: async () => ({ value: "$0", helper: "Will appear when operations start." }),
    }),
    []
  );

  useEffect(() => {
    Object.entries(loaders).forEach(([key, loader]) => loadCard(key, loader));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useRefreshSubscription(() => {
    Object.entries(loaders).forEach(([key, loader]) => loadCard(key, loader));
  });

  const goToShipment = () => navigate("/shipments/new");
  const goToDocuments = () => navigate("/documents/upload");
  const goToEmailLogs = () => navigate("/emails");

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <img
          src={gabaniLogo}
          alt="Gabani Transport Solutions"
          className="h-20 w-20 rounded-3xl object-contain ring-1 ring-white/15 bg-white/5 p-1.5"
        />
        <div>
          <div className="text-xl font-semibold text-slate-50">
            Gabani Transport Solutions (GTS)
          </div>
          <div className="text-base text-slate-300">Logistics Command &amp; Control</div>
        </div>
      </div>

      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-3xl lg:text-4xl font-bold text-slate-50 flex items-center gap-3">
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-sky-500/15 text-sky-300 border border-sky-400/20 text-xs font-semibold">
              CC
            </span>
            Dashboard Overview
          </h1>
          <p className="mt-2 text-sm text-slate-200">
            GTS Command Center status and daily operations snapshot.
          </p>
        </div>
        <span className="inline-flex items-center rounded-full bg-amber-500/10 px-4 py-1 text-xs font-medium text-amber-200 border border-amber-400/30">
          Ready to Start
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <StatCard
          title="Active Shipments"
          value={cards.shipments.value}
          helper={cards.shipments.helper}
          accent="text-slate-50"
          icon="SH"
          loading={cards.shipments.loading}
          error={cards.shipments.error}
          onRetry={() => loadCard("shipments", loaders.shipments)}
        />

        <CardShell title="Recent Activity" icon="ACT">
          <div className="space-y-3">
            <div className="flex items-center justify-between rounded-xl glass-15 bg-[var(--navy-glass-15)] border border-[var(--navy-border-10)] px-3 py-2">
              <div>
                <p className="text-sm text-slate-50">
                  Welcome to Gabani Transport Solutions (GTS) System
                </p>
                <p className="text-xs text-slate-300">Now</p>
              </div>
              <span className="text-emerald-200 text-xs font-medium">Ready</span>
            </div>

            <div className="flex items-center justify-between rounded-xl glass-15 bg-[var(--navy-glass-15)] border border-[var(--navy-border-10)] px-3 py-2">
              <div>
                <p className="text-sm text-slate-50">
                  Start by adding your first shipment
                </p>
                <p className="text-xs text-slate-300">Ready</p>
              </div>
              <span className="text-amber-200 text-xs font-medium">Action</span>
            </div>
          </div>
        </CardShell>

        <CardShell title="Quick Actions" icon="QS">
          <div className="space-y-3">
            <button
              className="w-full flex items-center justify-between rounded-xl glass-15 bg-[var(--navy-glass-15)] border border-[var(--navy-border-10)] px-3 py-2 text-left hover:-translate-y-[1px] transition"
              onClick={goToShipment}
            >
              <div>
                <p className="text-sm text-slate-50">Add a New Shipment</p>
                <p className="text-xs text-slate-300">
                  Start managing your shipments.
                </p>
              </div>
              <span className="text-sky-200 text-lg">+</span>
            </button>

            <button
              className="w-full flex items-center justify-between rounded-xl glass-15 bg-[var(--navy-glass-15)] border border-[var(--navy-border-10)] px-3 py-2 text-left hover:-translate-y-[1px] transition"
              onClick={goToDocuments}
            >
              <div>
                <p className="text-sm text-slate-50">Upload Documents</p>
                <p className="text-xs text-slate-300">
                  Add freight and clearance files.
                </p>
              </div>
              <span className="text-violet-200 text-lg">+</span>
            </button>

            <button
              className="w-full flex items-center justify-between rounded-xl glass-15 bg-[var(--navy-glass-15)] border border-[var(--navy-border-10)] px-3 py-2 text-left hover:-translate-y-[1px] transition"
              onClick={goToEmailLogs}
            >
              <div>
                <p className="text-sm text-slate-50">Review Email Logs</p>
                <p className="text-xs text-slate-300">
                  Track system notifications and alerts.
                </p>
              </div>
              <span className="text-emerald-200 text-lg">+</span>
            </button>
          </div>
        </CardShell>
      </div>

      <div className="rounded-2xl glass-15 p-5 shadow-xl shadow-black/35 border border-[var(--navy-border-10)]">
        <h2 className="text-sm font-semibold text-slate-50 flex items-center gap-2 mb-3">
          <span className="h-6 w-6 rounded-full bg-slate-500/20 flex items-center justify-center text-slate-200 text-[10px] border border-slate-400/20">
            LOG
          </span>
          Logistics Dispatch Center
        </h2>
        <p className="text-sm text-slate-200">
          GTS Command &amp; Control for dispatch operations, compliance, and activity tracking.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <StatCard
          title="Expiring Documents"
          value={cards.documents.value}
          helper={cards.documents.helper}
          accent="text-slate-50"
          icon="DOC"
          loading={cards.documents.loading}
          error={cards.documents.error}
          onRetry={() => loadCard("documents", loaders.documents)}
        />
        <StatCard
          title="Monthly Revenue"
          value={cards.revenue.value}
          helper={cards.revenue.helper}
          accent="text-emerald-200"
          icon="REV"
          loading={cards.revenue.loading}
          error={cards.revenue.error}
          onRetry={() => loadCard("revenue", loaders.revenue)}
        />
      </div>
    </div>
  );
};

export default Dashboard;
