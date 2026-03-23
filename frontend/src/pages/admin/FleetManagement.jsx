import React, { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import RequireAuth from "../../components/RequireAuth.jsx";
import fleetSafetyApi from "../../services/fleetSafetyApi";

const TABS = [
  { key: "dashboard", label: "Dashboard" },
  { key: "drivers", label: "Drivers" },
  { key: "vehicles", label: "Vehicles" },
  { key: "assignments", label: "Assignments" },
  { key: "incidents", label: "Incidents" },
];

const TAB_ROUTE_SUFFIX = {
  dashboard: "",
  drivers: "/drivers",
  vehicles: "/vehicles",
  assignments: "/assignments",
  incidents: "/incidents",
};

const emptyDriver = {
  full_name: "",
  email: "",
  phone_number: "",
  password: "",
  company: "",
  country: "",
  license_number: "",
  license_expiry: "",
  hire_date: "",
  status: "available",
  rating: 5,
  total_trips: 0,
  safety_score: 100,
  violations_count: 0,
  notes: "",
};

const emptyVehicle = {
  plate_number: "",
  type: "medium_truck",
  capacity_kg: "",
  year: "",
  status: "available",
  last_maintenance: "",
  next_maintenance: "",
  current_km: 0,
  fuel_type: "",
  insurance_expiry: "",
  notes: "",
};

const emptyAssignment = {
  driver_id: "",
  vehicle_id: "",
  notes: "",
};

const emptyIncident = {
  incident_date: new Date().toISOString().slice(0, 16),
  incident_type: "accident",
  driver_id: "",
  vehicle_id: "",
  location: "",
  description: "",
  severity: "medium",
  actions_taken: "",
  status: "open",
  police_report: "",
  insurance_claim: "",
  images: "",
};

const chipTone = {
  available: "border-emerald-400/30 bg-emerald-500/10 text-emerald-200",
  busy: "border-amber-400/30 bg-amber-500/10 text-amber-200",
  rest: "border-sky-400/30 bg-sky-500/10 text-sky-200",
  leave: "border-fuchsia-400/30 bg-fuchsia-500/10 text-fuchsia-200",
  inactive: "border-slate-400/30 bg-slate-500/10 text-slate-300",
  occupied: "border-orange-400/30 bg-orange-500/10 text-orange-200",
  maintenance: "border-rose-400/30 bg-rose-500/10 text-rose-200",
  broken: "border-red-400/30 bg-red-500/10 text-red-200",
  low: "border-emerald-400/30 bg-emerald-500/10 text-emerald-200",
  medium: "border-amber-400/30 bg-amber-500/10 text-amber-200",
  high: "border-orange-400/30 bg-orange-500/10 text-orange-200",
  critical: "border-red-400/30 bg-red-500/10 text-red-200",
  open: "border-red-400/30 bg-red-500/10 text-red-200",
  investigating: "border-amber-400/30 bg-amber-500/10 text-amber-200",
  closed: "border-emerald-400/30 bg-emerald-500/10 text-emerald-200",
};

const fmtDate = (value, withTime = false) => {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-US", withTime ? { dateStyle: "medium", timeStyle: "short" } : { dateStyle: "medium" });
};

const labelFor = (map, key) => map?.[key] || key || "-";

function Modal({ title, open, onClose, children, width = "max-w-3xl" }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/75 p-4 backdrop-blur-sm">
      <div className={`w-full ${width} rounded-3xl border border-white/10 bg-slate-950/95 shadow-2xl`}>
        <div className="flex items-center justify-between border-b border-white/10 px-6 py-4">
          <div>
            <h3 className="text-lg font-semibold text-white">{title}</h3>
            <p className="text-sm text-slate-400">Fleet Management workspace</p>
          </div>
          <button onClick={onClose} className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-300 hover:bg-white/5">
            Close
          </button>
        </div>
        <div className="max-h-[80vh] overflow-y-auto p-6">{children}</div>
      </div>
    </div>
  );
}

function Field({ label, children, full = false }) {
  return (
    <label className={`${full ? "md:col-span-2" : ""} block space-y-2`}>
      <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">{label}</span>
      {children}
    </label>
  );
}

function Input(props) {
  return <input {...props} className={`w-full rounded-2xl border border-white/10 bg-slate-900/80 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-sky-400/60 ${props.className || ""}`} />;
}

function Select(props) {
  return <select {...props} className={`w-full rounded-2xl border border-white/10 bg-slate-900/80 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-sky-400/60 ${props.className || ""}`} />;
}

function Textarea(props) {
  return <textarea {...props} className={`w-full rounded-2xl border border-white/10 bg-slate-900/80 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-sky-400/60 ${props.className || ""}`} />;
}

function SectionShell({ title, description, actionLabel, onAction, children }) {
  return (
    <div className="rounded-[30px] border border-white/10 bg-white/[0.03] p-6">
      <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">{title}</h2>
          <p className="mt-1 text-sm text-slate-400">{description}</p>
        </div>
        {actionLabel ? <button onClick={onAction} className="rounded-2xl border border-sky-400/20 bg-sky-500/10 px-4 py-3 text-sm font-semibold text-sky-100 hover:bg-sky-500/20">{actionLabel}</button> : null}
      </div>
      <div className="space-y-4">{children}</div>
    </div>
  );
}

function Table({ columns, rows, emptyText }) {
  return (
    <div className="overflow-hidden rounded-[24px] border border-white/10">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left">
          <thead className="bg-slate-950/60">
            <tr>{columns.map((column) => <th key={column} className="px-4 py-3 text-xs font-medium uppercase tracking-[0.2em] text-slate-400">{column}</th>)}</tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr><td colSpan={columns.length} className="px-4 py-8 text-center text-sm text-slate-400">{emptyText}</td></tr>
            ) : rows.map((row) => (
              <tr key={row.key} className="border-t border-white/5 bg-white/[0.02] align-top hover:bg-white/[0.04]">
                {row.cells.map((cell, index) => <td key={index} className="px-4 py-4 text-sm text-slate-300">{cell}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ActionButton({ tone = "default", className = "", ...props }) {
  const toneClass = tone === "danger" ? "border-rose-400/20 bg-rose-500/10 text-rose-100 hover:bg-rose-500/20" : "border-white/10 bg-white/5 text-slate-200 hover:bg-white/10";
  return <button {...props} className={`rounded-xl border px-3 py-2 text-sm font-medium transition ${toneClass} ${className}`} />;
}

export default function FleetManagement({
  initialTab = "dashboard",
  basePath = "/ai-bots/freight_broker",
  visibleTabs = TABS.map((tab) => tab.key),
  badge = "Fleet Operations Center",
  title = "Fleet Management & Safety Incident Log",
  description = "One control surface for driver readiness, vehicle utilization, active assignments, maintenance exposure, and safety incident response.",
  showFleetActions = true,
}) {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <FleetManagementContent
        initialTab={initialTab}
        basePath={basePath}
        visibleTabs={visibleTabs}
        badge={badge}
        title={title}
        description={description}
        showFleetActions={showFleetActions}
      />
    </RequireAuth>
  );
}

function FleetManagementContent({ initialTab, basePath, visibleTabs, badge, title, description, showFleetActions }) {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(initialTab || "dashboard");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [config, setConfig] = useState({});
  const [dashboard, setDashboard] = useState({ summary: {}, recent_incidents: [], maintenance_alerts: [] });
  const [drivers, setDrivers] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [driverSearch, setDriverSearch] = useState("");
  const [vehicleSearch, setVehicleSearch] = useState("");
  const [incidentSearch, setIncidentSearch] = useState("");
  const [driverModal, setDriverModal] = useState({ open: false, mode: "create", item: null });
  const [vehicleModal, setVehicleModal] = useState({ open: false, mode: "create", item: null });
  const [assignmentModal, setAssignmentModal] = useState(false);
  const [incidentModal, setIncidentModal] = useState({ open: false, mode: "create", item: null });
  const [incidentDetails, setIncidentDetails] = useState(null);
  const [driverForm, setDriverForm] = useState(emptyDriver);
  const [vehicleForm, setVehicleForm] = useState(emptyVehicle);
  const [assignmentForm, setAssignmentForm] = useState(emptyAssignment);
  const [incidentForm, setIncidentForm] = useState(emptyIncident);
  const [saving, setSaving] = useState(false);

  const loadAll = async () => {
    setLoading(true);
    setError("");
    try {
      const [cfg, dash, drv, veh, asg, inc] = await Promise.all([
        fleetSafetyApi.getConfig(),
        fleetSafetyApi.getDashboard(),
        fleetSafetyApi.listDrivers(),
        fleetSafetyApi.listVehicles(),
        fleetSafetyApi.listAssignments(),
        fleetSafetyApi.listIncidents(),
      ]);
      setConfig(cfg.data || {});
      setDashboard(dash.data || { summary: {} });
      setDrivers(drv.data?.drivers || []);
      setVehicles(veh.data?.vehicles || []);
      setAssignments(asg.data?.assignments || []);
      setIncidents(inc.data?.incidents || []);
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.normalized?.detail || err?.message || "Failed to load fleet workspace.";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  useEffect(() => {
    setActiveTab(initialTab || "dashboard");
  }, [initialTab]);

  const renderedTabs = TABS.filter((tab) => visibleTabs.includes(tab.key));

  const openTab = (tabKey) => {
    const suffix = TAB_ROUTE_SUFFIX[tabKey] ?? "";
    navigate(`${basePath}${suffix}`);
  };

  const filteredDrivers = useMemo(() => {
    const term = driverSearch.trim().toLowerCase();
    if (!term) return drivers;
    return drivers.filter((item) => [item.full_name, item.email, item.driver_code, item.phone_number].some((value) => String(value || "").toLowerCase().includes(term)));
  }, [drivers, driverSearch]);

  const filteredVehicles = useMemo(() => {
    const term = vehicleSearch.trim().toLowerCase();
    if (!term) return vehicles;
    return vehicles.filter((item) => [item.plate_number, item.vehicle_code, item.driver_name, item.type].some((value) => String(value || "").toLowerCase().includes(term)));
  }, [vehicles, vehicleSearch]);

  const filteredIncidents = useMemo(() => {
    const term = incidentSearch.trim().toLowerCase();
    if (!term) return incidents;
    return incidents.filter((item) => [item.incident_number, item.driver_name, item.plate_number, item.incident_type, item.location].some((value) => String(value || "").toLowerCase().includes(term)));
  }, [incidents, incidentSearch]);

  const availableDrivers = useMemo(() => drivers.filter((driver) => driver.status === "available" && driver.is_active), [drivers]);
  const assignableVehicles = useMemo(() => vehicles.filter((vehicle) => vehicle.status === "available"), [vehicles]);

  const openDriverModal = (item = null) => {
    setDriverModal({ open: true, mode: item ? "edit" : "create", item });
    setDriverForm(
      item
        ? {
            ...emptyDriver,
            ...item,
            license_expiry: item.license_expiry ? String(item.license_expiry).slice(0, 10) : "",
            hire_date: item.hire_date ? String(item.hire_date).slice(0, 10) : "",
            password: "",
          }
        : emptyDriver
    );
  };

  const openVehicleModal = (item = null) => {
    setVehicleModal({ open: true, mode: item ? "edit" : "create", item });
    setVehicleForm(
      item
        ? {
            ...emptyVehicle,
            ...item,
            last_maintenance: item.last_maintenance ? String(item.last_maintenance).slice(0, 10) : "",
            next_maintenance: item.next_maintenance ? String(item.next_maintenance).slice(0, 10) : "",
            insurance_expiry: item.insurance_expiry ? String(item.insurance_expiry).slice(0, 10) : "",
          }
        : emptyVehicle
    );
  };

  const openIncidentModal = (item = null) => {
    setIncidentModal({ open: true, mode: item ? "edit" : "create", item });
    setIncidentForm(
      item
        ? {
            ...emptyIncident,
            ...item,
            incident_date: item.incident_date ? new Date(item.incident_date).toISOString().slice(0, 16) : emptyIncident.incident_date,
            images: Array.isArray(item.images) ? item.images.join("\n") : "",
          }
        : emptyIncident
    );
  };

  const onDriverSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...driverForm,
        rating: Number(driverForm.rating || 5),
        total_trips: Number(driverForm.total_trips || 0),
        safety_score: Number(driverForm.safety_score || 100),
        violations_count: Number(driverForm.violations_count || 0),
      };
      if (driverModal.mode === "create") await fleetSafetyApi.createDriver(payload);
      else await fleetSafetyApi.updateDriver(driverModal.item.id, payload);
      setDriverModal({ open: false, mode: "create", item: null });
      toast.success(driverModal.mode === "create" ? "Driver created." : "Driver updated.");
      await loadAll();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to save driver.");
    } finally {
      setSaving(false);
    }
  };

  const onVehicleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...vehicleForm,
        capacity_kg: vehicleForm.capacity_kg === "" ? null : Number(vehicleForm.capacity_kg),
        year: vehicleForm.year === "" ? null : Number(vehicleForm.year),
        current_km: Number(vehicleForm.current_km || 0),
      };
      if (vehicleModal.mode === "create") await fleetSafetyApi.createVehicle(payload);
      else await fleetSafetyApi.updateVehicle(vehicleModal.item.id, payload);
      setVehicleModal({ open: false, mode: "create", item: null });
      toast.success(vehicleModal.mode === "create" ? "Vehicle created." : "Vehicle updated.");
      await loadAll();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to save vehicle.");
    } finally {
      setSaving(false);
    }
  };

  const onAssignmentSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await fleetSafetyApi.createAssignment({
        driver_id: Number(assignmentForm.driver_id),
        vehicle_id: Number(assignmentForm.vehicle_id),
        notes: assignmentForm.notes,
      });
      setAssignmentModal(false);
      setAssignmentForm(emptyAssignment);
      toast.success("Assignment saved.");
      await loadAll();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to assign driver.");
    } finally {
      setSaving(false);
    }
  };

  const onIncidentSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...incidentForm,
        driver_id: incidentForm.driver_id ? Number(incidentForm.driver_id) : null,
        vehicle_id: incidentForm.vehicle_id ? Number(incidentForm.vehicle_id) : null,
        images: incidentForm.images ? incidentForm.images.split("\n").map((item) => item.trim()).filter(Boolean) : [],
      };
      if (incidentModal.mode === "create") await fleetSafetyApi.createIncident(payload);
      else await fleetSafetyApi.updateIncident(incidentModal.item.id, payload);
      setIncidentModal({ open: false, mode: "create", item: null });
      toast.success(incidentModal.mode === "create" ? "Incident logged." : "Incident updated.");
      await loadAll();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to save incident.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (kind, id) => {
    if (!window.confirm(`Delete this ${kind}?`)) return;
    try {
      if (kind === "driver") await fleetSafetyApi.deleteDriver(id);
      if (kind === "vehicle") await fleetSafetyApi.deleteVehicle(id);
      if (kind === "incident") await fleetSafetyApi.deleteIncident(id);
      toast.success(`${kind[0].toUpperCase()}${kind.slice(1)} removed.`);
      await loadAll();
    } catch (err) {
      toast.error(err?.response?.data?.detail || `Failed to delete ${kind}.`);
    }
  };

  const handleUnassign = async (driverId) => {
    if (!window.confirm("Unassign this driver from the current vehicle?")) return;
    try {
      await fleetSafetyApi.unassignDriver(driverId);
      toast.success("Assignment released.");
      await loadAll();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to unassign driver.");
    }
  };

  const loadIncidentDetails = async (incidentId) => {
    try {
      const response = await fleetSafetyApi.getIncident(incidentId);
      setIncidentDetails(response.data?.incident || null);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to load incident details.");
    }
  };

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="overflow-hidden rounded-[32px] border border-sky-400/10 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.18),_rgba(2,6,23,0.96)_42%)] p-6 shadow-[0_24px_80px_rgba(2,6,23,0.45)]">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-3xl">
            <div className="mb-3 inline-flex rounded-full border border-sky-400/20 bg-sky-400/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-sky-200">{badge}</div>
            <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">{title}</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">{description}</p>
          </div>
          <div className="flex flex-wrap gap-3">
            {showFleetActions ? (
              <>
                <Link to="/ai-bots/freight_broker/live-map" className="rounded-2xl border border-emerald-400/20 bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-100 hover:bg-emerald-500/20">
                  Open Live Map
                </Link>
                {visibleTabs.includes("drivers") ? <button onClick={() => openDriverModal()} className="rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-slate-950 hover:bg-slate-100">New Driver</button> : null}
                {visibleTabs.includes("vehicles") ? <button onClick={() => openVehicleModal()} className="rounded-2xl border border-white/15 bg-white/5 px-4 py-3 text-sm font-semibold text-white hover:bg-white/10">New Vehicle</button> : null}
              </>
            ) : null}
            {visibleTabs.includes("incidents") ? <button onClick={() => openIncidentModal()} className="rounded-2xl border border-rose-400/20 bg-rose-500/10 px-4 py-3 text-sm font-semibold text-rose-100 hover:bg-rose-500/20">Log Incident</button> : null}
            <button onClick={loadAll} className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm font-semibold text-slate-200 hover:bg-slate-900">Refresh</button>
          </div>
        </div>
      </div>

      {error ? <div className="rounded-2xl border border-rose-400/30 bg-rose-500/10 p-4 text-sm text-rose-100">{error}</div> : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[
          ["Drivers Ready", `${dashboard.summary?.available_drivers || 0}/${dashboard.summary?.total_drivers || 0}`, "Live driver readiness"],
          ["Vehicles Ready", `${dashboard.summary?.available_vehicles || 0}/${dashboard.summary?.total_vehicles || 0}`, `${dashboard.summary?.maintenance_due || 0} in maintenance`],
          ["Incidents This Month", dashboard.summary?.incidents_this_month || 0, `${dashboard.summary?.incidents_this_week || 0} this week`],
          ["Open Safety Cases", dashboard.summary?.open_incidents || 0, `${dashboard.summary?.incidents_today || 0} today`],
        ].map(([title, value, meta]) => (
          <div key={title} className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5 shadow-[0_18px_45px_rgba(15,23,42,0.22)]">
            <div className="text-xs uppercase tracking-[0.24em] text-slate-400">{title}</div>
            <div className="mt-3 text-3xl font-semibold text-white">{value}</div>
            <div className="mt-2 text-sm text-slate-400">{meta}</div>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-2 rounded-[28px] border border-white/10 bg-white/[0.03] p-2">
        {renderedTabs.map((tab) => (
          <button key={tab.key} onClick={() => openTab(tab.key)} className={`rounded-2xl px-4 py-3 text-sm font-medium transition ${activeTab === tab.key ? "bg-sky-500 text-white shadow-[0_12px_30px_rgba(14,165,233,0.25)]" : "text-slate-300 hover:bg-white/5"}`}>
            {tab.label}
          </button>
        ))}
      </div>

      {loading ? <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-8 text-sm text-slate-400">Loading fleet workspace...</div> : null}

      {!loading && activeTab === "dashboard" ? (
        <div className="grid gap-6 xl:grid-cols-[1.35fr_0.95fr]">
          <div className="rounded-[30px] border border-white/10 bg-white/[0.03] p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-white">Recent safety incidents</h2>
                <p className="text-sm text-slate-400">Latest events requiring review or already resolved.</p>
              </div>
              <button onClick={() => openTab("incidents")} className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-200 hover:bg-white/5">Open incidents</button>
            </div>
            <div className="mt-5 space-y-3">
              {(dashboard.recent_incidents || []).length === 0 ? <div className="rounded-2xl border border-dashed border-white/10 p-5 text-sm text-slate-400">No incidents logged yet.</div> : dashboard.recent_incidents.map((item) => (
                <button key={item.id} onClick={() => loadIncidentDetails(item.id)} className="flex w-full items-center justify-between rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-4 text-left hover:border-sky-400/30 hover:bg-slate-950/60">
                  <div>
                    <div className="text-sm font-semibold text-white">{item.incident_number}</div>
                    <div className="mt-1 text-sm text-slate-400">{labelFor(config.incident_types, item.incident_type)} · {item.driver_name || "No driver linked"} · {item.plate_number || "No vehicle linked"}</div>
                  </div>
                  <div className="text-right">
                    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${chipTone[item.severity] || chipTone.medium}`}>{labelFor(config.incident_severity, item.severity)}</span>
                    <div className="mt-2 text-xs text-slate-500">{fmtDate(item.incident_date, true)}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
          <div className="rounded-[30px] border border-white/10 bg-white/[0.03] p-6">
            <h2 className="text-xl font-semibold text-white">Maintenance exposure</h2>
            <p className="text-sm text-slate-400">Vehicles due within the next 30 days.</p>
            <div className="mt-5 space-y-3">
              {(dashboard.maintenance_alerts || []).length === 0 ? <div className="rounded-2xl border border-dashed border-white/10 p-5 text-sm text-slate-400">No upcoming maintenance windows.</div> : dashboard.maintenance_alerts.map((item) => (
                <div key={item.id} className="rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="text-sm font-semibold text-white">{item.plate_number}</div>
                      <div className="mt-1 text-sm text-slate-400">{item.vehicle_code}</div>
                    </div>
                    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${chipTone[item.status] || chipTone.maintenance}`}>{labelFor(config.vehicle_status, item.status)}</span>
                  </div>
                  <div className="mt-3 text-xs uppercase tracking-[0.2em] text-slate-500">Next maintenance</div>
                  <div className="mt-1 text-sm text-slate-200">{fmtDate(item.next_maintenance)}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}

      {!loading && activeTab === "drivers" ? (
        <SectionShell title="Drivers roster" description="Manage driver profiles, licensing, availability, and safety posture." actionLabel="Add driver" onAction={() => openDriverModal()}>
          <Input value={driverSearch} onChange={(e) => setDriverSearch(e.target.value)} placeholder="Search drivers by name, email, code, or phone" />
          <Table
            columns={["Driver", "Status", "License", "Trips", "Safety", "Actions"]}
            rows={filteredDrivers.map((driver) => ({
              key: driver.id,
              cells: [
                <div key="name"><div className="font-medium text-white">{driver.full_name || driver.email}</div><div className="text-xs text-slate-400">{driver.driver_code} · {driver.email}</div></div>,
                <span key="status" className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${chipTone[driver.status] || chipTone.available}`}>{labelFor(config.driver_status, driver.status)}</span>,
                <div key="license" className="text-sm text-slate-300">{driver.license_number || "-"}<div className="text-xs text-slate-500">{fmtDate(driver.license_expiry)}</div></div>,
                <div key="trips" className="text-sm text-slate-200">{driver.total_trips || 0}</div>,
                <div key="safety" className="text-sm text-slate-200">{Number(driver.safety_score || 0).toFixed(1)}<div className="text-xs text-slate-500">{Number(driver.rating || 0).toFixed(1)} / 5 rating</div></div>,
                <div key="actions" className="flex gap-2"><ActionButton onClick={() => openDriverModal(driver)}>Edit</ActionButton><ActionButton tone="danger" onClick={() => handleDelete("driver", driver.id)}>Archive</ActionButton></div>,
              ],
            }))}
            emptyText="No drivers found."
          />
        </SectionShell>
      ) : null}

      {!loading && activeTab === "vehicles" ? (
        <SectionShell title="Vehicles registry" description="Track vehicle availability, payload capacity, maintenance dates, and insurance coverage." actionLabel="Add vehicle" onAction={() => openVehicleModal()}>
          <Input value={vehicleSearch} onChange={(e) => setVehicleSearch(e.target.value)} placeholder="Search vehicles by plate, code, type, or driver" />
          <Table
            columns={["Vehicle", "Type", "Status", "Driver", "Maintenance", "Actions"]}
            rows={filteredVehicles.map((vehicle) => ({
              key: vehicle.id,
              cells: [
                <div key="vehicle"><div className="font-medium text-white">{vehicle.plate_number}</div><div className="text-xs text-slate-400">{vehicle.vehicle_code}</div></div>,
                <div key="type" className="text-sm text-slate-300">{labelFor(config.vehicle_types, vehicle.type)}<div className="text-xs text-slate-500">{vehicle.capacity_kg || 0} kg</div></div>,
                <span key="status" className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${chipTone[vehicle.status] || chipTone.available}`}>{labelFor(config.vehicle_status, vehicle.status)}</span>,
                <div key="driver" className="text-sm text-slate-300">{vehicle.driver_name || "-"}</div>,
                <div key="maint" className="text-sm text-slate-300">{fmtDate(vehicle.next_maintenance)}<div className="text-xs text-slate-500">{Number(vehicle.current_km || 0).toLocaleString()} km</div></div>,
                <div key="actions" className="flex gap-2"><ActionButton onClick={() => openVehicleModal(vehicle)}>Edit</ActionButton><ActionButton tone="danger" onClick={() => handleDelete("vehicle", vehicle.id)}>Archive</ActionButton></div>,
              ],
            }))}
            emptyText="No vehicles found."
          />
        </SectionShell>
      ) : null}

      {!loading && activeTab === "assignments" ? (
        <SectionShell title="Driver to vehicle assignments" description="Control the live mapping between available drivers and available vehicles." actionLabel="New assignment" onAction={() => setAssignmentModal(true)}>
          <Table
            columns={["Driver", "Vehicle", "Assigned", "Notes", "Actions"]}
            rows={assignments.map((assignment) => ({
              key: assignment.id,
              cells: [
                <div key="driver"><div className="font-medium text-white">{assignment.driver_name}</div><div className="text-xs text-slate-400">{assignment.driver_code}</div></div>,
                <div key="vehicle"><div className="font-medium text-white">{assignment.plate_number}</div><div className="text-xs text-slate-400">{assignment.vehicle_code} · {labelFor(config.vehicle_types, assignment.vehicle_type)}</div></div>,
                <div key="assigned" className="text-sm text-slate-300">{fmtDate(assignment.assigned_date)}</div>,
                <div key="notes" className="max-w-xs truncate text-sm text-slate-400">{assignment.notes || "-"}</div>,
                <ActionButton key="release" tone="danger" onClick={() => handleUnassign(assignment.driver_id)}>Unassign</ActionButton>,
              ],
            }))}
            emptyText="No active assignments."
          />
        </SectionShell>
      ) : null}

      {!loading && activeTab === "incidents" ? (
        <SectionShell title="Safety incident log" description="Record, track, and resolve operational incidents across the fleet." actionLabel="Add incident" onAction={() => openIncidentModal()}>
          <Input value={incidentSearch} onChange={(e) => setIncidentSearch(e.target.value)} placeholder="Search incidents by number, type, driver, plate, or location" />
          <Table
            columns={["Incident", "Type", "Driver", "Severity", "Status", "Actions"]}
            rows={filteredIncidents.map((incident) => ({
              key: incident.id,
              cells: [
                <div key="incident"><div className="font-medium text-white">{incident.incident_number}</div><div className="text-xs text-slate-400">{fmtDate(incident.incident_date, true)}</div></div>,
                <div key="type" className="text-sm text-slate-300">{labelFor(config.incident_types, incident.incident_type)}<div className="text-xs text-slate-500">{incident.plate_number || "No vehicle"}</div></div>,
                <div key="driver" className="text-sm text-slate-300">{incident.driver_name || "-"}</div>,
                <span key="severity" className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${chipTone[incident.severity] || chipTone.medium}`}>{labelFor(config.incident_severity, incident.severity)}</span>,
                <span key="status" className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${chipTone[incident.status] || chipTone.open}`}>{labelFor(config.incident_status, incident.status)}</span>,
                <div key="actions" className="flex gap-2"><ActionButton onClick={() => loadIncidentDetails(incident.id)}>View</ActionButton><ActionButton onClick={() => openIncidentModal(incident)}>Edit</ActionButton><ActionButton tone="danger" onClick={() => handleDelete("incident", incident.id)}>Delete</ActionButton></div>,
              ],
            }))}
            emptyText="No incidents found."
          />
        </SectionShell>
      ) : null}

      <Modal title={driverModal.mode === "create" ? "Create driver" : "Edit driver"} open={driverModal.open} onClose={() => setDriverModal({ open: false, mode: "create", item: null })}>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={onDriverSave}>
          <Field label="Full name"><Input value={driverForm.full_name} onChange={(e) => setDriverForm((prev) => ({ ...prev, full_name: e.target.value }))} required /></Field>
          <Field label="Email"><Input type="email" value={driverForm.email} onChange={(e) => setDriverForm((prev) => ({ ...prev, email: e.target.value }))} required /></Field>
          <Field label="Phone"><Input value={driverForm.phone_number} onChange={(e) => setDriverForm((prev) => ({ ...prev, phone_number: e.target.value }))} /></Field>
          <Field label={driverModal.mode === "create" ? "Password" : "Reset password"}><Input type="password" value={driverForm.password} onChange={(e) => setDriverForm((prev) => ({ ...prev, password: e.target.value }))} /></Field>
          <Field label="Driver status"><Select value={driverForm.status} onChange={(e) => setDriverForm((prev) => ({ ...prev, status: e.target.value }))}>{Object.entries(config.driver_status || {}).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</Select></Field>
          <Field label="License number"><Input value={driverForm.license_number} onChange={(e) => setDriverForm((prev) => ({ ...prev, license_number: e.target.value }))} /></Field>
          <Field label="License expiry"><Input type="date" value={driverForm.license_expiry} onChange={(e) => setDriverForm((prev) => ({ ...prev, license_expiry: e.target.value }))} /></Field>
          <Field label="Hire date"><Input type="date" value={driverForm.hire_date} onChange={(e) => setDriverForm((prev) => ({ ...prev, hire_date: e.target.value }))} /></Field>
          <Field label="Rating"><Input type="number" min="1" max="5" step="0.1" value={driverForm.rating} onChange={(e) => setDriverForm((prev) => ({ ...prev, rating: e.target.value }))} /></Field>
          <Field label="Safety score"><Input type="number" min="0" max="100" step="0.1" value={driverForm.safety_score} onChange={(e) => setDriverForm((prev) => ({ ...prev, safety_score: e.target.value }))} /></Field>
          <Field label="Trips"><Input type="number" min="0" value={driverForm.total_trips} onChange={(e) => setDriverForm((prev) => ({ ...prev, total_trips: e.target.value }))} /></Field>
          <Field label="Violations"><Input type="number" min="0" value={driverForm.violations_count} onChange={(e) => setDriverForm((prev) => ({ ...prev, violations_count: e.target.value }))} /></Field>
          <Field label="Company"><Input value={driverForm.company} onChange={(e) => setDriverForm((prev) => ({ ...prev, company: e.target.value }))} /></Field>
          <Field label="Country"><Input value={driverForm.country} onChange={(e) => setDriverForm((prev) => ({ ...prev, country: e.target.value }))} /></Field>
          <Field label="Notes" full><Textarea rows={4} value={driverForm.notes} onChange={(e) => setDriverForm((prev) => ({ ...prev, notes: e.target.value }))} /></Field>
          <div className="md:col-span-2 flex justify-end gap-3 pt-2"><ActionButton type="button" onClick={() => setDriverModal({ open: false, mode: "create", item: null })}>Cancel</ActionButton><button type="submit" disabled={saving} className="rounded-2xl bg-sky-500 px-5 py-3 text-sm font-semibold text-white hover:bg-sky-400 disabled:opacity-60">{saving ? "Saving..." : "Save driver"}</button></div>
        </form>
      </Modal>

      <Modal title={vehicleModal.mode === "create" ? "Create vehicle" : "Edit vehicle"} open={vehicleModal.open} onClose={() => setVehicleModal({ open: false, mode: "create", item: null })}>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={onVehicleSave}>
          <Field label="Plate number"><Input value={vehicleForm.plate_number} onChange={(e) => setVehicleForm((prev) => ({ ...prev, plate_number: e.target.value }))} required /></Field>
          <Field label="Vehicle type"><Select value={vehicleForm.type} onChange={(e) => setVehicleForm((prev) => ({ ...prev, type: e.target.value }))}>{Object.entries(config.vehicle_types || {}).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</Select></Field>
          <Field label="Capacity kg"><Input type="number" min="0" value={vehicleForm.capacity_kg} onChange={(e) => setVehicleForm((prev) => ({ ...prev, capacity_kg: e.target.value }))} /></Field>
          <Field label="Model year"><Input type="number" min="2000" max="2100" value={vehicleForm.year} onChange={(e) => setVehicleForm((prev) => ({ ...prev, year: e.target.value }))} /></Field>
          <Field label="Status"><Select value={vehicleForm.status} onChange={(e) => setVehicleForm((prev) => ({ ...prev, status: e.target.value }))}>{Object.entries(config.vehicle_status || {}).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</Select></Field>
          <Field label="Current odometer km"><Input type="number" min="0" value={vehicleForm.current_km} onChange={(e) => setVehicleForm((prev) => ({ ...prev, current_km: e.target.value }))} /></Field>
          <Field label="Last maintenance"><Input type="date" value={vehicleForm.last_maintenance} onChange={(e) => setVehicleForm((prev) => ({ ...prev, last_maintenance: e.target.value }))} /></Field>
          <Field label="Next maintenance"><Input type="date" value={vehicleForm.next_maintenance} onChange={(e) => setVehicleForm((prev) => ({ ...prev, next_maintenance: e.target.value }))} /></Field>
          <Field label="Fuel type"><Input value={vehicleForm.fuel_type} onChange={(e) => setVehicleForm((prev) => ({ ...prev, fuel_type: e.target.value }))} /></Field>
          <Field label="Insurance expiry"><Input type="date" value={vehicleForm.insurance_expiry} onChange={(e) => setVehicleForm((prev) => ({ ...prev, insurance_expiry: e.target.value }))} /></Field>
          <Field label="Notes" full><Textarea rows={4} value={vehicleForm.notes} onChange={(e) => setVehicleForm((prev) => ({ ...prev, notes: e.target.value }))} /></Field>
          <div className="md:col-span-2 flex justify-end gap-3 pt-2"><ActionButton type="button" onClick={() => setVehicleModal({ open: false, mode: "create", item: null })}>Cancel</ActionButton><button type="submit" disabled={saving} className="rounded-2xl bg-sky-500 px-5 py-3 text-sm font-semibold text-white hover:bg-sky-400 disabled:opacity-60">{saving ? "Saving..." : "Save vehicle"}</button></div>
        </form>
      </Modal>

      <Modal title="Create assignment" open={assignmentModal} onClose={() => setAssignmentModal(false)} width="max-w-2xl">
        <form className="grid gap-4 md:grid-cols-2" onSubmit={onAssignmentSave}>
          <Field label="Available driver"><Select value={assignmentForm.driver_id} onChange={(e) => setAssignmentForm((prev) => ({ ...prev, driver_id: e.target.value }))} required><option value="">Select driver</option>{availableDrivers.map((driver) => <option key={driver.id} value={driver.id}>{driver.full_name || driver.email} · {driver.driver_code}</option>)}</Select></Field>
          <Field label="Available vehicle"><Select value={assignmentForm.vehicle_id} onChange={(e) => setAssignmentForm((prev) => ({ ...prev, vehicle_id: e.target.value }))} required><option value="">Select vehicle</option>{assignableVehicles.map((vehicle) => <option key={vehicle.id} value={vehicle.id}>{vehicle.plate_number} · {vehicle.vehicle_code}</option>)}</Select></Field>
          <Field label="Assignment notes" full><Textarea rows={4} value={assignmentForm.notes} onChange={(e) => setAssignmentForm((prev) => ({ ...prev, notes: e.target.value }))} /></Field>
          <div className="md:col-span-2 flex justify-end gap-3 pt-2"><ActionButton type="button" onClick={() => setAssignmentModal(false)}>Cancel</ActionButton><button type="submit" disabled={saving} className="rounded-2xl bg-sky-500 px-5 py-3 text-sm font-semibold text-white hover:bg-sky-400 disabled:opacity-60">{saving ? "Saving..." : "Create assignment"}</button></div>
        </form>
      </Modal>

      <Modal title={incidentModal.mode === "create" ? "Log safety incident" : "Edit safety incident"} open={incidentModal.open} onClose={() => setIncidentModal({ open: false, mode: "create", item: null })}>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={onIncidentSave}>
          <Field label="Incident date"><Input type="datetime-local" value={incidentForm.incident_date} onChange={(e) => setIncidentForm((prev) => ({ ...prev, incident_date: e.target.value }))} required /></Field>
          <Field label="Incident type"><Select value={incidentForm.incident_type} onChange={(e) => setIncidentForm((prev) => ({ ...prev, incident_type: e.target.value }))}>{Object.entries(config.incident_types || {}).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</Select></Field>
          <Field label="Driver"><Select value={incidentForm.driver_id} onChange={(e) => setIncidentForm((prev) => ({ ...prev, driver_id: e.target.value }))}><option value="">No driver</option>{drivers.map((driver) => <option key={driver.id} value={driver.id}>{driver.full_name || driver.email} · {driver.driver_code}</option>)}</Select></Field>
          <Field label="Vehicle"><Select value={incidentForm.vehicle_id} onChange={(e) => setIncidentForm((prev) => ({ ...prev, vehicle_id: e.target.value }))}><option value="">No vehicle</option>{vehicles.map((vehicle) => <option key={vehicle.id} value={vehicle.id}>{vehicle.plate_number} · {vehicle.vehicle_code}</option>)}</Select></Field>
          <Field label="Severity"><Select value={incidentForm.severity} onChange={(e) => setIncidentForm((prev) => ({ ...prev, severity: e.target.value }))}>{Object.entries(config.incident_severity || {}).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</Select></Field>
          <Field label="Status"><Select value={incidentForm.status} onChange={(e) => setIncidentForm((prev) => ({ ...prev, status: e.target.value }))}>{Object.entries(config.incident_status || {}).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</Select></Field>
          <Field label="Location" full><Input value={incidentForm.location} onChange={(e) => setIncidentForm((prev) => ({ ...prev, location: e.target.value }))} /></Field>
          <Field label="Description" full><Textarea rows={4} value={incidentForm.description} onChange={(e) => setIncidentForm((prev) => ({ ...prev, description: e.target.value }))} /></Field>
          <Field label="Actions taken" full><Textarea rows={4} value={incidentForm.actions_taken} onChange={(e) => setIncidentForm((prev) => ({ ...prev, actions_taken: e.target.value }))} /></Field>
          <Field label="Police report link"><Input value={incidentForm.police_report} onChange={(e) => setIncidentForm((prev) => ({ ...prev, police_report: e.target.value }))} /></Field>
          <Field label="Insurance claim"><Input value={incidentForm.insurance_claim} onChange={(e) => setIncidentForm((prev) => ({ ...prev, insurance_claim: e.target.value }))} /></Field>
          <Field label="Image URLs, one per line" full><Textarea rows={5} value={incidentForm.images} onChange={(e) => setIncidentForm((prev) => ({ ...prev, images: e.target.value }))} /></Field>
          <div className="md:col-span-2 flex justify-end gap-3 pt-2"><ActionButton type="button" onClick={() => setIncidentModal({ open: false, mode: "create", item: null })}>Cancel</ActionButton><button type="submit" disabled={saving} className="rounded-2xl bg-sky-500 px-5 py-3 text-sm font-semibold text-white hover:bg-sky-400 disabled:opacity-60">{saving ? "Saving..." : "Save incident"}</button></div>
        </form>
      </Modal>

      <Modal title="Incident details" open={Boolean(incidentDetails)} onClose={() => setIncidentDetails(null)}>
        {incidentDetails ? (
          <div className="grid gap-4 md:grid-cols-2">
            {[
              ["Incident number", incidentDetails.incident_number],
              ["Date and time", fmtDate(incidentDetails.incident_date, true)],
              ["Type", labelFor(config.incident_types, incidentDetails.incident_type)],
              ["Severity", labelFor(config.incident_severity, incidentDetails.severity)],
              ["Status", labelFor(config.incident_status, incidentDetails.status)],
              ["Driver", incidentDetails.driver_name ? `${incidentDetails.driver_name} · ${incidentDetails.driver_code || "-"}` : "No driver linked"],
              ["Vehicle", incidentDetails.plate_number ? `${incidentDetails.plate_number} · ${labelFor(config.vehicle_types, incidentDetails.vehicle_type)}` : "No vehicle linked"],
              ["Police report", incidentDetails.police_report || "-"],
              ["Insurance claim", incidentDetails.insurance_claim || "-"],
              ["Resolved at", fmtDate(incidentDetails.resolved_at, true)],
            ].map(([label, value]) => (
              <div key={label} className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">{label}</div>
                <div className="mt-2 text-sm text-slate-100">{value || "-"}</div>
              </div>
            ))}
            <div className="md:col-span-2 rounded-2xl border border-white/10 bg-slate-950/40 p-4"><div className="text-xs uppercase tracking-[0.2em] text-slate-500">Location</div><div className="mt-2 text-sm text-slate-100">{incidentDetails.location || "-"}</div></div>
            <div className="md:col-span-2 rounded-2xl border border-white/10 bg-slate-950/40 p-4"><div className="text-xs uppercase tracking-[0.2em] text-slate-500">Description</div><div className="mt-2 text-sm text-slate-100">{incidentDetails.description || "-"}</div></div>
            <div className="md:col-span-2 rounded-2xl border border-white/10 bg-slate-950/40 p-4"><div className="text-xs uppercase tracking-[0.2em] text-slate-500">Actions taken</div><div className="mt-2 text-sm text-slate-100">{incidentDetails.actions_taken || "-"}</div></div>
            <div className="md:col-span-2 rounded-2xl border border-white/10 bg-slate-950/40 p-4"><div className="text-xs uppercase tracking-[0.2em] text-slate-500">Images</div><div className="mt-3 flex flex-wrap gap-2">{(incidentDetails.images || []).length ? incidentDetails.images.map((item) => <a key={item} href={item} target="_blank" rel="noreferrer" className="rounded-xl border border-sky-400/20 bg-sky-500/10 px-3 py-2 text-sm text-sky-200 hover:bg-sky-500/20">Open image</a>) : <div className="text-sm text-slate-400">No images attached.</div>}</div></div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
