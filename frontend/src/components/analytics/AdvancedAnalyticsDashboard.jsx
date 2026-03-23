import React, { useState, useEffect } from 'react';
import {
    Box,
    Grid,
    Card,
    CardContent,
    Typography,
    LinearProgress,
} from '@mui/material';
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    AreaChart,
    Area,
} from 'recharts';
import {
    TrendingUp,
    TrendingDown,
    DollarSign,
    Package,
    Users,
    Activity,
    Truck,
    AlertCircle,
} from 'lucide-react';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const AdvancedAnalyticsDashboard = () => {
    const [timeRange, setTimeRange] = useState('7d');
    const [loading, setLoading] = useState(true);
    const [analytics, setAnalytics] = useState({
        revenue: [],
        shipments: [],
        users: [],
        bots: [],
        performance: {},
    });

    useEffect(() => {
        fetchAnalytics();
    }, [timeRange]);

    const fetchAnalytics = async () => {
        try {
            setLoading(true);
            // Mock data - replace with actual API calls
            const mockData = generateMockData();
            setAnalytics(mockData);
        } catch (error) {
            console.error('Error fetching analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    const generateMockData = () => {
        // Generate last 30 days of data
        const days = 30;
        const revenue = [];
        const shipments = [];
        const users = [];

        for (let i = days; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

            revenue.push({
                date: dateStr,
                revenue: Math.floor(Math.random() * 50000) + 30000,
                expenses: Math.floor(Math.random() * 30000) + 15000,
                profit: 0,
            });

            shipments.push({
                date: dateStr,
                completed: Math.floor(Math.random() * 50) + 20,
                pending: Math.floor(Math.random() * 30) + 10,
                cancelled: Math.floor(Math.random() * 5),
            });

            users.push({
                date: dateStr,
                active: Math.floor(Math.random() * 100) + 50,
                new: Math.floor(Math.random() * 20),
            });
        }

        // Calculate profit
        revenue.forEach(item => {
            item.profit = item.revenue - item.expenses;
        });

        return {
            revenue,
            shipments,
            users,
            bots: [
                { name: 'General Manager', usage: 95, status: 'active' },
                { name: 'Operations', usage: 87, status: 'active' },
                { name: 'Finance', usage: 92, status: 'active' },
                { name: 'Freight Broker', usage: 78, status: 'active' },
                { name: 'Dispatcher', usage: 85, status: 'active' },
            ],
            performance: {
                avgResponseTime: 1.2,
                uptime: 99.8,
                errorRate: 0.02,
                apiCallsPerDay: 125000,
            },
        };
    };

    const StatCard = ({ title, value, change, icon: Icon, color }) => (
        <Card sx={{ height: '100%' }}>
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
                                color={change >= 0 ? 'success.main' : 'error.main'}
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
            <Box sx={{ width: '100%', p: 3 }}>
                <LinearProgress />
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom fontWeight="bold">
                📊 Advanced Analytics Dashboard
            </Typography>

            {/* KPI Cards */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Total Revenue"
                        value="$2.4M"
                        change={12.5}
                        icon={DollarSign}
                        color="#10b981"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Active Shipments"
                        value="1,234"
                        change={8.2}
                        icon={Package}
                        color="#3b82f6"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Active Users"
                        value="127"
                        change={5.1}
                        icon={Users}
                        color="#8b5cf6"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Bot Uptime"
                        value="99.8%"
                        change={0.2}
                        icon={Activity}
                        color="#f59e0b"
                    />
                </Grid>
            </Grid>

            {/* Charts Row 1 */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                {/* Revenue Trend */}
                <Grid item xs={12} lg={8}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                💰 Revenue & Profit Trend (30 Days)
                            </Typography>
                            <ResponsiveContainer width="100%" height={300}>
                                <AreaChart data={analytics.revenue}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="date" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Area
                                        type="monotone"
                                        dataKey="revenue"
                                        stackId="1"
                                        stroke="#10b981"
                                        fill="#10b981"
                                        fillOpacity={0.6}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="expenses"
                                        stackId="2"
                                        stroke="#ef4444"
                                        fill="#ef4444"
                                        fillOpacity={0.6}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="profit"
                                        stackId="3"
                                        stroke="#3b82f6"
                                        fill="#3b82f6"
                                        fillOpacity={0.6}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Bot Performance */}
                <Grid item xs={12} lg={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                🤖 AI Bot Performance
                            </Typography>
                            <Box sx={{ mt: 2 }}>
                                {analytics.bots.map((bot, index) => (
                                    <Box key={index} sx={{ mb: 2 }}>
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
                                                bgcolor: '#e5e7eb',
                                                '& .MuiLinearProgress-bar': {
                                                    bgcolor: bot.usage > 80 ? '#10b981' : '#f59e0b',
                                                },
                                            }}
                                        />
                                    </Box>
                                ))}
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Charts Row 2 */}
            <Grid container spacing={3}>
                {/* Shipments Status */}
                <Grid item xs={12} lg={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                📦 Shipment Status Trend
                            </Typography>
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={analytics.shipments.slice(-15)}>
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

                {/* User Activity */}
                <Grid item xs={12} lg={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                👥 User Activity Trend
                            </Typography>
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={analytics.users.slice(-15)}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="date" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Line
                                        type="monotone"
                                        dataKey="active"
                                        stroke="#3b82f6"
                                        strokeWidth={2}
                                        dot={{ r: 4 }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="new"
                                        stroke="#10b981"
                                        strokeWidth={2}
                                        dot={{ r: 4 }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Performance Metrics */}
            <Grid container spacing={3} sx={{ mt: 0 }}>
                <Grid item xs={12}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                ⚡ System Performance Metrics
                            </Typography>
                            <Grid container spacing={2} sx={{ mt: 1 }}>
                                <Grid item xs={6} md={3}>
                                    <Box textAlign="center">
                                        <Typography variant="h4" color="primary" fontWeight="bold">
                                            {analytics.performance.avgResponseTime}s
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
                                            {(analytics.performance.apiCallsPerDay / 1000).toFixed(0)}K
                                        </Typography>
                                        <Typography variant="body2" color="textSecondary">
                                            API Calls/Day
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
