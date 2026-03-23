import React, { useEffect, useMemo, useState } from "react";
import {
  assignShipmentToDriver,
  getDispatchBoard,
  getDispatchInsights,
  getDriverGuidance,
  getDrivers,
  getRoutePlan,
} from "../services/dispatchApi";

const STATUS_COLUMNS = ["Unassigned", "Assigned", "In Transit", "Delivered", "Cancelled"];

const emptyInsights = {
  alerts: { summary: {}, alerts: [] },
  maintenance: { summary: {}, drivers: [] },
};

const Dispatch = () => {
  const [board, setBoard] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [selectedShipment, setSelectedShipment] = useState(null);
  const [form, setForm] = useState({ driver_user_id: "", eta: "", notes: "" });
  const [drivers, setDrivers] = useState([]);
  const [insights, setInsights] = useState(emptyInsights);
  const [routePlan, setRoutePlan] = useState(null);
  const [guidance, setGuidance] = useState(null);

  const fetchBoard = async () => {
    setLoading(true);
    setError("");
    try {
      const [boardData, driverList, dispatchInsights] = await Promise.all([
        getDispatchBoard(),
        getDrivers().catch(() => []),
        getDispatchInsights().catch(() => emptyInsights),
      ]);
      setBoard(boardData || {});
      setDrivers(driverList || []);
      setInsights(dispatchInsights || emptyInsights);
    } catch (err) {
      setError("Failed to load dispatch board");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBoard();
  }, []);

  const handleAssignClick = (shipment) => {
    setSelectedShipment(shipment);
    setForm({ driver_user_id: "", eta: "", notes: "" });
    setRoutePlan(null);
    setGuidance(null);
    setShowModal(true);

    Promise.all([
      getRoutePlan(shipment.id).catch(() => null),
      getDriverGuidance(shipment.id).catch(() => null),
    ]).then(([routeData, guidanceData]) => {
      setRoutePlan(routeData);
      setGuidance(guidanceData);
    });
  };

  const handleAssignSubmit = async (e) => {
    e.preventDefault();
    if (!selectedShipment) return;
    try {
      await assignShipmentToDriver(selectedShipment.id, {
        driver_user_id: Number(form.driver_user_id),
        eta: form.eta || undefined,
        notes: form.notes || undefined,
      });
      setShowModal(false);
      fetchBoard();
    } catch (err) {
      setError("Assignment failed");
    }
  };

  const columnData = useMemo(() => {
    const result = {};
    STATUS_COLUMNS.forEach((col) => {
      result[col] = board[col] || [];
    });
    return result;
  }, [board]);

  return (
    <div className="p-6 space-y-6">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Dispatch Board</h1>
          <p className="text-sm text-gray-500">Track assignments, route guidance, and fleet alerts.</p>
        </div>
        <button
          onClick={fetchBoard}
          className="px-4 py-2 rounded-lg bg-white border border-blue-200 text-blue-700 hover:bg-blue-50"
        >
          Refresh
        </button>
      </header>

      {error && <div className="text-sm text-red-600">{error}</div>}

      {loading ? (
        <div className="text-sm text-gray-500">Loading dispatch data...</div>
      ) : (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-4">
            <div className="rounded-lg border bg-white p-4 shadow-sm">
              <div className="text-xs uppercase tracking-wide text-gray-500">Dispatch Queue</div>
              <div className="mt-2 text-2xl font-bold text-slate-900">{insights?.alerts?.summary?.dispatch_queue ?? 0}</div>
            </div>
            <div className="rounded-lg border bg-white p-4 shadow-sm">
              <div className="text-xs uppercase tracking-wide text-gray-500">Active Alerts</div>
              <div className="mt-2 text-2xl font-bold text-amber-600">{insights?.alerts?.summary?.active_alerts ?? 0}</div>
            </div>
            <div className="rounded-lg border bg-white p-4 shadow-sm">
              <div className="text-xs uppercase tracking-wide text-gray-500">Delivery Success</div>
              <div className="mt-2 text-2xl font-bold text-emerald-600">{insights?.alerts?.summary?.delivery_success_rate ?? 0}%</div>
            </div>
            <div className="rounded-lg border bg-white p-4 shadow-sm">
              <div className="text-xs uppercase tracking-wide text-gray-500">Tracked Drivers</div>
              <div className="mt-2 text-2xl font-bold text-sky-600">{insights?.maintenance?.summary?.tracked_drivers ?? 0}</div>
            </div>
          </div>

          <div className="grid gap-6 xl:grid-cols-[2fr_1fr]">
            <div className="grid md:grid-cols-5 gap-4">
              {STATUS_COLUMNS.map((column) => (
                <div key={column} className="bg-white border rounded-lg shadow-sm p-3">
                  <h2 className="text-sm font-semibold text-gray-600 mb-2">{column}</h2>
                  {columnData[column].length === 0 ? (
                    <p className="text-xs text-gray-400">No shipments</p>
                  ) : (
                    columnData[column].map((shipment) => (
                      <div
                        key={shipment.id}
                        className="mb-3 rounded-lg border border-gray-100 p-2 bg-gray-50"
                      >
                        <p className="text-sm font-semibold">#{shipment.id}</p>
                        <p className="text-xs text-gray-600">{shipment.pickup_location} → {shipment.dropoff_location}</p>
                        {shipment.driver ? (
                          <p className="text-xs text-blue-600">Driver #{shipment.driver.driver_user_id}</p>
                        ) : (
                          <p className="text-xs text-gray-500">Unassigned</p>
                        )}
                        {shipment.last_location ? (
                          <p className="text-xs text-gray-500">
                            Last seen {new Date(shipment.last_location.recorded_at).toLocaleTimeString()}
                          </p>
                        ) : null}
                        <button
                          onClick={() => handleAssignClick(shipment)}
                          className="mt-2 text-xs text-blue-700 hover:underline"
                        >
                          Assign driver
                        </button>
                      </div>
                    ))
                  )}
                </div>
              ))}
            </div>

            <aside className="space-y-4">
              <div className="rounded-lg border bg-white p-4 shadow-sm">
                <h2 className="text-sm font-semibold text-gray-700">Dispatch Alerts</h2>
                <div className="mt-3 space-y-2">
                  {(insights?.alerts?.alerts || []).length === 0 ? (
                    <p className="text-xs text-gray-500">No active alerts.</p>
                  ) : (
                    insights.alerts.alerts.map((alert, index) => (
                      <div key={`${alert.type}-${index}`} className="rounded border border-amber-200 bg-amber-50 p-2">
                        <div className="text-xs font-semibold text-amber-800">{alert.type}</div>
                        <div className="text-xs text-amber-700">{alert.message}</div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div className="rounded-lg border bg-white p-4 shadow-sm">
                <h2 className="text-sm font-semibold text-gray-700">Fleet Risk Watch</h2>
                <div className="mt-3 space-y-2">
                  {(insights?.maintenance?.drivers || []).length === 0 ? (
                    <p className="text-xs text-gray-500">No fleet risk data available.</p>
                  ) : (
                    insights.maintenance.drivers.slice(0, 5).map((driver) => (
                      <div key={driver.driver_user_id} className="rounded border border-slate-200 bg-slate-50 p-2">
                        <div className="text-xs font-semibold text-slate-800">Driver #{driver.driver_user_id}</div>
                        <div className="text-xs text-slate-600">Risk score: {driver.risk_score} · {driver.health}</div>
                        <div className="text-xs text-slate-500">{driver.recommendation}</div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </aside>
          </div>
        </div>
      )}

      {showModal && selectedShipment && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center">
          <form
            onSubmit={handleAssignSubmit}
            className="bg-white p-6 rounded-lg shadow-lg max-w-2xl w-full space-y-4"
          >
            <h3 className="text-lg font-semibold">Assign Shipment #{selectedShipment.id}</h3>
            <div className="grid gap-6 md:grid-cols-2">
              <div className="space-y-4">
                <label className="block text-sm">
                  Driver
                  <select
                    value={form.driver_user_id}
                    onChange={(e) => setForm((prev) => ({ ...prev, driver_user_id: e.target.value }))}
                    className="mt-1 block w-full border px-3 py-2 rounded"
                    required
                  >
                    <option value="">Select an active driver</option>
                    {drivers.map((driver) => (
                      <option key={driver.id} value={driver.id}>
                        {driver.full_name || driver.email} ({driver.email})
                      </option>
                    ))}
                  </select>
                </label>
                <label className="block text-sm">
                  ETA
                  <input
                    type="datetime-local"
                    value={form.eta}
                    onChange={(e) => setForm((prev) => ({ ...prev, eta: e.target.value }))}
                    className="mt-1 block w-full border px-3 py-2 rounded"
                  />
                </label>
                <label className="block text-sm">
                  Notes
                  <textarea
                    value={form.notes}
                    onChange={(e) => setForm((prev) => ({ ...prev, notes: e.target.value }))}
                    className="mt-1 block w-full border px-3 py-2 rounded"
                  />
                </label>
              </div>

              <div className="space-y-4">
                <div className="rounded border bg-slate-50 p-3">
                  <div className="text-sm font-semibold text-slate-700">Route Plan</div>
                  {routePlan ? (
                    <div className="mt-2 text-xs text-slate-600 space-y-1">
                      <div>Traffic: {routePlan.traffic_level}</div>
                      <div>Distance: {routePlan.route.distance_km} km</div>
                      <div>Duration: {routePlan.route.duration_minutes} min</div>
                      <div>Fuel Cost: ${routePlan.route.estimated_fuel_cost_usd}</div>
                      <div>ETA: {routePlan.route.estimated_arrival}</div>
                    </div>
                  ) : (
                    <div className="mt-2 text-xs text-slate-500">Route guidance unavailable.</div>
                  )}
                </div>

                <div className="rounded border bg-slate-50 p-3">
                  <div className="text-sm font-semibold text-slate-700">Driver Guidance</div>
                  {guidance ? (
                    <div className="mt-2 text-xs text-slate-600 space-y-2">
                      <div>{guidance.driver_message}</div>
                      <div>{guidance.rest_recommendation?.message}</div>
                      {(guidance.alerts || []).map((alert, index) => (
                        <div key={`${alert.type}-${index}`} className="rounded border border-amber-200 bg-amber-50 px-2 py-1 text-amber-800">
                          {alert.message}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="mt-2 text-xs text-slate-500">No guidance available until the shipment is assigned.</div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="px-4 py-2 rounded border border-gray-200 text-sm"
              >
                Cancel
              </button>
              <button type="submit" className="px-4 py-2 rounded bg-blue-600 text-white text-sm">
                Assign
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default Dispatch;
