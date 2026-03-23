import { useEffect, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";

const TRAINER_KEY = "trainer_bot";

const prettyJson = (value) => JSON.stringify(value ?? {}, null, 2);

const statusTone = {
  completed: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  running: "border-blue-500/20 bg-blue-500/10 text-blue-200",
  active: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  training: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  draft: "border-violet-500/20 bg-violet-500/10 text-violet-200",
  pending: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  error: "border-rose-500/20 bg-rose-500/10 text-rose-200",
};

const glassCard =
  "rounded-2xl border border-white/10 bg-white/5 shadow-lg shadow-black/30 backdrop-blur-xl";

export default function AITrainerBot() {
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [trainerStatus, setTrainerStatus] = useState({});
  const [trainerConfig, setTrainerConfig] = useState({});
  const [stats, setStats] = useState({});
  const [trainableBots, setTrainableBots] = useState([]);
  const [reports, setReports] = useState([]);
  const [selectedBot, setSelectedBot] = useState("");
  const [form, setForm] = useState({
    level: "intermediate",
    version: "2.0",
    goal: "Increase readiness for production-grade multi-step workflows.",
  });
  const [latestPlan, setLatestPlan] = useState(null);
  const [lastAssessment, setLastAssessment] = useState(null);
  const [lastSession, setLastSession] = useState(null);
  const [actionLog, setActionLog] = useState([]);

  const logAction = (label, payload, status = "info") => {
    setActionLog((prev) => [
      {
        id: Date.now() + Math.random(),
        label,
        payload,
        status,
        timestamp: new Date().toISOString(),
      },
      ...prev.slice(0, 7),
    ]);
  };

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [statusRes, configRes, statsRes, botsRes, reportsRes, dashboardRes] = await Promise.all([
        axiosClient.get(`/api/v1/ai/bots/available/${TRAINER_KEY}/status`),
        axiosClient.post(`/api/v1/ai/bots/available/${TRAINER_KEY}/run`, {
          context: { action: "config" },
        }),
        axiosClient.get("/api/v1/training-center/stats"),
        axiosClient.get("/api/v1/training-center/bots"),
        axiosClient.get("/api/v1/training-center/reports"),
        axiosClient.post(`/api/v1/ai/bots/available/${TRAINER_KEY}/run`, {
          context: { action: "dashboard" },
        }),
      ]);

      setTrainerStatus(statusRes.data?.data || statusRes.data?.status || {});
      setTrainerConfig(configRes.data?.data || configRes.data?.result || {});
      setStats(statsRes.data?.stats || {});
      setTrainableBots(botsRes.data?.bots || []);
      setReports(reportsRes.data?.reports || []);

      const dashboard = dashboardRes.data?.data || dashboardRes.data?.result || {};
      const plans = dashboard?.plans || [];
      setLatestPlan(plans.length ? plans[plans.length - 1] : null);
      if (!selectedBot) {
        const firstBot = (botsRes.data?.bots || []).find((bot) => bot.id !== TRAINER_KEY);
        if (firstBot) {
          setSelectedBot(firstBot.id);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const selectedBotMeta = useMemo(
    () => trainableBots.find((bot) => bot.id === selectedBot) || null,
    [selectedBot, trainableBots]
  );

  const runAction = async (label, runner) => {
    setBusy(true);
    try {
      const result = await runner();
      logAction(label, result, "success");
      await fetchAll();
      return result;
    } catch (error) {
      const detail = error?.response?.data?.detail || error.message;
      logAction(label, { error: detail }, "error");
      throw error;
    } finally {
      setBusy(false);
    }
  };

  const handleRegister = async () => {
    if (!selectedBot) return;
    await runAction("Register Bot", async () => {
      const res = await axiosClient.post("/api/v1/training-center/bots/register", {
        bot_key: selectedBot,
        level: form.level,
        version: form.version,
      });
      return res.data?.profile || res.data;
    });
  };

  const handleAssess = async () => {
    if (!selectedBot) return;
    const result = await runAction("Assess Bot", async () => {
      const res = await axiosClient.post("/api/v1/training-center/assess", {
        bot_key: selectedBot,
      });
      return res.data?.assessment || res.data;
    });
    setLastAssessment(result);
  };

  const handleCreatePlan = async () => {
    if (!selectedBot) return;
    const result = await runAction("Create Training Plan", async () => {
      const res = await axiosClient.post("/api/v1/training-center/plans", {
        bot_key: selectedBot,
        goal: form.goal,
      });
      return res.data?.plan || res.data;
    });
    setLatestPlan(result);
  };

  const handleStartTraining = async () => {
    if (!latestPlan?.plan_id) return;
    const result = await runAction("Start Training Session", async () => {
      const res = await axiosClient.post("/api/v1/training-center/sessions/start", {
        plan_id: latestPlan.plan_id,
      });
      return res.data;
    });
    setLastSession(result);
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="text-center">
          <div className="mx-auto mb-4 h-16 w-16 animate-spin rounded-full border-b-2 border-teal-400" />
          <p className="text-slate-300">Loading Trainer Bot dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-teal-500 to-cyan-600 text-lg font-bold text-white shadow-lg shadow-cyan-900/40">
              TRN
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">AI Trainer Bot</h1>
              <p className="text-sm text-slate-300">
                Training center, readiness planning, simulations, and certification workflows.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className={`${glassCard} px-4 py-2`}>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Mode</p>
              <p className="text-sm font-semibold text-white">{trainerStatus.mode || "training_center"}</p>
            </div>
            <div className={`${glassCard} px-4 py-2`}>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Reports</p>
              <p className="text-sm font-semibold text-white">{stats.reports_generated || 0}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl space-y-6 px-4 py-6">
        <div className="grid gap-4 md:grid-cols-4">
          {[
            { label: "Registered Bots", value: stats.registered_bots || 0, tone: "from-teal-500 to-cyan-600" },
            { label: "Sessions Run", value: stats.sessions_run || 0, tone: "from-blue-500 to-indigo-600" },
            { label: "Reports Generated", value: stats.reports_generated || 0, tone: "from-violet-500 to-fuchsia-600" },
            { label: "Average Score", value: `${stats.average_score || 0}`, tone: "from-emerald-500 to-green-600" },
          ].map((item) => (
            <div key={item.label} className={`rounded-2xl bg-gradient-to-br ${item.tone} p-5 text-white shadow-lg`}>
              <p className="text-3xl font-bold">{item.value}</p>
              <p className="mt-1 text-sm text-white/80">{item.label}</p>
            </div>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <div className={`${glassCard} p-6`}>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-white">Training Control</h2>
                  <p className="text-sm text-slate-400">Register, assess, plan, and run sessions for any trainable bot.</p>
                </div>
                <span className={`rounded-full border px-3 py-1 text-xs ${statusTone[trainerStatus.is_active ? "active" : "pending"]}`}>
                  {trainerStatus.is_active ? "Online" : "Offline"}
                </span>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <label className="block">
                  <span className="mb-2 block text-sm text-slate-300">Trainable Bot</span>
                  <select
                    value={selectedBot}
                    onChange={(e) => setSelectedBot(e.target.value)}
                    className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none"
                  >
                    {trainableBots
                      .filter((bot) => bot.id !== TRAINER_KEY)
                      .map((bot) => (
                        <option key={bot.id} value={bot.id}>
                          {bot.name}
                        </option>
                      ))}
                  </select>
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm text-slate-300">Training Level</span>
                  <select
                    value={form.level}
                    onChange={(e) => setForm((prev) => ({ ...prev, level: e.target.value }))}
                    className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none"
                  >
                    {["beginner", "intermediate", "advanced", "expert", "master"].map((level) => (
                      <option key={level} value={level}>
                        {level}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm text-slate-300">Version</span>
                  <input
                    value={form.version}
                    onChange={(e) => setForm((prev) => ({ ...prev, version: e.target.value }))}
                    className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none"
                  />
                </label>

                <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Selected Specialization</p>
                  <p className="mt-2 text-sm font-semibold capitalize text-white">
                    {selectedBotMeta?.specialization?.replace(/_/g, " ") || "Not selected"}
                  </p>
                  <p className="mt-1 text-xs text-slate-400">{selectedBotMeta?.description || "Choose a bot to view training context."}</p>
                </div>
              </div>

              <label className="mt-4 block">
                <span className="mb-2 block text-sm text-slate-300">Training Goal</span>
                <textarea
                  value={form.goal}
                  onChange={(e) => setForm((prev) => ({ ...prev, goal: e.target.value }))}
                  className="min-h-[110px] w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none"
                />
              </label>

              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  disabled={busy || !selectedBot}
                  onClick={handleRegister}
                  className="rounded-xl bg-teal-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-teal-500 disabled:opacity-50"
                >
                  Register
                </button>
                <button
                  disabled={busy || !selectedBot}
                  onClick={handleAssess}
                  className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-500 disabled:opacity-50"
                >
                  Assess
                </button>
                <button
                  disabled={busy || !selectedBot}
                  onClick={handleCreatePlan}
                  className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-500 disabled:opacity-50"
                >
                  Create Plan
                </button>
                <button
                  disabled={busy || !latestPlan?.plan_id}
                  onClick={handleStartTraining}
                  className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-500 disabled:opacity-50"
                >
                  Start Training
                </button>
                <button
                  disabled={busy}
                  onClick={fetchAll}
                  className="rounded-xl border border-white/10 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/5 disabled:opacity-50"
                >
                  Refresh
                </button>
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              <div className={`${glassCard} p-6`}>
                <h2 className="mb-4 text-lg font-bold text-white">Trainer Config</h2>
                <pre className="overflow-x-auto rounded-xl border border-white/10 bg-slate-950/70 p-4 text-xs text-slate-200">
                  {prettyJson(trainerConfig)}
                </pre>
              </div>

              <div className={`${glassCard} p-6`}>
                <h2 className="mb-4 text-lg font-bold text-white">Latest Results</h2>
                <div className="space-y-4">
                  <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Assessment</p>
                    <pre className="mt-3 overflow-x-auto text-xs text-slate-200">
                      {prettyJson(lastAssessment || { message: "No assessment run in this session." })}
                    </pre>
                  </div>
                  <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Session</p>
                    <pre className="mt-3 overflow-x-auto text-xs text-slate-200">
                      {prettyJson(lastSession || { message: "No training session started in this session." })}
                    </pre>
                  </div>
                </div>
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-white">Recent Training Reports</h2>
                  <p className="text-sm text-slate-400">Latest generated reports from the training center.</p>
                </div>
                <span className="text-sm text-slate-400">{reports.length} reports</span>
              </div>

              <div className="space-y-3">
                {reports.length ? (
                  reports.slice(0, 8).map((report) => (
                    <div key={report.session_id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                          <p className="font-semibold text-white">{report.bot_name}</p>
                          <p className="text-xs text-slate-400">{report.specialization} · {report.session_id}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-emerald-300">{report.final_score}</p>
                          <p className="text-xs text-slate-400">{report.grade}</p>
                        </div>
                      </div>
                      <p className="mt-3 text-sm text-slate-300">{(report.recommendations || []).join(" • ") || "No recommendations."}</p>
                    </div>
                  ))
                ) : (
                  <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6 text-center text-sm text-slate-400">
                    No reports yet.
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className={`${glassCard} p-6`}>
              <h2 className="mb-4 text-lg font-bold text-white">Trainer Runtime Status</h2>
              <div className="space-y-3">
                {[
                  ["Display Name", trainerStatus.display_name || "AI Trainer Bot"],
                  ["Version", trainerStatus.version || "2.0.0"],
                  ["Active Sessions", trainerStatus.active_sessions || 0],
                  ["Average Score", trainerStatus.average_score || 0],
                ].map(([label, value]) => (
                  <div key={label} className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-900/50 px-4 py-3">
                    <span className="text-sm text-slate-400">{label}</span>
                    <span className="text-sm font-semibold text-white">{value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="mb-4 text-lg font-bold text-white">Trainable Bots</h2>
              <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
                {trainableBots.map((bot) => (
                  <button
                    key={bot.id}
                    onClick={() => setSelectedBot(bot.id)}
                    className={`w-full rounded-xl border p-4 text-left transition ${
                      selectedBot === bot.id
                        ? "border-teal-400/40 bg-teal-500/10"
                        : "border-white/10 bg-slate-900/50 hover:bg-white/5"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-semibold text-white">{bot.name}</p>
                        <p className="mt-1 text-xs text-slate-400">{bot.specialization}</p>
                      </div>
                      <span className="rounded-full border border-white/10 px-2 py-1 text-[10px] uppercase tracking-[0.2em] text-slate-300">
                        {bot.icon || "BOT"}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="mb-4 text-lg font-bold text-white">Action Log</h2>
              <div className="space-y-3">
                {actionLog.length ? (
                  actionLog.map((entry) => (
                    <div key={entry.id} className="rounded-xl border border-white/10 bg-slate-900/50 p-3">
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-semibold text-white">{entry.label}</p>
                        <span className={`rounded px-2 py-1 text-[10px] uppercase ${statusTone[entry.status] || "border-white/10 bg-white/5 text-slate-200"}`}>
                          {entry.status}
                        </span>
                      </div>
                      <p className="mt-2 text-xs text-slate-400">{new Date(entry.timestamp).toLocaleString()}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-slate-400">No actions yet.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
