import React, { useState, useEffect, useRef } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import { Mail, Send, Bot, CheckCircle, AlertCircle, Clock, Zap, TrendingUp, MessageSquare } from 'lucide-react';
import axiosClient from '../../api/axiosClient';

/**
 * AIEmailBot - Intelligent Email Bot Processing and Automation
 * Routes incoming emails to specialized AI bots, executes workflows, and sends responses
 */
export default function AIEmailBot() {
    const [stats, setStats] = useState(null);
    const [mappings, setMappings] = useState([]);
    const [history, setHistory] = useState([]);
    const [botStats, setBotStats] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [wsConnected, setWsConnected] = useState(false);
    const [activeTab, setActiveTab] = useState('overview');
    const [selectedEmail, setSelectedEmail] = useState(null);
    const wsRef = useRef(null);

    const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#3b82f6', '#8b5cf6'];

    // Fetch initial data
    useEffect(() => {
        const fetchData = async () => {
            try {
                const [statsRes, mappingsRes, historyRes] = await Promise.all([
                    axiosClient.get('/api/v1/email/monitoring/stats'),
                    axiosClient.get('/api/v1/email/mappings'),
                    axiosClient.get('/api/v1/email/execution-history?limit=50')
                ]);

                setStats(statsRes.data);
                setMappings(mappingsRes.data.mappings || []);
                setHistory(historyRes.data.history || []);

                // Aggregate bot stats
                if (statsRes.data.bot_performance) {
                    setBotStats(statsRes.data.bot_performance);
                }

                setLoading(false);
            } catch (err) {
                const status = err?.response?.status;
                if (status === 404) {
                    try {
                        const [mailboxesRes, threadsRes] = await Promise.all([
                            axiosClient.get('/api/v1/email/mailboxes'),
                            axiosClient.get('/api/v1/email/threads')
                        ]);

                        const mailboxes = Array.isArray(mailboxesRes.data) ? mailboxesRes.data : [];
                        const threads = Array.isArray(threadsRes.data?.threads) ? threadsRes.data.threads : [];

                        const mailboxById = new Map(mailboxes.map((m) => [m.id, m]));

                        const fallbackMappings = mailboxes.map((mb) => ({
                            email_pattern: mb.email_address,
                            bot_name: mb.bot_code || 'unassigned',
                            workflow: null,
                        }));

                        const historyItems = threads.map((t) => {
                            const mailbox = mailboxById.get(t.mailbox_id);
                            return {
                                id: t.id,
                                email_from: mailbox?.email_address || 'Unknown',
                                subject: t.subject || 'No Subject',
                                bot_name: mailbox?.bot_code || 'N/A',
                                workflow: null,
                                status: t.status || 'unknown',
                                timestamp: t.last_message_at || t.created_at || null,
                                processed_count: 1,
                                success_count: t.status === 'processed' ? 1 : 0,
                                error_count: t.status === 'failed' ? 1 : 0,
                                success_rate: t.status === 'processed' ? 1 : 0,
                            };
                        });

                        const normalizeStatus = (value) => (value || '').toString().toLowerCase();
                        const total = historyItems.length;
                        const successful = historyItems.filter((h) => normalizeStatus(h.status) === 'processed').length;
                        const pending = historyItems.filter((h) => ['pending', 'new', 'open', 'queued'].includes(normalizeStatus(h.status))).length;
                        const failed = historyItems.filter((h) => ['failed', 'error', 'rejected'].includes(normalizeStatus(h.status))).length;

                        const botPerf = mailboxes.reduce((acc, mb) => {
                            const key = mb.bot_code || 'unassigned';
                            acc[key] = (acc[key] || 0) + 1;
                            return acc;
                        }, {});

                        setMappings(fallbackMappings);
                        setHistory(historyItems);
                        setStats({
                            total_processed: total,
                            successful,
                            pending,
                            failed,
                            bot_performance: botPerf,
                        });
                        setBotStats(botPerf);
                        setError(null);
                        setLoading(false);
                        return;
                    } catch (fallbackErr) {
                        console.error('Failed to fetch email center data:', fallbackErr);
                        setError(fallbackErr?.message || 'Failed to load email data');
                        setLoading(false);
                        return;
                    }
                }

                console.error('Failed to fetch email bot data:', err);
                setError(err.message);
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
        return () => clearInterval(interval);
    }, []);

    // WebSocket for real-time updates
    useEffect(() => {
        const connectWs = () => {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/live`;
            wsRef.current = new WebSocket(wsUrl);

            wsRef.current.onopen = () => {
                setWsConnected(true);
                // Subscribe to email-bot channel
                wsRef.current.send(JSON.stringify({ type: 'subscribe', channel: 'email-bot' }));
            };
            wsRef.current.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'execution_update' || data.type === 'email_processed') {
                    setHistory((prev) => [data.execution || data.data, ...prev.slice(0, 49)]);
                }
                if (data.type === 'stats_update') {
                    setStats(data.stats || data.data);
                }
            };
            wsRef.current.onerror = () => setWsConnected(false);
            wsRef.current.onclose = () => {
                setWsConnected(false);
                setTimeout(connectWs, 3000);
            };
        };

        connectWs();
        return () => wsRef.current?.close();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-900">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
                    <p className="text-gray-300">Loading Email Bot System...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white p-6">
            {/* Header */}
            <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-lg">
                            <Mail className="w-8 h-8" />
                        </div>
                        <div>
                            <h1 className="text-4xl font-bold">📧 Email Bot System</h1>
                            <p className="text-gray-400 mt-1">Intelligent email routing and automated bot processing</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${wsConnected ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'}`}>
                            <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
                            {wsConnected ? 'Live' : 'Offline'}
                        </div>
                    </div>
                </div>

                {error && (
                    <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg">
                        Error: {error}
                    </div>
                )}
            </div>

            {/* Stats Cards */}
            {stats && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <div className="bg-gradient-to-br from-blue-900 to-blue-800 p-6 rounded-lg border border-blue-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-blue-200 text-sm font-medium">Total Processed</p>
                                <p className="text-3xl font-bold mt-2">{stats.total_processed || 0}</p>
                            </div>
                            <Zap className="w-8 h-8 text-blue-400 opacity-50" />
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-green-900 to-green-800 p-6 rounded-lg border border-green-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-green-200 text-sm font-medium">Successful</p>
                                <p className="text-3xl font-bold mt-2">{stats.successful || 0}</p>
                            </div>
                            <CheckCircle className="w-8 h-8 text-green-400 opacity-50" />
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-yellow-900 to-yellow-800 p-6 rounded-lg border border-yellow-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-yellow-200 text-sm font-medium">Pending</p>
                                <p className="text-3xl font-bold mt-2">{stats.pending || 0}</p>
                            </div>
                            <Clock className="w-8 h-8 text-yellow-400 opacity-50" />
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-red-900 to-red-800 p-6 rounded-lg border border-red-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-red-200 text-sm font-medium">Failed</p>
                                <p className="text-3xl font-bold mt-2">{stats.failed || 0}</p>
                            </div>
                            <AlertCircle className="w-8 h-8 text-red-400 opacity-50" />
                        </div>
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="mb-6 border-b border-gray-700">
                <div className="flex gap-4">
                    {['overview', 'mappings', 'history', 'performance'].map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-4 py-3 font-medium border-b-2 transition-colors ${activeTab === tab
                                ? 'text-blue-400 border-blue-400'
                                : 'text-gray-400 border-transparent hover:text-gray-200'
                                }`}
                        >
                            {tab.charAt(0).toUpperCase() + tab.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            {/* Tab Content */}
            <div>
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Success Rate Chart */}
                        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                                <TrendingUp className="w-5 h-5 text-blue-400" />
                                Success Rate Over Time
                            </h3>
                            {history.length > 0 ? (
                                <ResponsiveContainer width="100%" height={300}>
                                    <AreaChart data={history.slice(-20).reverse()}>
                                        <defs>
                                            <linearGradient id="colorSuccess" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                                                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#404040" />
                                        <XAxis dataKey="timestamp" stroke="#808080" />
                                        <YAxis stroke="#808080" />
                                        <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} />
                                        <Area type="monotone" dataKey="success_rate" stroke="#10b981" fillOpacity={1} fill="url(#colorSuccess)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            ) : (
                                <p className="text-gray-400 text-center py-8">No data available</p>
                            )}
                        </div>

                        {/* Bot Performance */}
                        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                                <Bot className="w-5 h-5 text-purple-400" />
                                Bot Performance Distribution
                            </h3>
                            {Object.keys(botStats).length > 0 ? (
                                <ResponsiveContainer width="100%" height={300}>
                                    <PieChart>
                                        <Pie
                                            data={Object.entries(botStats).map(([bot, count]) => ({
                                                name: bot,
                                                value: count
                                            }))}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={60}
                                            outerRadius={100}
                                            paddingAngle={2}
                                            dataKey="value"
                                        >
                                            {Object.keys(botStats).map((_, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} />
                                    </PieChart>
                                </ResponsiveContainer>
                            ) : (
                                <p className="text-gray-400 text-center py-8">No performance data</p>
                            )}
                        </div>
                    </div>
                )}

                {/* Mappings Tab */}
                {activeTab === 'mappings' && (
                    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                            <Mail className="w-5 h-5 text-blue-400" />
                            Email to Bot Mappings
                        </h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="border-b border-gray-600">
                                    <tr>
                                        <th className="text-left py-3 px-4">Email Pattern</th>
                                        <th className="text-left py-3 px-4">Assigned Bot</th>
                                        <th className="text-left py-3 px-4">Workflow</th>
                                        <th className="text-left py-3 px-4">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {mappings.map((mapping, idx) => (
                                        <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700/50 transition-colors">
                                            <td className="py-3 px-4 font-mono text-blue-400">{mapping.email_pattern}</td>
                                            <td className="py-3 px-4">{mapping.bot_name}</td>
                                            <td className="py-3 px-4 text-gray-400">{mapping.workflow || '-'}</td>
                                            <td className="py-3 px-4">
                                                <span className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-green-900/50 text-green-400">
                                                    <CheckCircle className="w-3 h-3" />
                                                    Active
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {mappings.length === 0 && (
                                <p className="text-center text-gray-400 py-8">No email mappings configured</p>
                            )}
                        </div>
                    </div>
                )}

                {/* History Tab */}
                {activeTab === 'history' && (
                    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                            <MessageSquare className="w-5 h-5 text-green-400" />
                            Execution History
                        </h3>
                        <div className="space-y-3 max-h-96 overflow-y-auto">
                            {history.map((exec, idx) => (
                                <div
                                    key={idx}
                                    onClick={() => setSelectedEmail(exec)}
                                    className="bg-gray-700/50 p-4 rounded-lg border border-gray-600 hover:border-blue-500 hover:bg-gray-700 transition-all cursor-pointer"
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <p className="font-medium text-blue-300">{exec.email_from || 'Unknown'}</p>
                                            <p className="text-sm text-gray-400 mt-1">{exec.subject || 'No Subject'}</p>
                                            <div className="flex items-center gap-3 mt-2">
                                                <span className="text-xs bg-blue-900/50 text-blue-300 px-2 py-1 rounded">
                                                    {exec.bot_name || 'N/A'}
                                                </span>
                                                <span className={`text-xs px-2 py-1 rounded ${exec.status === 'success'
                                                    ? 'bg-green-900/50 text-green-300'
                                                    : exec.status === 'pending'
                                                        ? 'bg-yellow-900/50 text-yellow-300'
                                                        : 'bg-red-900/50 text-red-300'
                                                    }`}>
                                                    {(exec.status || 'unknown').toUpperCase()}
                                                </span>
                                            </div>
                                        </div>
                                        <p className="text-xs text-gray-500 whitespace-nowrap ml-4">
                                            {exec.timestamp ? new Date(exec.timestamp).toLocaleTimeString() : '-'}
                                        </p>
                                    </div>
                                </div>
                            ))}
                            {history.length === 0 && (
                                <p className="text-center text-gray-400 py-8">No execution history</p>
                            )}
                        </div>
                    </div>
                )}

                {/* Performance Tab */}
                {activeTab === 'performance' && (
                    <div className="space-y-6">
                        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                            <h3 className="text-xl font-bold mb-4">Processing Rate</h3>
                            {stats && history.length > 0 ? (
                                <ResponsiveContainer width="100%" height={300}>
                                    <BarChart data={history.slice(-10).reverse()}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#404040" />
                                        <XAxis dataKey="timestamp" stroke="#808080" />
                                        <YAxis stroke="#808080" />
                                        <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} />
                                        <Legend />
                                        <Bar dataKey="processed_count" fill="#3b82f6" name="Processed" />
                                        <Bar dataKey="success_count" fill="#10b981" name="Successful" />
                                        <Bar dataKey="error_count" fill="#ef4444" name="Failed" />
                                    </BarChart>
                                </ResponsiveContainer>
                            ) : (
                                <p className="text-gray-400 text-center py-8">No performance data</p>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Email Detail Modal */}
            {selectedEmail && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-gray-800 rounded-lg max-w-2xl w-full max-h-96 overflow-y-auto border border-gray-700">
                        <div className="bg-gray-700 p-4 border-b border-gray-600 flex items-center justify-between sticky top-0">
                            <h3 className="text-xl font-bold flex items-center gap-2">
                                <Mail className="w-5 h-5 text-blue-400" />
                                Email Details
                            </h3>
                            <button
                                onClick={() => setSelectedEmail(null)}
                                className="text-gray-400 hover:text-white text-2xl"
                            >
                                ×
                            </button>
                        </div>
                        <div className="p-4 space-y-3">
                            <div>
                                <p className="text-xs text-gray-400 uppercase font-bold">From</p>
                                <p className="text-white">{selectedEmail.email_from || 'Unknown'}</p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-400 uppercase font-bold">Subject</p>
                                <p className="text-white">{selectedEmail.subject || 'No Subject'}</p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-400 uppercase font-bold">Bot</p>
                                <p className="text-white">{selectedEmail.bot_name || 'N/A'}</p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-400 uppercase font-bold">Status</p>
                                <p className="text-white">{(selectedEmail.status || 'unknown').toUpperCase()}</p>
                            </div>
                            {selectedEmail.response && (
                                <div>
                                    <p className="text-xs text-gray-400 uppercase font-bold">Response</p>
                                    <p className="text-gray-300 bg-gray-900 p-2 rounded text-sm">{selectedEmail.response}</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
