import { useEffect, useState } from "react";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import axiosClient from "../api/axiosClient";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend,
  CartesianGrid, BarChart, Bar, PieChart, Pie, Cell
} from "recharts";

const DevelopmentBot = () => {
  const [maintenanceData, setMaintenanceData] = useState({
    logs: [],
    suggestions: [],
    performance: [],
    systemHealth: {},
    botStatus: {}
  });

  const [loading, setLoading] = useState(true);
  const [autoMode, setAutoMode] = useState(true);

  // Self-instructions for development bot
  const devBotInstructions = {
    role: "ai_development_maintenance_bot",
    self_monitoring: {
      enabled: true,
      checks: ["performance", "errors", "resource_usage", "response_times"],
      frequency: 30000
    },
    auto_optimization: {
      enabled: autoMode,
      actions: ["clean_logs", "optimize_memory", "update_algorithms", "retrain_models"]
    },
    learning_cycle: {
      enabled: true,
      data_sources: ["user_interactions", "error_patterns", "performance_data"],
      adaptation: "continuous"
    }
  };

  useEffect(() => {
    localStorage.setItem("dev_bot_instructions", JSON.stringify(devBotInstructions));
    fetchMaintenanceData();

    // Real-time monitoring
    const interval = setInterval(fetchMaintenanceData, 15000);

    // WebSocket for instant updates
    const ws = new WebSocket(`ws://${window.location.host.replace('http', 'ws')}/ws/devbot/updates`);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleRealTimeUpdate(data);
      } catch (error) {
        console.error("WebSocket message error:", error);
      }
    };

    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, [autoMode]);

  const fetchMaintenanceData = async () => {
    try {
      const response = await axiosClient.get("/ai/devbot/overview");
      setMaintenanceData(response.data);

      // Auto-trigger optimizations if needed
      if (autoMode) {
        checkAndTriggerOptimizations(response.data);
      }
    } catch (err) {
      console.error("Error fetching development bot data", err);
      toast.error("Failed to load bot data");
    } finally {
      setLoading(false);
    }
  };

  const handleRealTimeUpdate = (data) => {
    if (data.type === "error_alert" && data.severity === "high") {
      toast.error(`🚨 ${data.message}`);
    } else if (data.type === "optimization_applied") {
      toast.info(`⚡ ${data.message}`);
    }

    setMaintenanceData(prev => ({
      ...prev,
      logs: data.logs ? [...data.logs, ...prev.logs].slice(0, 10) : prev.logs,
      performance: data.performance || prev.performance
    }));
  };

  const checkAndTriggerOptimizations = (data) => {
    // Auto-trigger optimizations based on thresholds
    if (data.systemHealth?.memory > 80) {
      triggerOptimization("memory_cleanup");
    }

    if (data.systemHealth?.error_rate > 5) {
      triggerOptimization("error_analysis");
    }

    if (data.performance?.length > 0) {
      const latest = data.performance[data.performance.length - 1];
      if (latest.response_time > 1000) {
        triggerOptimization("performance_tuning");
      }
    }
  };

  const triggerOptimization = async (action) => {
    try {
      await axiosClient.post("/ai/devbot/optimize", { action });
      console.log(`Auto-optimization triggered: ${action}`);
    } catch (error) {
      console.error("Optimization failed:", error);
    }
  };

  const runDiagnostic = async () => {
    try {
      const response = await axiosClient.post("/ai/devbot/diagnose");
      toast.success(`🔍 Diagnostic completed: ${response.data.summary}`);
      fetchMaintenanceData();
    } catch (error) {
      toast.error("Diagnostic failed");
    }
  };

  const applySuggestion = async (suggestion) => {
    try {
      await axiosClient.post("/ai/devbot/apply-suggestion", { suggestion });
      toast.success("✅ Suggestion applied");
      fetchMaintenanceData();
    } catch (error) {
      toast.error("Failed to apply suggestion");
    }
  };

  // Chart colors
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const performanceData = maintenanceData.performance || [];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <ToastContainer position="top-right" />

      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                🧠 AI Development & Maintenance Bot
              </h1>
              <p className="text-gray-600">
                Autonomous system monitoring and self-improvement
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoMode}
                    onChange={(e) => setAutoMode(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
                <span className="ml-2 text-sm font-medium text-gray-700">
                  Auto Mode
                </span>
              </div>
              <button
                onClick={runDiagnostic}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200"
              >
                Run Diagnostic
              </button>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading bot data...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            {/* Left Column - System Health */}
            <div className="xl:col-span-2 space-y-6">
              {/* Performance Charts */}
              <div className="bg-white rounded-lg shadow border p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  📈 System Performance Trends
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={performanceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="response_time"
                          stroke="#8884d8"
                          name="Response Time (ms)"
                          strokeWidth={2}
                        />
                        <Line
                          type="monotone"
                          dataKey="accuracy"
                          stroke="#82ca9d"
                          name="Accuracy (%)"
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={performanceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="cpu" fill="#0088FE" name="CPU Usage (%)" />
                        <Bar dataKey="memory" fill="#00C49F" name="Memory Usage (%)" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Error Logs */}
              <div className="bg-white rounded-lg shadow border p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold text-gray-900">
                    🚨 Recent System Events
                  </h3>
                  <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-sm">
                    {maintenanceData.logs.length} events
                  </span>
                </div>
                <div className="space-y-3 max-h-80 overflow-y-auto">
                  {maintenanceData.logs.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">No recent events</p>
                  ) : (
                    maintenanceData.logs.map((log, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-lg border ${log.severity === 'error'
                            ? 'bg-red-50 border-red-200'
                            : log.severity === 'warning'
                              ? 'bg-yellow-50 border-yellow-200'
                              : 'bg-blue-50 border-blue-200'
                          }`}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{log.message}</p>
                            <p className="text-sm text-gray-600 mt-1">{log.details}</p>
                          </div>
                          <div className="text-right">
                            <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${log.severity === 'error'
                                ? 'bg-red-100 text-red-800'
                                : log.severity === 'warning'
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-blue-100 text-blue-800'
                              }`}>
                              {log.severity}
                            </span>
                            <p className="text-xs text-gray-500 mt-1">
                              {new Date(log.timestamp).toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Right Column - AI Suggestions & Status */}
            <div className="space-y-6">
              {/* AI Suggestions */}
              <div className="bg-white rounded-lg shadow border p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  ⚡ AI Optimization Suggestions
                </h3>
                <div className="space-y-3">
                  {maintenanceData.suggestions.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">No suggestions available</p>
                  ) : (
                    maintenanceData.suggestions.map((suggestion, index) => (
                      <div
                        key={index}
                        className="p-3 border border-green-200 rounded-lg bg-green-50"
                      >
                        <p className="text-sm text-green-800 mb-2">{suggestion.description}</p>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-green-600">
                            Impact: {suggestion.impact}
                          </span>
                          <button
                            onClick={() => applySuggestion(suggestion)}
                            className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-xs transition duration-200"
                          >
                            Apply
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* System Health Overview */}
              <div className="bg-white rounded-lg shadow border p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  🖥️ System Health Overview
                </h3>
                <div className="space-y-4">
                  {maintenanceData.systemHealth && Object.entries(maintenanceData.systemHealth).map(([key, value]) => (
                    <div key={key} className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 capitalize">
                        {key.replace(/_/g, ' ')}:
                      </span>
                      <span className={`font-medium ${typeof value === 'number'
                          ? value > 80
                            ? 'text-red-600'
                            : value > 60
                              ? 'text-yellow-600'
                              : 'text-green-600'
                          : 'text-gray-600'
                        }`}>
                        {typeof value === 'number' ? `${value}%` : value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Bot Instructions */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-3">🤖 Active Instructions</h3>
                <ul className="text-sm text-blue-800 space-y-2">
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                    Self-monitoring: {devBotInstructions.self_monitoring.enabled ? 'Active' : 'Inactive'}
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                    Auto-optimization: {devBotInstructions.auto_optimization.enabled ? 'Active' : 'Inactive'}
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                    Continuous learning: Active
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DevelopmentBot;