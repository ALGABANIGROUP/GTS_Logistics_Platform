// frontend/src/pages/GeneralManager.jsx
import { useEffect, useState } from "react";

const GeneralManager = () => {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      setError("");

      try {
        // Use relative URL so Vite proxy sends it to the backend
        const res = await fetch("/api/v1/ai/bots/available/general_manager/run", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ action: "status" }),
        });

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();

        if (!data || !data.ok || !data.report) {
          throw new Error("Invalid response shape");
        }

        setReport(data.report);
      } catch (err) {
        console.error("Failed to fetch general manager report:", err);
        setError("Could not fetch the report from the server.");
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, []);

  const shipments = report?.shipments || {};
  const finance = report?.finance || {};
  const kpis = report?.kpis || {};
  const period = report?.period || {};
  const sources = report?.sources || {};

  return (
    <div className="container mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">AI General Manager Report</h2>

      {loading && <p>Loading report...</p>}

      {!loading && error && (
        <p className="text-red-600 font-medium">Error: {error}</p>
      )}

      {!loading && !error && report && (
        <div className="space-y-6">
          {/* Meta info */}
          <div className="bg-white shadow p-4 rounded">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
              <div>
                <p className="text-sm text-gray-600">
                  Period: <strong>{report.period_label || "N/A"}</strong>
                </p>
                <p className="text-xs text-gray-500">
                  {period.start} to {period.end}
                </p>
              </div>
              <div className="text-xs text-gray-500">
                Generated at:{" "}
                <strong>{report.generated_at || "N/A"}</strong>
              </div>
            </div>
          </div>

          {/* Shipments + Finance KPIs */}
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <div className="bg-white shadow p-4 rounded">
              <h3 className="font-semibold text-sm mb-1">Total Shipments</h3>
              <p className="text-xl">
                {shipments.total != null ? shipments.total : "-"}
              </p>
            </div>
            <div className="bg-white shadow p-4 rounded">
              <h3 className="font-semibold text-sm mb-1">In Transit</h3>
              <p className="text-xl">
                {shipments.in_transit != null ? shipments.in_transit : "-"}
              </p>
            </div>
            <div className="bg-white shadow p-4 rounded">
              <h3 className="font-semibold text-sm mb-1">Delivered</h3>
              <p className="text-xl">
                {shipments.delivered != null ? shipments.delivered : "-"}
              </p>
            </div>
            <div className="bg-white shadow p-4 rounded">
              <h3 className="font-semibold text-sm mb-1">Total Revenue</h3>
              <p className="text-xl">
                {finance.revenue_total != null
                  ? `$${finance.revenue_total}`
                  : "-"}
              </p>
            </div>
            <div className="bg-white shadow p-4 rounded">
              <h3 className="font-semibold text-sm mb-1">Total Expenses</h3>
              <p className="text-xl">
                {finance.expenses_total != null
                  ? `$${finance.expenses_total}`
                  : "-"}
              </p>
            </div>
          </div>

          {/* KPIs */}
          <div className="bg-white shadow p-4 rounded">
            <h3 className="text-xl font-semibold mb-2">
              Key Performance Indicators
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Shipments Total</p>
                <p className="text-lg">
                  {kpis.shipments_total != null
                    ? kpis.shipments_total
                    : "-"}
                </p>
              </div>
              <div>
                <p className="text-gray-500">On-time Rate</p>
                <p className="text-lg">
                  {kpis.on_time_rate != null
                    ? `${(kpis.on_time_rate * 100).toFixed(1)}%`
                    : "-"}
                </p>
              </div>
              <div>
                <p className="text-gray-500">Profit</p>
                <p className="text-lg">
                  {kpis.profit != null ? `$${kpis.profit}` : "-"}
                </p>
              </div>
            </div>
          </div>

          {/* Data sources */}
          <div className="bg-white shadow p-4 rounded">
            <h3 className="text-xl font-semibold mb-2">Data Sources</h3>
            <ul className="list-disc ml-6 text-sm text-gray-600">
              <li>Finance source: {sources.finance || "N/A"}</li>
              <li>Shipments source: {sources.shipments || "N/A"}</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default GeneralManager;
