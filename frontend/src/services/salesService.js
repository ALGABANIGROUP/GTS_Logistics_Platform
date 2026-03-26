import axiosClient from '../api/axiosClient';

/**
 * Sales Service - Real API Integration
 * Connects to the active Sales bot through the unified AI route.
 */

class SalesService {
    async runAction(action, context = {}) {
        const response = await axiosClient.post('/api/v1/bots/sales_bot/run', {
            message: action.replaceAll('_', ' '),
            context: {
                action,
                ...context,
            },
            meta: {
                source: 'salesService',
            },
        });

        return response.data?.data || response.data?.result || response.data || {};
    }

    async getStatus() {
        try {
            const response = await axiosClient.get('/api/v1/bots/sales_bot/status');
            return response.data?.data || response.data || {};
        } catch (error) {
            console.error('Failed to get sales bot status:', error);
            throw error;
        }
    }

    async getDashboardData() {
        try {
            return await this.runAction('dashboard');
        } catch (error) {
            console.error('Failed to get sales dashboard:', error);
            throw error;
        }
    }

    async getLeads() {
        try {
            const data = await this.runAction('get_leads');
            return data.leads || [];
        } catch (error) {
            console.error('Failed to get leads:', error);
            return [];
        }
    }

    async getDeals() {
        try {
            const data = await this.runAction('get_deals');
            return data.deals || [];
        } catch (error) {
            console.error('Failed to get deals:', error);
            return [];
        }
    }

    async getCustomers() {
        try {
            const data = await this.runAction('get_customers');
            return data.customers || [];
        } catch (error) {
            console.error('Failed to get customers:', error);
            return [];
        }
    }

    async getForecast(months = 12) {
        try {
            const data = await this.runAction('forecast_revenue', { months });
            return data.forecast?.projections || data.forecast || [];
        } catch (error) {
            console.error('Failed to get forecast:', error);
            return [];
        }
    }

    async createLead(leadData) {
        try {
            return await this.runAction('create_lead', { data: leadData });
        } catch (error) {
            console.error('Failed to create lead:', error);
            throw error;
        }
    }

    async updateLeadStatus(leadId, status) {
        try {
            return await this.runAction('update_lead', {
                lead_id: leadId,
                status,
            });
        } catch (error) {
            console.error('Failed to update lead:', error);
            throw error;
        }
    }

    async createDeal(dealData) {
        try {
            return await this.runAction('create_deal', { data: dealData });
        } catch (error) {
            console.error('Failed to create deal:', error);
            throw error;
        }
    }

    async updateDealStage(dealId, stage) {
        try {
            return await this.runAction('update_deal', {
                deal_id: dealId,
                stage,
            });
        } catch (error) {
            console.error('Failed to update deal:', error);
            throw error;
        }
    }

    async analyzeCustomer(customerId) {
        try {
            return await this.runAction('analyze_customers', {
                customer_id: customerId,
            });
        } catch (error) {
            console.error('Failed to analyze customer:', error);
            throw error;
        }
    }

    async optimizeSales() {
        try {
            return await this.runAction('optimize_sales');
        } catch (error) {
            console.error('Failed to optimize sales:', error);
            throw error;
        }
    }

    async activateBackend() {
        try {
            return await this.runAction('activate');
        } catch (error) {
            console.error('Failed to activate backend:', error);
            throw error;
        }
    }
}

export default new SalesService();
