// src/services/adminService.js
import axiosClient from '../api/axiosClient';

const ADMIN_API = '/api/v1/admin';

export const adminService = {
    // ==================== System Health ====================
    getSystemHealth: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/health/system`);
            return response.data;
        } catch {
            // Silently use fallback - endpoint not yet implemented
            return {
                status: 'error',
                system: {
                    cpu: { percent: 0, cores: 0, cores_physical: 0 },
                    memory: { percent: 0, total_gb: 0, available_gb: 0, used_gb: 0 },
                    disk: { percent: 0, total_gb: 0, free_gb: 0, used_gb: 0 },
                    uptime: 'unknown'
                }
            };
        }
    },

    getDatabaseHealth: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/health/database`);
            return response.data;
        } catch {
            // Silently use fallback - endpoint not yet implemented
            return { status: 'error', database: { size_gb: null, table_counts: {} } };
        }
    },

    getDetailedHealth: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/health/detailed`);
            return response.data;
        } catch {
            // Silently use fallback - endpoint not yet implemented
            return { overall_status: 'unknown', components: {} };
        }
    },

    // ==================== User Management ====================
    listUsers: async (page = 1, limit = 20, filters = {}) => {
        try {
            const params = { page, limit, ...filters };
            const response = await axiosClient.get(`${ADMIN_API}/users/list`, { params });
            return response.data;
        } catch {
            // Silently use fallback - endpoint not yet implemented
            return { users: [], total: 0, page: 1, total_pages: 0 };
        }
    },

    getUserDetails: async (userId) => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/users/${userId}`);
            return response.data;
        } catch (error) {
            console.error('Failed to fetch user details:', error);
            throw error;
        }
    },

    createUser: async (userData) => {
        try {
            const response = await axiosClient.post(`${ADMIN_API}/users/create`, userData);
            return response.data;
        } catch (error) {
            console.error('Failed to create user:', error);
            throw error;
        }
    },

    updateUser: async (userId, updateData) => {
        try {
            const response = await axiosClient.put(`${ADMIN_API}/users/update/${userId}`, updateData);
            return response.data;
        } catch (error) {
            console.error('Failed to update user:', error);
            throw error;
        }
    },

    disableUser: async (userId) => {
        try {
            const response = await axiosClient.put(`${ADMIN_API}/users/disable/${userId}`);
            return response.data;
        } catch (error) {
            console.error('Failed to disable user:', error);
            throw error;
        }
    },

    enableUser: async (userId) => {
        try {
            const response = await axiosClient.put(`${ADMIN_API}/users/enable/${userId}`);
            return response.data;
        } catch (error) {
            console.error('Failed to enable user:', error);
            throw error;
        }
    },

    getUsersStatistics: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/users/statistics`);
            return response.data;
        } catch {
            // Silently use fallback - endpoint not yet implemented
            return {
                summary: {
                    total_users: 0,
                    active_users: 0,
                    inactive_users: 0,
                    new_users_7d: 0
                },
                by_role: {}
            };
        }
    },

    // ==================== Data Management ====================
    createBackup: async (backupType = 'full') => {
        try {
            const response = await axiosClient.post(`${ADMIN_API}/data/backup`, { backup_type: backupType });
            return response.data;
        } catch (error) {
            console.error('Failed to create backup:', error);
            throw error;
        }
    },

    listBackups: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/data/backup/list`);
            return response.data;
        } catch {
            // Silently use fallback - endpoint not yet implemented
            return { backups: [], total: 0 };
        }
    },

    cleanupTempFiles: async () => {
        try {
            const response = await axiosClient.post(`${ADMIN_API}/data/cleanup/temp`);
            return response.data;
        } catch (error) {
            console.error('Failed to cleanup temp files:', error);
            throw error;
        }
    },

    optimizeDatabase: async () => {
        try {
            const response = await axiosClient.post(`${ADMIN_API}/data/optimize/database`);
            return response.data;
        } catch (error) {
            console.error('Failed to optimize database:', error);
            throw error;
        }
    },

    getDataUsageStatistics: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/data/statistics/usage`);
            return response.data;
        } catch {
            // Silently use fallback - endpoint not yet implemented
            return {
                database: {
                    size_gb: 0,
                    users_count: 0,
                    shipments_count: 0,
                    customers_count: 0
                },
                tables: []
            };
        }
    },

    // ==================== Security & Audit ====================
    getAuditLogs: async (filters = {}) => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/users/audit/logs`, { params: filters });
            return response.data;
        } catch {
            // Silently use fallback - endpoint not yet implemented
            return { logs: [], total: 0 };
        }
    },

    getSecurityAlerts: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/security/alerts`);
            return response.data;
        } catch {
            // Silently use fallback - endpoint not yet implemented
            return { alerts: [] };
        }
    },

    // ==================== Dashboard ====================
    getDashboardStats: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/dashboard/stats`);
            return response.data;
        } catch {
            // Silently use fallback - endpoint not yet implemented
            return {
                status: 'error',
                metrics: { total_users: 0, active_users: 0 }
            };
        }
    },

    getSystemStatus: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/status`);
            return response.data;
        } catch {
            // Silently use fallback - endpoint not yet implemented
            return { status: 'unknown' };
        }
    },

    // ==================== DATA SOURCES - From Specific Bots ====================

    // Health Monitoring from Maintenance Bot
    getHealthFromMaintenanceBot: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/data-sources/health/maintenance-bot`);
            return response.data;
        } catch (error) {
            // Silently use fallback - endpoint not yet implemented
            return { source: 'maintenance_dev_bot', error: error.message, health_status: 'unknown' };
        }
    },

    getDetailedHealthFromMaintenance: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/data-sources/health/detailed-maintenance`);
            return response.data;
        } catch (error) {
            // Silently use fallback - endpoint not yet implemented
            return { source: 'maintenance_dev_bot', error: error.message };
        }
    },

    // User Management from Database
    getUsersFromDatabase: async (page = 1, limit = 20, filters = {}) => {
        try {
            const params = { page, limit, ...filters };
            const response = await axiosClient.get(`${ADMIN_API}/data-sources/users/database`, { params });
            return response.data;
        } catch (error) {
            // Silently use fallback - endpoint not yet implemented
            return { source: 'database', error: error.message, users: [], total: 0 };
        }
    },

    getUserStatisticsFromDatabase: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/data-sources/users/statistics-database`);
            return response.data;
        } catch (error) {
            // Silently use fallback - endpoint not yet implemented
            return {
                source: 'database',
                error: error.message,
                summary: {
                    total_users: 0,
                    active_users: 0,
                    inactive_users: 0,
                    new_users_7d: 0
                }
            };
        }
    },

    // Security & Audit from Security Bot
    getAuditLogsFromSecurityBot: async (filters = {}) => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/data-sources/security/audit-logs`, { params: filters });
            return response.data;
        } catch (error) {
            // Silently use fallback - endpoint not yet implemented
            return { source: 'security_bot', error: error.message, logs: [] };
        }
    },

    getSecurityAlertsFromSecurityBot: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/data-sources/security/alerts`);
            return response.data;
        } catch (error) {
            // Silently use fallback - endpoint not yet implemented
            return { source: 'security_bot', error: error.message, alerts: [] };
        }
    },

    getSecurityRecommendationsFromSecurityBot: async () => {
        try {
            const response = await axiosClient.get(`${ADMIN_API}/data-sources/security/recommendations`);
            return response.data;
        } catch (error) {
            // Silently use fallback - endpoint not yet implemented
            return { source: 'security_bot', error: error.message, recommendations: [] };
        }
    }
};

export default adminService;
