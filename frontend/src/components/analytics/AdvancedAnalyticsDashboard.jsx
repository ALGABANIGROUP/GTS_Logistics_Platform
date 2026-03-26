import React, { useEffect, useState } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
} from "@mui/material";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Package,
  Users,
  Activity,
} from "lucide-react";
import axiosClient from "../../api/axiosClient";

const buildDateBuckets = (days) => {
  const buckets = [];
  const byKey = new Map();
  for (let i = days - 1; i >= 0; i -= 1) {
    const date = new Date();
    date.setHours(0, 0, 0, 0);
    date.setDate(date.getDate() - i);
    const key = date.toISOString().slice(0, 10);
    const label = date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    const entry = { key, label };
    buckets.push(entry);
    byKey.set(key, entry);
  }
  return { buckets, byKey };
};

const normalizeDateKey = (value) => {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toISOString().slice(0, 10);
};

const calcChange = (series, key) => {
  if (!Array.isArray(series) || series.length < 2) return 0;
  const first = Number(series[0]?.[key] || 0);
  const last = Number(series[series.length - 1]?.[key] || 0);
  if (!first) return last ? 100 : 0;
  return Number((((last - first) / first) * 100).toFixed(1));
};

const timeRangeToDays = {
  "7d": 7,
  "30d": 30,
  "90d": 90,
};

const AdvancedAnalyticsDashboard = () => {
  const [timeRange] = useState("30d");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [analytics, setAnalytics] = useState({
    revenue: [],
    shipments: [],
    users: [],
    bots: [],
    performance: {
      avgResponseTime: "-",
      uptime: 0,
      errorRate: 0,
      apiCallsPerDay: 0,
    },
    cards: {
      totalRevenue: 0,
      activeShipments: 0,
      activeUsers: 0,
      botUptime: 0,
      revenueChange: 0,
      shipmentChange: 0,
      userChange: 0,
      botUptimeChange: 0,
    },
  });

  useEffect(() => {
    const fetchAnalytics = async () => {
      const days = timeRangeToDays[timeRange] || 30;
      const { buckets, byKey } = buildDateBuckets(days);
      setLoading(true);
      setError("");

      try {
        const [
          financeRes,
          shipmentsRes,
          usersRes,
          activityRes,
          managementRes,
          botsRes,
          systemHealthRes,
        ] = await Promise.all([
          axiosClient.get("/api/v1/finance/dashboard"),
          axiosClient.get("/api/v1/admin/shipments/analytics"),
          axiosClient.get("/api/v1/admin/users/stats/summary"),
          axiosClient.get("/api/v1/admin/users/activity/recent?limit=500"),
          axiosClient.get("/api/v1/admin/users/management?limit=500"),
          axiosClient.get("/api/v1/admin/bots/status"),
          axiosClient.get("/api/v1/admin/system-health"),
        ]);

        const finance = financeRes?.data || {};
        const shipments = shipmentsRes?.data?.shipments || {};
        const users = usersRes?.data || {};
        const activity = Array.isArray(activityRes?.data) ? activityRes.data : [];
        const management = Array.isArray(managementRes?.data?.users) ? managementRes.data.users : [];
        const botsPayload = botsRes?.data?.bots?.gts_platform || {};
        const systemHealth = systemHealthRes?.data?.health || {};

        const revenueSeriesMap = new Map(
          buckets.map(({ key, label }) => [
            key,
            { date: label, revenue: 0, expenses: 0, profit: 0 },
          ])
        );

        const invoices = finance?.recent?.invoices || [];
        const expenses = finance?.recent?.expenses || [];
        invoices.forEach((item) => {
          const key = normalizeDateKey(item?.created_at || item?.date);
          if (!key || !revenueSeriesMap.has(key)) return;
          revenueSeriesMap.get(key).revenue += Number(item?.amount_usd || 0);
        });
        expenses.forEach((item) => {
          const key = normalizeDateKey(item?.created_at);
          if (!key || !revenueSeriesMap.has(key)) return;
          revenueSeriesMap.get(key).expenses += Number(item?.amount || 0);
        });

        const revenueSeries = Array.from(revenueSeriesMap.values()).map((item) => ({
          ...item,
          revenue: Number(item.revenue.toFixed(2)),
          expenses: Number(item.expenses.toFixed(2)),
          profit: Number((item.revenue - item.expenses).toFixed(2)),
        }));

        const userSeriesMap = new Map(
          buckets.map(({ key, label }) => [
            key,
            { date: label, active: 0, new: 0 },
          ])
        );
        activity.forEach((item) => {
          const key = normalizeDateKey(item?.last_login);
          if (!key || !userSeriesMap.has(key)) return;
          userSeriesMap.get(key).active += 1;
        });
        management.forEach((item) => {
          const key = normalizeDateKey(item?.created_at);
          if (!key || !userSeriesMap.has(key)) return;
          userSeriesMap.get(key).new += 1;
        });
        const userSeries = Array.from(userSeriesMap.values());

        const shipmentSeries = [
          {
            date: "Today",
            completed: Number(shipments?.today?.completed || 0),
            pending: Number(shipments?.today?.in_transit || 0),
            cancelled: Number(shipments?.today?.failed || 0),
          },
          {
            date: "This Month",
            completed: Number(shipments?.this_month?.completed || 0),
            pending: Math.max(
              Number(shipments?.this_month?.total || 0) - Number(shipments?.this_month?.completed || 0) - Number(shipments?.this_month?.failed || 0),
              0
            ),
            cancelled: Number(shipments?.this_month?.failed || 0),
          },
        ];

        const bots = Object.entries(botsPayload).map(([name, details]) => {
          const runsToday = Number(details?.runs_today || 0);
          const failedRuns = Number(details?.failed_runs || 0);
          const usage = runsToday > 0 ? Math.max(0, Math.min(100, Math.round(((runsToday - failedRuns) / runsToday) * 100))) : 0;
          return {
            name: String(name).replace(/_/g, " "),
            usage,
            status: details?.status || "unknown",
          };
        });

        const apiHealthy = systemHealth?.api?.status === "healthy";
        const dbHealthy = systemHealth?.database?.status === "healthy";
        const enabledBots = bots.length || 1;
        const healthyBots = bots.filter((bot) => bot.status !== "error" && bot.status !== "inactive").length;
        const botUptime = Math.round((healthyBots / enabledBots) * 100);

        const nextAnalytics = {
          revenue: revenueSeries,
          shipments: shipmentSeries,
          users: userSeries,
          bots,
          performance: {
            avgResponseTime: systemHealth?.database?.latency_ms ? `${systemHealth.database.latency_ms}ms` : "-",
            uptime: apiHealthy && dbHealthy ? 100 : apiHealthy || dbHealthy ? 50 : 0,
            errorRate: Number((100 - botUptime).toFixed(1)),
            apiCallsPerDay: Number(finance?.metrics?.payment_count || 0) + Number(finance?.metrics?.invoice_count || 0) + Number(finance?.metrics?.expense_count || 0),
          },
          cards: {
            totalRevenue: Number(finance?.metrics?.total_revenue || 0),
            activeShipments: Number(shipments?.today?.in_transit || 0) + Number(shipments?.today?.total || 0),
            activeUsers: Number(users?.active_users || 0),
            botUptime,
            revenueChange: calcChange(revenueSeries, "revenue"),
            shipmentChange: calcChange(shipmentSeries, "completed"),
            userChange: calcChange(userSeries, "active"),
            botUptimeChange: 0,
          },
        };

        setAnalytics(nextAnalytics);
      } catch (fetchError) {
        console.error("Error fetching analytics:", fetchError);
        setError(
          fetchError?.response?.data?.detail ||
            fetchError?.message ||
            "Failed to load analytics."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [timeRange]);

  const StatCard = ({ title, value, change, icon: Icon, color }) => (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" fontWeight="bold">
              {value}
            </Typography>
            <Box display="flex" alignItems="center" mt={1}>
              {change >= 0 ? (
                <TrendingUp size={16} color="#10b981" />
              ) : (
                <TrendingDown size={16} color="#ef4444" />
              )}
              <Typography
                variant="body2"
                color={change >= 0 ? "success.main" : "error.main"}
                ml={0.5}
              >
                {Math.abs(change)}%
              </Typography>
            </Box>
          </Box>
          <Box
            sx={{
              bgcolor: `${color}20`,
              p: 1.5,
              borderRadius: 2,
            }}
          >
            <Icon size={24} color={color} />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box sx={{ width: "100%", p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Advanced Analytics Dashboard
      </Typography>
      {error ? (
        <Typography variant="body2" color="error.main" sx={{ mb: 2 }}>
          {error}
        </Typography>
      ) : null}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Revenue"
            value={`$${analytics.cards.totalRevenue.toLocaleString()}`}
            change={analytics.cards.revenueChange}
            icon={DollarSign}
            color="#10b981"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Shipments"
            value={analytics.cards.activeShipments}
            change={analytics.cards.shipmentChange}
            icon={Package}
            color="#3b82f6"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Users"
            value={analytics.cards.activeUsers}
            change={analytics.cards.userChange}
            icon={Users}
            color="#8b5cf6"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Bot Uptime"
            value={`${analytics.cards.botUptime}%`}
            change={analytics.cards.botUptimeChange}
            icon={Activity}
            color="#f59e0b"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Revenue Snapshot
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={analytics.revenue}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area type="monotone" dataKey="revenue" stroke="#10b981" fill="#10b981" fillOpacity={0.45} />
                  <Area type="monotone" dataKey="expenses" stroke="#ef4444" fill="#ef4444" fillOpacity={0.35} />
                  <Area type="monotone" dataKey="profit" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.25} />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                AI Bot Health
              </Typography>
              <Box sx={{ mt: 2 }}>
                {analytics.bots.length === 0 ? (
                  <Typography variant="body2" color="textSecondary">
                    No active bot data.
                  </Typography>
                ) : (
                  analytics.bots.map((bot) => (
                    <Box key={bot.name} sx={{ mb: 2 }}>
                      <Box display="flex" justifyContent="space-between" mb={0.5}>
                        <Typography variant="body2">{bot.name}</Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {bot.usage}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={bot.usage}
                        sx={{
                          height: 8,
                          borderRadius: 4,
                          bgcolor: "#e5e7eb",
                          "& .MuiLinearProgress-bar": {
                            bgcolor: bot.usage > 80 ? "#10b981" : bot.usage > 0 ? "#f59e0b" : "#94a3b8",
                          },
                        }}
                      />
                    </Box>
                  ))
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Shipment Status Snapshot
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analytics.shipments}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="completed" fill="#10b981" />
                  <Bar dataKey="pending" fill="#f59e0b" />
                  <Bar dataKey="cancelled" fill="#ef4444" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                User Activity Snapshot
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analytics.users}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="active" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="new" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mt: 0 }}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Performance Metrics
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary" fontWeight="bold">
                      {analytics.performance.avgResponseTime}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Avg Response Time
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="success.main" fontWeight="bold">
                      {analytics.performance.uptime}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Uptime
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="error.main" fontWeight="bold">
                      {analytics.performance.errorRate}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Error Rate
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="info.main" fontWeight="bold">
                      {analytics.performance.apiCallsPerDay}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Finance Events
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdvancedAnalyticsDashboard;
