/**
 * Config Tab - Bot Configuration Management
 */
import { useState, useEffect, useCallback } from "react";
import axiosClient from "../../../api/axiosClient";

export default function ConfigTab({
    botKey,
    configData,
    onRefresh,
    isPreview = false,
}) {
    const [editMode, setEditMode] = useState(false);
    const [configJson, setConfigJson] = useState("");
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        if (configData) {
            setConfigJson(JSON.stringify(configData, null, 2));
        }
    }, [configData]);

    const handleSave = async () => {
        if (isPreview) return;
        setSaving(true);
        setError(null);
        setSuccess(false);

        try {
            const parsed = JSON.parse(configJson);
            await axiosClient.put(
                `/api/v1/ai/bots/available/${encodeURIComponent(botKey)}/config`,
                { config: parsed }
            );
            setSuccess(true);
            setEditMode(false);
            onRefresh?.();
            setTimeout(() => setSuccess(false), 3000);
        } catch (err) {
            if (err instanceof SyntaxError) {
                setError("Invalid JSON format");
            } else {
                setError(err.response?.data?.detail || "Failed to save configuration");
            }
        } finally {
            setSaving(false);
        }
    };

    const handleReset = () => {
        if (configData) {
            setConfigJson(JSON.stringify(configData, null, 2));
        }
        setEditMode(false);
        setError(null);
    };

    // Extract key settings from config
    const keySettings = configData
        ? [
            { label: "Display Name", value: configData.display_name || botKey },
            { label: "Mode", value: configData.mode || "standard" },
            { label: "Version", value: configData.version || "1.0.0" },
            { label: "Priority", value: configData.priority || "normal" },
            { label: "Timeout", value: `${configData.timeout || 30}s` },
            { label: "Max Retries", value: configData.max_retries || 3 },
        ]
        : [];

    return (
        <div className="space-y-6">
            {/* Preview Warning */}
            {isPreview && (
                <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-4">
                    <p className="text-sm text-amber-200">
                         Configuration changes are not available in preview mode.
                    </p>
                </div>
            )}

            {/* Success Message */}
            {success && (
                <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-200">
                     Configuration saved successfully!
                </div>
            )}

            {/* Key Settings Overview */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="mb-3 flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-white"> Key Settings</h3>
                    {!isPreview && (
                        <button
                            onClick={() => setEditMode(!editMode)}
                            className="rounded-lg bg-white/10 px-3 py-1 text-xs font-medium text-slate-300 transition hover:bg-white/20"
                        >
                            {editMode ? "Cancel Edit" : "Edit Config"}
                        </button>
                    )}
                </div>

                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {keySettings.map((setting, i) => (
                        <div key={i} className="rounded-lg bg-white/5 p-3">
                            <div className="text-xs text-slate-400">{setting.label}</div>
                            <div className="mt-1 truncate text-sm font-medium text-white">
                                {setting.value}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Capabilities */}
            {configData?.capabilities?.length > 0 && (
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <h3 className="mb-3 text-sm font-semibold text-white">
                         Capabilities
                    </h3>
                    <div className="flex flex-wrap gap-2">
                        {configData.capabilities.map((cap, i) => (
                            <span
                                key={i}
                                className="rounded-full bg-blue-500/20 px-3 py-1 text-xs font-medium text-blue-300"
                            >
                                {cap}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Full JSON Editor */}
            {editMode && (
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <h3 className="mb-3 text-sm font-semibold text-white">
                         Raw Configuration (JSON)
                    </h3>
                    <textarea
                        value={configJson}
                        onChange={(e) => setConfigJson(e.target.value)}
                        rows={15}
                        disabled={isPreview}
                        className="w-full rounded-lg border border-white/10 bg-slate-900/50 p-4 font-mono text-xs text-slate-300 focus:border-blue-500 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
                    />

                    {/* Error Display */}
                    {error && (
                        <div className="mt-3 rounded-lg border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-200">
                             {error}
                        </div>
                    )}

                    {/* Actions */}
                    <div className="mt-4 flex gap-2">
                        <button
                            onClick={handleSave}
                            disabled={isPreview || saving}
                            className="rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg transition hover:shadow-blue-500/50 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            {saving ? "Saving..." : "Save Configuration"}
                        </button>
                        <button
                            onClick={handleReset}
                            disabled={isPreview}
                            className="rounded-lg bg-white/10 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            Reset
                        </button>
                    </div>
                </div>
            )}

            {/* Read-only JSON View (when not editing) */}
            {!editMode && configData && (
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <h3 className="mb-3 text-sm font-semibold text-white">
                         Full Configuration
                    </h3>
                    <pre className="max-h-64 overflow-auto rounded-lg bg-slate-900/50 p-4 text-xs text-slate-400">
                        {JSON.stringify(configData, null, 2)}
                    </pre>
                </div>
            )}

            {/* No Config State */}
            {!configData && (
                <div className="rounded-xl border border-white/10 bg-white/5 p-8 text-center">
                    <div className="text-3xl"></div>
                    <p className="mt-2 text-sm text-slate-400">
                        No configuration data available
                    </p>
                    {!isPreview && (
                        <button
                            onClick={onRefresh}
                            className="mt-4 rounded-lg bg-white/10 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-white/20"
                        >
                            Refresh
                        </button>
                    )}
                </div>
            )}
        </div>
    );
}
