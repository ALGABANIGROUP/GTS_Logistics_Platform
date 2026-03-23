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
            return {
                leads: [
                    { id: 1, name: 'Acme Corp', contact: 'John Smith', email: 'john@acme.com', status: 'QUALIFIED', value: 250000, source: 'linkedin' },
                    { id: 2, name: 'TechStart Inc', contact: 'Sarah Johnson', email: 'sarah@techstart.com', status: 'PROPOSAL', value: 180000, source: 'referral' },
                    { id: 3, name: 'Global Industries', contact: 'Mike Davis', email: 'mike@global.com', status: 'NEW', value: 150000, source: 'website' }
                ],
                deals: [
                    { id: 1, customer: 'Acme Corp', value: 500000, stage: 'NEGOTIATION', probability: 75, expected_close: '2026-03-15' },
                    { id: 2, customer: 'TechStart Inc', value: 350000, stage: 'PROPOSAL', probability: 60, expected_close: '2026-02-28' },
                    { id: 3, customer: 'Global Industries', value: 800000, stage: 'DISCOVERY', probability: 40, expected_close: '2026-04-30' }
                ],
                customers: [
                    { id: 1, name: 'Acme Corp', segment: 'VIP', lifetime_value: 2500000, health: 95 },
                    { id: 2, name: 'TechStart Inc', segment: 'REGULAR', lifetime_value: 850000, health: 80 },
                    { id: 3, name: 'Global Industries', segment: 'POTENTIAL', lifetime_value: 1200000, health: 70 }
                ],
                forecast: [
                    { month: '2026-04', projected: 1200000, actual: 980000 },
                    { month: '2026-05', projected: 1500000, actual: null },
                    { month: '2026-06', projected: 1800000, actual: null }
                ],
                stats: {
                    totalLeads: 15,
                    totalDeals: 8,
                    totalRevenue: 1650000,
                    conversionRate: 45
                }
            };
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
