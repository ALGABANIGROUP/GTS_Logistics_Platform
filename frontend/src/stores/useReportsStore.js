import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Report, PredefinedReport } from "../models/Report";
import { downloadBlob, exportWorkbookXml, openPrintDocument } from "../utils/exportUtils";
import { getDocumentLogoDataUrl } from "../utils/documentBranding";
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
                    try {
                        const params = buildReportQueryParams(filters);
                        const [listResponse, statsResponse] = await Promise.all([
                            axiosClient.get("/api/v1/reports/list", { params }),
                            axiosClient.get("/api/v1/reports/stats"),
                        ]);

                        const realReports = listResponse?.data?.reports || [];
                        if (Array.isArray(realReports) && realReports.length) {
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
                            return;
                        }
                    } catch (apiError) {
                        console.warn("Failed to fetch real reports data, falling back to mock data:", apiError);
                    }

                    const mockReports = get().generateMockReports(15);
                    set({
                        reports: mockReports,
                        stats: buildStatsFromReports(mockReports, get().categories),
                    });
                    get().updateStats();
                } catch (error) {
                    set({ error: error?.message || "Failed to load reports" });
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
                    console.warn("Live report generation failed, falling back to local generator:", apiError);
                }

                const reportInstance = report instanceof Report ? report : new Report(report);
                const reportData = await get().generateReportData(reportInstance, options);

                reportInstance.lastGeneratedAt = new Date().toISOString();
                reportInstance.generationCount = (reportInstance.generationCount || 0) + 1;
                reportInstance.addToHistory("generated", {
                    options,
                    dataPoints: reportData.data?.length || 0,
                    timestamp: new Date().toISOString(),
                });

                await get().updateReport(reportId, reportInstance);
                return reportData;
            },

            generateReportData: async (report) => {
                const dateRange = report.calculateDateRange();
                const { start, end } = dateRange;
                const data = [];
                const daysDiff = Math.ceil((end - start) / (1000 * 60 * 60 * 24));

                for (let i = 0; i < Math.min(daysDiff, report.settings.dataPoints); i += 1) {
                    const date = new Date(start);
                    date.setDate(start.getDate() + i);

                    const baseData = {
                        date: date.toISOString().split("T")[0],
                        timestamp: date.toISOString(),
                        value: Math.random() * 1000 + 500,
                        count: Math.floor(Math.random() * 100) + 10,
                        percentage: Math.random() * 100,
                        duration: Math.random() * 3600 + 600,
                    };

                    report.metrics.forEach((metric) => {
                        switch (metric.type) {
                            case "currency":
                                baseData[metric.id] = Math.random() * 10000 + 1000;
                                break;
                            case "count":
                                baseData[metric.id] = Math.floor(Math.random() * 1000) + 100;
                                break;
                            case "percentage":
                                baseData[metric.id] = Math.random() * 100;
                                break;
                            case "duration":
                                baseData[metric.id] = Math.random() * 3600 + 600;
                                break;
                            default:
                                baseData[metric.id] = Math.random() * 1000;
                        }
                    });

                    data.push(baseData);
                }

                const summary = get().analyzeData(data, report.metrics);
                const charts = get().generateCharts(data, report.charts);
                const insights = get().extractInsights(data, report.metrics);

                return {
                    report: report.toJSON(),
                    data,
                    summary,
                    charts,
                    insights,
                    metadata: {
                        generatedAt: new Date().toISOString(),
                        dataPoints: data.length,
                        dateRange: {
                            start: start.toISOString(),
                            end: end.toISOString(),
                            days: daysDiff,
                        },
                        filters: report.criteria.filters,
                    },
                };
            },

            analyzeData: (data, metrics) => {
                if (!data.length) return {};

                const summary = {};
                metrics.forEach((metric) => {
                    const values = data.map((d) => d[metric.id]).filter((v) => v != null);
                    if (values.length > 0) {
                        summary[metric.id] = {
                            name: metric.name,
                            type: metric.type,
                            total: values.reduce((a, b) => a + b, 0),
                            average: values.reduce((a, b) => a + b, 0) / values.length,
                            min: Math.min(...values),
                            max: Math.max(...values),
                            count: values.length,
                            lastValue: values[values.length - 1],
                            change: values.length > 1 ? ((values[values.length - 1] - values[0]) / values[0] * 100) : 0,
                        };
                    }
                });

                return summary;
            },

            generateCharts: (data, chartConfigs) =>
                (chartConfigs || []).map((config) => ({
                    id: `chart_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                    type: config.type,
                    title: config.title,
                    data: data.map((d) => ({ x: d[config.dimension], y: d[config.metric] })),
                    config: {
                        backgroundColor: "rgba(59, 130, 246, 0.1)",
                        borderColor: "#3B82F6",
                        pointBackgroundColor: "#3B82F6",
                    },
                })),

            extractInsights: (data, metrics) => {
                const insights = [];
                if (data.length < 2) return insights;

                metrics.forEach((metric) => {
                    const values = data.map((d) => d[metric.id]);
                    const firstValue = values[0];
                    const lastValue = values[values.length - 1];
                    const change = ((lastValue - firstValue) / firstValue) * 100;

                    if (Math.abs(change) > 10) {
                        insights.push({
                            type: change > 0 ? "increase" : "decrease",
                            metric: metric.name,
                            change: Math.abs(change).toFixed(1),
                            description: `${metric.name} ${change > 0 ? "increased" : "decreased"} by ${Math.abs(change).toFixed(1)}% during the period`,
                            significance: Math.abs(change) > 50 ? "high" : Math.abs(change) > 20 ? "medium" : "low",
                        });
                    }

                    const maxValue = Math.max(...values);
                    if (maxValue > firstValue * 2) {
                        insights.push({
                            type: "peak",
                            metric: metric.name,
                            value: maxValue.toFixed(0),
                            description: `${metric.name} reached a peak value (${maxValue.toFixed(0)}) during the period`,
                            significance: "medium",
                        });
                    }
                });

                return insights.slice(0, 5);
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
                    console.warn("Live report export failed, falling back to local export:", apiError);
                }

                const reportData = await get().generateReport(reportId, options);

                switch (format) {
                    case "pdf":
                        return get().exportToPDF(reportData, options);
                    case "excel":
                        return get().exportToExcel(reportData, options);
                    case "csv":
                        return get().exportToCSV(reportData, options);
                    case "json":
                        return get().exportToJSON(reportData, options);
                    default:
                        throw new Error("Unsupported export format");
                }
            },

            exportToPDF: async (reportData) => {
                const reportName = reportData.report.name || "Report";
                const fileName = reportData.report.generateFileName("pdf");
                const logoDataUrl = await getDocumentLogoDataUrl();

                openPrintDocument({
                    title: reportName,
                    subtitle: `Generated: ${new Date().toLocaleString()}`,
                    logoDataUrl,
                    sections: [
                        {
                            type: "list",
                            title: "Summary",
                            items: Object.values(reportData.summary || {}).slice(0, 6).map((metric) =>
                                `${metric.name}: ${metric.average?.toFixed?.(2) ?? metric.total ?? "-"}`
                            ),
                        },
                        {
                            type: "list",
                            title: "Insights",
                            items: (reportData.insights || []).map((insight) => insight.description),
                        },
                        {
                            type: "table",
                            title: "Data Preview",
                            headers: Object.keys(reportData.data?.[0] || {}),
                            rows: (reportData.data || []).slice(0, 25).map((row) => Object.values(row || {})),
                        },
                    ],
                });

                return { fileName, format: "pdf", size: "~60KB" };
            },

            exportToExcel: async (reportData) => {
                const fileName = reportData.report.generateFileName("xls");
                const dataRows = reportData.data || [];
                const headers = Object.keys(dataRows[0] || {});

                exportWorkbookXml({
                    fileName,
                    sheets: [
                        {
                            name: "Summary",
                            headers: ["Metric", "Value"],
                            rows: Object.values(reportData.summary || {}).map((metric) => [
                                metric.name,
                                metric.average?.toFixed?.(2) ?? metric.total ?? "",
                            ]),
                        },
                        {
                            name: "Report",
                            headers,
                            rows: dataRows.map((row) => headers.map((header) => row?.[header] ?? "")),
                        },
                    ],
                });

                return { fileName, format: "xls", size: "~120KB" };
            },

            exportToCSV: (reportData) => {
                const fileName = reportData.report.generateFileName("csv");
                const rows = reportData.data || [];
                const headers = Object.keys(rows[0] || {});
                const csvContent = [
                    headers.join(","),
                    ...rows.map((row) => headers.map((header) => `"${row[header] ?? ""}"`).join(",")),
                ].join("\n");

                const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
                downloadBlob(fileName, blob);

                return { fileName, format: "csv", size: "~500KB" };
            },

            exportToJSON: (reportData) => {
                const fileName = reportData.report.generateFileName("json");
                const blob = new Blob([JSON.stringify(reportData, null, 2)], {
                    type: "application/json;charset=utf-8;",
                });
                downloadBlob(fileName, blob);
                return { fileName, format: "json", size: "~1MB" };
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

            generateMockReports: (count) => {
                const categories = ["users", "system", "sales", "shipments", "finance"];
                const statuses = ["draft", "active", "archived"];

                return Array.from({ length: count }, (_, i) => {
                    const category = categories[i % categories.length];
                    return new Report({
                        id: `report_${i + 1}`,
                        name: `${get().getCategoryName(category)} Report ${i + 1}`,
                        description: `Detailed ${get().getCategoryName(category).toLowerCase()} report for the system`,
                        category,
                        type: i % 3 === 0 ? "predefined" : "custom",
                        status: statuses[i % statuses.length],
                        createdBy: `user_${Math.floor(Math.random() * 10) + 1}`,
                        createdAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
                        updatedAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
                        lastGeneratedAt: Math.random() > 0.3 ? new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString() : null,
                        generationCount: Math.floor(Math.random() * 100),
                        tags: Math.random() > 0.5 ? ["favorite", "monthly"] : ["monthly"],
                    });
                });
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
