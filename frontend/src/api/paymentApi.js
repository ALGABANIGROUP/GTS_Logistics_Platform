import axiosClient from './axiosClient';

const API_BASE = '/api/v1/payments';
const DEFAULT_CURRENCY = 'USD';
const DEFAULT_GATEWAY = 'stripe';
const USE_MOCK_DATA = true;

const paymentApi = {
    async create(data) {
        try {
            console.log('Creating payment:', data);

            const response = await axiosClient.post(`${API_BASE}/create`, {
                invoice_id: data.invoice_id,
                amount: data.amount,
                currency: data.currency || DEFAULT_CURRENCY,
                gateway: data.gateway || DEFAULT_GATEWAY,
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
        if (USE_MOCK_DATA) {
            return {
                transactions: [
                    { id: 1, customer: "Fast Freight Inc.", amount: 12500, status: "completed", date: new Date().toISOString(), method: "credit_card", type: "payment" },
                    { id: 2, customer: "Maple Load Canada", amount: 8750, status: "pending", date: new Date().toISOString(), method: "bank_transfer", type: "invoice" },
                    { id: 3, customer: "GTS Logistics", amount: 34200, status: "completed", date: new Date(Date.now() - 86400000).toISOString(), method: "credit_card", type: "payment" },
                    { id: 4, customer: "ABC Manufacturing", amount: 5600, status: "completed", date: new Date(Date.now() - 172800000).toISOString(), method: "paypal", type: "payment" }
                ],
                total: 4,
                balance: 261100,
                items: [
                    { id: 1, amount: 12500, status: "completed", created_at: new Date().toISOString(), payment_gateway: "credit_card" },
                    { id: 2, amount: 8750, status: "pending", created_at: new Date().toISOString(), payment_gateway: "bank_transfer" },
                    { id: 3, amount: 34200, status: "completed", created_at: new Date(Date.now() - 86400000).toISOString(), payment_gateway: "credit_card" },
                    { id: 4, amount: 5600, status: "completed", created_at: new Date(Date.now() - 172800000).toISOString(), payment_gateway: "paypal" }
                ]
            };
        }

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
        if (USE_MOCK_DATA) {
            return {
                total_payments: 156,
                total_amount: 284500,
                success_rate: 94.2,
                pending_invoices: 3,
                recent_payments: [
                    { id: 1, date: new Date().toISOString(), amount: 12500, status: "completed", method: "Credit Card", currency: "USD", reference_id: "REF001" },
                    { id: 2, date: new Date().toISOString(), amount: 8750, status: "pending", method: "Bank Transfer", currency: "USD", reference_id: "REF002" },
                    { id: 3, date: new Date(Date.now() - 86400000).toISOString(), amount: 34200, status: "completed", method: "Credit Card", currency: "USD", reference_id: "REF003" },
                    { id: 4, date: new Date(Date.now() - 172800000).toISOString(), amount: 5600, status: "completed", method: "Paypal", currency: "USD", reference_id: "REF004" }
                ],
                payment_methods: [
                    { name: "CREDIT_CARD", usage_count: 89 },
                    { name: "BANK_TRANSFER", usage_count: 45 },
                    { name: "PAYPAL", usage_count: 22 }
                ],
                items: [
                    { id: 1, amount: 12500, status: "completed", created_at: new Date().toISOString(), payment_gateway: "credit_card" },
                    { id: 2, amount: 8750, status: "pending", created_at: new Date().toISOString(), payment_gateway: "bank_transfer" },
                    { id: 3, amount: 34200, status: "completed", created_at: new Date(Date.now() - 86400000).toISOString(), payment_gateway: "credit_card" },
                    { id: 4, amount: 5600, status: "completed", created_at: new Date(Date.now() - 172800000).toISOString(), payment_gateway: "paypal" }
                ]
            };
        }

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
                currency: item.currency || DEFAULT_CURRENCY,
                reference_id: item.reference_id,
            })),
            payment_methods: Object.values(paymentMethodMap),
            items,
        };
    },

    async handlePaymentSuccess(paymentId) {
        try {
            console.log('Loading payment state after gateway success');
            const result = await this.get(paymentId);
            console.log('Payment state loaded:', result);
            return result;
        } catch (error) {
            console.error('Payment confirmation failed:', error);
            throw error;
        }
    },

    async handlePaymentFailure(paymentId, reason = 'Unknown error') {
        try {
            console.log('Payment failure handler:', reason);

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

    formatAmount(amount, currency = 'USD') {
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
            stripe: 'Stripe',
        };
        return gateways[gateway] || gateway;
    },

    getPaymentStatus(status) {
        const statuses = {
            pending: { label: 'Pending', icon: '⏳', color: 'warning' },
            processing: { label: 'Processing', icon: '🔄', color: 'info' },
            completed: { label: 'Completed', icon: '✅', color: 'success' },
            failed: { label: 'Failed', icon: '❌', color: 'danger' },
            cancelled: { label: 'Cancelled', icon: '⏹️', color: 'secondary' },
            refunded: { label: 'Refunded', icon: '↩️', color: 'info' },
        };
        return statuses[status] || { label: 'Unknown', icon: '❓', color: 'dark' };
    },
};

export default paymentApi;
