/**
 * Schedule Tab - Bot Automation & Scheduling Configuration
 */
import { useState, useEffect, useCallback } from "react";
import axiosClient from "../../../api/axiosClient";

export default function ScheduleTab({ botKey, botConfig = {}, isPreview = false }) {
    const [schedule, setSchedule] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);

    // Schedule form state
    const [enabled, setEnabled] = useState(false);
    const [cronExpression, setCronExpression] = useState("0 * * * *");
    const [automationLevel, setAutomationLevel] = useState("semi-auto");

    const loadSchedule = useCallback(async () => {
        if (isPreview || !botKey) {
            setLoading(false);
            return;
        }
        try {
            const res = await axiosClient.get(`/api/v1/bots`);
            const bots = res?.data?.bots || [];
            const botData = bots.find((b) => b.name === botKey);
            if (botData) {
                setSchedule(botData);
                setEnabled(botData.enabled !== false);
                setCronExpression(botData.schedule || "0 * * * *");
                setAutomationLevel(botData.automation_level || "semi-auto");
            }
        } catch (err) {
            console.warn("Schedule load failed:", err);
        } finally {
            setLoading(false);
        }
    }, [botKey, isPreview]);

    useEffect(() => {
        loadSchedule();
    }, [loadSchedule]);

    const handleSave = async () => {
        if (isPreview) return;
        setSaving(true);
        setError(null);
        try {
            // Note: This endpoint may need to be implemented on backend
            await axiosClient.put(`/api/v1/bots/${encodeURIComponent(botKey)}/schedule`, {
                enabled,
                cron: cronExpression,
                automation_level: automationLevel,
            });
            await loadSchedule();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to save schedule");
        } finally {
            setSaving(false);
        }
    };

    const handlePause = async () => {
        if (isPreview || !botKey) return;
        try {
            await axiosClient.post(`/api/v1/bots/${encodeURIComponent(botKey)}/pause`);
            await loadSchedule();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to pause bot");
        }
    };

    const handleResume = async () => {
        if (isPreview || !botKey) return;
        try {
            await axiosClient.post(`/api/v1/bots/${encodeURIComponent(botKey)}/resume`);
            await loadSchedule();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to resume bot");
        }
    };

    const presetSchedules = [
        { label: "Every hour", cron: "0 * * * *" },
        { label: "Every 15 min", cron: "*/15 * * * *" },
        { label: "Daily at 6 AM", cron: "0 6 * * *" },
        { label: "Weekdays at 8 AM", cron: "0 8 * * 1-5" },
        { label: "Every 5 min", cron: "*/5 * * * *" },
    ];

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <span className="text-sm text-slate-400">Loading schedule...</span>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Preview Warning */}
            {isPreview && (
                <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-4">
                    <p className="text-sm text-amber-200">
                         Schedule configuration is view-only in preview mode.
                    </p>
                </div>
            )}

            {/* Current Status */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <h3 className="mb-3 text-sm font-semibold text-white">
                    Current Schedule Status
                </h3>
                <div className="grid gap-4 sm:grid-cols-3">
                    <div className="rounded-lg bg-white/5 p-3">
                        <div className="text-xs text-slate-400">Status</div>
                        <div
                            className={`mt-1 text-sm font-semibold ${schedule?.enabled !== false
                                    ? "text-emerald-400"
                                    : "text-slate-400"
                                }`}
                        >
                            {schedule?.enabled !== false ? "Active" : "Paused"}
                        </div>
                    </div>
                    <div className="rounded-lg bg-white/5 p-3">
                        <div className="text-xs text-slate-400">Schedule</div>
                        <div className="mt-1 font-mono text-sm text-white">
                            {schedule?.schedule || "Not set"}
                        </div>
                    </div>
                    <div className="rounded-lg bg-white/5 p-3">
                        <div className="text-xs text-slate-400">Next Run</div>
                        <div className="mt-1 text-sm text-white">
                            {schedule?.next_run
                                ? new Date(schedule.next_run).toLocaleString()
                                : ""}
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="mt-4 flex gap-2">
                    <button
                        onClick={handlePause}
                        disabled={isPreview || schedule?.enabled === false}
                        className="rounded-lg bg-amber-500/20 px-4 py-2 text-xs font-semibold text-amber-300 transition hover:bg-amber-500/30 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                         Pause
                    </button>
                    <button
                        onClick={handleResume}
                        disabled={isPreview || schedule?.enabled !== false}
                        className="rounded-lg bg-emerald-500/20 px-4 py-2 text-xs font-semibold text-emerald-300 transition hover:bg-emerald-500/30 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                         Resume
                    </button>
                </div>
            </div>

            {/* Schedule Configuration */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <h3 className="mb-4 text-sm font-semibold text-white">
                    Schedule Configuration
                </h3>

                <div className="space-y-4">
                    {/* Enable Toggle */}
                    <div className="flex items-center justify-between rounded-lg bg-white/5 p-3">
                        <div>
                            <div className="text-sm font-medium text-white">
                                Enable Automation
                            </div>
                            <div className="text-xs text-slate-400">
                                Allow bot to run automatically on schedule
                            </div>
                        </div>
                        <button
                            onClick={() => setEnabled(!enabled)}
                            disabled={isPreview}
                            className={`relative h-6 w-11 rounded-full transition ${enabled ? "bg-blue-600" : "bg-slate-600"
                                } ${isPreview ? "cursor-not-allowed opacity-50" : ""}`}
                        >
                            <div
                                className={`absolute top-1 h-4 w-4 rounded-full bg-white transition ${enabled ? "left-6" : "left-1"
                                    }`}
                            />
                        </button>
                    </div>

                    {/* Cron Expression */}
                    <div>
                        <label className="mb-2 block text-xs font-medium text-slate-400">
                            Cron Expression
                        </label>
                        <input
                            type="text"
                            value={cronExpression}
                            onChange={(e) => setCronExpression(e.target.value)}
                            disabled={isPreview}
                            placeholder="0 * * * *"
                            className="w-full rounded-lg border border-white/10 bg-slate-900/50 px-3 py-2 font-mono text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
                        />
                        <div className="mt-2 flex flex-wrap gap-2">
                            {presetSchedules.map((preset) => (
                                <button
                                    key={preset.cron}
                                    onClick={() => setCronExpression(preset.cron)}
                                    disabled={isPreview}
                                    className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-300 transition hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                    {preset.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Automation Level */}
                    <div>
                        <label className="mb-2 block text-xs font-medium text-slate-400">
                            Automation Level
                        </label>
                        <select
                            value={automationLevel}
                            onChange={(e) => setAutomationLevel(e.target.value)}
                            disabled={isPreview}
                            className="w-full rounded-lg border border-white/10 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            <option value="manual">Manual Only</option>
                            <option value="semi-auto">Semi-Automatic</option>
                            <option value="full-auto">Full Automation</option>
                        </select>
                    </div>

                    {/* Save Button */}
                    <button
                        onClick={handleSave}
                        disabled={isPreview || saving}
                        className="w-full rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg transition hover:shadow-blue-500/50 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        {saving ? "Saving..." : "Save Schedule"}
                    </button>
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-200">
                     {error}
                </div>
            )}
        </div>
    );
}
