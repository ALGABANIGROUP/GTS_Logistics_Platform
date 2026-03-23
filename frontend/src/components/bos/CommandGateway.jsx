import React, { useState } from "react";
import axiosClient from "../../api/axiosClient";

export default function CommandGateway({ onExecuted }) {
  const [command, setCommand] = useState("");
  const [botName, setBotName] = useState("");
  const [taskType, setTaskType] = useState("");
  const [paramsText, setParamsText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setResult(null);

    let params = {};
    if (paramsText.trim()) {
      try {
        params = JSON.parse(paramsText);
      } catch {
        setError("Params must be valid JSON.");
        setSubmitting(false);
        return;
      }
    }

    try {
      const res = await axiosClient.post("/api/v1/commands/human", {
        command,
        bot_name: botName || undefined,
        task_type: taskType || undefined,
        params,
      });
      setResult(res?.data || null);
      setCommand("");
      setBotName("");
      setTaskType("");
      setParamsText("");
      onExecuted?.();
    } catch (err) {
      const message =
        err?.response?.data?.detail?.error ||
        err?.response?.data?.detail ||
        err?.message ||
        "Command failed";
      setError(typeof message === "string" ? message : "Command failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-5 shadow-lg shadow-black/30">
      <div>
        <div className="text-lg font-semibold text-white">Human Command Gateway</div>
        <div className="text-sm text-slate-300">
          Send natural language commands to the Bot OS.
        </div>
      </div>

      <form className="mt-4 space-y-3" onSubmit={handleSubmit}>
        <textarea
          className="w-full rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
          rows={3}
          placeholder='Example: run finance summary'
          value={command}
          onChange={(event) => setCommand(event.target.value)}
          required
        />
        <div className="grid gap-3 md:grid-cols-3">
          <input
            className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
            placeholder="Bot name override (optional)"
            value={botName}
            onChange={(event) => setBotName(event.target.value)}
          />
          <input
            className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
            placeholder="Task type override (optional)"
            value={taskType}
            onChange={(event) => setTaskType(event.target.value)}
          />
          <input
            className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
            placeholder='Params JSON (optional)'
            value={paramsText}
            onChange={(event) => setParamsText(event.target.value)}
          />
        </div>

        {error ? (
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-200">
            {error}
          </div>
        ) : null}

        {result ? (
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-xs text-emerald-100">
            Command executed · Bot: {result.bot_name} · Status:{" "}
            {result.ok ? "OK" : "FAILED"}
          </div>
        ) : null}

        <button
          type="submit"
          disabled={submitting || !command.trim()}
          className="inline-flex items-center justify-center rounded-xl bg-sky-500/80 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {submitting ? "Executing..." : "Execute Command"}
        </button>
      </form>
    </div>
  );
}
