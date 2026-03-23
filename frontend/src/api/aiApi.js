// frontend/src/api/aiApi.js
import axiosClient from "./axiosClient";

export const aiApi = {
    // AI General Analysis (live only)
    getGeneralAnalysis: async (params) => {
        const response = await axiosClient.post("/api/v1/ai/bots/available/general_manager/run", {
            message: "analysis",
            context: params || {},
            meta: { source: "ui" },
        });
        const payload = response?.data || {};
        const report =
            payload?.result?.report ||
            payload?.report ||
            payload?.data?.report ||
            payload?.data ||
            {};
        const finance = report?.finance || {};
        const revenue =
            finance.revenue_total ??
            finance.total_revenue ??
            finance.total_income ??
            0;
        const expenses =
            finance.expenses_total ??
            finance.total_expenses ??
            finance.total_cost ??
            0;
        const profit =
            report?.kpis?.profit ??
            (typeof revenue === "number" && typeof expenses === "number"
                ? revenue - expenses
                : 0);
        return {
            total_income: revenue,
            total_expense: expenses,
            profit,
            month: report?.period_label || report?.period?.start || "",
            report,
        };
    },

    // Weekly Reports (live only)
    getWeeklyReports: async (params) => {
        const response = await axiosClient.get("/api/reports/weekly", { params });
        console.log("âœ… Using real weekly reports data");
        return response;
    },

    // AI Bots Status (live only)
    getAIBotsStatus: async () => {
        return await axiosClient.get("/api/v1/ai/bots/available");
    },

    // System Health (live only)
    getSystemHealth: async () => {
        return await axiosClient.get("/api/ai/system/health");
    }
};
