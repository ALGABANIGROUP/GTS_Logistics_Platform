import React, { useState, useEffect, useCallback, useRef } from "react";
import axiosClient from "../../api/axiosClient";
import {
    AlertCircle,
    Play,
    Pause,
    RefreshCw,
    Send,
    CheckCircle,
    Clock,
    Users,
    TrendingUp,
    Zap,
    Settings,
    Plus,
    X,
    Eye,
    Edit,
    Trash2,
    BarChart3,
    Activity,
    Target,
    Shield,
    FileText,
    Truck,
    UserCheck,
    Briefcase,
    Wrench,
    Brain,
    Handshake,
    AlertTriangle,
    Info,
    ChevronDown,
    ChevronUp
} from "lucide-react";

const APPROVED_BOT_CATALOG = {
    customer_service: {
        name: "AI Customer Service",
        description: "Customer support and request intake.",
        department: "frontend",
        icon: "CS",
        priority: 80
    },
    documents_manager: {
        name: "AI Documents Manager",
        description: "Document processing and compliance workflows.",
        department: "operations",
        icon: "DOC",
        priority: 72
    },
    general_manager: {
        name: "AI General Manager",
        description: "Executive oversight and strategic reporting.",
        department: "management",
        icon: "GM",
        priority: 95
    },
    information_coordinator: {
        name: "AI Information Coordinator",
        description: "Knowledge routing and intelligence coordination.",
        department: "ai",
        icon: "IC",
        priority: 85
    },
    intelligence_bot: {
        name: "AI Intelligence Bot",
        description: "Strategic analysis and executive insights.",
        department: "executive",
        icon: "INT",
        priority: 92
    },
    finance_bot: {
        name: "AI Finance Bot",
        description: "Billing, revenue tracking, and financial reporting.",
        department: "finance",
        icon: "FIN",
        priority: 90
    },
    legal_bot: {
        name: "AI Legal Consultant",
        description: "Legal review and compliance guidance.",
        department: "legal",
        icon: "LAW",
        priority: 76
    },
    maintenance_dev: {
        name: "AI Maintenance Dev",
        description: "System maintenance and health checks.",
        department: "tech",
        icon: "DEV",
        priority: 60
    },
    mapleload_bot: {
        name: "AI MapleLoad Canada",
        description: "Canadian market intelligence and load matching.",
        department: "operations",
        icon: "MLC",
        priority: 70
    },
    operations_manager_bot: {
        name: "AI Operations Manager",
        description: "Operational workflow coordination.",
        department: "operations",
        icon: "OPS",
        priority: 88
    },
    safety_manager_bot: {
        name: "AI Safety Manager",
        description: "Safety compliance and incident tracking.",
        department: "quality",
        icon: "SAFE",
        priority: 74
    },
    sales_bot: {
        name: "AI Sales Bot",
        description: "Sales analytics and pipeline support.",
        department: "sales",
        icon: "SAL",
        priority: 68
    },
    marketing_manager: {
        name: "AI Marketing Manager",
        description: "Marketing campaign automation and lead optimization.",
        department: "marketing",
        icon: "MKT",
        priority: 66
    },
    partner_manager: {
        name: "AI Partner Manager",
        description: "Partner ecosystem governance and strategic alliance workflows.",
        department: "management",
        icon: "PRT",
        priority: 64
    },
    security_manager_bot: {
        name: "AI Security Manager",
        description: "Security monitoring and threat response.",
        department: "security",
        icon: "SEC",
        priority: 82
    },
    system_manager_bot: {
        name: "AI System Manager",
        description: "System health monitoring and optimization.",
        department: "admin",
        icon: "SYS",
        priority: 84
    },
    ai_dispatcher: {
        name: "AI Dispatcher",
        description: "Intelligent task distribution and routing.",
        department: "ai",
        icon: "AID",
        priority: 86
    },
    trainer_bot: {
        name: "AI Trainer Bot",
        description: "Training and simulation orchestration for bot readiness.",
        department: "training",
        icon: "TRN",
        priority: 78
    }
};

const APPROVED_BOT_IDS = Object.keys(APPROVED_BOT_CATALOG);

const BOT_ALIASES = {
    operations_bot: "operations_manager_bot",
    operations_manager: "operations_manager_bot",
    operations_manager_bot: "operations_manager_bot",
    system_bot: "system_manager_bot",
    system_manager: "system_manager_bot",
    system_admin: "system_manager_bot",
    security_bot: "security_manager_bot",
    security_manager: "security_manager_bot",
    security_manager_bot: "security_manager_bot",
    safety_bot: "safety_manager_bot",
    safety_manager: "safety_manager_bot",
    safety_manager_bot: "safety_manager_bot",
    mapleload: "mapleload_bot",
    mapleload_canada: "mapleload_bot",
    mapleload_bot: "mapleload_bot",
    legal_consultant: "legal_bot",
    legal_counsel: "legal_bot",
    legal_bot: "legal_bot",
    sales_team: "sales_bot",
    sales: "sales_bot",
    sales_bot: "sales_bot",
    finance: "finance_bot",
    finance_bot: "finance_bot",
    marketing: "marketing_manager",
    marketing_bot: "marketing_manager",
    marketing_manager: "marketing_manager",
    partner: "partner_manager",
    partner_bot: "partner_manager",
    partner_manager: "partner_manager",
    executive_intelligence: "intelligence_bot",
    intelligence_bot: "intelligence_bot",
    information_coordinator: "information_coordinator",
    general_manager: "general_manager",
    documents_manager: "documents_manager",
    customer_service: "customer_service",
    maintenance_dev: "maintenance_dev",
    dev_maintenance: "maintenance_dev",
    ai_dispatcher: "ai_dispatcher",
    trainer_bot: "trainer_bot",
    trainer: "trainer_bot",
    training_bot: "trainer_bot"
};

const normalizeBotKey = (value) => {
    const raw = String(value || "").trim();
    if (!raw) return "";
    return raw.toLowerCase().replace(/[^a-z0-9_]/g, "_");
};

const resolveBotKey = (value) => {
    const normalized = normalizeBotKey(value);
    if (!normalized) return "";
    const canonical = BOT_ALIASES[normalized] || normalized;
    return APPROVED_BOT_CATALOG[canonical] ? canonical : "";
};

const OrchestrationDashboard = () => {
    // State management
    const [bots, setBots] = useState([]);
    const [workflows, setWorkflows] = useState([]);
    const [activeOperations, setActiveOperations] = useState([]);
    const [statistics, setStatistics] = useState(null);
    const [loading, setLoading] = useState(false);
    const [operationsError, setOperationsError] = useState(null);
    const [selectedBot, setSelectedBot] = useState(null);
    const [showNewRequestModal, setShowNewRequestModal] = useState(false);
    const [operationFilter, setOperationFilter] = useState('all');
    const [notification, setNotification] = useState(null);
    const [currentTime, setCurrentTime] = useState('');

    // New request form state
    const [newRequest, setNewRequest] = useState({
        type: 'new_customer',
        customerName: '',
        customerContact: '',
        priority: 'normal',
        description: ''
    });

    // Orchestration settings
    const [settings, setSettings] = useState({
        autoEscalation: true,
        notificationLevel: 'high',
        reportFrequency: 'hourly',
        maxConcurrentOperations: 50,
        escalationThreshold: 30
    });

    // WebSocket connection for real-time updates
    const wsRef = useRef(null);
    const subscriptionsRef = useRef(new Set());

    // Load initial data
    useEffect(() => {
        loadDashboardData();
        connectWebSocket();
        updateCurrentTime();

        // Update time every second
        const timeInterval = setInterval(updateCurrentTime, 1000);

        return () => {
            clearInterval(timeInterval);
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    const loadDashboardData = async () => {
        setLoading(true);
        setOperationsError(null);
        try {
            const [botsRes, workflowsRes, operationsRes, statsRes] = await Promise.allSettled([
                axiosClient.get('/api/v1/orchestration/bots'),
                axiosClient.get('/api/v1/orchestration/workflows'),
                axiosClient.get('/api/v1/orchestration/operations/active'),
                axiosClient.get('/api/v1/orchestration/statistics/bots')
            ]);

            if (botsRes.status === 'fulfilled') {
                const payload = botsRes.value.data;
                const list = Array.isArray(payload) ? payload : (payload?.bots || []);
                const normalized = list
                    .map((bot) => {
                        const rawId = bot?.id || bot?.bot_id || bot?.botId || bot?.name;
                        const canonicalId = resolveBotKey(rawId);
                        if (!canonicalId) return null;
                        const catalog = APPROVED_BOT_CATALOG[canonicalId] || {};
                        const priority = Number.isFinite(bot?.priority)
                            ? bot.priority
                            : catalog.priority || 0;
                        return {
                            ...bot,
                            id: canonicalId,
                            name: bot?.name || catalog.name || canonicalId,
                            description: bot?.description || catalog.description || "",
                            department: bot?.department || catalog.department || "operations",
                            icon: bot?.icon || catalog.icon || "AI",
                            priority
                        };
                    })
                    .filter(Boolean);
                setBots(normalized);
            } else {
                console.error('Error loading bots:', botsRes.reason);
                showNotification('Failed to load bots', 'error');
            }

            if (workflowsRes.status === 'fulfilled') {
                setWorkflows(workflowsRes.value.data);
            } else {
                console.error('Error loading workflows:', workflowsRes.reason);
                showNotification('Failed to load workflows', 'error');
            }

            if (operationsRes.status === 'fulfilled') {
                setActiveOperations(operationsRes.value.data.operations || []);
            } else {
                console.error('Error loading active operations:', operationsRes.reason);
                setActiveOperations([]);
                setOperationsError('Failed to load active operations. Please try again later.');
                showNotification('Failed to load active operations', 'error');
            }

            if (statsRes.status === 'fulfilled') {
                setStatistics(statsRes.value.data.statistics);
            } else {
                console.error('Error loading statistics:', statsRes.reason);
                showNotification('Failed to load statistics', 'error');
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            showNotification('Failed to load dashboard data', 'error');
        } finally {
            setLoading(false);
        }
    };

    const connectWebSocket = () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/ws/live`);

        ws.onopen = () => {
            console.log('WebSocket connected for orchestration');
            ws.send(JSON.stringify({ type: "subscribe", channel: "orchestration.*" }));
            subscriptionsRef.current.add("orchestration.*");
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.channel?.startsWith('orchestration.')) {
                    handleRealtimeUpdate(data);
                }
            } catch (e) {
                console.error("WebSocket message parse error:", e);
            }
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected, reconnecting...');
            setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        wsRef.current = ws;
    };

    const handleRealtimeUpdate = (data) => {
        switch (data.type) {
            case 'operation_started':
                loadDashboardData(); // Reload to get updated operations
                showNotification(`New operation started: ${data.operationId}`, 'success');
                break;
            case 'operation_completed':
                loadDashboardData();
                showNotification(`Operation completed: ${data.operationId}`, 'success');
                break;
            case 'operation_escalated':
                loadDashboardData();
                showNotification(`Operation escalated: ${data.operationId}`, 'warning');
                break;
            default:
                break;
        }
    };

    const updateCurrentTime = () => {
        const now = new Date();
        setCurrentTime(now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        }));
    };

    const showNotification = (message, type = 'info') => {
        setNotification({ message, type });
        setTimeout(() => setNotification(null), 5000);
    };

    // Computed values
    const activeBotsCount = bots.filter(bot => bot.status === 'active').length;
    const totalBotsCount = bots.length;
    const approvedBotsCount = APPROVED_BOT_IDS.length;
    const activeOperationsCount = activeOperations.filter(op => op.status === 'active').length;

    const botsByPriority = [...bots].sort((a, b) => b.priority - a.priority);

    const filteredOperations = activeOperations.filter(op => {
        if (operationFilter === 'all') return true;
        return op.status === operationFilter;
    });

    const operationsNeedingAttention = activeOperations.filter(op =>
        op.status === 'stalled' || op.status === 'escalated'
    );

    const botStats = statistics?.botUtilization || {};
    const normalizedBotStats = Object.entries(botStats).reduce((acc, [key, value]) => {
        const canonicalId = resolveBotKey(key);
        if (canonicalId) {
            acc[canonicalId] = value;
        }
        return acc;
    }, {});

    const botUtilizationRate = Object.values(normalizedBotStats).length > 0
        ? Object.values(normalizedBotStats).reduce((sum, stat) => sum + stat.utilization, 0) / Object.values(normalizedBotStats).length
        : 0;

    const averageBotLoad = Object.values(normalizedBotStats).length > 0
        ? Object.values(normalizedBotStats).reduce((sum, stat) => sum + stat.activeOperations, 0) / Object.values(normalizedBotStats).length
        : 0;

    const successRate = statistics
        ? (statistics.totalOperations > 0 ? (statistics.completedToday / statistics.totalOperations) * 100 : 0)
        : 0;

    const topLoadedBots = bots
        .map(bot => ({
            ...bot,
            load: normalizedBotStats[bot.id]?.utilization || 0
        }))
        .sort((a, b) => b.load - a.load)
        .slice(0, 5);

    const suggestedBots = (() => {
        switch (newRequest.type) {
            case 'new_customer':
                return ['customer_service', 'sales_bot', 'legal_bot', 'security_manager_bot'];
            case 'shipping_request':
                return ['operations_manager_bot', 'customer_service', 'legal_bot', 'ai_dispatcher'];
            case 'partner_onboarding':
                return ['operations_manager_bot', 'legal_bot', 'security_manager_bot'];
            default:
                return ['customer_service', 'operations_manager_bot', 'ai_dispatcher'];
        }
    })();

    // Helper functions
    const getDepartmentName = (department) => {
        const departments = {
            frontend: 'Customer Service',
            management: 'Management',
            executive: 'Executive',
            ai: 'AI',
            sales: 'Sales',
            legal: 'Legal',
            operations: 'Operations',
            security: 'Security',
            admin: 'Admin',
            tech: 'Technology',
            partnership: 'Partnership',
            quality: 'Quality'
        };
        return departments[department] || department;
    };

    const getStatusText = (status) => {
        const statuses = {
            active: 'Active',
            inactive: 'Inactive',
            busy: 'Busy',
            maintenance: 'Maintenance',
            error: 'Error'
        };
        return statuses[status] || status;
    };

    const getOperationStatusText = (status) => {
        const statuses = {
            active: 'Active',
            stalled: 'Stalled',
            escalated: 'Escalated',
            completed: 'Completed',
            cancelled: 'Cancelled'
        };
        return statuses[status] || status;
    };

    const getOperationTypeText = (type) => {
        const types = {
            new_customer: 'New Customer',
            shipping_request: 'Shipping Request',
            partner_onboarding: 'Partner Onboarding',
            support_request: 'Support Request',
            complaint: 'Complaint',
            inquiry: 'Inquiry'
        };
        return types[type] || type;
    };

    const getPriorityText = (priority) => {
        const priorities = {
            low: 'Low',
            normal: 'Normal',
            high: 'High',
            urgent: 'Urgent'
        };
        return priorities[priority] || priority;
    };

    const getBotName = (botId) => {
        const canonicalId = resolveBotKey(botId);
        const catalog = APPROVED_BOT_CATALOG[canonicalId];
        const bot = bots.find(b => b.id === canonicalId || b.id === botId);
        return bot?.name || catalog?.name || String(botId || "");
    };

    const getBotIcon = (botId) => {
        const canonicalId = resolveBotKey(botId);
        const catalog = APPROVED_BOT_CATALOG[canonicalId];
        const bot = bots.find(b => b.id === canonicalId || b.id === botId);
        return bot?.icon || catalog?.icon || "AI";
    };

    const getBotById = (botId) => {
        const canonicalId = resolveBotKey(botId);
        return bots.find(b => b.id === canonicalId || b.id === botId);
    };

    const formatTime = (timestamp) => {
        if (!timestamp) return 'Unknown';
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const calculateDuration = (startTime) => {
        if (!startTime) return '0 min';
        const start = new Date(startTime);
        const now = new Date();
        const diff = Math.floor((now - start) / 60000); // minutes
        return `${diff} min`;
    };

    const getProgressColor = (progress) => {
        if (progress < 30) return 'low';
        if (progress < 70) return 'medium';
        return 'high';
    };

    const getLoadColor = (load) => {
        if (load < 50) return 'low';
        if (load < 80) return 'medium';
        return 'high';
    };

    const getCapabilityText = (capability) => {
        const capabilities = {
            reception: 'Reception',
            query_handling: 'Query Handling',
            routing: 'Routing',
            coordination: 'Coordination',
            monitoring: 'Monitoring',
            reporting: 'Reporting',
            escalation: 'Escalation',
            oversight: 'Oversight',
            decision_making: 'Decision Making',
            strategic_planning: 'Strategic Planning',
            intelligent_routing: 'Intelligent Routing',
            load_balancing: 'Load Balancing',
            priority_management: 'Priority Management',
            order_processing: 'Order Processing',
            quotation: 'Quotation',
            customer_followup: 'Customer Followup',
            contract_review: 'Contract Review',
            compliance_check: 'Compliance Check',
            legal_advice: 'Legal Advice',
            shipping: 'Shipping',
            logistics: 'Logistics',
            tracking: 'Tracking',
            security_check: 'Security Check',
            fraud_detection: 'Fraud Detection',
            access_control: 'Access Control',
            document_management: 'Document Management',
            archiving: 'Archiving',
            version_control: 'Version Control',
            system_maintenance: 'System Maintenance',
            updates: 'Updates',
            bug_fixes: 'Bug Fixes',
            data_analysis: 'Data Analysis',
            intelligence: 'Intelligence',
            partner_management: 'Partner Management',
            collaboration: 'Collaboration',
            safety_checks: 'Safety Checks',
            quality_control: 'Quality Control',
            system_monitoring: 'System Monitoring',
            performance: 'Performance',
            alerts: 'Alerts'
        };
        return capabilities[capability] || capability;
    };

    // Action handlers
    const startWorkflow = async (workflow) => {
        try {
            const operationData = {
                type: workflow.id,
                name: `Operation ${workflow.name}`,
                description: workflow.description,
                priority: 'normal',
                estimatedTime: workflow.estimatedTime
            };

            const response = await axiosClient.post('/api/v1/orchestration/operations', operationData);
            showNotification(`Started operation ${workflow.name} successfully`, 'success');
            loadDashboardData();
        } catch (error) {
            console.error('Error starting workflow:', error);
            showNotification('Failed to start workflow', 'error');
        }
    };

    const updateOperationStatus = async (operationId, updates) => {
        try {
            await axiosClient.put(`/api/v1/orchestration/operations/${operationId}`, updates);
            showNotification('Operation updated successfully', 'success');
            loadDashboardData();
        } catch (error) {
            console.error('Error updating operation:', error);
            showNotification('Failed to update operation', 'error');
        }
    };

    const pauseOperation = (operation) => {
        updateOperationStatus(operation.id, { status: 'stalled' });
    };

    const resumeOperation = (operation) => {
        updateOperationStatus(operation.id, { status: 'active' });
    };

    const completeOperation = (operation) => {
        updateOperationStatus(operation.id, {
            status: 'completed',
            progress: 100,
            completedAt: new Date().toISOString()
        });
    };

    const escalateOperation = (operation) => {
        updateOperationStatus(operation.id, { status: 'escalated' });
    };

    const refreshBotsStatus = async () => {
        // Simulate refreshing bot statuses
        setLoading(true);
        setTimeout(() => {
            loadDashboardData();
            showNotification('Bot statuses refreshed', 'success');
        }, 1000);
    };

    const generateHourlyReport = async () => {
        try {
            const response = await axiosClient.post('/api/v1/orchestration/reports', {
                type: 'hourly_report',
                data: statistics
            });
            showNotification(`Generated hourly report: ${response.data.report.id}`, 'success');
        } catch (error) {
            console.error('Error generating report:', error);
            showNotification('Failed to generate report', 'error');
        }
    };

    const submitNewRequest = async () => {
        if (!newRequest.customerName.trim()) {
            showNotification('Customer name is required', 'error');
            return;
        }

        try {
            const operationData = {
                type: newRequest.type,
                name: `Request: ${newRequest.customerName}`,
                description: newRequest.description,
                priority: newRequest.priority,
                customerName: newRequest.customerName,
                customerContact: newRequest.customerContact
            };

            await axiosClient.post('/api/v1/orchestration/operations', operationData);

            // Reset form
            setNewRequest({
                type: 'new_customer',
                customerName: '',
                customerContact: '',
                priority: 'normal',
                description: ''
            });

            setShowNewRequestModal(false);
            showNotification('Request submitted successfully', 'success');
            loadDashboardData();
        } catch (error) {
            console.error('Error submitting request:', error);
            showNotification('Failed to submit request', 'error');
        }
    };

    const clearCompletedOperations = () => {
        setActiveOperations(prev => prev.filter(op => op.status !== 'completed'));
        showNotification('Completed operations cleared', 'success');
    };

    if (loading && bots.length === 0) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="orchestration-dashboard p-6 bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
            {/* Header */}
            <div className="dashboard-header bg-white rounded-3xl p-8 mb-8 shadow-xl border border-white/50 backdrop-blur-sm">
                <div className="header-main flex items-center gap-6">
                    <div className="header-icon text-6xl bg-gradient-to-br from-indigo-600 to-slate-800 w-24 h-24 rounded-full flex items-center justify-center text-white shadow-lg">
                        🎯
                    </div>
                    <div>
                        <h1 className="text-4xl font-black bg-gradient-to-r from-indigo-600 to-slate-800 bg-clip-text text-transparent mb-2">
                            AI Orchestration System
                        </h1>
                        <p className="text-xl text-slate-600 font-semibold">
                            Intelligent coordination between {approvedBotsCount} specialized bots
                        </p>
                        <div className="system-status flex gap-4 mt-4 flex-wrap">
                            <span className="status-badge active px-4 py-2 bg-green-100 text-green-800 rounded-full font-bold text-sm uppercase tracking-wide">
                                ✅ System Active
                            </span>
                            <span className="bots-count px-4 py-2 bg-slate-100 text-slate-700 rounded-full font-bold text-sm">
                                {activeBotsCount} Active Bots
                            </span>
                            <span className="operations-count px-4 py-2 bg-blue-100 text-blue-800 rounded-full font-bold text-sm">
                                {activeOperationsCount} Active Operations
                            </span>
                        </div>
                    </div>
                </div>

                <div className="header-actions flex gap-4 items-center mt-6">
                    <button
                        className="emergency-btn px-6 py-3 bg-red-600 text-white rounded-xl font-bold text-lg flex items-center gap-2 hover:bg-red-700 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                        onClick={() => showNotification('Emergency mode activated', 'warning')}
                    >
                        🚨 Emergency Mode
                    </button>
                    <button
                        className="report-btn px-6 py-3 bg-blue-600 text-white rounded-xl font-bold text-lg flex items-center gap-2 hover:bg-blue-700 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                        onClick={generateHourlyReport}
                    >
                        📊 Hourly Report
                    </button>
                    <div className="system-time flex items-center gap-2 px-4 py-2 bg-slate-50 rounded-xl border-2 border-slate-200">
                        <Clock className="w-5 h-5 text-slate-600" />
                        <span className="time-text font-mono text-lg font-bold text-slate-800">{currentTime}</span>
                    </div>
                </div>
            </div>

            {/* Main Grid */}
            <div className="dashboard-grid grid grid-cols-1 xl:grid-cols-5 gap-8">
                {/* Left Column */}
                <div className="dashboard-column xl:col-span-3 space-y-8">
                    {/* Bots Overview */}
                    <div className="card bots-overview-card bg-white rounded-3xl p-8 shadow-xl border border-white/50">
                        <div className="card-header flex justify-between items-center mb-6">
                            <h3 className="text-2xl font-black text-slate-800 flex items-center gap-2">
                                🤖 Bots Overview
                            </h3>
                            <div className="card-actions flex gap-2">
                                <button
                                    className="refresh-btn px-4 py-2 bg-slate-100 text-slate-700 rounded-lg font-semibold flex items-center gap-2 hover:bg-slate-200 transition-colors"
                                    onClick={refreshBotsStatus}
                                >
                                    <RefreshCw className="w-4 h-4" />
                                    Refresh
                                </button>
                                <button
                                    className="all-bots-btn px-4 py-2 bg-indigo-100 text-indigo-700 rounded-lg font-semibold flex items-center gap-2 hover:bg-indigo-200 transition-colors"
                                    onClick={() => showNotification('View all bots', 'info')}
                                >
                                    <Eye className="w-4 h-4" />
                                    View All
                                </button>
                            </div>
                        </div>

                        <div className="bots-grid grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                            {botsByPriority.map((bot) => (
                                <div
                                    key={bot.id}
                                    className={`bot-card p-4 bg-slate-50 rounded-xl border-2 border-slate-200 cursor-pointer transition-all hover:border-indigo-300 hover:bg-white hover:shadow-lg ${bot.status === 'active' ? 'border-l-4 border-l-green-500' : ''}`}
                                    onClick={() => setSelectedBot(bot)}
                                >
                                    <div className="bot-icon text-3xl mb-3">{bot.icon}</div>
                                    <div className="bot-info">
                                        <h4 className="font-bold text-slate-800 mb-1">{bot.name}</h4>
                                        <p className="text-slate-600 text-sm mb-3 leading-relaxed">{bot.description}</p>
                                        <div className="bot-meta flex justify-between items-center text-xs">
                                            <span className="bot-department bg-slate-200 text-slate-700 px-2 py-1 rounded-full">
                                                {getDepartmentName(bot.department)}
                                            </span>
                                            <span className="bot-priority bg-red-100 text-red-700 px-2 py-1 rounded-full font-bold">
                                                🔝 {bot.priority}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="bot-status-indicator flex items-center justify-between mt-3">
                                        <div className={`status-dot w-3 h-3 rounded-full ${bot.status === 'active' ? 'bg-green-500' : 'bg-slate-400'}`}></div>
                                        <span className="status-text text-xs font-semibold text-slate-600">{getStatusText(bot.status)}</span>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="bots-summary grid grid-cols-3 gap-4 pt-4 border-t border-slate-200">
                            <div className="summary-item text-center p-4 bg-slate-50 rounded-lg">
                                <div className="summary-label text-slate-600 font-semibold mb-1">Active Bots</div>
                                <div className="summary-value text-3xl font-black text-indigo-600">{activeBotsCount}/{totalBotsCount}</div>
                            </div>
                            <div className="summary-item text-center p-4 bg-slate-50 rounded-lg">
                                <div className="summary-label text-slate-600 font-semibold mb-1">Utilization</div>
                                <div className="summary-value text-3xl font-black text-green-600">{Math.round(botUtilizationRate)}%</div>
                            </div>
                            <div className="summary-item text-center p-4 bg-slate-50 rounded-lg">
                                <div className="summary-label text-slate-600 font-semibold mb-1">Avg Load</div>
                                <div className="summary-value text-3xl font-black text-orange-600">{Math.round(averageBotLoad)}/10</div>
                            </div>
                        </div>
                    </div>

                    {/* Workflows */}
                    <div className="card workflows-card bg-white rounded-3xl p-8 shadow-xl border border-white/50">
                        <div className="card-header flex justify-between items-center mb-6">
                            <h3 className="text-2xl font-black text-slate-800 flex items-center gap-2">
                                🔄 Workflows
                            </h3>
                            <button
                                className="new-workflow-btn px-4 py-2 bg-green-600 text-white rounded-lg font-semibold flex items-center gap-2 hover:bg-green-700 transition-colors"
                                onClick={() => showNotification('Create new workflow', 'info')}
                            >
                                <Plus className="w-4 h-4" />
                                New Workflow
                            </button>
                        </div>

                        <div className="workflows-list space-y-4">
                            {workflows.map((workflow) => (
                                <div key={workflow.id} className="workflow-item bg-slate-50 rounded-xl p-6 border-2 border-slate-200 hover:border-indigo-300 transition-colors">
                                    <div className="workflow-header flex justify-between items-center mb-4">
                                        <span className="workflow-name font-bold text-lg text-slate-800">{workflow.name}</span>
                                        <span className="workflow-time bg-slate-200 text-slate-700 px-3 py-1 rounded-full font-semibold">
                                            {workflow.estimatedTime} min
                                        </span>
                                    </div>
                                    <div className="workflow-description text-slate-600 mb-4">{workflow.description}</div>
                                    <div className="workflow-steps bg-white rounded-lg p-4 mb-4 border border-slate-200">
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                                            {workflow.steps.map((step, index) => (
                                                <div key={index} className="workflow-step flex items-center gap-2 p-2 bg-slate-50 rounded">
                                                    <span className="step-number w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                                                        {index + 1}
                                                    </span>
                                                    <span className="step-bot font-semibold text-slate-700">{getBotName(step.bot)}</span>
                                                    <span className="step-duration bg-slate-200 text-slate-600 px-2 py-1 rounded text-xs">
                                                        {step.duration}min
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                    <div className="workflow-actions flex justify-end">
                                        <button
                                            className="start-btn px-6 py-2 bg-indigo-600 text-white rounded-lg font-semibold flex items-center gap-2 hover:bg-indigo-700 transition-all shadow-md hover:shadow-lg transform hover:-translate-y-1"
                                            onClick={() => startWorkflow(workflow)}
                                        >
                                            <Play className="w-4 h-4" />
                                            Start Execution
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* New Requests */}
                    <div className="card new-requests-card bg-white rounded-3xl p-8 shadow-xl border border-white/50">
                        <div className="card-header flex justify-between items-center mb-6">
                            <h3 className="text-2xl font-black text-slate-800 flex items-center gap-2">
                                🆕 New Requests
                            </h3>
                            <button
                                className="add-request-btn px-4 py-2 bg-green-600 text-white rounded-lg font-semibold flex items-center gap-2 hover:bg-green-700 transition-colors"
                                onClick={() => setShowNewRequestModal(true)}
                            >
                                <Plus className="w-4 h-4" />
                                New Request
                            </button>
                        </div>

                        <div className="requests-list space-y-4">
                            {activeOperations.filter(op => op.status === 'active').slice(0, 3).map((request) => (
                                <div key={request.id} className="request-item bg-slate-50 rounded-xl p-6 border-l-4 border-l-blue-500">
                                    <div className="request-header flex justify-between items-center mb-3">
                                        <span className="request-type font-bold text-slate-800">{getOperationTypeText(request.type)}</span>
                                        <span className={`request-priority px-3 py-1 rounded-full text-xs font-bold uppercase ${request.priority === 'urgent' ? 'bg-red-100 text-red-800' :
                                            request.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                                                'bg-blue-100 text-blue-800'
                                            }`}>
                                            {getPriorityText(request.priority)}
                                        </span>
                                    </div>
                                    <div className="request-content mb-4">
                                        <div className="request-details text-slate-700 mb-1">
                                            <strong>Customer:</strong> {request.customerName || 'N/A'}
                                        </div>
                                        {request.description && (
                                            <div className="request-details text-slate-600 text-sm">
                                                {request.description}
                                            </div>
                                        )}
                                    </div>
                                    <div className="request-actions flex gap-2">
                                        <button className="assign-btn px-4 py-2 bg-green-600 text-white rounded-lg font-semibold text-sm hover:bg-green-700 transition-colors">
                                            👤 Assign
                                        </button>
                                        <button className="reject-btn px-4 py-2 bg-slate-200 text-slate-700 rounded-lg font-semibold text-sm hover:bg-slate-300 transition-colors">
                                            ❌ Reject
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {activeOperations.filter(op => op.status === 'active').length === 0 && (
                            <div className="empty-requests text-center py-12">
                                <div className="empty-icon text-6xl text-slate-300 mb-4">📭</div>
                                <p className="text-slate-500 text-lg">No active requests</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Column */}
                <div className="dashboard-column xl:col-span-2 space-y-8">
                    {/* Active Operations */}
                    <div className="card active-operations-card bg-white rounded-3xl p-8 shadow-xl border border-white/50">
                        <div className="card-header flex justify-between items-center mb-6">
                            <h3 className="text-2xl font-black text-slate-800 flex items-center gap-2">
                                ⚡ Active Operations
                            </h3>
                            <div className="operations-filters flex gap-2">
                                <select
                                    className="filter-select px-3 py-2 bg-slate-100 text-slate-700 rounded-lg border-0 font-semibold"
                                    value={operationFilter}
                                    onChange={(e) => setOperationFilter(e.target.value)}
                                >
                                    <option value="all">All</option>
                                    <option value="active">Active</option>
                                    <option value="stalled">Stalled</option>
                                    <option value="escalated">Escalated</option>
                                    <option value="completed">Completed</option>
                                </select>
                                <button
                                    className="clear-completed-btn px-3 py-2 bg-slate-100 text-slate-700 rounded-lg font-semibold hover:bg-slate-200 transition-colors"
                                    onClick={clearCompletedOperations}
                                >
                                    🗑️ Clear
                                </button>
                            </div>
                        </div>

                        <div className="operations-list space-y-4 max-h-96 overflow-y-auto">
                            {operationsError && (
                                <div className="bg-red-50 text-red-700 border border-red-200 rounded-lg px-4 py-3">
                                    {operationsError}
                                </div>
                            )}
                            {filteredOperations.map((operation) => (
                                <div key={operation.id} className={`operation-item bg-slate-50 rounded-xl p-6 border-l-4 ${operation.status === 'active' ? 'border-l-green-500' :
                                    operation.status === 'stalled' ? 'border-l-orange-500' :
                                        operation.status === 'escalated' ? 'border-l-red-500' :
                                            'border-l-purple-500'
                                    }`}>
                                    <div className="operation-header flex justify-between items-center mb-4">
                                        <div className="operation-id font-mono text-sm font-bold text-slate-800 bg-white px-3 py-1 rounded border">
                                            {operation.id}
                                        </div>
                                        <div className={`operation-status px-3 py-1 rounded-full text-xs font-bold uppercase ${operation.status === 'active' ? 'bg-green-100 text-green-800' :
                                            operation.status === 'stalled' ? 'bg-orange-100 text-orange-800' :
                                                operation.status === 'escalated' ? 'bg-red-100 text-red-800' :
                                                    'bg-purple-100 text-purple-800'
                                            }`}>
                                            {getOperationStatusText(operation.status)}
                                        </div>
                                    </div>

                                    <div className="operation-details bg-white rounded-lg p-4 mb-4 border border-slate-200">
                                        <div className="detail-row flex justify-between mb-2">
                                            <span className="detail-label font-semibold text-slate-700">Type:</span>
                                            <span className="detail-value text-slate-800">{getOperationTypeText(operation.type)}</span>
                                        </div>
                                        <div className="detail-row flex justify-between mb-2">
                                            <span className="detail-label font-semibold text-slate-700">Started:</span>
                                            <span className="detail-value text-slate-600">{formatTime(operation.startTime)}</span>
                                        </div>
                                        <div className="detail-row flex justify-between mb-2">
                                            <span className="detail-label font-semibold text-slate-700">Duration:</span>
                                            <span className="detail-value text-slate-600">{calculateDuration(operation.startTime)}</span>
                                        </div>
                                        <div className="detail-row mb-2">
                                            <span className="detail-label font-semibold text-slate-700 block mb-2">Assigned Bots:</span>
                                            <div className="assigned-bots flex flex-wrap gap-2">
                                                {operation.assignedBots?.map((botId) => (
                                                    <span
                                                        key={botId}
                                                        className="bot-tag bg-slate-100 text-slate-700 px-3 py-1 rounded-full text-sm font-semibold cursor-pointer hover:bg-slate-200 transition-colors"
                                                        onClick={() => setSelectedBot(getBotById(botId))}
                                                    >
                                                        {getBotIcon(botId)} {getBotName(botId)}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="operation-progress mb-4">
                                        <div className="progress-label flex justify-between items-center mb-2">
                                            <span className="font-semibold text-slate-700">Progress</span>
                                            <span className="text-slate-600 font-bold">{operation.progress || 0}%</span>
                                        </div>
                                        <div className="progress-bar w-full h-3 bg-slate-200 rounded-full overflow-hidden">
                                            <div
                                                className={`progress-fill h-full rounded-full transition-all duration-500 ${getProgressColor(operation.progress || 0) === 'low' ? 'bg-red-500' :
                                                    getProgressColor(operation.progress || 0) === 'medium' ? 'bg-orange-500' :
                                                        'bg-green-500'
                                                    }`}
                                                style={{ width: `${operation.progress || 0}%` }}
                                            ></div>
                                        </div>
                                    </div>

                                    <div className="operation-actions flex flex-wrap gap-2">
                                        {operation.status === 'active' && (
                                            <>
                                                <button
                                                    className="pause-btn px-3 py-2 bg-orange-100 text-orange-800 rounded-lg font-semibold text-sm hover:bg-orange-200 transition-colors"
                                                    onClick={() => pauseOperation(operation)}
                                                >
                                                    ⏸️ Pause
                                                </button>
                                                <button
                                                    className="complete-btn px-3 py-2 bg-green-100 text-green-800 rounded-lg font-semibold text-sm hover:bg-green-200 transition-colors"
                                                    onClick={() => completeOperation(operation)}
                                                >
                                                    ✅ Complete
                                                </button>
                                            </>
                                        )}
                                        {operation.status === 'stalled' && (
                                            <button
                                                className="resume-btn px-3 py-2 bg-blue-100 text-blue-800 rounded-lg font-semibold text-sm hover:bg-blue-200 transition-colors"
                                                onClick={() => resumeOperation(operation)}
                                            >
                                                ▶️ Resume
                                            </button>
                                        )}
                                        {operation.status !== 'escalated' && (
                                            <button
                                                className="escalate-btn px-3 py-2 bg-red-100 text-red-800 rounded-lg font-semibold text-sm hover:bg-red-200 transition-colors"
                                                onClick={() => escalateOperation(operation)}
                                            >
                                                🚨 Escalate
                                            </button>
                                        )}
                                        <button
                                            className="details-btn px-3 py-2 bg-slate-100 text-slate-700 rounded-lg font-semibold text-sm hover:bg-slate-200 transition-colors"
                                            onClick={() => showNotification(`View details for ${operation.id}`, 'info')}
                                        >
                                            🔍 Details
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {filteredOperations.length === 0 && (
                            <div className="empty-operations text-center py-12">
                                <div className="empty-icon text-6xl text-slate-300 mb-4">📊</div>
                                <p className="text-slate-500 text-lg">No operations found</p>
                            </div>
                        )}
                    </div>

                    {/* System Statistics */}
                    <div className="card statistics-card bg-white rounded-3xl p-8 shadow-xl border border-white/50">
                        <div className="card-header flex justify-between items-center mb-6">
                            <h3 className="text-2xl font-black text-slate-800 flex items-center gap-2">
                                📈 System Statistics
                            </h3>
                            <button
                                className="refresh-stats-btn px-4 py-2 bg-slate-100 text-slate-700 rounded-lg font-semibold flex items-center gap-2 hover:bg-slate-200 transition-colors"
                                onClick={loadDashboardData}
                            >
                                <RefreshCw className="w-4 h-4" />
                                Refresh
                            </button>
                        </div>

                        {statistics && (
                            <>
                                <div className="stats-grid grid grid-cols-2 gap-4 mb-6">
                                    <div className="stat-item bg-slate-50 rounded-lg p-4 text-center">
                                        <div className="stat-icon text-3xl mb-2">📊</div>
                                        <div className="stat-label text-slate-600 font-semibold mb-1">Total Ops</div>
                                        <div className="stat-value text-3xl font-black text-indigo-600">{statistics.totalOperations}</div>
                                    </div>
                                    <div className="stat-item bg-slate-50 rounded-lg p-4 text-center">
                                        <div className="stat-icon text-3xl mb-2">⚡</div>
                                        <div className="stat-label text-slate-600 font-semibold mb-1">Active</div>
                                        <div className="stat-value text-3xl font-black text-green-600">{statistics.activeOperations}</div>
                                    </div>
                                    <div className="stat-item bg-slate-50 rounded-lg p-4 text-center">
                                        <div className="stat-icon text-3xl mb-2">✅</div>
                                        <div className="stat-label text-slate-600 font-semibold mb-1">Completed Today</div>
                                        <div className="stat-value text-3xl font-black text-blue-600">{statistics.completedToday}</div>
                                    </div>
                                    <div className="stat-item bg-slate-50 rounded-lg p-4 text-center">
                                        <div className="stat-icon text-3xl mb-2">⏱️</div>
                                        <div className="stat-label text-slate-600 font-semibold mb-1">Avg Time</div>
                                        <div className="stat-value text-3xl font-black text-orange-600">{Math.round(statistics.averageProcessingTime)}m</div>
                                    </div>
                                    <div className="stat-item bg-slate-50 rounded-lg p-4 text-center">
                                        <div className="stat-icon text-3xl mb-2">🎯</div>
                                        <div className="stat-label text-slate-600 font-semibold mb-1">Success Rate</div>
                                        <div className="stat-value text-3xl font-black text-purple-600">{Math.round(successRate)}%</div>
                                    </div>
                                    <div className="stat-item bg-slate-50 rounded-lg p-4 text-center">
                                        <div className="stat-icon text-3xl mb-2">🚨</div>
                                        <div className="stat-label text-slate-600 font-semibold mb-1">Need Attention</div>
                                        <div className="stat-value text-3xl font-black text-red-600">{operationsNeedingAttention.length}</div>
                                    </div>
                                </div>

                                <div className="charts-section bg-slate-50 rounded-lg p-6">
                                    <h4 className="text-lg font-bold text-slate-800 mb-4 text-center">Bot Load Distribution</h4>
                                    <div className="bot-load-chart space-y-3">
                                        {topLoadedBots.map((bot) => (
                                            <div key={bot.id} className="bot-load-item flex items-center gap-3">
                                                <div className="bot-name font-semibold text-slate-700 min-w-0 flex-1">
                                                    {bot.name}
                                                </div>
                                                <div className="load-bar flex-1 h-4 bg-slate-200 rounded-full overflow-hidden">
                                                    <div
                                                        className={`load-fill h-full rounded-full transition-all duration-500 ${getLoadColor(bot.load) === 'low' ? 'bg-green-500' :
                                                            getLoadColor(bot.load) === 'medium' ? 'bg-orange-500' :
                                                                'bg-red-500'
                                                            }`}
                                                        style={{ width: `${bot.load}%` }}
                                                    ></div>
                                                </div>
                                                <div className="load-value font-bold text-slate-800 w-12 text-right">
                                                    {Math.round(bot.load)}%
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </>
                        )}
                    </div>

                    {/* Orchestration Settings */}
                    <div className="card settings-card bg-white rounded-3xl p-8 shadow-xl border border-white/50">
                        <div className="card-header flex justify-between items-center mb-6">
                            <h3 className="text-2xl font-black text-slate-800 flex items-center gap-2">
                                ⚙️ Orchestration Settings
                            </h3>
                            <button
                                className="save-settings-btn px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold flex items-center gap-2 hover:bg-indigo-700 transition-colors"
                                onClick={() => showNotification('Settings saved', 'success')}
                            >
                                💾 Save
                            </button>
                        </div>

                        <div className="settings-grid space-y-4">
                            <div className="setting-item bg-slate-50 rounded-lg p-4">
                                <label className="setting-label flex items-center gap-2 mb-2 font-semibold text-slate-700">
                                    <input
                                        type="checkbox"
                                        checked={settings.autoEscalation}
                                        onChange={(e) => setSettings({ ...settings, autoEscalation: e.target.checked })}
                                        className="setting-checkbox w-5 h-5"
                                    />
                                    <span className="setting-text">Auto Escalation</span>
                                </label>
                                <div className="setting-description text-slate-600 text-sm">
                                    Automatically escalate stalled operations
                                </div>
                            </div>

                            <div className="setting-item bg-slate-50 rounded-lg p-4">
                                <label className="setting-label block mb-2 font-semibold text-slate-700">
                                    Notification Level
                                </label>
                                <select
                                    value={settings.notificationLevel}
                                    onChange={(e) => setSettings({ ...settings, notificationLevel: e.target.value })}
                                    className="setting-select w-full px-3 py-2 bg-white text-slate-700 rounded-lg border border-slate-300 font-semibold"
                                >
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                    <option value="critical">Critical</option>
                                </select>
                            </div>

                            <div className="setting-item bg-slate-50 rounded-lg p-4">
                                <label className="setting-label block mb-2 font-semibold text-slate-700">
                                    Report Frequency
                                </label>
                                <select
                                    value={settings.reportFrequency}
                                    onChange={(e) => setSettings({ ...settings, reportFrequency: e.target.value })}
                                    className="setting-select w-full px-3 py-2 bg-white text-slate-700 rounded-lg border border-slate-300 font-semibold"
                                >
                                    <option value="hourly">Hourly</option>
                                    <option value="daily">Daily</option>
                                    <option value="weekly">Weekly</option>
                                </select>
                            </div>

                            <div className="setting-item bg-slate-50 rounded-lg p-4">
                                <label className="setting-label block mb-2 font-semibold text-slate-700">
                                    Max Concurrent Operations
                                </label>
                                <input
                                    type="number"
                                    value={settings.maxConcurrentOperations}
                                    onChange={(e) => setSettings({ ...settings, maxConcurrentOperations: parseInt(e.target.value) })}
                                    className="setting-input w-full px-3 py-2 bg-white text-slate-700 rounded-lg border border-slate-300 font-semibold"
                                    min="1"
                                    max="100"
                                />
                            </div>

                            <div className="setting-item bg-slate-50 rounded-lg p-4">
                                <label className="setting-label block mb-2 font-semibold text-slate-700">
                                    Escalation Threshold (minutes)
                                </label>
                                <input
                                    type="number"
                                    value={settings.escalationThreshold}
                                    onChange={(e) => setSettings({ ...settings, escalationThreshold: parseInt(e.target.value) })}
                                    className="setting-input w-full px-3 py-2 bg-white text-slate-700 rounded-lg border border-slate-300 font-semibold"
                                    min="5"
                                    max="120"
                                />
                            </div>
                        </div>

                        <div className="settings-note bg-amber-50 rounded-lg p-4 mt-6 border border-amber-200">
                            <div className="note-icon text-2xl mb-2">💡</div>
                            <div className="note-content text-amber-800 text-sm">
                                <strong>Note:</strong> Settings changes affect all new operations.
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bot Details Modal */}
            {selectedBot && (
                <div className="bot-details-modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="modal-content bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="modal-header bg-gradient-to-r from-indigo-600 to-slate-800 text-white p-6 rounded-t-3xl flex justify-between items-center">
                            <h3 className="text-2xl font-black">🤖 {selectedBot.name}</h3>
                            <button
                                onClick={() => setSelectedBot(null)}
                                className="close-modal-btn w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center text-white hover:bg-opacity-30 transition-colors"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="modal-body p-6">
                            <div className="bot-details space-y-6">
                                <div className="detail-section bg-slate-50 rounded-lg p-6">
                                    <h4 className="text-lg font-bold text-slate-800 mb-4 border-b border-slate-200 pb-2">📋 Basic Information</h4>
                                    <div className="detail-grid grid grid-cols-2 gap-4">
                                        <div className="detail-item">
                                            <span className="detail-label block text-slate-600 font-semibold mb-1">ID:</span>
                                            <span className="detail-value text-slate-800 font-bold">{selectedBot.id}</span>
                                        </div>
                                        <div className="detail-item">
                                            <span className="detail-label block text-slate-600 font-semibold mb-1">Department:</span>
                                            <span className="detail-value text-slate-800 font-bold">{getDepartmentName(selectedBot.department)}</span>
                                        </div>
                                        <div className="detail-item">
                                            <span className="detail-label block text-slate-600 font-semibold mb-1">Priority:</span>
                                            <span className="detail-value text-slate-800 font-bold">{selectedBot.priority}</span>
                                        </div>
                                        <div className="detail-item">
                                            <span className="detail-label block text-slate-600 font-semibold mb-1">Status:</span>
                                            <span className={`detail-value px-3 py-1 rounded-full text-sm font-bold uppercase ${selectedBot.status === 'active' ? 'bg-green-100 text-green-800' :
                                                'bg-slate-100 text-slate-800'
                                                }`}>
                                                {getStatusText(selectedBot.status)}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div className="detail-section bg-slate-50 rounded-lg p-6">
                                    <h4 className="text-lg font-bold text-slate-800 mb-4 border-b border-slate-200 pb-2">🎯 Capabilities</h4>
                                    <div className="capabilities-list flex flex-wrap gap-2">
                                        {selectedBot.capabilities.map((capability) => (
                                            <span key={capability} className="capability-tag bg-white text-slate-700 px-3 py-1 rounded-full text-sm font-semibold border border-slate-300">
                                                {getCapabilityText(capability)}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                {botStats[selectedBot.id] && (
                                    <div className="detail-section bg-slate-50 rounded-lg p-6">
                                        <h4 className="text-lg font-bold text-slate-800 mb-4 border-b border-slate-200 pb-2">📊 Statistics</h4>
                                        <div className="stats-grid grid grid-cols-2 gap-4">
                                            <div className="stat-item text-center p-3 bg-white rounded">
                                                <div className="stat-label text-slate-600 font-semibold mb-1">Total Ops</div>
                                                <div className="stat-value text-2xl font-black text-indigo-600">{botStats[selectedBot.id].totalOperations}</div>
                                            </div>
                                            <div className="stat-item text-center p-3 bg-white rounded">
                                                <div className="stat-label text-slate-600 font-semibold mb-1">Active</div>
                                                <div className="stat-value text-2xl font-black text-green-600">{botStats[selectedBot.id].activeOperations}</div>
                                            </div>
                                            <div className="stat-item text-center p-3 bg-white rounded">
                                                <div className="stat-label text-slate-600 font-semibold mb-1">Completed</div>
                                                <div className="stat-value text-2xl font-black text-blue-600">{botStats[selectedBot.id].completedOperations}</div>
                                            </div>
                                            <div className="stat-item text-center p-3 bg-white rounded">
                                                <div className="stat-label text-slate-600 font-semibold mb-1">Utilization</div>
                                                <div className="stat-value text-2xl font-black text-orange-600">{Math.round(botStats[selectedBot.id].utilization)}%</div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="modal-actions flex gap-3 mt-6 pt-6 border-t border-slate-200">
                                <button
                                    className={`flex-1 py-3 rounded-lg font-bold text-lg transition-all ${selectedBot.status === 'active'
                                        ? 'bg-orange-600 text-white hover:bg-orange-700'
                                        : 'bg-green-600 text-white hover:bg-green-700'
                                        }`}
                                    onClick={() => {
                                        selectedBot.status = selectedBot.status === 'active' ? 'inactive' : 'active';
                                        showNotification(`Bot ${selectedBot.name} ${selectedBot.status === 'active' ? 'activated' : 'deactivated'}`, 'success');
                                        setSelectedBot({ ...selectedBot });
                                    }}
                                >
                                    {selectedBot.status === 'active' ? '⏸️ Deactivate Bot' : '▶️ Activate Bot'}
                                </button>
                                <button
                                    className="flex-1 py-3 bg-blue-600 text-white rounded-lg font-bold text-lg hover:bg-blue-700 transition-all"
                                    onClick={() => showNotification(`Assign task to ${selectedBot.name}`, 'info')}
                                >
                                    📝 Assign Task
                                </button>
                                <button
                                    className="flex-1 py-3 bg-purple-600 text-white rounded-lg font-bold text-lg hover:bg-purple-700 transition-all"
                                    onClick={() => showNotification(`Test bot ${selectedBot.name}`, 'info')}
                                >
                                    🧪 Test Bot
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* New Request Modal */}
            {showNewRequestModal && (
                <div className="new-request-modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="modal-content bg-white rounded-3xl shadow-2xl max-w-lg w-full">
                        <div className="modal-header bg-gradient-to-r from-indigo-600 to-slate-800 text-white p-6 rounded-t-3xl flex justify-between items-center">
                            <h3 className="text-2xl font-black">🆕 New Request</h3>
                            <button
                                onClick={() => setShowNewRequestModal(false)}
                                className="close-modal-btn w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center text-white hover:bg-opacity-30 transition-colors"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="modal-body p-6 space-y-4">
                            <div className="form-group">
                                <label className="block text-slate-700 font-bold mb-2">Request Type *</label>
                                <select
                                    value={newRequest.type}
                                    onChange={(e) => setNewRequest({ ...newRequest, type: e.target.value })}
                                    className="form-input w-full px-4 py-3 bg-slate-50 text-slate-800 rounded-lg border-2 border-slate-200 font-semibold focus:border-indigo-500 focus:outline-none"
                                >
                                    <option value="new_customer">New Customer</option>
                                    <option value="shipping_request">Shipping Request</option>
                                    <option value="partner_onboarding">Partner Onboarding</option>
                                    <option value="support_request">Support Request</option>
                                    <option value="complaint">Complaint</option>
                                    <option value="inquiry">Inquiry</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label className="block text-slate-700 font-bold mb-2">Customer Name *</label>
                                <input
                                    type="text"
                                    value={newRequest.customerName}
                                    onChange={(e) => setNewRequest({ ...newRequest, customerName: e.target.value })}
                                    placeholder="Enter customer name"
                                    className="form-input w-full px-4 py-3 bg-slate-50 text-slate-800 rounded-lg border-2 border-slate-200 font-semibold focus:border-indigo-500 focus:outline-none"
                                />
                            </div>

                            <div className="form-group">
                                <label className="block text-slate-700 font-bold mb-2">Contact Information</label>
                                <input
                                    type="text"
                                    value={newRequest.customerContact}
                                    onChange={(e) => setNewRequest({ ...newRequest, customerContact: e.target.value })}
                                    placeholder="Email or phone"
                                    className="form-input w-full px-4 py-3 bg-slate-50 text-slate-800 rounded-lg border-2 border-slate-200 font-semibold focus:border-indigo-500 focus:outline-none"
                                />
                            </div>

                            <div className="form-group">
                                <label className="block text-slate-700 font-bold mb-2">Priority</label>
                                <select
                                    value={newRequest.priority}
                                    onChange={(e) => setNewRequest({ ...newRequest, priority: e.target.value })}
                                    className="form-input w-full px-4 py-3 bg-slate-50 text-slate-800 rounded-lg border-2 border-slate-200 font-semibold focus:border-indigo-500 focus:outline-none"
                                >
                                    <option value="low">Low</option>
                                    <option value="normal">Normal</option>
                                    <option value="high">High</option>
                                    <option value="urgent">Urgent</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label className="block text-slate-700 font-bold mb-2">Description</label>
                                <textarea
                                    value={newRequest.description}
                                    onChange={(e) => setNewRequest({ ...newRequest, description: e.target.value })}
                                    placeholder="Detailed description..."
                                    className="form-textarea w-full px-4 py-3 bg-slate-50 text-slate-800 rounded-lg border-2 border-slate-200 font-semibold focus:border-indigo-500 focus:outline-none resize-none"
                                    rows="4"
                                ></textarea>
                            </div>

                            <div className="form-group">
                                <label className="block text-slate-700 font-bold mb-2">Suggested Bots:</label>
                                <div className="suggested-bots flex flex-wrap gap-2">
                                    {suggestedBots.map((botId) => (
                                        <span key={botId} className="suggested-bot bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm font-semibold">
                                            {getBotIcon(botId)} {getBotName(botId)}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="modal-actions flex gap-3 p-6 pt-0">
                            <button
                                onClick={submitNewRequest}
                                className="submit-btn flex-1 py-3 bg-green-600 text-white rounded-lg font-bold text-lg hover:bg-green-700 transition-all"
                            >
                                📤 Submit Request
                            </button>
                            <button
                                onClick={() => setShowNewRequestModal(false)}
                                className="cancel-btn flex-1 py-3 bg-slate-200 text-slate-700 rounded-lg font-bold text-lg hover:bg-slate-300 transition-all"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Notifications */}
            {notification && (
                <div className={`notification fixed bottom-6 right-6 p-4 rounded-lg shadow-lg flex items-center gap-3 z-50 max-w-md ${notification.type === 'success' ? 'bg-green-100 border-l-4 border-green-500 text-green-800' :
                    notification.type === 'error' ? 'bg-red-100 border-l-4 border-red-500 text-red-800' :
                        notification.type === 'warning' ? 'bg-orange-100 border-l-4 border-orange-500 text-orange-800' :
                            'bg-blue-100 border-l-4 border-blue-500 text-blue-800'
                    }`}>
                    <span className="flex-1 font-semibold">{notification.message}</span>
                    <button
                        onClick={() => setNotification(null)}
                        className="close-notification w-6 h-6 rounded-full flex items-center justify-center hover:bg-black hover:bg-opacity-10 transition-colors"
                    >
                        ✕
                    </button>
                </div>
            )}
        </div>
    );
};

export default OrchestrationDashboard;
