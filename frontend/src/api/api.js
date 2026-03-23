// D:\GTS Logistics\frontend\src\api\api.js

import axiosClient from "./axiosClient";

const apiClient = axiosClient;

/* ======================================================
   ðŸ”§ Maintenance System & AI Bots Services
====================================================== */

// Get system status
export const getSystemStatus = async () => {
    try {
        const response = await apiClient.get('/system/status');
        return response.data;
    } catch (error) {
        throw new Error(`System status check failed: ${error.message}`);
    }
};

// Run bot health check
export const runHealthCheck = async (botName) => {
    try {
        const response = await apiClient.get(`/api/v1/ai/bots/available/${botName}/health`);
        return response.data;
    } catch (error) {
        throw new Error(`Health check failed for ${botName}: ${error.message}`);
    }
};

// Run AI bot
export const runAIBot = async (botName) => {
    try {
        const response = await apiClient.post(`/api/v1/ai/bots/available/${botName}/run`);
        return response.data;
    } catch (error) {
        throw new Error(`Failed to start ${botName}: ${error.message}`);
    }
};

// Get AI bot status
export const getBotStatus = async (botName) => {
    try {
        const response = await apiClient.get(`/api/v1/ai/bots/available/${botName}/status`);
        return response.data;
    } catch (error) {
        throw new Error(`Failed to get status for ${botName}: ${error.message}`);
    }
};

// Stop AI bot
export const stopAIBot = async (botName) => {
    try {
        const response = await apiClient.post(`/api/v1/ai/bots/available/${botName}/run`, {
            message: "stop",
            context: { action: "stop" },
            meta: { source: "ui" },
        });
        return response.data;
    } catch (error) {
        throw new Error(`Failed to stop ${botName}: ${error.message}`);
    }
};

/* ======================================================
   ðŸ“Š Extra System & Server Metrics Services
====================================================== */

// Get database statistics
export const getDatabaseStats = async () => {
    try {
        const response = await apiClient.get('/system/database/stats');
        return response.data;
    } catch (error) {
        throw new Error(`Database stats fetch failed: ${error.message}`);
    }
};

// Get server metrics
export const getServerMetrics = async () => {
    try {
        const response = await apiClient.get('/system/metrics');
        return response.data;
    } catch (error) {
        throw new Error(`Server metrics fetch failed: ${error.message}`);
    }
};

export default apiClient;
