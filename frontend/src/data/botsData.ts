import { Bot, BotCategory, BotStatus } from '../types/bots';

const rawBots: Bot[] = [
    {
        id: 1,
        key: 'general_manager',
        name: 'AI General Manager',
        displayName: 'AI General Manager',
        email: null,
        status: 'active',
        category: 'management',
        description: 'Executive oversight, decisions, and company-level orchestration.',
        icon: '👔',
        automationLevel: 'full',
        health: 'excellent',
        lastActive: '2024-01-15T16:45:00'
    },
    {
        id: 2,
        key: 'operations_manager_bot',
        name: 'AI Operations Manager',
        displayName: 'AI Operations Manager',
        email: 'operations@gabanilogistics.com',
        status: 'active',
        category: 'operations',
        description: 'Operations orchestration, workflow execution, and escalation handling.',
        icon: '⚙️',
        automationLevel: 'full',
        health: 'excellent',
        reportsTo: 'general_manager',
        lastActive: '2024-01-15T14:30:00'
    },
    {
        id: 3,
        key: 'freight_broker',
        name: 'AI Freight Broker',
        displayName: 'AI Freight Broker',
        email: 'freight@gabanilogistics.com',
        status: 'active',
        category: 'operations',
        description: 'Freight operations, load handling, and lane execution.',
        icon: '🚚',
        automationLevel: 'full',
        health: 'excellent',
        reportsTo: 'operations_manager_bot',
        lastActive: '2024-01-15T14:10:00'
    },
    {
        id: 4,
        key: 'ai_dispatcher',
        name: 'AI Dispatcher',
        displayName: 'AI Dispatcher',
        email: 'aidispatcher@gabanilogistics.com',
        status: 'active',
        category: 'operations',
        description: 'Intelligent dispatching, routing, and execution handoff.',
        icon: '🗺️',
        automationLevel: 'full',
        health: 'excellent',
        reportsTo: 'operations_manager_bot',
        lastActive: '2024-01-15T11:20:00'
    },
    {
        id: 5,
        key: 'information_coordinator',
        name: 'AI Information Coordinator',
        displayName: 'AI Information Coordinator',
        email: 'intel@gabanilogistics.com',
        status: 'active',
        category: 'intelligence',
        description: 'Data intake, coordination, and information governance.',
        icon: '📋',
        automationLevel: 'full',
        health: 'good',
        reportsTo: 'intelligence_bot',
        lastActive: '2024-01-15T12:00:00'
    },
    {
        id: 6,
        key: 'intelligence_bot',
        name: 'Executive Intelligence',
        displayName: 'Executive Intelligence',
        email: 'strategy@gabanilogistics.com',
        status: 'active',
        category: 'intelligence',
        description: 'Executive analytics, strategy insights, and trend intelligence.',
        icon: '📊',
        automationLevel: 'full',
        health: 'excellent',
        reportsTo: 'general_manager',
        lastActive: '2024-01-15T11:10:00'
    },
    {
        id: 7,
        key: 'customer_service',
        name: 'AI Customer Service',
        displayName: 'AI Customer Service',
        email: 'customers@gabanilogistics.com',
        status: 'active',
        category: 'services',
        description: 'Customer support, intake, and escalation.',
        icon: '💬',
        automationLevel: 'full',
        health: 'good',
        reportsTo: 'operations_manager_bot',
        lastActive: '2024-01-15T09:30:00'
    },
    {
        id: 8,
        key: 'documents_manager',
        name: 'AI Documents Manager',
        displayName: 'AI Documents Manager',
        email: 'doccontrol@gabanilogistics.com',
        status: 'active',
        category: 'operations',
        description: 'Document processing, compliance, and archival workflows.',
        icon: '📄',
        automationLevel: 'full',
        health: 'good',
        reportsTo: 'operations_manager_bot',
        lastActive: '2024-01-15T08:45:00'
    },
    {
        id: 9,
        key: 'legal_bot',
        name: 'AI Legal Consultant',
        displayName: 'AI Legal Consultant',
        email: null,
        secondaryEmail: 'operations@gabanilogistics.com',
        status: 'active',
        category: 'security',
        description: 'Legal review and compliance guidance (uses Operations bot mailbox).',
        icon: '⚖️',
        automationLevel: 'manual',
        health: 'good',
        reportsTo: 'general_manager',
        lastActive: '2024-01-15T10:30:00'
    },
    {
        id: 10,
        key: 'mapleload_bot',
        name: 'MapleLoad Canada Bot',
        displayName: 'MapleLoad Canada Bot',
        email: 'freight@gabanilogistics.com',
        status: 'active',
        category: 'operations',
        description: 'Canadian load-board integration and market execution support.',
        icon: '🍁',
        automationLevel: 'full',
        health: 'excellent',
        reportsTo: 'operations_manager_bot',
        lastActive: '2024-01-15T06:15:00'
    },
    {
        id: 11,
        key: 'safety_manager_bot',
        name: 'AI Safety Manager',
        displayName: 'AI Safety Manager',
        email: 'safety@gabanilogistics.com',
        status: 'intelligence_mode',
        category: 'safety',
        description: 'Safety compliance, incident tracking, and proactive alerts.',
        icon: '🛡️',
        automationLevel: 'semi',
        health: 'good',
        reportsTo: 'operations_manager_bot',
        lastActive: '2024-01-14T16:00:00'
    },
    {
        id: 12,
        key: 'sales_bot',
        name: 'AI Sales Bot',
        displayName: 'AI Sales Bot',
        email: 'sales@gabanilogistics.com',
        status: 'intelligence_mode',
        category: 'sales',
        description: 'Sales pipeline intelligence and opportunity tracking.',
        icon: '💼',
        automationLevel: 'semi',
        health: 'good',
        reportsTo: 'operations_manager_bot',
        lastActive: '2024-01-14T18:30:00'
    },
    {
        id: 13,
        key: 'system_manager_bot',
        name: 'AI System Admin',
        displayName: 'AI System Admin',
        email: 'admin@gabanilogistics.com',
        secondaryEmail: 'no-reply@gabanilogistics.com',
        status: 'active',
        category: 'maintenance',
        description: 'System administration, health monitoring, and platform controls.',
        icon: '🔧',
        automationLevel: 'full',
        health: 'excellent',
        reportsTo: 'general_manager',
        lastActive: '2024-01-15T10:15:00'
    },
    {
        id: 14,
        key: 'finance_bot',
        name: 'AI Finance Bot',
        displayName: 'AI Finance Bot',
        email: 'finance@gabanilogistics.com',
        secondaryEmail: 'accounts@gabanilogistics.com',
        status: 'active',
        category: 'finance',
        description: 'Billing, revenue tracking, and financial reporting (expenses via accounts mailbox).',
        icon: '💰',
        automationLevel: 'full',
        health: 'excellent',
        reportsTo: 'general_manager',
        lastActive: '2024-01-15T10:05:00'
    },
    {
        id: 15,
        key: 'marketing_manager',
        name: 'AI Marketing Manager',
        displayName: 'AI Marketing Manager',
        email: 'marketing@gabanilogistics.com',
        status: 'active',
        category: 'marketing',
        description: 'Marketing campaign automation and lead optimization.',
        icon: 'MKT',
        automationLevel: 'full',
        health: 'excellent',
        reportsTo: 'general_manager',
        lastActive: '2024-01-15T09:50:00'
    },
    {
        id: 16,
        key: 'partner_manager',
        name: 'AI Partner Manager',
        displayName: 'AI Partner Manager',
        email: 'investments@gabanilogistics.com',
        status: 'active',
        category: 'management',
        description: 'Partner ecosystem governance and strategic alliance workflows.',
        icon: 'PRT',
        automationLevel: 'full',
        health: 'excellent',
        reportsTo: 'general_manager',
        lastActive: '2026-03-21T09:00:00'
    },
    {
        id: 17,
        key: 'maintenance_dev',
        name: 'AI Dev Maintenance Bot (CTO)',
        displayName: 'AI Dev Maintenance Bot (CTO)',
        email: null,
        status: 'active',
        category: 'maintenance',
        description: 'DevOps maintenance, automated fixes, and CTO-level diagnostics.',
        icon: 'CTO',
        automationLevel: 'full',
        health: 'excellent',
        reportsTo: 'system_manager_bot',
        lastActive: '2024-01-15T02:00:00'
    },
    {
        id: 18,
        key: 'security_manager_bot',
        name: 'AI Security Manager',
        displayName: 'AI Security Manager',
        email: 'security@gabanilogistics.com',
        status: 'active',
        category: 'security',
        description: 'Security monitoring, threat detection, and access governance.',
        icon: '🔒',
        automationLevel: 'full',
        health: 'excellent',
        reportsTo: 'general_manager',
        lastActive: '2024-01-15T15:20:00'
    },
    {
        id: 19,
        key: 'trainer_bot',
        name: 'AI Trainer Bot',
        displayName: 'AI Trainer Bot',
        email: null,
        status: 'active',
        category: 'training',
        description: 'Owns the Training & Simulation Center, runs readiness drills, and evaluates bot performance before production use.',
        icon: 'TRN',
        automationLevel: 'full',
        health: 'excellent',
        reportsTo: 'general_manager',
        lastActive: '2026-03-19T12:30:00'
    }
];

const makeInitials = (name: string) => {
    const cleaned = name.replace(/[^A-Za-z0-9 ]/g, ' ').trim();
    const parts = cleaned.split(/\s+/).filter(Boolean);
    const initials = parts.slice(0, 2).map(part => part[0]).join('');
    return (initials || cleaned.slice(0, 2) || 'AI').toUpperCase();
};

const normalizeBot = (bot: Bot): Bot => {
    const label = bot.name || bot.key;
    return {
        ...bot,
        displayName: label,
        description: bot.description || `${label} bot.`,
        icon: bot.icon || makeInitials(label),
    };
};

export const unifiedBots: Bot[] = rawBots.map(normalizeBot);

export const emailTemplates = [
    {
        id: 'daily_report',
        name: 'Daily Report',
        subject: 'Daily Performance Report - {date}',
        body: `Hello Manager,

Here is the daily performance summary:

- Completed tasks: {completedTasks}
- Warnings: {warnings}
- Revenue: {revenue}

Regards,
{botName}`,
        category: 'report'
    },
    {
        id: 'alert_urgent',
        name: 'Urgent Alert',
        subject: 'Urgent Alert: {issue}',
        body: `Urgent alert!

{description}

Time: {time}
Bot: {botName}

Please take immediate action.`,
        category: 'alert'
    },
    {
        id: 'maintenance_notice',
        name: 'Maintenance Notice',
        subject: 'Scheduled Maintenance Notice',
        body: `Hello,

Scheduled maintenance is planned for:
Time: {time}
Duration: {duration}
Impact: {impact}

Thank you for your understanding.`,
        category: 'notification'
    }
];

export function getBotStats(bots: Bot[] = unifiedBots) {
    const stats = {
        total: bots.length,
        active: bots.filter(b => b.status === 'active').length,
        intelligenceMode: bots.filter(b => b.status === 'intelligence_mode').length,
        paused: bots.filter(b => b.status === 'paused').length,
        withEmail: bots.filter(b => b.email !== null).length,
        withoutEmail: bots.filter(b => b.email === null).length,
        byCategory: {} as Record<string, number>
    };

    bots.forEach(bot => {
        stats.byCategory[bot.category] = (stats.byCategory[bot.category] || 0) + 1;
    });

    return stats;
}

export function getBotHierarchy(): Record<string, string[]> {
    const hierarchy: Record<string, string[]> = {};

    unifiedBots.forEach(bot => {
        if (bot.reportsTo) {
            if (!hierarchy[bot.reportsTo]) {
                hierarchy[bot.reportsTo] = [];
            }
            hierarchy[bot.reportsTo].push(bot.key);
        }
    });

    return hierarchy;
}

export function findBotByEmail(email: string): Bot | undefined {
    return unifiedBots.find(bot =>
        bot.email === email || bot.secondaryEmail === email
    );
}

export function getBotsByCategory(category: BotCategory): Bot[] {
    return unifiedBots.filter(bot => bot.category === category);
}

export function getBotsByStatus(status: BotStatus): Bot[] {
    return unifiedBots.filter(bot => bot.status === status);
}
