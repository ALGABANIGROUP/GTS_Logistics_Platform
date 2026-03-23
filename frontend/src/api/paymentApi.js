import axiosClient from './axiosClient';

const API_BASE = '/api/v1/payments';

const paymentApi = {
    async create(data) {
        try {
            console.log('Creating payment with SUDAPAY:', data);

            const response = await axiosClient.post(`${API_BASE}/create`, {
                invoice_id: data.invoice_id,
                amount: data.amount,
                currency: data.currency || 'SDG',
                gateway: data.gateway || 'sudapay',
                description: data.description,
            });

            console.log('Payment created successfully:', response.data);
            return response.data;
        } catch (error) {
            console.error('Failed to create payment:', error.response?.data || error.message);
            throw error;
        }
    },

    async confirm(paymentId, options = {}) {
        try {
            console.log('Confirming payment:', paymentId);

            const response = await axiosClient.post(
                `${API_BASE}/${paymentId}/confirm`,
                options,
            );

            console.log('Payment confirmed:', response.data);
            return response.data;
        } catch (error) {
            console.error('Failed to confirm payment:', error.response?.data || error.message);
            throw error;
        }
    },

    async refund(paymentId, data = {}) {
        try {
            console.log('Processing refund for payment:', paymentId);

            const response = await axiosClient.post(
                `${API_BASE}/${paymentId}/refund`,
                {
                    amount: data.amount,
                    reason: data.reason || 'Customer request',
                },
            );

            console.log('Refund processed:', response.data);
            return response.data;
        } catch (error) {
            console.error('Failed to refund payment:', error.response?.data || error.message);
            throw error;
        }
    },

    async get(paymentId) {
        try {
            console.log('Fetching payment details:', paymentId);

            const response = await axiosClient.get(`${API_BASE}/${paymentId}`);
            return response.data;
        } catch (error) {
            console.error('Failed to get payment:', error.response?.data || error.message);
            throw error;
        }
    },

    async getInvoicePayments(invoiceId) {
        try {
            console.log('Fetching payments for invoice:', invoiceId);

            const response = await axiosClient.get(`${API_BASE}/invoice/${invoiceId}`);
            return response.data || [];
        } catch (error) {
            console.error('Failed to get invoice payments:', error.response?.data || error.message);
            throw error;
        }
    },

    async getUserHistory(options = {}) {
        try {
            const limit = options.limit || 50;
            const offset = options.offset || 0;

            console.log('Fetching payment history');

            const response = await axiosClient.get(
                `${API_BASE}/user/history?limit=${limit}&offset=${offset}`,
            );

            if (response.data?.items) {
                return response.data;
            }
            return response.data || [];
        } catch (error) {
            console.error('Failed to get payment history:', error.response?.data || error.message);
            throw error;
        }
    },

    async getStats(options = {}) {
        const historyResponse = await this.getUserHistory(options);
        const items = Array.isArray(historyResponse?.items) ? historyResponse.items : [];

        const totalAmount = items.reduce((sum, item) => sum + Number(item.amount || 0), 0);
        const completedItems = items.filter((item) => String(item.status || "").toLowerCase() === "completed");
        const pendingItems = items.filter((item) =>
            ["pending", "processing"].includes(String(item.status || "").toLowerCase())
        );

        const paymentMethodMap = items.reduce((acc, item) => {
            const key = String(item.payment_gateway || item.gateway || "unknown").toLowerCase();
            if (!acc[key]) {
                acc[key] = {
                    name: this.getGatewayName(key).toUpperCase(),
                    usage_count: 0,
                };
            }
            acc[key].usage_count += 1;
            return acc;
        }, {});

        return {
            total_payments: items.length,
            total_amount: totalAmount,
            success_rate: items.length ? Number(((completedItems.length / items.length) * 100).toFixed(1)) : 0,
            pending_invoices: pendingItems.length,
            recent_payments: items.slice(0, 10).map((item) => ({
                id: item.id,
                date: item.created_at,
                amount: Number(item.amount || 0),
                status: String(item.status || "").toLowerCase(),
                method: this.getGatewayName(item.payment_gateway || item.gateway || "unknown"),
                currency: item.currency || "SDG",
                reference_id: item.reference_id,
            })),
            payment_methods: Object.values(paymentMethodMap),
            items,
        };
    },

    async handleSudapaySuccess(paymentId) {
        try {
            console.log('SUDAPAY success handler - loading payment state');
            const result = await this.get(paymentId);
            console.log('Payment state loaded:', result);
            return result;
        } catch (error) {
            console.error('Payment confirmation failed:', error);
            throw error;
        }
    },

    async handleSudapayFailure(paymentId, reason = 'Unknown error') {
        try {
            console.log('SUDAPAY failure handler:', reason);

            return {
                status: 'failed',
                paymentId,
                reason,
            };
        } catch (error) {
            console.error('Payment failure handler error:', error);
            throw error;
        }
    },

    formatAmount(amount, currency = 'SDG') {
        const formatter = new Intl.NumberFormat('ar-SD', {
            style: 'currency',
            currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 2,
        });

        return formatter.format(amount);
    },

    getGatewayName(gateway) {
        const gateways = {
            sudapay: 'SUDAPAY',
            stripe: 'Stripe',
            paypal: 'PayPal',
        };
        return gateways[gateway] || gateway;
    },

    getPaymentStatus(status) {
        const statuses = {
            pending: { label: 'قيد الانتظار', icon: '⏳', color: 'warning' },
            processing: { label: 'قيد المعالجة', icon: '🔄', color: 'info' },
            completed: { label: 'مكتمل', icon: '✅', color: 'success' },
            failed: { label: 'فاشل', icon: '❌', color: 'danger' },
            cancelled: { label: 'ملغى', icon: '⏹️', color: 'secondary' },
            refunded: { label: 'مسترجع', icon: '↩️', color: 'info' },
        };
        return statuses[status] || { label: 'غير معروف', icon: '❓', color: 'dark' };
    },
};

export default paymentApi;
