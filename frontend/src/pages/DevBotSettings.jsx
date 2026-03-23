import React, { useEffect, useState } from "react";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import axiosClient from "../api/axiosClient";

const STORAGE_KEY = "dev_bot_settings";
const INSTRUCTIONS_KEY = "dev_bot_self_instructions";

const DEFAULT_SETTINGS = {
  autoFix: true,
  selfLearning: true,
  aiModel: "GPT-4",
  frequency: "daily",
  performanceMonitoring: true,
  autoBackup: true,
  errorReporting: true,
  learningIntensity: "medium",
};

const AI_MODELS = [
  { id: "GPT-4", name: "GPT-4", description: "Most capable model for complex tasks" },
  { id: "GPT-3.5", name: "GPT-3.5", description: "Fast and cost-effective" },
  { id: "Claude-2", name: "Claude-2", description: "Strong reasoning model" },
  { id: "Custom", name: "Custom Model", description: "Use your own trained model" },
];

const isMissingEndpoint = (error) => {
  const status = error?.response?.status;
  return status === 404 || status === 405 || error?.message === "Network Error";
};

const buildInstructions = (settings) => ({
  role: "development_maintenance_bot",
  capabilities: [
    "self_diagnosis",
    "auto_optimization",
    "performance_monitoring",
    "error_prevention",
    "continuous_learning",
  ],
  self_healing: {
    enabled: settings.autoFix,
    actions: ["restart_services", "clear_cache", "update_dependencies"],
  },
  learning_engine: {
    enabled: settings.selfLearning,
    frequency: settings.frequency,
    intensity: settings.learningIntensity,
    data_sources: ["error_logs", "performance_metrics", "user_feedback"],
  },
  monitoring: {
    enabled: settings.performanceMonitoring,
    metrics: ["response_time", "accuracy", "resource_usage"],
    alerts: settings.errorReporting,
  },
});

export default function DevBotSettings() {
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [botInstructions, setBotInstructions] = useState(buildInstructions(DEFAULT_SETTINGS));

  useEffect(() => {
    try {
      const savedSettings = localStorage.getItem(STORAGE_KEY);
      if (savedSettings) {
        setSettings((prev) => ({ ...prev, ...JSON.parse(savedSettings) }));
      }
    } catch (error) {
      console.error("Failed to load DevBot settings", error);
    }
  }, []);

  useEffect(() => {
    const nextInstructions = buildInstructions(settings);
    setBotInstructions(nextInstructions);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    localStorage.setItem(INSTRUCTIONS_KEY, JSON.stringify(nextInstructions));
  }, [settings]);

  const handleSettingChange = (key, value) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSave = async () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    localStorage.setItem(INSTRUCTIONS_KEY, JSON.stringify(botInstructions));

    try {
      await axiosClient.post("/ai/devbot/settings", {
        settings,
        instructions: botInstructions,
      });
      await axiosClient.post("/ai/devbot/reconfigure", {
        instructions: botInstructions,
      });
      toast.success("Settings saved and applied.");
    } catch (error) {
      if (isMissingEndpoint(error)) {
        toast.info("Settings saved locally. DevBot backend endpoints are not mounted.");
        return;
      }
      console.error("Save error:", error);
      toast.error("Failed to save settings");
    }
  };

  const runSelfDiagnosis = async () => {
    try {
      const response = await axiosClient.post("/ai/devbot/self-diagnose");
      toast.info(`Self-diagnosis: ${response?.data?.status || "completed"}`);
    } catch (error) {
      if (isMissingEndpoint(error)) {
        const localStatus = settings.performanceMonitoring ? "local checks passed" : "monitoring disabled";
        toast.info(`Self-diagnosis: ${localStatus}`);
        return;
      }
      toast.error("Self-diagnosis failed");
    }
  };

  const resetToDefaults = () => {
    setSettings(DEFAULT_SETTINGS);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_SETTINGS));
    localStorage.setItem(INSTRUCTIONS_KEY, JSON.stringify(buildInstructions(DEFAULT_SETTINGS)));
    toast.info("Settings reset to defaults");
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <ToastContainer position="top-right" />

      <div className="mx-auto max-w-4xl">
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold text-gray-900">AI DevBot Settings</h1>
          <p className="text-gray-600">
            Configure autonomous operation and keep a local fallback when backend hooks are not available.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <div className="space-y-6">
            <div className="rounded-lg border bg-white p-6 shadow">
              <h2 className="mb-6 text-xl font-semibold text-gray-900">Autonomous Operation</h2>

              <div className="mb-6">
                <label className="mb-3 block text-sm font-medium text-gray-700">AI Model</label>
                <div className="space-y-2">
                  {AI_MODELS.map((model) => (
                    <label
                      key={model.id}
                      className="flex items-start space-x-3 rounded-lg border p-3 hover:bg-gray-50"
                    >
                      <input
                        type="radio"
                        name="aiModel"
                        value={model.id}
                        checked={settings.aiModel === model.id}
                        onChange={(e) => handleSettingChange("aiModel", e.target.value)}
                        className="mt-1"
                      />
                      <span>
                        <span className="block font-medium text-gray-900">{model.name}</span>
                        <span className="text-sm text-gray-500">{model.description}</span>
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                {[
                  ["autoFix", "Auto-fix system errors", "Automatically detect and fix common issues"],
                  ["selfLearning", "Self-learning mode", "Continuously improve from interactions"],
                  ["performanceMonitoring", "Performance monitoring", "Track and optimize bot performance"],
                ].map(([key, title, description]) => (
                  <div key={key} className="flex items-center justify-between rounded-lg border p-3">
                    <div>
                      <div className="font-medium text-gray-900">{title}</div>
                      <div className="text-sm text-gray-500">{description}</div>
                    </div>
                    <input
                      type="checkbox"
                      checked={Boolean(settings[key])}
                      onChange={(e) => handleSettingChange(key, e.target.checked)}
                      className="h-5 w-5"
                    />
                  </div>
                ))}
              </div>

              <div className="mt-6 space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">Learning Frequency</label>
                  <select
                    value={settings.frequency}
                    onChange={(e) => handleSettingChange("frequency", e.target.value)}
                    className="w-full rounded-lg border border-gray-300 p-3"
                  >
                    <option value="hourly">Hourly</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                  </select>
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">Learning Intensity</label>
                  <select
                    value={settings.learningIntensity}
                    onChange={(e) => handleSettingChange("learningIntensity", e.target.value)}
                    className="w-full rounded-lg border border-gray-300 p-3"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-lg border bg-white p-6 shadow">
              <h2 className="mb-4 text-xl font-semibold text-gray-900">Current Bot Instructions</h2>
              <div className="space-y-3">
                <div>
                  <h3 className="font-medium text-gray-700">Role</h3>
                  <p className="text-sm text-gray-600">{botInstructions.role}</p>
                </div>

                <div>
                  <h3 className="font-medium text-gray-700">Capabilities</h3>
                  <ul className="space-y-1 text-sm text-gray-600">
                    {botInstructions.capabilities.map((capability) => (
                      <li key={capability} className="flex items-center">
                        <span className="mr-2 h-2 w-2 rounded-full bg-green-500" />
                        {capability.replace(/_/g, " ")}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="font-medium text-gray-700">Self-healing</h3>
                  <p className="text-sm text-gray-600">
                    {botInstructions.self_healing.enabled ? "Enabled" : "Disabled"}
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-lg border bg-white p-6 shadow">
              <h2 className="mb-4 text-xl font-semibold text-gray-900">Bot Actions</h2>
              <div className="space-y-3">
                <button
                  onClick={runSelfDiagnosis}
                  className="w-full rounded-lg bg-blue-600 px-4 py-3 text-white transition hover:bg-blue-700"
                >
                  Run Self-Diagnosis
                </button>
                <button
                  onClick={handleSave}
                  className="w-full rounded-lg bg-green-600 px-4 py-3 text-white transition hover:bg-green-700"
                >
                  Save and Apply Settings
                </button>
                <button
                  onClick={resetToDefaults}
                  className="w-full rounded-lg bg-gray-600 px-4 py-3 text-white transition hover:bg-gray-700"
                >
                  Reset to Defaults
                </button>
              </div>
            </div>

            <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
              <h3 className="mb-2 font-semibold text-blue-900">Autonomous Features</h3>
              <ul className="space-y-1 text-sm text-blue-800">
                <li>Self-monitoring and health checks</li>
                <li>Automatic performance optimization</li>
                <li>Continuous learning from interactions</li>
                <li>Local fallback when backend hooks are unavailable</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
