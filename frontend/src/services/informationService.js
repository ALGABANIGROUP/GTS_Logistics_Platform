// Information Coordinator Bot - API Service
import axiosClient from '@/api/axiosClient';

/**
 * Information Coordinator Service
 * Handles data collection, analysis, and reporting
 */

// ==================== Dashboard APIs ====================

export const getOperationalDashboard = async () => {
    try {
        const response = await axiosClient.get('/coordinator/dashboard/operational');
        return response.data;
    } catch (error) {
        console.error('Error fetching operational dashboard:', error);
        return {
            status: 'error',
            timestamp: new Date().toISOString(),
            metrics: {
                shipments: { completed_today: 0, delayed_shipments: 0, total_active: 0 },
                financial: { daily_revenue: 0, monthly_revenue: 0 },
                inventory: { total_items: 0, low_stock_count: 0 },
                customers: { total_customers: 0, active_customers: 0 }
            },
            insights: [],
            alerts: []
        };
    }
};

export const getSystemMetrics = async (timeRange = 'today', metricType = null) => {
    try {
        const params = { time_range: timeRange };
        if (metricType) params.metric_type = metricType;

        const response = await axiosClient.get('/coordinator/dashboard/metrics', { params });
        return response.data;
    } catch (error) {
        console.error('Error fetching system metrics:', error);
        return {
            time_range: timeRange,
            metrics: {
                shipments: { total: 0, delivered: 0, pending: 0, delayed: 0 },
                financial: { revenue: 0, expenses: 0, profit: 0 },
                customers: { total: 0, active: 0, new_today: 0 }
            }
        };
    }
};

export const getSystemAlerts = async (severity = null, limit = 20) => {
    try {
        const params = { limit };
        if (severity) params.severity = severity;

        const response = await axiosClient.get('/coordinator/dashboard/alerts', { params });
        return response.data;
    } catch (error) {
        console.error('Error fetching system alerts:', error);
        return {
            total_alerts: 0,
            unresolved: 0,
            alerts: []
        };
    }
};

export const getKPIs = async () => {
    try {
        const response = await axiosClient.get('/coordinator/dashboard/kpis');
        return response.data;
    } catch (error) {
        console.error('Error fetching KPIs:', error);
        return {
            timestamp: new Date().toISOString(),
            kpis: {
                operational: {},
                financial: {},
                customer: {}
            }
        };
    }
};

// ==================== Analytics APIs ====================

export const getShipmentsAnalytics = async (startDate, endDate) => {
    try {
        const response = await axiosClient.get('/coordinator/analytics/shipments', {
            params: { start_date: startDate, end_date: endDate }
        });
        return response.data;
    } catch (error) {
        console.error('Error fetching shipments analytics:', error);
        return { status: 'error', message: error.message };
    }
};

export const getFinancialAnalytics = async (startDate, endDate) => {
    try {
        const response = await axiosClient.get('/coordinator/analytics/financial', {
            params: { start_date: startDate, end_date: endDate }
        });
        return response.data;
    } catch (error) {
        console.error('Error fetching financial analytics:', error);
        return { status: 'error', message: error.message };
    }
};

export const getInventoryAnalytics = async () => {
    try {
        const response = await axiosClient.get('/coordinator/analytics/inventory');
        return response.data;
    } catch (error) {
        console.error('Error fetching inventory analytics:', error);
        return { status: 'error', message: error.message };
    }
};

export const getCustomerAnalytics = async (startDate, endDate) => {
    try {
        const response = await axiosClient.get('/coordinator/analytics/customers', {
            params: { start_date: startDate, end_date: endDate }
        });
        return response.data;
    } catch (error) {
        console.error('Error fetching customer analytics:', error);
        return { status: 'error', message: error.message };
    }
};

export const getTrendsAnalysis = async (dataType, period = '30days') => {
    try {
        const response = await axiosClient.get('/coordinator/analytics/trends', {
            params: { data_type: dataType, period }
        });
        return response.data;
    } catch (error) {
        console.error('Error fetching trends analysis:', error);
        return { status: 'error', message: error.message };
    }
};

// ==================== Predictions APIs ====================

export const predictDemand = async (period = 'next_7_days') => {
    try {
        const response = await axiosClient.post('/coordinator/analytics/predict', {
            type: 'demand',
            period
        });
        return response.data;
    } catch (error) {
        console.error('Error predicting demand:', error);
        return { status: 'error', message: error.message };
    }
};

export const predictRevenue = async (period = 'next_30_days') => {
    try {
        const response = await axiosClient.post('/coordinator/analytics/predict', {
            type: 'revenue',
            period
        });
        return response.data;
    } catch (error) {
        console.error('Error predicting revenue:', error);
        return { status: 'error', message: error.message };
    }
};

export const predictInventoryNeeds = async () => {
    try {
        const response = await axiosClient.post('/coordinator/analytics/predict', {
            type: 'inventory',
            period: 'next_14_days'
        });
        return response.data;
    } catch (error) {
        console.error('Error predicting inventory needs:', error);
        return { status: 'error', message: error.message };
    }
};

// ==================== Reports APIs ====================

export const generateCustomReport = async (reportType, startDate, endDate, filters = {}, format = 'json') => {
    try {
        const response = await axiosClient.post('/coordinator/reports/generate', {
            type: reportType,
            start_date: startDate,
            end_date: endDate,
            filters,
            format
        });
        return response.data;
    } catch (error) {
        console.error('Error generating custom report:', error);
        return { status: 'error', message: error.message };
    }
};

export const listReports = async (reportType = null, limit = 50) => {
    try {
        const params = { limit };
        if (reportType) params.type = reportType;

        const response = await axiosClient.get('/coordinator/reports/list', { params });
        return response.data;
    } catch (error) {
        console.error('Error listing reports:', error);
        return { reports: [], total: 0 };
    }
};

export const getReportDetails = async (reportId) => {
    try {
        const response = await axiosClient.get(`/coordinator/reports/${reportId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching report details:', error);
        return { status: 'error', message: error.message };
    }
};

export const downloadReport = async (reportId, format = 'pdf') => {
    try {
        const response = await axiosClient.get(`/coordinator/reports/${reportId}/download`, {
            params: { format },
            responseType: 'blob'
        });

        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `report_${reportId}.${format}`);
        document.body.appendChild(link);
        link.click();
        link.remove();

        return { status: 'success', message: 'Report downloaded successfully' };
    } catch (error) {
        console.error('Error downloading report:', error);
        return { status: 'error', message: error.message };
    }
};

export const scheduleReport = async (reportConfig) => {
    try {
        const response = await axiosClient.post('/coordinator/reports/schedule', reportConfig);
        return response.data;
    } catch (error) {
        console.error('Error scheduling report:', error);
        return { status: 'error', message: error.message };
    }
};

export const deleteReport = async (reportId) => {
    try {
        const response = await axiosClient.delete(`/coordinator/reports/${reportId}`);
        return response.data;
    } catch (error) {
        console.error('Error deleting report:', error);
        return { status: 'error', message: error.message };
    }
};

// ==================== Data Sync APIs ====================

export const syncAllDataSources = async () => {
    try {
        const response = await axiosClient.post('/coordinator/sync/all');
        return response.data;
    } catch (error) {
        console.error('Error syncing data sources:', error);
        return { status: 'error', message: error.message };
    }
};

export const syncSpecificSource = async (sourceName) => {
    try {
        const response = await axiosClient.post(`/coordinator/sync/${sourceName}`);
        return response.data;
    } catch (error) {
        console.error(`Error syncing ${sourceName}:`, error);
        return { status: 'error', message: error.message };
    }
};

export const getSyncStatus = async () => {
    try {
        const response = await axiosClient.get('/coordinator/sync/status');
        return response.data;
    } catch (error) {
        console.error('Error fetching sync status:', error);
        return {
            status: 'unknown',
            last_sync: null,
            sources: []
        };
    }
};

// ==================== Integration APIs ====================

export const getCarrierData = async (carrier) => {
    try {
        const response = await axiosClient.get(`/coordinator/integrations/carriers/${carrier}`);
        return response.data;
    } catch (error) {
        console.error(`Error fetching carrier data for ${carrier}:`, error);
        return { status: 'error', message: error.message };
    }
};

export const getExternalAPIStatus = async () => {
    try {
        const response = await axiosClient.get('/coordinator/integrations/status');
        return response.data;
    } catch (error) {
        console.error('Error fetching external API status:', error);
        return { apis: [], all_connected: false };
    }
};

// ==================== Coordinator Status ====================

export const getCoordinatorStatus = async () => {
    try {
        const response = await axiosClient.get('/coordinator/status');
        return response.data;
    } catch (error) {
        console.error('Error fetching coordinator status:', error);
        return {
            status: 'unknown',
            last_sync: null,
            tasks_active: 0,
            config: {}
        };
    }
};

export const restartCoordinator = async () => {
    try {
        const response = await axiosClient.post('/coordinator/restart');
        return response.data;
    } catch (error) {
        console.error('Error restarting coordinator:', error);
        return { status: 'error', message: error.message };
    }
};

export const updateCoordinatorConfig = async (config) => {
    try {
        const response = await axiosClient.put('/coordinator/config', config);
        return response.data;
    } catch (error) {
        console.error('Error updating coordinator config:', error);
        return { status: 'error', message: error.message };
    }
};

export default {
    // Dashboard
    getOperationalDashboard,
    getSystemMetrics,
    getSystemAlerts,
    getKPIs,

    // Analytics
    getShipmentsAnalytics,
    getFinancialAnalytics,
    getInventoryAnalytics,
    getCustomerAnalytics,
    getTrendsAnalysis,

    // Predictions
    predictDemand,
    predictRevenue,
    predictInventoryNeeds,

    // Reports
    generateCustomReport,
    listReports,
    getReportDetails,
    downloadReport,
    scheduleReport,
    deleteReport,

    // Sync
    syncAllDataSources,
    syncSpecificSource,
    getSyncStatus,

    // Integrations
    getCarrierData,
    getExternalAPIStatus,

    // Status
    getCoordinatorStatus,
    restartCoordinator,
    updateCoordinatorConfig
};
