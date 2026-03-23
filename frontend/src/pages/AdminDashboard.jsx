import { useEffect, useState } from "react";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import axiosClient from "../api/axiosClient";

const AdminDashboard = () => {
  const [bots, setBots] = useState([]);
  const [systemHealth, setSystemHealth] = useState({});
  const [loading, setLoading] = useState(true);

  // Auto-maintenance instructions for admin bot
  const adminBotInstructions = {
    role: "system_administrator_bot",
    monitoring: {
      interval: 30000, // 30 seconds
      metrics: ["cpu", "memory", "response_time", "error_rate"]
    },
    auto_maintenance: [
      "restart_failed_services",
      "clear_cache_when_full",
      "notify_critical_issues",
      "scale_resources_automatically"
    ],
    thresholds: {
      cpu: 80,
      memory: 85,
      errors: 5
    }
  };

  useEffect(() => {
    localStorage.setItem("admin_bot_instructions", JSON.stringify(adminBotInstructions));
    fetchSystemStatus();

    // WebSocket for real-time monitoring
    const ws = new WebSocket(`ws://${window.location.host.replace('http', 'ws')}/ws/system/monitor`);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setBots(data.bots || []);
        setSystemHealth(data.system_health || {});

        // Auto-alerts for critical issues
        checkCriticalIssues(data);
      } catch (error) {
        console.error("WebSocket message error:", error);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
      toast.error("Real-time monitoring disconnected");
    };

    ws.onclose = () => {
      console.log("Monitor socket closed");
    };

    return () => ws.close();
  }, []);

  const fetchSystemStatus = async () => {
    try {
      setLoading(true);
      const [botsRes, healthRes] = await Promise.all([
        axiosClient.get("/system/bots/status"),
        axiosClient.get("/system/health")
      ]);

      setBots(botsRes.data || []);
      setSystemHealth(healthRes.data || {});
    } catch (error) {
      console.error("Failed to fetch system status:", error);
      toast.error("Failed to load system status");
    } finally {
      setLoading(false);
    }
  };

  const checkCriticalIssues = (data) => {
    const criticalBots = data.bots?.filter(bot =>
      bot.status === "error" || bot.health_score < 50
    );

    if (criticalBots?.length > 0) {
      toast.error(`🚨 ${criticalBots.length} bot(s) need attention`);
    }

    // Check system resources
    if (data.system_health?.cpu > adminBotInstructions.thresholds.cpu) {
      toast.warning("⚠️ High CPU usage detected");
    }
  };

  const restartBot = async (botName) => {
    try {
      await axiosClient.post("/system/bots/restart", { bot_name: botName });
      toast.success(`🔄 ${botName} restart initiated`);
      setTimeout(fetchSystemStatus, 2000);
    } catch (error) {
      toast.error(`Failed to restart ${botName}`);
    }
  };

  const runMaintenance = async (action) => {
    try {
      await axiosClient.post("/system/maintenance", { action });
      toast.success(`🔧 ${action} completed`);
    } catch (error) {
      toast.error(`Maintenance action failed`);
    }
  };

  const getHealthColor = (score) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "active": return "bg-green-100 text-green-800";
      case "idle": return "bg-yellow-100 text-yellow-800";
      case "error": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="min-h-screen bg-[var(--navy-solid)] p-6">
      <ToastContainer position="top-right" />

      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                🧠 AI System Admin Dashboard
              </h1>
              <p className="text-gray-600">
                Real-time monitoring and automated maintenance
              </p>
            </div>
            <button
              onClick={fetchSystemStatus}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200 disabled:opacity-50"
            >
              {loading ? "Refreshing..." : "Refresh"}
            </button>
          </div>
        </div>

        {/* System Health Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="glass-15 rounded-lg shadow border p-6 text-center">
            <div className="text-2xl font-bold text-slate-100">{bots.length}</div>
            <div className="text-slate-300">Total Bots</div>
          </div>

          <div className="glass-15 rounded-lg shadow border p-6 text-center">
            <div className="text-2xl font-bold text-emerald-400">
              {bots.filter(b => b.status === 'active').length}
            </div>
            <div className="text-slate-300">Active</div>
          </div>

          <div className="glass-15 rounded-lg shadow border p-6 text-center">
            <div className="text-2xl font-bold text-rose-400">
              {bots.filter(b => b.status === 'error').length}
            </div>
            <div className="text-slate-300">Errors</div>
          </div>

          <div className="glass-15 rounded-lg shadow border p-6 text-center">
            <div className={`text-2xl font-bold ${getHealthColor(systemHealth.health_score)}`}>
              {systemHealth.health_score || 0}%
            </div>
            <div className="text-slate-300">System Health</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Bot Status Table */}
          <div className="lg:col-span-2">
            <div className="glass-15 rounded-lg shadow border">
              <div className="p-6 border-b border-[var(--navy-border-10)]">
                <h2 className="text-xl font-semibold text-slate-50">
                  Bot Status Monitor ({bots.length})
                </h2>
              </div>
              <div className="p-6">
                {bots.length === 0 ? (
                  <div className="text-center py-8 text-slate-400">
                    No bots configured
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead>
                        <tr className="border-b border-[var(--navy-border-10)]">
                          <th className="text-left p-3 font-medium text-slate-200">Bot Name</th>
                          <th className="text-left p-3 font-medium text-slate-200">Status</th>
                          <th className="text-left p-3 font-medium text-slate-200">Health</th>
                          <th className="text-left p-3 font-medium text-slate-200">Last Updated</th>
                          <th className="text-left p-3 font-medium text-slate-200">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {bots.map((bot, index) => (
                          <tr key={index} className="border-b border-[var(--navy-border-10)] hover:bg-[var(--navy-glass-15)]">
                            <td className="p-3 font-medium text-slate-100">{bot.name}</td>
                            <td className="p-3">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(bot.status)}`}>
                                {bot.status.toUpperCase()}
                              </span>
                            </td>
                            <td className="p-3">
                              <span className={getHealthColor(bot.health_score)}>
                                {bot.health_score}%
                              </span>
                            </td>
                            <td className="p-3 text-sm text-slate-300">
                              {new Date(bot.last_updated).toLocaleString()}
                            </td>
                            <td className="p-3">
                              <button
                                onClick={() => restartBot(bot.name)}
                                className="text-sky-400 hover:text-sky-300 text-sm font-medium"
                              >
                                Restart
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Maintenance Actions */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="glass-15 rounded-lg shadow border p-6">
              <h3 className="text-lg font-semibold text-slate-50 mb-4">
                ⚡ Quick Actions
              </h3>
              <div className="space-y-3">
                <button
                  onClick={() => runMaintenance("clear_cache")}
                  className="w-full bg-[var(--navy-glass-15)] hover:bg-[rgba(14,28,45,0.22)] text-slate-100 py-2 px-4 rounded-lg transition duration-200 text-sm border border-[var(--navy-border-10)]"
                >
                  Clear System Cache
                </button>
                <button
                  onClick={() => runMaintenance("optimize_database")}
                  className="w-full bg-[var(--navy-glass-15)] hover:bg-[rgba(14,28,45,0.22)] text-slate-100 py-2 px-4 rounded-lg transition duration-200 text-sm border border-[var(--navy-border-10)]"
                >
                  Optimize Database
                </button>
                <button
                  onClick={() => runMaintenance("update_bots")}
                  className="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 px-4 rounded-lg transition duration-200 text-sm"
                >
                  Update All Bots
                </button>
              </div>
            </div>

            {/* System Info */}
            <div className="glass-15 rounded-lg shadow border p-6">
              <h3 className="text-lg font-semibold text-slate-50 mb-4">
                🖥️ System Info
              </h3>
              <div className="space-y-2 text-sm text-slate-300">
                <div className="flex justify-between">
                  <span>CPU Usage:</span>
                  <span className="text-slate-100">{systemHealth.cpu || 0}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Memory Usage:</span>
                  <span className="text-slate-100">{systemHealth.memory || 0}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Active Connections:</span>
                  <span className="text-slate-100">{systemHealth.connections || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>Uptime:</span>
                  <span className="text-slate-100">{systemHealth.uptime || "0h"}</span>
                </div>
              </div>
            </div>

            {/* Auto-Maintenance Info */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-3">🤖 Auto-Maintenance</h3>
              <ul className="space-y-1 text-xs text-blue-800">
                {adminBotInstructions.auto_maintenance.map((action, index) => (
                  <li key={index} className="flex items-center">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                    {action.replace(/_/g, ' ')}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;