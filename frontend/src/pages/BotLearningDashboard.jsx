import React, { useState, useEffect } from "react";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import axiosClient from "../api/axiosClient";

const BotLearningDashboard = () => {
    const [bots, setBots] = useState([]);
    const [selectedBot, setSelectedBot] = useState(null);
    const [botProfile, setBotProfile] = useState(null);
    const [learningStats, setLearningStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dataLogs, setDataLogs] = useState({ errors: [], metrics: [], feedback: [] });

    // Bot configuration state
    const [botConfig, setBotConfig] = useState({
        enabled: true,
        frequency: "daily",
        intensity: "medium",
        data_sources: ["error_logs", "performance_metrics", "user_feedback"]
    });

    // Fetch available bots
    useEffect(() => {
        const fetchBots = async () => {
            try {
                const response = await axiosClient.get("/ai/bots");
                if (response.data && Array.isArray(response.data)) {
                    setBots(response.data);
                    if (response.data.length > 0 && !selectedBot) {
                        setSelectedBot(response.data[0].name);
                    }
                }
            } catch (error) {
                console.error("Failed to fetch bots:", error);
            }
        };

        fetchBots();
    }, []);

    // Fetch bot profile when selected bot changes
    useEffect(() => {
        if (selectedBot) {
            fetchBotProfile();
        }
    }, [selectedBot]);

    const fetchBotProfile = async () => {
        if (!selectedBot) return;

        try {
            setLoading(true);
            const profileResponse = await axiosClient.get(`/ai/learning/profile/${selectedBot}`);
            if (profileResponse.data.profile) {
                setBotProfile(profileResponse.data.profile);

                // Update config from profile
                setBotConfig({
                    enabled: profileResponse.data.profile.enabled,
                    frequency: profileResponse.data.profile.frequency,
                    intensity: profileResponse.data.profile.intensity,
                    data_sources: profileResponse.data.profile.data_sources
                });
            }

            // Fetch data summary
            const summaryResponse = await axiosClient.get(`/ai/learning/data/summary/${selectedBot}`);
            if (summaryResponse.data.summary) {
                const summary = summaryResponse.data.summary;
                // Fetch detailed logs
                const [errorsResponse, metricsResponse, feedbackResponse] = await Promise.all([
                    axiosClient.get(`/ai/learning/data/errors/${selectedBot}?limit=10`),
                    axiosClient.get(`/ai/learning/data/performance/${selectedBot}?limit=10`),
                    axiosClient.get(`/ai/learning/data/feedback/${selectedBot}?limit=10`)
                ]);

                setDataLogs({
                    errors: errorsResponse.data.errors || [],
                    metrics: metricsResponse.data.metrics || [],
                    feedback: feedbackResponse.data.feedback || []
                });
            }

            // Fetch learning stats
            const statsResponse = await axiosClient.get("/ai/learning/stats");
            setLearningStats(statsResponse.data.learning_stats);
        } catch (error) {
            console.error("Failed to fetch bot profile:", error);
            toast.error("Failed to load bot learning profile");
        } finally {
            setLoading(false);
        }
    };

    const handleConfigChange = (key, value) => {
        setBotConfig(prev => ({
            ...prev,
            [key]: value
        }));
    };

    const handleToggleDataSource = (source) => {
        setBotConfig(prev => ({
            ...prev,
            data_sources: prev.data_sources.includes(source)
                ? prev.data_sources.filter(s => s !== source)
                : [...prev.data_sources, source]
        }));
    };

    const saveConfig = async () => {
        if (!selectedBot) return;

        try {
            await axiosClient.put(`/ai/learning/profile/${selectedBot}`, {
                enabled: botConfig.enabled,
                frequency: botConfig.frequency,
                intensity: botConfig.intensity,
                data_sources: botConfig.data_sources
            });

            toast.success("✅ Bot learning configuration saved!");
            await fetchBotProfile();
        } catch (error) {
            console.error("Failed to save config:", error);
            toast.error("Failed to save learning configuration");
        }
    };

    const triggerLearning = async () => {
        if (!selectedBot) return;

        try {
            setLoading(true);
            const response = await axiosClient.post(`/ai/learning/trigger/${selectedBot}`);

            if (response.data.learning_result) {
                const result = response.data.learning_result;
                const adaptationCount = result.adaptations ? result.adaptations.length : 0;

                toast.success(`✅ Learning triggered! ${adaptationCount} adaptations applied`);
                await fetchBotProfile();
            }
        } catch (error) {
            console.error("Failed to trigger learning:", error);
            toast.error("Failed to trigger learning update");
        } finally {
            setLoading(false);
        }
    };

    const exportLearningData = async () => {
        if (!selectedBot) return;

        try {
            const response = await axiosClient.get(`/ai/learning/export/${selectedBot}`);
            const dataStr = JSON.stringify(response.data.export_data, null, 2);
            const dataBlob = new Blob([dataStr], { type: "application/json" });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement("a");
            link.href = url;
            link.download = `${selectedBot}_learning_data_${new Date().toISOString()}.json`;
            link.click();

            toast.success("✅ Learning data exported!");
        } catch (error) {
            console.error("Failed to export data:", error);
            toast.error("Failed to export learning data");
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <ToastContainer position="top-right" />

            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">
                        🧠 Bot Self-Learning Dashboard
                    </h1>
                    <p className="text-gray-600">
                        Monitor and configure bot self-learning capabilities
                    </p>
                </div>

                {/* Overall Stats */}
                {learningStats && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                            <div className="text-sm font-medium text-blue-900">Registered Bots</div>
                            <div className="text-2xl font-bold text-blue-600">{learningStats.total_bots_registered}</div>
                            <div className="text-xs text-blue-700">{learningStats.enabled_bots} enabled</div>
                        </div>
                        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                            <div className="text-sm font-medium text-green-900">Avg Accuracy</div>
                            <div className="text-2xl font-bold text-green-600">{(learningStats.average_accuracy * 100).toFixed(1)}%</div>
                        </div>
                        <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                            <div className="text-sm font-medium text-purple-900">Avg Performance</div>
                            <div className="text-2xl font-bold text-purple-600">{(learningStats.average_performance * 100).toFixed(1)}%</div>
                        </div>
                        <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
                            <div className="text-sm font-medium text-orange-900">Total Adaptations</div>
                            <div className="text-2xl font-bold text-orange-600">{learningStats.total_adaptations || 0}</div>
                        </div>
                    </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                    {/* Bot Selection */}
                    <div className="bg-white rounded-lg shadow border p-4">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">📋 Available Bots</h2>
                        <div className="space-y-2">
                            {bots.map(bot => (
                                <button
                                    key={bot.name}
                                    onClick={() => setSelectedBot(bot.name)}
                                    className={`w-full text-left p-3 rounded-lg transition ${selectedBot === bot.name
                                            ? "bg-blue-50 border-blue-200 border-2"
                                            : "bg-gray-50 border border-gray-200 hover:bg-gray-100"
                                        }`}
                                >
                                    <div className="font-medium text-gray-900">{bot.name}</div>
                                    <div className="text-xs text-gray-600">{bot.description || "No description"}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Main Content */}
                    <div className="lg:col-span-3">
                        {selectedBot && botProfile ? (
                            <div className="space-y-6">
                                {/* Learning Configuration */}
                                <div className="bg-white rounded-lg shadow border p-6">
                                    <h2 className="text-xl font-semibold text-gray-900 mb-4">⚙️ Learning Configuration</h2>

                                    {/* Enable/Disable */}
                                    <div className="mb-6">
                                        <label className="flex items-center space-x-3 cursor-pointer">
                                            <input
                                                type="checkbox"
                                                checked={botConfig.enabled}
                                                onChange={(e) => handleConfigChange("enabled", e.target.checked)}
                                                className="w-5 h-5 rounded border-gray-300"
                                            />
                                            <span className="text-sm font-medium text-gray-700">Enable Self-Learning</span>
                                        </label>
                                    </div>

                                    {botConfig.enabled && (
                                        <>
                                            {/* Learning Frequency */}
                                            <div className="mb-4">
                                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                                    ⏱️ Learning Frequency
                                                </label>
                                                <select
                                                    value={botConfig.frequency}
                                                    onChange={(e) => handleConfigChange("frequency", e.target.value)}
                                                    className="w-full p-2 border border-gray-300 rounded-lg"
                                                >
                                                    <option value="hourly">Hourly</option>
                                                    <option value="daily">Daily</option>
                                                    <option value="weekly">Weekly</option>
                                                </select>
                                            </div>

                                            {/* Learning Intensity */}
                                            <div className="mb-4">
                                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                                    🎯 Learning Intensity
                                                </label>
                                                <select
                                                    value={botConfig.intensity}
                                                    onChange={(e) => handleConfigChange("intensity", e.target.value)}
                                                    className="w-full p-2 border border-gray-300 rounded-lg"
                                                >
                                                    <option value="low">Low (Conservative)</option>
                                                    <option value="medium">Medium (Balanced)</option>
                                                    <option value="high">High (Aggressive)</option>
                                                </select>
                                            </div>

                                            {/* Data Sources */}
                                            <div className="mb-4">
                                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                                    📊 Data Sources
                                                </label>
                                                <div className="space-y-2">
                                                    {["error_logs", "performance_metrics", "user_feedback"].map(source => (
                                                        <label key={source} className="flex items-center space-x-3 cursor-pointer">
                                                            <input
                                                                type="checkbox"
                                                                checked={botConfig.data_sources.includes(source)}
                                                                onChange={() => handleToggleDataSource(source)}
                                                                className="w-4 h-4 rounded border-gray-300"
                                                            />
                                                            <span className="text-sm text-gray-700 capitalize">
                                                                {source.replace(/_/g, " ")}
                                                            </span>
                                                        </label>
                                                    ))}
                                                </div>
                                            </div>

                                            {/* Save Button */}
                                            <button
                                                onClick={saveConfig}
                                                className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
                                            >
                                                💾 Save Configuration
                                            </button>
                                        </>
                                    )}
                                </div>

                                {/* Learning Metrics */}
                                {botProfile && (
                                    <div className="bg-white rounded-lg shadow border p-6">
                                        <h2 className="text-xl font-semibold text-gray-900 mb-4">📈 Learning Metrics</h2>

                                        <div className="grid grid-cols-2 gap-4 mb-6">
                                            <div>
                                                <div className="text-sm text-gray-600">Accuracy Score</div>
                                                <div className="text-2xl font-bold text-green-600">
                                                    {(botProfile.accuracy_score * 100).toFixed(1)}%
                                                </div>
                                            </div>
                                            <div>
                                                <div className="text-sm text-gray-600">Performance Score</div>
                                                <div className="text-2xl font-bold text-blue-600">
                                                    {(botProfile.performance_score * 100).toFixed(1)}%
                                                </div>
                                            </div>
                                            <div>
                                                <div className="text-sm text-gray-600">Reliability Score</div>
                                                <div className="text-2xl font-bold text-purple-600">
                                                    {(botProfile.reliability_score * 100).toFixed(1)}%
                                                </div>
                                            </div>
                                            <div>
                                                <div className="text-sm text-gray-600">Samples Processed</div>
                                                <div className="text-2xl font-bold text-orange-600">
                                                    {botProfile.total_samples_processed}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4 text-sm">
                                            <div className="bg-gray-50 p-3 rounded">
                                                <div className="text-gray-600">Adaptations Applied</div>
                                                <div className="font-bold text-gray-900">{botProfile.adaptations_applied}</div>
                                            </div>
                                            <div className="bg-gray-50 p-3 rounded">
                                                <div className="text-gray-600">Last Update</div>
                                                <div className="font-bold text-gray-900">
                                                    {botProfile.last_learning_update
                                                        ? new Date(botProfile.last_learning_update).toLocaleDateString()
                                                        : "Never"}
                                                </div>
                                            </div>
                                            <div className="bg-gray-50 p-3 rounded">
                                                <div className="text-gray-600">Next Update</div>
                                                <div className="font-bold text-gray-900">
                                                    {botProfile.next_learning_update
                                                        ? new Date(botProfile.next_learning_update).toLocaleDateString()
                                                        : "Pending"}
                                                </div>
                                            </div>
                                            <div className="bg-gray-50 p-3 rounded">
                                                <div className="text-gray-600">Errors Logged</div>
                                                <div className="font-bold text-gray-900">{botProfile.error_count}</div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Data Summary */}
                                <div className="grid grid-cols-3 gap-4">
                                    <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                                        <div className="text-sm font-medium text-red-900">Error Logs</div>
                                        <div className="text-2xl font-bold text-red-600">{dataLogs.errors.length}</div>
                                    </div>
                                    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                                        <div className="text-sm font-medium text-blue-900">Performance Metrics</div>
                                        <div className="text-2xl font-bold text-blue-600">{dataLogs.metrics.length}</div>
                                    </div>
                                    <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                                        <div className="text-sm font-medium text-yellow-900">Feedback Entries</div>
                                        <div className="text-2xl font-bold text-yellow-600">{dataLogs.feedback.length}</div>
                                    </div>
                                </div>

                                {/* Action Buttons */}
                                <div className="flex gap-3">
                                    <button
                                        onClick={triggerLearning}
                                        disabled={loading || !botConfig.enabled}
                                        className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {loading ? "⏳ Learning..." : "🚀 Trigger Learning"}
                                    </button>
                                    <button
                                        onClick={exportLearningData}
                                        disabled={loading}
                                        className="flex-1 bg-gray-600 text-white py-2 rounded-lg hover:bg-gray-700 transition disabled:opacity-50"
                                    >
                                        📥 Export Data
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="bg-white rounded-lg shadow border p-6 text-center">
                                <p className="text-gray-600">Select a bot to view learning details</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BotLearningDashboard;
