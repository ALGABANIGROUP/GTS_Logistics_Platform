import axiosClient from "./api/axiosClient";

const unwrap = (response) => response?.data ?? response;

const normalizeAnalysis = (payload) => {
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
};

export const api = {
  getWeeklyReports: async (params = {}) => {
    const sinceDays = params.since_days || 7;
    const response = await axiosClient.get("/reports/weekly", {
      params: { since_days: sinceDays, format: "json", save: false },
    });
    return unwrap(response);
  },

  getAiGeneralAnalysis: async (params = {}) => {
    const response = await axiosClient.post(
      "/api/v1/ai/bots/available/general_manager/run",
      {
        message: "analysis",
        context: params || {},
        meta: { source: "ui" },
      }
    );
    return normalizeAnalysis(unwrap(response));
  },

  getSystemHealth: async () => {
    const response = await axiosClient.get("/ai/system/health");
    return unwrap(response);
  },

  getAIBotsStatus: async () => {
    const response = await axiosClient.get("/api/v1/ai/bots/available");
    return unwrap(response);
  },

  get: async (endpoint, config = {}) => {
    const response = await axiosClient.get(endpoint, config);
    return unwrap(response);
  },

  post: async (endpoint, data, config = {}) => {
    const response = await axiosClient.post(endpoint, data, config);
    return unwrap(response);
  },
};

export const getWeeklyReport = (params = {}) => api.getWeeklyReports(params);
export const getAiGeneralAnalysis = (params = {}) =>
  api.getAiGeneralAnalysis(params);
export const getSystemHealth = () => api.getSystemHealth();
export const getAIBotsStatus = () => api.getAIBotsStatus();

export default api;
