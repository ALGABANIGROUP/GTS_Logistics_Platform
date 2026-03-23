export type BotStatus = 'active' | 'intelligence_mode' | 'paused' | 'stopped';
export type BotCategory = 'management' | 'operations' | 'finance' | 'services' | 'intelligence' | 'maintenance' | 'safety' | 'security' | 'sales' | 'marketing' | 'training';

export interface Bot {
    id: number;
    key: string;
    name: string;
    displayName: string;
    email: string | null;
    secondaryEmail?: string;
    status: BotStatus;
    category: BotCategory;
    description: string;
    icon: string;
    reportsTo?: string;
    automationLevel: 'full' | 'semi' | 'manual';
    lastActive?: string;
    health: 'excellent' | 'good' | 'warning' | 'critical';
}

export interface BotStats {
    total: number;
    active: number;
    intelligenceMode: number;
    paused: number;
    withEmail: number;
    withoutEmail: number;
    byCategory: Record<BotCategory, number>;
}

export interface EmailTemplate {
    id: string;
    name: string;
    subject: string;
    body: string;
    category: 'alert' | 'report' | 'notification' | 'reminder';
}

export interface BotHierarchy {
    [managerKey: string]: string[];
}
