// src/api/settings.js - API Structure (English only)
export const settingsAPI = {
    // Platform Settings
    getPlatformSettings: () => fetch('/api/platform/settings'),
    updatePlatformSettings: (data) => fetch('/api/platform/settings', {
        method: 'PUT',
        body: JSON.stringify(data)
    }),

    // Tenant Settings
    getTenantSettings: (tenantId) => fetch(`/api/tenants/${tenantId}/settings`),
    updateTenantSettings: (tenantId, data) => fetch(`/api/tenants/${tenantId}/settings`, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),

    // User Settings
    getUserSettings: () => fetch('/api/user/settings'),
    updateUserSettings: (data) => fetch('/api/user/settings', {
        method: 'PUT',
        body: JSON.stringify(data)
    }),

    // Social Media
    connectSocialMedia: (platform, data) => fetch(`/api/social/${platform}/connect`, {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    verifySocialConnection: (platform) => fetch(`/api/social/${platform}/verify`),

    // Audit Logs
    getAuditLogs: (filters) => fetch('/api/audit/logs?' + new URLSearchParams(filters)),

    // Feature Flags
    getFeatureFlags: () => fetch('/api/feature-flags'),
    updateFeatureFlag: (flag, data) => fetch(`/api/feature-flags/${flag}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    })
};
