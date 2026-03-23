/**
 * Execute Tab - Bot Command Execution Interface
 */
import { useState } from "react";

const QUICK_COMMANDS = [
    { id: "run", label: "Run", icon: "", command: "run" },
    { id: "status", label: "Status Check", icon: "", command: "status" },
    { id: "report", label: "Generate Report", icon: "", command: "generate_report" },
    { id: "analyze", label: "Analyze", icon: "", command: "analyze" },
];

export default function ExecuteTab({
    botKey,
    botConfig = {},
    onExecute,
    isPreview = false,
}) {
    const [message, setMessage] = useState("");
    const [context, setContext] = useState("{}");
    const [executing, setExecuting] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [showAdvanced, setShowAdvanced] = useState(false);

    const customCommands = botConfig.commands || [];

    const handleExecute = async (customMessage = null) => {
        if (isPreview) {
            setError("Cannot execute in preview mode - backend not active");
            return;
        }

        const msg = customMessage || message;
        if (!msg.trim()) {
            setError("Please enter a command or message");
            return;
        }

        setExecuting(true);
        setError(null);
        setResult(null);

        try {
            let parsedContext = {};
            if (context.trim()) {
                try {
                    parsedContext = JSON.parse(context);
                } catch {
                    // Ignore JSON parse errors, use empty context
                }
            }

            const res = await onExecute({ message: msg, context: parsedContext });
            if (res.ok) {
                setResult(res.data);
                setMessage("");
            } else {
                setError(res.error || "Execution failed");
            }
        } catch (err) {
            setError(err.message || "Execution failed");
        } finally {
            setExecuting(false);
        }
    };

    const handleQuickCommand = (cmd) => {
        setMessage(cmd);
        handleExecute(cmd);
    };

    return (
        <div className="space-y-6">
            {/* Preview Mode Warning */}
            {isPreview && (
                <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-4">
                    <p className="text-sm text-amber-200">
                         This bot is in preview mode. Commands will not be executed until the backend is activated.
                    </p>
                </div>
            )}

            {/* Quick Commands */}
            <div>
                <h3 className="mb-3 text-sm font-semibold text-white">Quick Commands</h3>
                <div className="flex flex-wrap gap-2">
                    {QUICK_COMMANDS.map((cmd) => (
                        <button
                            key={cmd.id}
                            onClick={() => handleQuickCommand(cmd.command)}
                            disabled={isPreview || executing}
                            className="flex items-center gap-2 rounded-lg bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            <span>{cmd.icon}</span>
                            {cmd.label}
                        </button>
                    ))}
                    {customCommands.map((cmd, i) => (
                        <button
                            key={`custom-${i}`}
                            onClick={() => handleQuickCommand(cmd.command || cmd)}
                            disabled={isPreview || executing}
                            className="flex items-center gap-2 rounded-lg bg-indigo-500/20 px-4 py-2 text-sm font-medium text-indigo-200 transition hover:bg-indigo-500/30 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            <span></span>
                            {cmd.label || cmd}
                        </button>
                    ))}
                </div>
            </div>

            {/* Command Input */}
            <div>
                <h3 className="mb-3 text-sm font-semibold text-white">
                    Custom Command / Message
                </h3>
                <div className="space-y-3">
                    <textarea
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Enter command or natural language message..."
                        rows={4}
                        className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />

                    {/* Advanced Options Toggle */}
                    <button
                        onClick={() => setShowAdvanced(!showAdvanced)}
                        className="flex items-center gap-2 text-xs text-slate-400 hover:text-white"
                    >
                        <span>{showAdvanced ? "" : ""}</span>
                        Advanced Options
                    </button>

                    {/* Advanced Options */}
                    {showAdvanced && (
                        <div className="space-y-2 rounded-lg border border-white/10 bg-white/5 p-4">
                            <label className="block text-xs font-medium text-slate-400">
                                Context (JSON)
                            </label>
                            <textarea
                                value={context}
                                onChange={(e) => setContext(e.target.value)}
                                placeholder='{"key": "value"}'
                                rows={3}
                                className="w-full rounded-lg border border-white/10 bg-slate-900/50 px-3 py-2 font-mono text-xs text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                            />
                        </div>
                    )}

                    {/* Execute Button */}
                    <button
                        onClick={() => handleExecute()}
                        disabled={isPreview || executing || !message.trim()}
                        className={`w-full rounded-lg px-4 py-3 text-sm font-semibold transition ${isPreview || executing || !message.trim()
                                ? "bg-slate-700 text-slate-400 cursor-not-allowed"
                                : "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50"
                            }`}
                    >
                        {executing ? (
                            <span className="flex items-center justify-center gap-2">
                                <span className="animate-spin"></span> Executing...
                            </span>
                        ) : (
                            <span className="flex items-center justify-center gap-2">
                                <span></span> Execute Command
                            </span>
                        )}
                    </button>
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 p-4">
                    <div className="flex items-start gap-2">
                        <span className="text-rose-400"></span>
                        <p className="text-sm text-rose-200">{error}</p>
                    </div>
                </div>
            )}

            {/* Result Display */}
            {result && (
                <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4">
                    <h4 className="mb-2 flex items-center gap-2 text-sm font-semibold text-emerald-300">
                        <span></span> Execution Result
                    </h4>
                    <pre className="max-h-64 overflow-auto rounded-lg bg-slate-900/50 p-3 text-xs text-slate-300">
                        {typeof result === "string"
                            ? result
                            : JSON.stringify(result, null, 2)}
                    </pre>
                </div>
            )}
        </div>
    );
}
