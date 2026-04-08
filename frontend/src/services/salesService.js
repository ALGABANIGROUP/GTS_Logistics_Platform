// frontend/src/services/salesService.js
import axiosClient from '../api/axiosClient';

// Use Mock Data temporarily
const USE_MOCK_DATA = true;

export const SalesService = {
  /**
  * Get sales dashboard data
   */
  async getDashboardData() {
    if (USE_MOCK_DATA) {
      // Test data
      return {
        summary: {
          total_revenue: 284500,
          total_orders: 156,
          active_customers: 42,
          conversion_rate: 24.5,
          average_order_value: 1824,
          revenue_growth: 15.5,
          monthly_target: 300000,
          monthly_achieved: 284500
        },
        recent_activities: [
          { id: 1, action: "New lead acquired", customer: "Fast Freight Inc.", value: 12500, status: "qualified", date: new Date().toISOString() },
          { id: 2, action: "Quote sent", customer: "Maple Load Canada", value: 8750, status: "pending", date: new Date().toISOString() },
          { id: 3, action: "Deal closed", customer: "GTS Logistics", value: 34200, status: "won", date: new Date(Date.now() - 86400000).toISOString() }
        ],
        pipeline: [
          { stage: "Lead", count: 23, value: 184000 },
          { stage: "Qualified", count: 15, value: 125000 },
          { stage: "Proposal", count: 8, value: 89000 },
          { stage: "Negotiation", count: 5, value: 67000 },
          { stage: "Closed Won", count: 12, value: 245000 }
        ],
        top_customers: [
          { id: 1, name: "Fast Freight Inc.", revenue: 125000, orders: 28, last_order: "2026-04-01" },
          { id: 2, name: "Maple Load Canada", revenue: 89000, orders: 19, last_order: "2026-03-28" },
          { id: 3, name: "GTS Logistics", revenue: 67000, orders: 15, last_order: "2026-03-25" }
        ],
        performance_metrics: [
          { metric: "Calls Made", target: 200, achieved: 185, percentage: 92.5 },
          { metric: "Meetings Scheduled", target: 50, achieved: 42, percentage: 84 },
          { metric: "Proposals Sent", target: 30, achieved: 28, percentage: 93.3 },
          { metric: "Deals Closed", target: 20, achieved: 18, percentage: 90 }
        ],
        bot_status: {
          name: "AI Sales Bot",
          status: "active",
          last_run: new Date().toISOString(),
          tasks_completed: 156,
          success_rate: 94.5
        }
      };
    }

    // Original code for real API connection
    try {
      const response = await axiosClient.get('/api/v1/sales/dashboard');
      return response.data;
    } catch (error) {
      console.error('Error fetching sales dashboard:', error);
      throw error;
    }
  },

  /**
  * Get customer list
   */
  async getCustomers() {
    if (USE_MOCK_DATA) {
      return [
        { id: 1, name: "Fast Freight Inc.", email: "contact@fastfreight.com", phone: "+1-800-555-0100", status: "active", total_spent: 125000 },
        { id: 2, name: "Maple Load Canada", email: "info@mapleload.ca", phone: "+1-800-555-0200", status: "active", total_spent: 89000 },
        { id: 3, name: "GTS Logistics", email: "info@gtslogistics.com", phone: "+1-800-555-0300", status: "active", total_spent: 67000 }
      ];
    }
    try {
      const response = await axiosClient.get('/api/v1/sales/customers');
      return response.data;
    } catch (error) {
      console.error('Error fetching customers:', error);
      throw error;
    }
  },

  /**
  * Get sales list
   */
  async getSales() {
    if (USE_MOCK_DATA) {
      return [
        { id: 1, customer: "Fast Freight Inc.", amount: 12500, date: new Date().toISOString(), status: "completed" },
        { id: 2, customer: "Maple Load Canada", amount: 8750, date: new Date().toISOString(), status: "pending" },
        { id: 3, customer: "GTS Logistics", amount: 34200, date: new Date(Date.now() - 86400000).toISOString(), status: "completed" }
      ];
    }
    try {
      const response = await axiosClient.get('/api/v1/sales/list');
      return response.data;
    } catch (error) {
      console.error('Error fetching sales:', error);
      throw error;
    }
  },

  /**
  * Create new deal
   */
  async createDeal(data) {
    if (USE_MOCK_DATA) {
      return { id: Date.now(), ...data, status: "pending", created_at: new Date().toISOString() };
    }
    try {
      const response = await axiosClient.post('/api/v1/sales/deals', data);
      return response.data;
    } catch (error) {
      console.error('Error creating deal:', error);
      throw error;
    }
  }
};

export default SalesService;