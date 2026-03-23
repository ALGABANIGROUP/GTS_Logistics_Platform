// frontend/src/api/expensesApi.js
import axiosClient from "./axiosClient";

export const expensesApi = {
    // Fetch all expenses
    getAll: () => axiosClient.get("/finance/expenses"),

    // Fetch a single expense by ID
    getById: (id) => axiosClient.get(`/finance/expenses/${id}`),

    // Create a new expense
    create: (data) => axiosClient.post("/finance/expenses", data),

    // Update an existing expense
    update: (id, data) => axiosClient.put(`/finance/expenses/${id}`, data),

    // Delete an expense
    delete: (id) => axiosClient.delete(`/finance/expenses/${id}`),

    // Toggle expense status (active/inactive)
    toggleStatus: (id) => axiosClient.put(`/finance/expenses/${id}/status`),

    // Get expense statistics
    getStats: () => axiosClient.get("/finance/expenses/stats"),
};
