import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { useNavigate } from "react-router-dom";
import { useRefreshSubscription } from "../contexts/UiActionsContext.jsx";
import { useCurrencyStore } from "../stores/useCurrencyStore";
import CurrencySwitcher from "../components/CurrencySwitcher";
import SystemHealthWidget from "../components/SystemHealthWidget";
import axiosClient from "../api/axiosClient";
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

CardShell.propTypes = {
  title: PropTypes.string.isRequired,
  icon: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
};

StatCard.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  helper: PropTypes.string.isRequired,
  accent: PropTypes.string.isRequired,
  icon: PropTypes.string.isRequired,
  loading: PropTypes.bool.isRequired,
  error: PropTypes.string,
  onRetry: PropTypes.func.isRequired,
};

const ACTIVE_SHIPMENT_STATUSES = new Set(["Pending", "Booked", "Dispatched", "Assigned", "In Transit"]);

const normalizeShipments = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.shipments)) return payload.shipments;
  if (Array.isArray(payload?.data)) return payload.data;
  return [];
};

const toNumber = (value) => {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
};

const formatRelativeTime = (value) => {
  if (!value) return "Recently";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Recently";
  const diffMs = Date.now() - date.getTime();
  const diffMin = Math.max(0, Math.floor(diffMs / 60000));
  if (diffMin < 1) return "Just now";
  if (diffMin < 60) return `${diffMin} min ago`;
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
};

const deriveRecentActivity = (shipments) => {
  const recent = [...shipments]
    .sort((a, b) => {
      const aTime = new Date(a?.updated_at || a?.created_at || 0).getTime();
      const bTime = new Date(b?.updated_at || b?.created_at || 0).getTime();
      return bTime - aTime;
    })
    .slice(0, 3)
    .map((shipment) => ({
      id: shipment.id || shipment.reference_number || `${shipment.status}-${shipment.pickup_location}`,
      title: `Shipment #${shipment.id || "N/A"} ${shipment.status || "updated"}`,
      subtitle: [shipment.pickup_location, shipment.dropoff_location].filter(Boolean).join(" -> ") || "Shipment activity",
      time: formatRelativeTime(shipment.updated_at || shipment.created_at),
      badge: shipment.status || "Updated",
      badgeClass: ACTIVE_SHIPMENT_STATUSES.has(shipment.status) ? "text-sky-200" : "text-emerald-200",
    }));

  if (recent.length > 0) return recent;

  return [
    {
      id: "welcome",
      title: "Welcome to Gabani Transport Solutions (GTS) System",
      subtitle: "Dashboard connected and ready.",
      time: "Now",
      badge: "Ready",
      badgeClass: "text-emerald-200",
    },
    {
      id: "empty",
      title: "No recent shipment activity yet",
      subtitle: "Create or import shipments to populate this feed.",
      time: "Waiting",
      badge: "Action",
      badgeClass: "text-amber-200",
    },
  ];
};

const Dashboard = () => {
  const navigate = useNavigate();
  const { currency, currencySymbol, formatCurrency, convertToCurrentCurrency } = useCurrencyStore();

  // Initialize cards with empty state - will be populated after currency is loaded
  const [cards, setCards] = useState({
    shipments: { loading: true, error: null, value: "0", helper: "Start by adding your first shipment." },
    documents: { loading: true, error: null, value: "0", helper: "No documents currently." },
    revenue: { loading: true, error: null, value: "", helper: "" },
  });
  const [recentActivity, setRecentActivity] = useState(() => deriveRecentActivity([]));

  // Update revenue card whenever currency changes
  useEffect(() => {
    setCards((prev) => ({
      ...prev,
      revenue: {
        ...prev.revenue,
        value: formatCurrency(0),
        helper: `Will appear when operations start. (${currency})`,
      },
    }));
  }, [currency, currencySymbol, formatCurrency]);

  const loadDashboardData = async () => {
    console.log("[Dashboard] Fetching shipments and dashboard cards...");
    setCards((prev) => ({
      ...prev,
      shipments: { ...prev.shipments, loading: true, error: null },
      documents: { ...prev.documents, loading: true, error: null },
      revenue: { ...prev.revenue, loading: true, error: null },
    }));

    try {
      const [statsRes, shipmentsRes, documentsRes] = await Promise.allSettled([
        axiosClient.get("/api/v1/shipments/stats"),
        axiosClient.get("/api/v1/shipments/?limit=50"),
        axiosClient.get("/ai/documents/status"),
      ]);

      console.log("[Dashboard] Shipments stats response:", statsRes);
      console.log("[Dashboard] Shipments list response:", shipmentsRes);
      console.log("[Dashboard] Documents status response:", documentsRes);

      const statsData = statsRes.status === "fulfilled" ? statsRes.value?.data || {} : {};
      const shipmentsData = shipmentsRes.status === "fulfilled" ? shipmentsRes.value?.data || {} : {};
      const documentsData = documentsRes.status === "fulfilled" ? documentsRes.value?.data || {} : null;
      const shipments = normalizeShipments(shipmentsData);

      const activeCount =
        toNumber(statsData?.active) ||
        shipments.filter((shipment) => ACTIVE_SHIPMENT_STATUSES.has(shipment?.status)).length;

      const totalRevenue = shipments.reduce((sum, shipment) => sum + toNumber(shipment?.rate), 0);
      // Convert revenue from base currency (default AED if not specified) to current currency
      const baseCurrency = shipments.find(s => s?.currency)?.currency || 'AED'; // Use currency from first shipment or default to AED
      const convertedRevenue = convertToCurrentCurrency(totalRevenue, baseCurrency);
      const expiringDocuments = documentsData
        ? toNumber(documentsData.expiring_soon) + toNumber(documentsData.expired)
        : 0;

      setCards({
        shipments: {
          loading: false,
          error: statsRes.status === "rejected" && shipmentsRes.status === "rejected"
            ? "Could not load shipments."
            : null,
          value: String(activeCount),
          helper:
            activeCount > 0
              ? `${toNumber(statsData?.in_transit)} in transit, ${toNumber(statsData?.pending)} pending.`
              : "No active shipments right now.",
        },
        documents: {
          loading: false,
          error: documentsRes.status === "rejected" ? "Document status unavailable." : null,
          value: String(expiringDocuments),
          helper:
            documentsData
              ? `${toNumber(documentsData.expiring_soon)} expiring soon, ${toNumber(documentsData.expired)} expired.`
              : "No document alerts currently.",
        },
        revenue: {
          loading: false,
          error: shipmentsRes.status === "rejected" ? "Revenue unavailable." : null,
          value: formatCurrency(convertedRevenue),
          helper:
            convertedRevenue > 0
              ? `Calculated from ${shipments.length} shipments. (${currency})`
              : `Will appear when operations start. (${currency})`,
        },
      });

      setRecentActivity(deriveRecentActivity(shipments));
    } catch (error) {
      console.error("[Dashboard] Failed to load data:", error);
      setCards({
        shipments: { loading: false, error: "Could not load shipments.", value: "0", helper: "Retry after backend check." },
        documents: { loading: false, error: "Could not load documents.", value: "0", helper: "Retry after backend check." },
        revenue: { loading: false, error: "Could not load revenue.", value: formatCurrency(0), helper: `Will appear when operations start. (${currency})` },
      });
      setRecentActivity(deriveRecentActivity([]));
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [currency]);

  // Listen to currency changes from other components
  useEffect(() => {
    const handleCurrencyChange = () => {
      // Currency changed, reload all cards with new currency
      loadDashboardData();
    };

    window.addEventListener('currencyChanged', handleCurrencyChange);
    return () => window.removeEventListener('currencyChanged', handleCurrencyChange);
  }, [currency]);

  useRefreshSubscription(() => {
    loadDashboardData();
  });

  const goToShipment = () => navigate("/shipments/new");
  const goToDocuments = () => navigate("/documents/upload");
  const goToEmailLogs = () => navigate("/emails");

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4 justify-between">
        <div className="flex items-center gap-4">
          <img
            src={gabaniLogo}
            alt="Gabani Transport Solutions"
            className="h-24 w-24 rounded-3xl object-contain ring-1 ring-white/15 bg-white/5 p-1.5"
          />
          <div>
            <div className="text-xl font-semibold text-slate-50">
              Gabani Transport Solutions (GTS)
            </div>
            <div className="text-base text-slate-300">Logistics Command &amp; Control</div>
          </div>
        </div>
        <div className="min-w-max">
          <CurrencySwitcher />
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
            GTS Command Center status and daily operations snapshot. Currency: <span className="font-semibold text-sky-300">{currency} ({currencySymbol})</span>
          </p>
        </div>
        <span className="inline-flex items-center rounded-full bg-amber-500/10 px-4 py-1 text-xs font-medium text-amber-200 border border-amber-400/30">
          Ready to Start
        </span>
      </div>

      {/* System Health Widget */}
      <SystemHealthWidget />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <StatCard
          title="Active Shipments"
          value={cards.shipments.value}
          helper={cards.shipments.helper}
          accent="text-slate-50"
          icon="SH"
          loading={cards.shipments.loading}
          error={cards.shipments.error}
          onRetry={loadDashboardData}
        />

        <CardShell title="Recent Activity" icon="ACT">
          <div className="space-y-3">
            {recentActivity.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between rounded-xl glass-15 bg-[var(--navy-glass-15)] border border-[var(--navy-border-10)] px-3 py-2"
              >
                <div>
                  <p className="text-sm text-slate-50">{item.title}</p>
                  <p className="text-xs text-slate-300">{item.subtitle} · {item.time}</p>
                </div>
                <span className={`${item.badgeClass} text-xs font-medium`}>{item.badge}</span>
              </div>
            ))}
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
                  Start managing your shipments in {currency}.
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
          GTS Command &amp; Control for dispatch operations, compliance, and activity tracking. All monetary values are displayed in {currency} ({currencySymbol}).
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
          onRetry={loadDashboardData}
        />
        <StatCard
          title={`Monthly Revenue (${currency})`}
          value={cards.revenue.value}
          helper={cards.revenue.helper}
          accent="text-emerald-200"
          icon="REV"
          loading={cards.revenue.loading}
          error={cards.revenue.error}
          onRetry={loadDashboardData}
        />
      </div>
    </div>
  );
};

export default Dashboard;
