
import { useEffect, useState } from "react";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function getWsBaseUrl() {
  // Use VITE_API_BASE_URL and convert http(s) to ws(s)
  let apiUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
  if (apiUrl.startsWith("https://")) return apiUrl.replace("https://", "wss://");
  if (apiUrl.startsWith("http://")) return apiUrl.replace("http://", "ws://");
  return apiUrl;
}

const SystemAdmin = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {

    // Compose correct WebSocket URL
    const wsUrl = `${getWsBaseUrl()}/api/v1/ws/system/monitor`;
    let ws;
    try {
      ws = new WebSocket(wsUrl);
    } catch (err) {
      console.error("WebSocket connection failed:", err);
      toast.error("❌ WebSocket connection failed");
      return;
    }

    ws.onmessage = (event) => {
      try {
        const liveStats = JSON.parse(event.data);
        setStats({
          memory: liveStats.memory_usage,
          cpu: liveStats.cpu_usage,
          disk: liveStats.disk_usage,
          requests: liveStats.requests_today,
          failed_logins: liveStats.failed_logins,
          alerts: liveStats.warnings,
        });
      } catch (e) {
        console.warn("WebSocket message parse error", e);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket Error:", err);
      toast.error("❌ WebSocket connection failed");
      setStats(null);
    };

    ws.onclose = () => {
      console.warn("SystemAdmin WebSocket Closed");
      setStats(null);
    };

    return () => {
      if (ws) ws.close();
    };
  }, []);

  // ✅ Handler to open the project report
  const openProjectReport = () => {
    window.open("/project-report", "_blank");
  };

  return (
    <div className="flex bg-gray-100 min-h-screen">
      <div className="flex-1 p-6">
        <ToastContainer />
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">🛠️ System Admin Dashboard</h2>
          {/* ✅ Button to open the project report */}
          <button
            onClick={openProjectReport}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            📄 View Project Report
          </button>
        </div>

        {stats ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-4 rounded shadow">
              <h3 className="text-lg font-semibold mb-2">🧠 Memory Usage</h3>
              <p>{stats.memory}%</p>
            </div>
            <div className="bg-white p-4 rounded shadow">
              <h3 className="text-lg font-semibold mb-2">🧠 CPU Usage</h3>
              <p>{stats.cpu}%</p>
            </div>
            <div className="bg-white p-4 rounded shadow">
              <h3 className="text-lg font-semibold mb-2">💾 Disk Usage</h3>
              <p>{stats.disk}%</p>
            </div>
            <div className="bg-white p-4 rounded shadow">
              <h3 className="text-lg font-semibold mb-2">📈 Requests Today</h3>
              <p>{stats.requests}</p>
            </div>
            <div className="bg-white p-4 rounded shadow">
              <h3 className="text-lg font-semibold mb-2">🚫 Failed Logins</h3>
              <p>{stats.failed_logins}</p>
            </div>
            <div className="bg-white p-4 rounded shadow col-span-full">
              <h3 className="text-lg font-semibold mb-2">⚠️ Alerts</h3>
              <ul className="list-disc ml-6 text-sm text-red-600">
                {stats.alerts && stats.alerts.length > 0 ? (
                  stats.alerts.map((alert, index) => (
                    <li key={index}>{alert}</li>
                  ))
                ) : (
                  <li>No alerts</li>
                )}
              </ul>
            </div>
          </div>
        ) : (
          <p>Loading system statistics...</p>
        )}
      </div>
    </div>
  );
};

export default SystemAdmin;
