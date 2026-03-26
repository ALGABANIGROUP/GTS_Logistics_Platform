import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Report, PredefinedReport } from "../models/Report";
import { downloadBlob } from "../utils/exportUtils";
import axiosClient from "../api/axiosClient";

const CATEGORY_LIST = [
    { id: "users", name: "Users", icon: "fas fa-users", color: "#3B82F6" },
    { id: "system", name: "System", icon: "fas fa-cogs", color: "#10B981" },
    { id: "shipments", name: "Shipments", icon: "fas fa-truck", color: "#F59E0B" },
    { id: "finance", name: "Finance", icon: "fas fa-money-bill-wave", color: "#EF4444" },
    { id: "marketing", name: "Marketing", icon: "fas fa-bullhorn", color: "#06B6D4" },
    { id: "support", name: "Support", icon: "fas fa-headset", color: "#84CC16" },
];

const DEFAULT_SETTINGS = {
    defaultFormat: "dashboard",
    autoRefresh: true,
    refreshInterval: 300,
    dataRetention: 365,
    maxExportSize: 100000,
    exportFormats: ["pdf", "excel", "csv", "json"],
    chartTypes: ["line", "bar", "pie", "area", "scatter", "radar"],
    theme: "dark",
};

const buildReportQueryParams = (filters = {}) => {
    const params = {};
    ["category", "status", "period", "search"].forEach((key) => {
        if (filters?.[key]) {
            params[key] = filters[key];
        }
    });
    return params;
};

const buildStatsFromReports = (reports, categories) => {
    const total = reports.length;
    const active = reports.filter((report) => report.status === "active").length;
    const scheduled = reports.filter(
        (report) => report.settings?.autoGenerate && report.settings?.refreshInterval > 0
    ).length;
    const byCategory = {};
    (categories || []).forEach((category) => {
        byCategory[category.id] = reports.filter((report) => report.category === category.id).length;
    });
    const recent = [...reports]
        .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
        .slice(0, 5);
    return { total, active, scheduled, byCategory, recent };
};

export const useReportsStore = create(
    persist(
        (set, get) => ({
            reports: [],
            templates: [],
            categories: CATEGORY_LIST,
            loading: false,
            error: null,
            stats: {
                total: 0,
                active: 0,
                scheduled: 0,
                byCategory: {},
                recent: [],
            },
            settings: DEFAULT_SETTINGS,

            activeReports: () => get().reports.filter((r) => r.status === "active"),
            scheduledReports: () => get().reports.filter((r) => r.settings?.autoGenerate && r.settings?.refreshInterval > 0),
            reportsByCategory: (category) => get().reports.filter((r) => r.category === category),
            publicReports: () => get().reports.filter((r) => r.isPublic),
            favoriteReports: () => get().reports.filter((r) => r.tags?.includes("favorite")),

            buildPreviewModel: () => {
                const now = new Date();
                const reportName = "Operations Preview Model";
                return {
                    report: {
                        name: reportName,
                        description: "Instant preview model for layout and data validation",
                    },
                    summary: {
                        shipments: {
                            name: "Active Shipments",
                            average: 142,
                            total: 142,
                        },
                        revenue: {
                            name: "Monthly Revenue",
                            average: 284500,
                            total: 284500,
                        },
                        incidents: {
                            name: "Open Incidents",
                            average: 7,
                            total: 7,
                        },
                        sla: {
                            name: "SLA Compliance %",
                            average: 96.4,
                            total: 96.4,
                        },
                    },
                    insights: [
                        {
                            metric: "Monthly Revenue",
                            description: "Revenue increased by 12.4% compared to last period.",
                        },
                        {
                            metric: "SLA Compliance %",
                            description: "SLA remains above target threshold with stable trend.",
                        },
                        {
                            metric: "Open Incidents",
                            description: "Incident volume dropped after maintenance automation rollout.",
                        },
                    ],
                    data: [
                        { date: "2026-03-11", shipments: 131, revenue: 87400, incidents: 3, sla: 95.1 },
                        { date: "2026-03-12", shipments: 138, revenue: 90250, incidents: 2, sla: 96.0 },
                        { date: "2026-03-13", shipments: 145, revenue: 95600, incidents: 1, sla: 97.2 },
                        { date: "2026-03-14", shipments: 149, revenue: 98500, incidents: 1, sla: 96.8 },
                        { date: "2026-03-15", shipments: 147, revenue: 100250, incidents: 0, sla: 97.0 },
                    ],
                    metadata: {
                        generatedAt: now.toISOString(),
                        source: "preview-model",
                        dataPoints: 5,
                    },
                };
            },

            fetchReports: async (filters = {}) => {
                set({ loading: true, error: null });
                try {
                    const params = buildReportQueryParams(filters);
                    const [listResponse, statsResponse] = await Promise.all([
                        axiosClient.get("/api/v1/reports/list", { params }),
                        axiosClient.get("/api/v1/reports/stats"),
                    ]);

                    const realReports = Array.isArray(listResponse?.data?.reports)
                        ? listResponse.data.reports
                        : [];
                    const reports = realReports.map((report) => new Report(report));
                    const fallbackStats = buildStatsFromReports(reports, get().categories);
                    const backendStats = statsResponse?.data || {};
                    set({
                        reports,
                        stats: {
                            total: backendStats.total ?? fallbackStats.total,
                            active: backendStats.active ?? fallbackStats.active,
                            scheduled: backendStats.scheduled ?? fallbackStats.scheduled,
                            byCategory: backendStats.byCategory ?? fallbackStats.byCategory,
                            recent: fallbackStats.recent,
                        },
                    });
                } catch (error) {
                    set({
                        reports: [],
                        stats: buildStatsFromReports([], get().categories),
                        error:
                            error?.response?.data?.detail ||
                            error?.response?.data?.message ||
                            error?.message ||
                            "Failed to load reports",
                    });
                    throw error;
                } finally {
                    set({ loading: false });
                }
            },

            createReport: async (reportData) => {
                const report = reportData.type === "predefined" ? new PredefinedReport(reportData) : new Report(reportData);
                set((state) => ({ reports: [report, ...state.reports] }));
                get().updateStats();
                return report;
            },

            updateReport: async (reportId, updates) => {
                set((state) => ({
                    reports: state.reports.map((r) => {
                        if (r.id !== reportId) return r;
                        const updated = r instanceof Report ? r : new Report(r);
                        updated.update(updates);
                        return updated;
                    }),
                }));
                get().updateStats();
            },

            deleteReport: async (reportId) => {
                set((state) => ({ reports: state.reports.filter((r) => r.id !== reportId) }));
                get().updateStats();
            },

            toggleReportStatus: async (reportId, status) => {
                await get().updateReport(reportId, { status });
            },

            generateReport: async (reportId, options = {}) => {
                const report = get().reports.find((r) => r.id === reportId);
                if (!report) throw new Error("Report not found");

                try {
                    const response = await axiosClient.get(`/api/v1/reports/generate/${reportId}`, {
                        params: { format: "json" },
                    });
                    const reportData = response?.data || {};
                    await get().updateReport(reportId, {
                        lastGeneratedAt: reportData.metadata?.generatedAt || new Date().toISOString(),
                        generationCount: (report.generationCount || 0) + 1,
                    });
                    return reportData;
                } catch (apiError) {
                    set({
                        error:
                            apiError?.response?.data?.detail ||
                            apiError?.response?.data?.message ||
                            apiError?.message ||
                            "Failed to generate report",
                    });
                    throw apiError;
                }
            },

            exportReport: async (reportId, format, options = {}) => {
                try {
                    const response = await axiosClient.get(`/api/v1/reports/export/${reportId}`, {
                        params: { format },
                        responseType: "blob",
                    });

                    const extension = format === "excel" ? "xls" : format;
                    const fileName = `${String(reportId).replace(/\s+/g, "_")}.${extension}`;
                    downloadBlob(fileName, response.data);
                    return { fileName, format: extension, size: `${response.data?.size || 0} bytes` };
                } catch (apiError) {
                    set({
                        error:
                            apiError?.response?.data?.detail ||
                            apiError?.response?.data?.message ||
                            apiError?.message ||
                            "Failed to export report",
                    });
                    throw apiError;
                }
            },

            scheduleReport: async (reportId, schedule) => {
                await get().updateReport(reportId, {
                    settings: { autoGenerate: true, refreshInterval: schedule.interval },
                    schedule,
                });
            },

            unscheduleReport: async (reportId) => {
                await get().updateReport(reportId, {
                    settings: { autoGenerate: false, refreshInterval: 0 },
                });
            },

            duplicateReport: async (reportId, newName) => {
                const original = get().reports.find((r) => r.id === reportId);
                if (!original) throw new Error("Report not found");

                const duplicated = new Report({
                    ...original,
                    id: `report_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                    name: newName || `${original.name} (Copy)`,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    lastGeneratedAt: null,
                    generationCount: 0,
                    history: [],
                });

                set((state) => ({ reports: [duplicated, ...state.reports] }));
                get().updateStats();
                return duplicated;
            },

            getCategoryName: (categoryId) => {
                const category = get().categories.find((c) => c.id === categoryId);
                return category ? category.name : categoryId;
            },

            updateStats: () => {
                const reports = get().reports;
                const total = reports.length;
                const active = reports.filter((r) => r.status === "active").length;
                const scheduled = reports.filter((r) => r.settings?.autoGenerate && r.settings?.refreshInterval > 0).length;

                const byCategory = {};
                get().categories.forEach((cat) => {
                    byCategory[cat.id] = reports.filter((r) => r.category === cat.id).length;
                });

                const recent = [...reports].sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt)).slice(0, 5);

                set({ stats: { total, active, scheduled, byCategory, recent } });
            },
        }),
        {
            name: "reports-store",
            partialize: (state) => ({ reports: state.reports, settings: state.settings }),
        }
    )
);
