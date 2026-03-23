import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  Bell,
  Bot,
  Mail,
  MessageSquare,
  Phone,
  RefreshCw,
  Send,
  TrendingUp,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import axiosClient from "../api/axiosClient";

const CHANNEL_COLORS = {
  email: "#38bdf8",
  call: "#34d399",
  sms: "#f59e0b",
  whatsapp: "#10b981",
  push: "#f472b6",
};

const SENTIMENT_COLORS = {
  positive: "#22c55e",
  neutral: "#f59e0b",
  negative: "#ef4444",
};

function StatCard({ title, value, hint, icon: Icon, color }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-5 shadow-[0_12px_40px_rgba(2,6,23,0.35)]">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm font-medium text-slate-400">{title}</span>
        <span
          className="flex h-10 w-10 items-center justify-center rounded-xl"
          style={{ backgroundColor: `${color}22`, color }}
        >
          <Icon className="h-5 w-5" />
        </span>
      </div>
      <div className="text-3xl font-semibold text-white">{value}</div>
      <div className="mt-2 text-sm text-slate-500">{hint}</div>
    </div>
  );
}

function StatusBadge({ value }) {
  const normalized = String(value || "unknown").toLowerCase();
  const styles =
    normalized === "active" || normalized === "success" || normalized === "completed"
      ? "bg-emerald-500/15 text-emerald-300 border-emerald-400/20"
      : normalized === "failed" || normalized === "error"
        ? "bg-rose-500/15 text-rose-300 border-rose-400/20"
        : "bg-amber-500/15 text-amber-200 border-amber-400/20";
  return (
    <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium ${styles}`}>
      {value || "unknown"}
    </span>
  );
}

export default function CommunicationsDashboard() {
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState("week");
  const [stats, setStats] = useState({
    total: 0,
    emails: 0,
    calls: 0,
    sms: 0,
    whatsapp: 0,
    push: 0,
    services: {},
  });
  const [botStats, setBotStats] = useState([]);
  const [recentCommunications, setRecentCommunications] = useState([]);
  const [sentimentData, setSentimentData] = useState({
    positive: 0,
    neutral: 0,
    negative: 0,
    trend: [],
  });

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [statsRes, botsRes, recentRes, sentimentRes] = await Promise.all([
        axiosClient.get("/api/v1/communications/stats", { params: { range: timeRange } }),
        axiosClient.get("/api/v1/communications/bot-stats"),
        axiosClient.get("/api/v1/communications/recent", { params: { limit: 20 } }),
        axiosClient.get("/api/v1/communications/sentiment-trends", { params: { range: timeRange } }),
      ]);
      setStats(statsRes.data || {});
      setBotStats(botsRes.data?.bots || []);
      setRecentCommunications(recentRes.data?.communications || []);
      setSentimentData(sentimentRes.data || {});
    } catch (error) {
      console.error("Error fetching communications dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    const id = window.setInterval(fetchAllData, 30000);
    return () => window.clearInterval(id);
  }, [timeRange]);

  const channelDistribution = useMemo(
    () => [
      { name: "Email", value: stats.emails || 0, color: CHANNEL_COLORS.email },
      { name: "Calls", value: stats.calls || 0, color: CHANNEL_COLORS.call },
      { name: "SMS", value: stats.sms || 0, color: CHANNEL_COLORS.sms },
      { name: "WhatsApp", value: stats.whatsapp || 0, color: CHANNEL_COLORS.whatsapp },
      { name: "Push", value: stats.push || 0, color: CHANNEL_COLORS.push },
    ],
    [stats]
  );

  const sentimentDistribution = useMemo(
    () => [
      { name: "Positive", value: sentimentData.positive || 0, color: SENTIMENT_COLORS.positive },
      { name: "Neutral", value: sentimentData.neutral || 0, color: SENTIMENT_COLORS.neutral },
      { name: "Negative", value: sentimentData.negative || 0, color: SENTIMENT_COLORS.negative },
    ],
    [sentimentData]
  );

  const performanceSummary = useMemo(() => {
    const totalBots = botStats.length || 1;
    const activeBots = botStats.filter((bot) => bot.status === "active").length;
    const totalHandled = botStats.reduce(
      (sum, bot) => sum + (bot.email_count || 0) + (bot.call_count || 0),
      0
    );
    return {
      activeRate: Math.round((activeBots / totalBots) * 100),
      totalHandled,
    };
  }, [botStats]);

  return (
    <div className="space-y-8">
      <section className="overflow-hidden rounded-[28px] border border-cyan-400/10 bg-[radial-gradient(circle_at_top_left,_rgba(34,211,238,0.16),_transparent_34%),linear-gradient(135deg,_rgba(15,23,42,0.96),_rgba(30,41,59,0.92))] p-6 shadow-[0_24px_80px_rgba(15,23,42,0.45)] lg:p-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">
              <Activity className="h-3.5 w-3.5" />
              Unified Communications
            </div>
            <h1 className="max-w-3xl text-3xl font-semibold tracking-tight text-white lg:text-4xl">
              Communications Center
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
              One view for email, calls, SMS, WhatsApp, push, bot performance, and live communication activity.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <select
              value={timeRange}
              onChange={(event) => setTimeRange(event.target.value)}
              className="rounded-xl border border-white/10 bg-slate-950/70 px-4 py-2.5 text-sm text-white outline-none transition focus:border-cyan-400/40"
            >
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="quarter">Last 90 Days</option>
            </select>
            <button
              onClick={fetchAllData}
              className="inline-flex items-center gap-2 rounded-xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2.5 text-sm font-medium text-cyan-100 transition hover:bg-cyan-400/20"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <StatCard title="Total" value={stats.total || 0} hint="All tracked communications" icon={TrendingUp} color="#38bdf8" />
        <StatCard title="Emails" value={stats.emails || 0} hint="Inbound and outbound" icon={Mail} color="#60a5fa" />
        <StatCard title="Calls" value={stats.calls || 0} hint="Recent call records" icon={Phone} color="#34d399" />
        <StatCard title="SMS" value={stats.sms || 0} hint={stats.services?.sms_enabled ? "Twilio enabled" : "Twilio disabled"} icon={MessageSquare} color="#f59e0b" />
        <StatCard title="Push" value={stats.push || 0} hint={stats.services?.push_enabled ? "Firebase enabled" : "Firebase disabled"} icon={Bell} color="#f472b6" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.35fr_0.95fr]">
        <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-5">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">Communication Timeline</h2>
              <p className="text-sm text-slate-400">Call sentiment trend over the selected range.</p>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sentimentData.trend || []}>
                <defs>
                  <linearGradient id="positiveFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.45} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
                <XAxis dataKey="date" stroke="#94a3b8" tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ background: "#0f172a", border: "1px solid rgba(148,163,184,0.16)", borderRadius: "14px" }}
                  labelStyle={{ color: "#e2e8f0" }}
                />
                <Legend />
                <Area type="monotone" dataKey="positive" stroke="#22c55e" fill="url(#positiveFill)" strokeWidth={2.5} />
                <Area type="monotone" dataKey="neutral" stroke="#f59e0b" fill="transparent" strokeWidth={2} />
                <Area type="monotone" dataKey="negative" stroke="#ef4444" fill="transparent" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="grid gap-6">
          <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-5">
            <h2 className="mb-4 text-lg font-semibold text-white">Channel Distribution</h2>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={channelDistribution} dataKey="value" nameKey="name" innerRadius={52} outerRadius={88} paddingAngle={4}>
                    {channelDistribution.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: "#0f172a", border: "1px solid rgba(148,163,184,0.16)", borderRadius: "14px" }}
                    labelStyle={{ color: "#e2e8f0" }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-5">
            <h2 className="mb-4 text-lg font-semibold text-white">Sentiment Snapshot</h2>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sentimentDistribution}>
                  <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
                  <XAxis dataKey="name" stroke="#94a3b8" tickLine={false} axisLine={false} />
                  <YAxis stroke="#94a3b8" tickLine={false} axisLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ background: "#0f172a", border: "1px solid rgba(148,163,184,0.16)", borderRadius: "14px" }}
                    labelStyle={{ color: "#e2e8f0" }}
                  />
                  <Bar dataKey="value" radius={[10, 10, 0, 0]}>
                    {sentimentDistribution.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.05fr_1.45fr]">
        <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">Bot Performance</h2>
              <p className="text-sm text-slate-400">Activity by communication bot.</p>
            </div>
            <div className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-200">
              {performanceSummary.activeRate}% active
            </div>
          </div>
          <div className="space-y-3">
            {botStats.slice(0, 8).map((bot) => {
              const total = (bot.email_count || 0) + (bot.call_count || 0);
              return (
                <div key={bot.bot_name} className="rounded-2xl border border-white/8 bg-slate-950/60 p-4">
                  <div className="mb-2 flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2 text-white">
                        <Bot className="h-4 w-4 text-cyan-300" />
                        <span className="font-medium capitalize">{String(bot.bot_name).replaceAll("_", " ")}</span>
                      </div>
                      <div className="mt-1 text-sm text-slate-400">
                        {bot.email_count || 0} emails, {bot.call_count || 0} calls
                      </div>
                    </div>
                    <StatusBadge value={bot.status} />
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500">Handled</span>
                    <span className="font-medium text-slate-200">{total}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">Recent Communications</h2>
              <p className="text-sm text-slate-400">Latest messages and calls across all channels.</p>
            </div>
            <div className="text-sm text-slate-500">{performanceSummary.totalHandled} handled this period</div>
          </div>
          <div className="overflow-hidden rounded-2xl border border-white/8">
            <div className="grid grid-cols-[1.1fr_0.7fr_0.9fr_0.8fr_0.8fr] gap-3 bg-slate-950/80 px-4 py-3 text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              <div>Time</div>
              <div>Channel</div>
              <div>Direction</div>
              <div>Bot</div>
              <div>Status</div>
            </div>
            <div className="divide-y divide-white/6 bg-slate-950/40">
              {recentCommunications.length === 0 ? (
                <div className="px-4 py-8 text-center text-sm text-slate-500">No recent communication records yet.</div>
              ) : (
                recentCommunications.map((item, index) => (
                  <div
                    key={`${item.channel}-${item.timestamp}-${index}`}
                    className="grid grid-cols-[1.1fr_0.7fr_0.9fr_0.8fr_0.8fr] gap-3 px-4 py-4 text-sm text-slate-300"
                  >
                    <div>{item.timestamp ? new Date(item.timestamp).toLocaleString() : "-"}</div>
                    <div className="capitalize">{item.channel}</div>
                    <div className="capitalize text-slate-400">{item.direction}</div>
                    <div className="capitalize">{String(item.bot_name || "unknown").replaceAll("_", " ")}</div>
                    <div><StatusBadge value={item.status} /></div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-4">
        {[
          { key: "email", label: "Send Test Email", color: "bg-sky-500/15 text-sky-200 border-sky-400/20", icon: Mail },
          { key: "call", label: "Make Test Call", color: "bg-emerald-500/15 text-emerald-200 border-emerald-400/20", icon: Phone },
          { key: "sms", label: "Send Test SMS", color: "bg-amber-500/15 text-amber-200 border-amber-400/20", icon: MessageSquare },
          { key: "whatsapp", label: "Send Test WhatsApp", color: "bg-teal-500/15 text-teal-200 border-teal-400/20", icon: Send },
        ].map(({ key, label, color, icon: Icon }) => (
          <button
            key={key}
            onClick={() => axiosClient.get(`/api/v1/communications/test/${key}`).catch((error) => console.error(error))}
            className={`inline-flex items-center justify-center gap-2 rounded-2xl border px-4 py-3 text-sm font-medium transition hover:translate-y-[-1px] ${color}`}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </section>
    </div>
  );
}
