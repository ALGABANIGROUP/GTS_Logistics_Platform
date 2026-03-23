/**
 * GTS Integration API Client
 * Centralized client for integrations with tracking systems, load boards, and external services
 */

import axiosClient from "./axiosClient";

const INTEGRATIONS_API = "/api/v1/integrations";

const integrationClient = {
    get: (path, config) => axiosClient.get(`${INTEGRATIONS_API}${path}`, config),
    post: (path, data, config) => axiosClient.post(`${INTEGRATIONS_API}${path}`, data, config),
    put: (path, data, config) => axiosClient.put(`${INTEGRATIONS_API}${path}`, data, config),
    delete: (path, config) => axiosClient.delete(`${INTEGRATIONS_API}${path}`, config),
};

/**
 * Tracking System Integration
 */
export const trackingAPI = {
    /**
     * Get shipment tracking data
     * @param {string} shipmentId - Shipment reference (BL number)
     */
    getShipmentStatus: async (shipmentId) => {
        const response = await integrationClient.get(`/tracking/shipment/${shipmentId}`);
        return response.data;
    },

    /**
     * Get real-time location for shipment
     * @param {string} shipmentId - Shipment reference
     */
    getShipmentLocation: async (shipmentId) => {
        const response = await integrationClient.get(`/tracking/shipment/${shipmentId}/location`);
        return response.data;
    },

    /**
     * Get proof of delivery
     * @param {string} shipmentId - Shipment reference
     */
    getProofOfDelivery: async (shipmentId) => {
        const response = await integrationClient.get(`/tracking/shipment/${shipmentId}/pod`);
        return response.data;
    },

    /**
     * Subscribe to shipment updates via webhook
     * @param {string} shipmentId - Shipment reference
     * @param {string} callbackUrl - Webhook URL to receive updates
     */
    subscribeToUpdates: async (shipmentId, callbackUrl) => {
        const response = await integrationClient.post(`/tracking/shipment/${shipmentId}/subscribe`, {
            callback_url: callbackUrl
        });
        return response.data;
    },

    /**
     * Get tracking history for shipment
     * @param {string} shipmentId - Shipment reference
     */
    getTrackingHistory: async (shipmentId) => {
        const response = await integrationClient.get(`/tracking/shipment/${shipmentId}/history`);
        return response.data;
    }
};

/**
 * Load Board Integration
 */
export const loadBoardAPI = {
    /**
     * Get available loads from connected load boards
     * @param {Object} filters - Filter criteria (origin, destination, weight, etc.)
     */
    getAvailableLoads: async (filters = {}) => {
        const response = await integrationClient.get('/loadboards/available', { params: filters });
        return response.data;
    },

    /**
     * Post load to load boards (DAT, 123LoadBoard, etc.)
     * @param {Object} loadData - Load details
     */
    postLoad: async (loadData) => {
        const response = await integrationClient.post('/loadboards/post', loadData);
        return response.data;
    },

    /**
     * Update existing load posting
     * @param {string} loadId - Load posting ID
     * @param {Object} updateData - Updated load details
     */
    updateLoad: async (loadId, updateData) => {
        const response = await integrationClient.put(`/loadboards/post/${loadId}`, updateData);
        return response.data;
    },

    /**
     * Remove load from load boards
     * @param {string} loadId - Load posting ID
     */
    removeLoad: async (loadId) => {
        const response = await integrationClient.delete(`/loadboards/post/${loadId}`);
        return response.data;
    },

    /**
     * Get current market rates for a lane
     * @param {string} origin - Origin location
     * @param {string} destination - Destination location
     */
    getMarketRates: async (origin, destination) => {
        const response = await integrationClient.get('/loadboards/rates', {
            params: { origin, destination }
        });
        return response.data;
    }
};

/**
 * Carrier Integration
 */
export const carrierAPI = {
    /**
     * Get carrier availability
     * @param {string} carrierId - Carrier ID
     */
    getAvailability: async (carrierId) => {
        const response = await integrationClient.get(`/carriers/${carrierId}/availability`);
        return response.data;
    },

    /**
     * Get carrier rates
     * @param {string} carrierId - Carrier ID
     * @param {Object} shipmentDetails - Shipment details for quote
     */
    getRates: async (carrierId, shipmentDetails) => {
        const response = await integrationClient.post(`/carriers/${carrierId}/quote`, shipmentDetails);
        return response.data;
    },

    /**
     * Book carrier for shipment
     * @param {string} carrierId - Carrier ID
     * @param {Object} bookingDetails - Booking details
     */
    bookCarrier: async (carrierId, bookingDetails) => {
        const response = await integrationClient.post(`/carriers/${carrierId}/book`, bookingDetails);
        return response.data;
    },

    /**
     * Get carrier performance metrics
     * @param {string} carrierId - Carrier ID
     * @param {string} period - Time period (week, month, quarter, year)
     */
    getPerformance: async (carrierId, period = 'month') => {
        const response = await integrationClient.get(`/carriers/${carrierId}/performance`, {
            params: { period }
        });
        return response.data;
    },

    /**
     * Get all active carriers
     */
    listCarriers: async () => {
        const response = await integrationClient.get('/carriers');
        return response.data;
    }
};

/**
 * Invoice Integration (Finance Bot)
 */
export const invoiceAPI = {
    /**
     * Get all invoices with filters
     * @param {Object} filters - Filter criteria
     */
    listInvoices: async (filters = {}) => {
        const response = await integrationClient.get('/finance/invoices', { params: filters });
        return response.data;
    },

    /**
     * Get invoice details
     * @param {string} invoiceId - Invoice ID
     */
    getInvoice: async (invoiceId) => {
        const response = await integrationClient.get(`/finance/invoices/${invoiceId}`);
        return response.data;
    },

    /**
     * Create new invoice from shipment
     * @param {Object} invoiceData - Invoice data
     */
    createInvoice: async (invoiceData) => {
        const response = await integrationClient.post('/finance/invoices', invoiceData);
        return response.data;
    },

    /**
     * Generate invoice automatically from shipment
     * @param {string} shipmentId - Shipment reference
     */
    generateFromShipment: async (shipmentId) => {
        const response = await integrationClient.post(`/finance/invoices/generate/${shipmentId}`);
        return response.data;
    },

    /**
     * Update invoice
     * @param {string} invoiceId - Invoice ID
     * @param {Object} updateData - Updated invoice data
     */
    updateInvoice: async (invoiceId, updateData) => {
        const response = await integrationClient.put(`/finance/invoices/${invoiceId}`, updateData);
        return response.data;
    },

    /**
     * Send invoice to client
     * @param {string} invoiceId - Invoice ID
     */
    sendInvoice: async (invoiceId) => {
        const response = await integrationClient.post(`/finance/invoices/${invoiceId}/send`);
        return response.data;
    },

    /**
     * Record payment for invoice
     * @param {string} invoiceId - Invoice ID
     * @param {Object} paymentData - Payment details
     */
    recordPayment: async (invoiceId, paymentData) => {
        const response = await integrationClient.post(`/finance/invoices/${invoiceId}/payment`, paymentData);
        return response.data;
    },

    /**
     * Get invoice PDF
     * @param {string} invoiceId - Invoice ID
     */
    downloadPDF: async (invoiceId) => {
        const response = await integrationClient.get(`/finance/invoices/${invoiceId}/pdf`, {
            responseType: 'blob'
        });
        return response.data;
    }
};

/**
 * Analytics Integration
 */
export const analyticsAPI = {
    /**
     * Get lane profitability analysis
     * @param {string} period - Time period
     */
    getLaneProfitability: async (period = 'month') => {
        const response = await integrationClient.get('/analytics/lanes', { params: { period } });
        return response.data;
    },

    /**
     * Get carrier performance comparison
     * @param {string} period - Time period
     */
    getCarrierPerformance: async (period = 'month') => {
        const response = await integrationClient.get('/analytics/carriers', { params: { period } });
        return response.data;
    },

    /**
     * Get customer DSO (Days Sales Outstanding) analysis
     */
    getCustomerDSO: async () => {
        const response = await integrationClient.get('/analytics/dso');
        return response.data;
    },

    /**
     * Get margin analysis
     * @param {string} groupBy - Group by (lane, customer, carrier, service)
     * @param {string} period - Time period
     */
    getMarginAnalysis: async (groupBy = 'lane', period = 'month') => {
        const response = await integrationClient.get('/analytics/margin', {
            params: { group_by: groupBy, period }
        });
        return response.data;
    },

    /**
     * Get cash flow forecast
     * @param {number} days - Number of days to forecast
     */
    getCashFlowForecast: async (days = 30) => {
        const response = await integrationClient.get('/analytics/cash-flow', { params: { days } });
        return response.data;
    }
};

/**
 * Webhook Management
 */
export const webhookAPI = {
    /**
     * Register webhook endpoint
     * @param {Object} webhookConfig - Webhook configuration
     */
    register: async (webhookConfig) => {
        const response = await integrationClient.post('/webhooks/register', webhookConfig);
        return response.data;
    },

    /**
     * List registered webhooks
     */
    list: async () => {
        const response = await integrationClient.get('/webhooks');
        return response.data;
    },

    /**
     * Delete webhook
     * @param {string} webhookId - Webhook ID
     */
    delete: async (webhookId) => {
        const response = await integrationClient.delete(`/webhooks/${webhookId}`);
        return response.data;
    },

    /**
     * Test webhook endpoint
     * @param {string} webhookId - Webhook ID
     */
    test: async (webhookId) => {
        const response = await integrationClient.post(`/webhooks/${webhookId}/test`);
        return response.data;
    }
};

/**
 * Accounting System Integration
 */
export const accountingAPI = {
    /**
     * Sync invoice to accounting system
     * @param {string} invoiceId - Invoice ID
     */
    syncInvoice: async (invoiceId) => {
        const response = await integrationClient.post(`/accounting/sync/invoice/${invoiceId}`);
        return response.data;
    },

    /**
     * Sync payment to accounting system
     * @param {string} paymentId - Payment ID
     */
    syncPayment: async (paymentId) => {
        const response = await integrationClient.post(`/accounting/sync/payment/${paymentId}`);
        return response.data;
    },

    /**
     * Get sync status
     */
    getSyncStatus: async () => {
        const response = await integrationClient.get('/accounting/sync/status');
        return response.data;
    },

    /**
     * Get chart of accounts mapping
     */
    getAccountMapping: async () => {
        const response = await integrationClient.get('/accounting/mapping');
        return response.data;
    },

    /**
     * Update chart of accounts mapping
     * @param {Object} mapping - Account mapping configuration
     */
    updateAccountMapping: async (mapping) => {
        const response = await integrationClient.put('/accounting/mapping', mapping);
        return response.data;
    }
};

/**
 * CRM Integration
 */
export const crmAPI = {
    /**
     * Sync customer data
     * @param {string} customerId - Customer ID
     */
    syncCustomer: async (customerId) => {
        const response = await integrationClient.post(`/crm/sync/customer/${customerId}`);
        return response.data;
    },

    /**
     * Get customer from CRM
     * @param {string} crmCustomerId - CRM customer ID
     */
    getCustomer: async (crmCustomerId) => {
        const response = await integrationClient.get(`/crm/customer/${crmCustomerId}`);
        return response.data;
    },

    /**
     * Log interaction
     * @param {Object} interaction - Interaction details
     */
    logInteraction: async (interaction) => {
        const response = await integrationClient.post('/crm/interaction', interaction);
        return response.data;
    }
};

export default integrationClient;
