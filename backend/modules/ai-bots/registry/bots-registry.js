// src/modules/ai-bots/registry/bots-registry.js
const botsRegistry = {
    // ==================== USER BOTS (10) ====================
    finance_bot: {
        key: "finance_bot",
        name_ar: "AI Finance Bot",
        name_en: "AI Finance Bot",
        type: "user",
        category: "Finance",
        tier: "Enterprise",
        phase: "enterprise",
        description: "Manage invoices, payments, financial reports",
        icon: "💰",
        email_local_part: "finance",
        version: "2.5.0",
        status: "active",
        availability: "platform_only",
        endpoints: {
            dashboard: "/ai-bots/finance",
            api: "/api/v1/ai/finance",
            webhook: "/webhooks/ai/finance"
        },
        features: ["invoice_management", "payment_processing", "financial_reports", "tax_calculation"],
        dependencies: [],
        required_features: ["finance_bot.access"],
        ui_config: {
            color: "#10B981",
            dashboard_component: "FinanceDashboard"
        }
    },
    payment_bot: {
        key: "payment_bot",
        name_ar: "Payment Gateway Dashboard",
        name_en: "Payment Gateway Dashboard",
        type: "user",
        category: "Finance",
        tier: "Enterprise",
        phase: "enterprise",
        description: "Secure payment processing, invoice management, transaction tracking, and finance bot integration",
        icon: "PAY",
        email_local_part: "payments",
        version: "1.0.0",
        status: "active",
        availability: "platform_only",
        endpoints: {
            dashboard: "/ai-bots/payment",
            api: "/api/v1/payments",
            webhook: "/api/v1/webhooks/sudapay/payment"
        },
        features: ["secure_payments", "invoice_management", "transaction_history", "refund_processing", "finance_bot_integration"],
        dependencies: ["finance_bot"],
        required_features: [],
        ui_config: {
            color: "#2563EB",
            dashboard_component: "PaymentBotDashboard"
        }
    },
    sudapay: {
        key: "sudapay",
        name_ar: "SUDAPAY Payment Gateway",
        name_en: "SUDAPAY Payment Gateway",
        type: "user",
        category: "Finance",
        tier: "Enterprise",
        phase: "enterprise",
        description: "Secure payment processing, invoice management, and transaction tracking",
        icon: "💳",
        email_local_part: "payments",
        version: "1.0.0",
        status: "active",
        availability: "platform_only",
        endpoints: {
            dashboard: "/ai-bots/sudapay",
            api: "/api/v1/payments",
            webhook: "/api/v1/webhooks/sudapay/payment"
        },
        features: ["secure_payments", "invoice_management", "transaction_history", "refund_processing"],
        dependencies: [],
        required_features: [],
        ui_config: {
            color: "#2563EB",
            dashboard_component: "SUDAPayBotDashboard"
        }
    },

    freight_broker: {
        key: "freight_broker",
        name_ar: "AI Freight Broker",
        name_en: "AI Freight Broker",
        type: "user",
        category: "Logistics",
        description: "Shipments matching, pricing, brokerage",
        icon: "🚚",
        email_local_part: "freight",
        version: "3.2.0",
        status: "active",
        availability: "all",
        endpoints: {
            dashboard: "/ai-bots/freight-broker",
            api: "/api/v1/ai/broker",
            webhook: "/webhooks/ai/broker"
        },
        features: ["load_matching", "rate_analysis", "carrier_scoring", "brokerage"],
        dependencies: [],
        required_features: ["freight_broker.access"],
        ui_config: {
            color: "#3B82F6",
            dashboard_component: "FreightBrokerDashboard"
        }
    },

    documents_manager: {
        key: "documents_manager",
        name_ar: "AI Documents Manager",
        name_en: "AI Documents Manager",
        type: "user",
        category: "Documents",
        description: "Document management, contracts, archive",
        icon: "📄",
        email_local_part: "doccontrol",
        version: "2.1.0",
        status: "active",
        availability: "all",
        endpoints: {
            dashboard: "/ai-bots/documents",
            api: "/api/v1/ai/documents",
            webhook: "/webhooks/ai/documents"
        },
        features: ["document_management", "contract_analysis", "archive_system", "compliance_check"],
        dependencies: [],
        required_features: ["documents_manager.access"],
        ui_config: {
            color: "#8B5CF6",
            dashboard_component: "DocumentsDashboard"
        }
    },

    customer_service: {
        key: "customer_service",
        name_ar: "AI Customer Service",
        name_en: "AI Customer Service",
        type: "user",
        category: "Support",
        description: "Customer support, issue resolution",
        icon: "💬",
        email_local_part: "customers",
        version: "3.0.0",
        status: "active",
        availability: "all",
        endpoints: {
            dashboard: "/ai-bots/customer-service",
            api: "/api/v1/ai/customer-service",
            webhook: "/webhooks/ai/customer-service"
        },
        features: ["chat_support", "ticket_routing", "faq_generation", "sentiment_analysis"],
        dependencies: [],
        required_features: ["customer_service.access"],
        ui_config: {
            color: "#EC4899",
            dashboard_component: "CustomerServiceDashboard"
        }
    },

    strategy_advisor: {
        key: "strategy_advisor",
        name_ar: "AI Strategy Advisor",
        name_en: "AI Strategy Advisor",
        type: "user",
        category: "Strategy",
        description: "Strategic advice, market analysis",
        icon: "🎯",
        email_local_part: null,
        version: "1.8.0",
        status: "premium",
        availability: "paid_feature",
        endpoints: {
            dashboard: "/ai-bots/strategy",
            api: "/api/v1/ai/strategy",
            webhook: "/webhooks/ai/strategy"
        },
        features: ["market_analysis", "strategy_recommendations", "competitor_analysis", "trend_prediction"],
        dependencies: [],
        required_features: ["strategy_advisor.access"],
        ui_config: {
            color: "#F59E0B",
            dashboard_component: "StrategyDashboard"
        }
    },

    marketing_manager: {
        key: "marketing_manager",
        name_ar: "AI Marketing Manager",
        name_en: "AI Marketing Manager",
        type: "user",
        category: "Marketing",
        description: "Marketing campaigns, data analysis",
        icon: "📢",
        email_local_part: "marketing",
        version: "2.3.0",
        status: "active",
        availability: "all",
        endpoints: {
            dashboard: "/ai-bots/marketing",
            api: "/api/v1/ai/marketing",
            webhook: "/webhooks/ai/marketing"
        },
        features: ["campaign_management", "audience_analysis", "performance_tracking", "content_generation"],
        dependencies: [],
        required_features: ["marketing_manager.access"],
        ui_config: {
            color: "#8B5CF6",
            dashboard_component: "MarketingDashboard"
        }
    },

    safety_manager: {
        key: "safety_manager",
        name_ar: "AI Safety Manager",
        name_en: "AI Safety Manager",
        type: "user",
        category: "Safety",
        description: "Safety monitoring, compliance",
        icon: "🛡️",
        email_local_part: "safety",
        version: "2.0.0",
        status: "active",
        availability: "all",
        endpoints: {
            dashboard: "/ai-bots/safety",
            api: "/api/v1/ai/safety",
            webhook: "/webhooks/ai/safety"
        },
        features: ["safety_monitoring", "compliance_check", "incident_reporting", "risk_assessment"],
        dependencies: [],
        required_features: ["safety_manager.access"],
        ui_config: {
            color: "#10B981",
            dashboard_component: "SafetyDashboard"
        }
    },

    sales_team: {
        key: "sales_team",
        name_ar: "AI Sales Team",
        name_en: "AI Sales Team",
        type: "user",
        category: "Sales",
        description: "Sales, customer follow-up",
        icon: "👥",
        email_local_part: "sales",
        version: "2.4.0",
        status: "active",
        availability: "all",
        endpoints: {
            dashboard: "/ai-bots/sales",
            api: "/api/v1/ai/sales",
            webhook: "/webhooks/ai/sales"
        },
        features: ["lead_management", "customer_followup", "deal_tracking", "sales_analytics"],
        dependencies: [],
        required_features: ["sales_team.access"],
        ui_config: {
            color: "#EC4899",
            dashboard_component: "SalesDashboard"
        }
    },

    dispatcher: {
        key: "dispatcher",
        name_ar: "AI Dispatcher",
        name_en: "AI Dispatcher",
        type: "user",
        category: "Dispatch",
        description: "Transport coordination, fleet management",
        icon: "🚀",
        email_local_part: "dispatcher",
        version: "4.0.0",
        status: "active",
        availability: "integrated",
        endpoints: {
            dashboard: "/ai-bots/dispatcher",
            api: "/api/v1/ai/dispatcher",
            webhook: "/webhooks/ai/dispatcher"
        },
        features: ["smart_dispatch", "route_optimization", "fleet_management", "real_time_tracking"],
        dependencies: [],
        required_features: ["dispatcher.access"],
        ui_config: {
            color: "#3B82F6",
            dashboard_component: "DispatcherDashboard"
        }
    },

    operations_manager: {
        key: "operations_manager",
        name_ar: "AI Operations Manager",
        name_en: "AI Operations Manager",
        type: "user",
        category: "Operations",
        description: "System brain - manages daily operations",
        icon: "⚙️",
        email_local_part: "operations",
        version: "4.5.0",
        status: "active",
        availability: "all",
        endpoints: {
            dashboard: "/ai-bots/operations",
            api: "/api/v1/ai/operations",
            webhook: "/webhooks/ai/operations"
        },
        features: ["operations_management", "process_optimization", "resource_allocation", "performance_monitoring"],
        dependencies: [],
        required_features: ["operations_manager.access"],
        ui_config: {
            color: "#6366F1",
            dashboard_component: "OperationsDashboard"
        }
    },

    // ==================== SYSTEM BOTS (7) ====================
    general_manager: {
        key: "general_manager",
        name_ar: "AI General Manager",
        name_en: "AI General Manager",
        type: "user",
        category: "System",
        description: "System management, bots coordination",
        icon: "👑",
        email_local_part: null,
        version: "5.0.0",
        status: "active",
        availability: "system_only",
        endpoints: {
            dashboard: "/system/bots/general-manager",
            api: "/api/v1/system/general-manager",
            webhook: "/webhooks/system/general-manager"
        },
        features: ["system_coordination", "bot_management", "report_aggregation", "system_health"],
        dependencies: ["operations_manager"],
        required_features: ["system.admin"],
        ui_config: {
            color: "#F59E0B",
            dashboard_component: "GeneralManagerDashboard",
            show_in_user_dashboard: true
        }
    },

    system_admin: {
        key: "system_admin",
        name_ar: "AI System Admin",
        name_en: "AI System Admin",
        type: "system",
        category: "System",
        description: "User management, permissions, settings",
        icon: "🔧",
        email_local_part: "admin",
        version: "3.5.0",
        status: "active",
        availability: "admin_only",
        endpoints: {
            dashboard: "/system/bots/system-admin",
            api: "/api/v1/system/system-admin",
            webhook: "/webhooks/system/system-admin"
        },
        features: ["user_management", "permission_control", "system_settings", "audit_logs"],
        dependencies: [],
        required_features: ["system.admin"],
        ui_config: {
            color: "#6B7280",
            dashboard_component: "SystemAdminDashboard",
            show_in_user_dashboard: false
        }
    },

    dev_maintenance: {
        key: "dev_maintenance",
        name_ar: "AI Dev Maintenance Bot",
        name_en: "AI Dev Maintenance Bot",
        type: "system",
        category: "Tech",
        description: "System maintenance, updates, monitoring",
        icon: "🔩",
        email_local_part: null,
        version: "3.0.0",
        status: "active",
        availability: "system_only",
        endpoints: {
            dashboard: "/system/bots/dev-maintenance",
            api: "/api/v1/system/dev-maintenance",
            webhook: "/webhooks/system/dev-maintenance"
        },
        features: ["system_maintenance", "update_management", "performance_monitoring", "backup_management"],
        dependencies: [],
        required_features: ["system.admin"],
        ui_config: {
            color: "#6B7280",
            dashboard_component: "MaintenanceDashboard",
            show_in_user_dashboard: false
        }
    },

    security_manager: {
        key: "security_manager",
        name_ar: "AI Security Manager",
        name_en: "AI Security Manager",
        type: "system",
        category: "Security",
        description: "Security monitoring, threat detection",
        icon: "🔒",
        email_local_part: "security",
        version: "3.2.0",
        status: "active",
        availability: "admin_only",
        endpoints: {
            dashboard: "/system/bots/security",
            api: "/api/v1/system/security",
            webhook: "/webhooks/system/security"
        },
        features: ["security_monitoring", "threat_detection", "access_control", "audit_trail"],
        dependencies: [],
        required_features: ["system.admin"],
        ui_config: {
            color: "#EF4444",
            dashboard_component: "SecurityDashboard",
            show_in_user_dashboard: false
        }
    },

    partner_manager: {
        key: "partner_manager",
        name_ar: "AI Partner Manager",
        name_en: "AI Partner Manager",
        type: "system",
        category: "Partnerships",
        description: "Partnership management, relationships",
        icon: "🤝",
        email_local_part: "investments",
        version: "2.0.0",
        status: "active",
        availability: "platform_only",
        endpoints: {
            dashboard: "/ai-bots/partner-management",
            api: "/api/v1/partner-manager",
            webhook: "/webhooks/system/partner"
        },
        features: ["partner_management", "relationship_tracking", "investment_analysis", "collaboration"],
        dependencies: [],
        required_features: [],
        ui_config: {
            color: "#8B5CF6",
            dashboard_component: "PartnerDashboard",
            show_in_user_dashboard: false
        }
    },

    information_coordinator: {
        key: "information_coordinator",
        name_ar: "AI Information Coordinator",
        name_en: "AI Information Coordinator",
        type: "system",
        category: "Information",
        description: "Information gathering and analysis",
        icon: "📊",
        email_local_part: null,
        version: "2.5.0",
        status: "active",
        availability: "system_only",
        endpoints: {
            dashboard: "/system/bots/information-coordinator",
            api: "/api/v1/system/information-coordinator",
            webhook: "/webhooks/system/information-coordinator"
        },
        features: ["data_collection", "information_analysis", "report_generation", "knowledge_management"],
        dependencies: [],
        required_features: ["system.admin"],
        ui_config: {
            color: "#3B82F6",
            dashboard_component: "InformationCoordinatorDashboard",
            show_in_user_dashboard: false
        }
    },

    // ==================== SPECIALIZED BOT ====================
    mapleload_ai: {
        key: "mapleload_ai",
        name_ar: "AI MapleLoad",
        name_en: "AI MapleLoad",
        type: "system",
        category: "Logistics",
        description: "AI system specialized in managing and optimizing shipment loading operations",
        icon: "🍁",
        email_local_part: "freight",
        version: "4.0.0",
        status: "active",
        availability: "integrated",
        endpoints: {
            dashboard: "/ai-bots/mapleload",
            api: "/api/v1/ai/mapleload",
            webhook: "/webhooks/ai/mapleload"
        },
        features: [
            "load_analysis",
            "load_optimization",
            "route_planning",
            "load_forecasting",
            "space_utilization",
            "weight_distribution",
            "loading_sequence"
        ],
        dependencies: ["freight_broker", "dispatcher", "operations_manager", "safety_manager"],
        required_features: ["mapleload_ai.access"],
        ui_config: {
            color: "#10B981",
            dashboard_component: "MapleLoadDashboard"
        }
    }
};

// Aliases mapping
const botAliases = {
    // User Bots
    "finance": "finance_bot",
    "bot_finance": "finance_bot",
    "payment_bot": "payment_bot",
    "payment": "payment_bot",
    "payment_gateway": "payment_bot",
    "sudapay": "sudapay",
    "freight": "freight_broker",
    "documents": "documents_manager",
    "customer": "customer_service",
    "strategy": "strategy_advisor",
    "marketing": "marketing_manager",
    "safety": "safety_manager",
    "sales": "sales_team",
    "dispatch": "dispatcher",
    "operations": "operations_manager",

    // System Bots
    "general": "general_manager",
    "admin": "system_admin",
    "maintenance": "dev_maintenance",
    "security": "security_manager",
    "partner": "partner_manager",
    "info": "information_coordinator",

    // Specialized
    "maple": "mapleload_ai",
    "load_optimizer": "mapleload_ai"
};

module.exports = {
    botsRegistry,
    botAliases,

    getRealBotKey(aliasKey) {
        return botAliases[aliasKey] || aliasKey;
    },

    getBotInfo(botKey) {
        const realKey = this.getRealBotKey(botKey);
        return botsRegistry[realKey];
    },

    getAllBots() {
        return Object.values(botsRegistry);
    },

    getUserBots() {
        return Object.values(botsRegistry).filter(bot => bot.type === 'user');
    },

    getSystemBots() {
        return Object.values(botsRegistry).filter(bot => bot.type === 'system');
    },

    getAvailableBotsForPlan(planFeatures) {
        return this.getAllBots().filter(bot => {
            if (bot.status !== 'active') return false;
            if (!bot.required_features) return true;
            return bot.required_features.some(feature => planFeatures.includes(feature));
        });
    }
};
