export class Report {
    constructor(data = {}) {
        this.id = data.id || `report_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.name = data.name || "Untitled Report";
        this.description = data.description || "";
        this.type = data.type || "custom"; // predefined, custom, scheduled
        this.category = data.category || "general"; // users, sales, system, etc.
        this.format = data.format || "dashboard"; // dashboard, pdf, excel, csv, json

        this.settings = {
            refreshInterval: data.settings?.refreshInterval || 0,
            autoGenerate: data.settings?.autoGenerate || false,
            includeCharts: data.settings?.includeCharts !== undefined ? data.settings.includeCharts : true,
            includeTables: data.settings?.includeTables !== undefined ? data.settings.includeTables : true,
            includeSummary: data.settings?.includeSummary !== undefined ? data.settings.includeSummary : true,
            dataPoints: data.settings?.dataPoints || 1000,
            ...data.settings,
        };

        this.criteria = {
            dateRange: data.criteria?.dateRange || {
                type: "last30days",
                start: null,
                end: null,
            },
            filters: data.criteria?.filters || {},
            groupings: data.criteria?.groupings || [],
            aggregations: data.criteria?.aggregations || [],
            ...data.criteria,
        };

        this.metrics = data.metrics || [];
        this.dimensions = data.dimensions || [];
        this.charts = data.charts || [];
        this.tables = data.tables || [];

        this.createdBy = data.createdBy || null;
        this.createdAt = data.createdAt || new Date().toISOString();
        this.updatedAt = data.updatedAt || new Date().toISOString();
        this.lastGeneratedAt = data.lastGeneratedAt || null;
        this.generationCount = data.generationCount || 0;

        this.status = data.status || "draft"; // draft, active, archived
        this.isPublic = data.isPublic !== undefined ? data.isPublic : false;
        this.accessLevel = data.accessLevel || "private"; // private, team, public
        this.tags = data.tags || [];

        this.version = data.version || "1.0";
        this.history = data.history || [];
    }

    getDateRangeLabel() {
        const types = {
            today: "Today",
            yesterday: "Yesterday",
            last7days: "Last 7 Days",
            last30days: "Last 30 Days",
            thisMonth: "This Month",
            lastMonth: "Last Month",
            thisYear: "This Year",
            lastYear: "Last Year",
            custom: "Custom Range",
        };
        return types[this.criteria.dateRange.type] || "Custom Range";
    }

    calculateDateRange() {
        const now = new Date();
        const range = this.criteria.dateRange;

        if (range.type === "custom" && range.start && range.end) {
            return { start: new Date(range.start), end: new Date(range.end) };
        }

        let start;
        let end = new Date();

        switch (range.type) {
            case "today":
                start = new Date(now.setHours(0, 0, 0, 0));
                break;
            case "yesterday":
                start = new Date(now.setDate(now.getDate() - 1));
                start.setHours(0, 0, 0, 0);
                end = new Date(start);
                end.setHours(23, 59, 59, 999);
                break;
            case "last7days":
                start = new Date(now.setDate(now.getDate() - 7));
                break;
            case "last30days":
                start = new Date(now.setDate(now.getDate() - 30));
                break;
            case "thisMonth":
                start = new Date(now.getFullYear(), now.getMonth(), 1);
                break;
            case "lastMonth":
                start = new Date(now.getFullYear(), now.getMonth() - 1, 1);
                end = new Date(now.getFullYear(), now.getMonth(), 0);
                break;
            case "thisYear":
                start = new Date(now.getFullYear(), 0, 1);
                break;
            case "lastYear":
                start = new Date(now.getFullYear() - 1, 0, 1);
                end = new Date(now.getFullYear() - 1, 11, 31);
                break;
            default:
                start = new Date(now.setDate(now.getDate() - 30));
        }

        return { start, end };
    }

    addToHistory(action, data) {
        this.history.unshift({
            action,
            data,
            timestamp: new Date().toISOString(),
            user: this.createdBy,
        });

        if (this.history.length > 50) {
            this.history = this.history.slice(0, 50);
        }
    }

    update(data) {
        const oldVersion = { ...this };

        Object.keys(data).forEach((key) => {
            if (this[key] !== undefined) {
                this[key] = data[key];
            }
        });

        this.updatedAt = new Date().toISOString();
        this.version = this.incrementVersion(this.version);

        this.addToHistory("update", {
            oldVersion,
            newVersion: { ...this },
        });
    }

    incrementVersion(version) {
        const parts = version.split(".");
        const minor = parseInt(parts[1], 10) + 1;
        return `${parts[0]}.${minor}`;
    }

    generateFileName(format) {
        const date = new Date().toISOString().split("T")[0];
        const time = new Date().toTimeString().split(" ")[0].replace(/:/g, "-");
        return `${this.name.replace(/\s+/g, "_")}_${date}_${time}.${format}`;
    }

    hasAccess(userId, userRole) {
        if (this.accessLevel === "public") return true;
        if (this.accessLevel === "team" && userRole !== "user") return true;
        if (this.accessLevel === "private") return this.createdBy === userId;
        return false;
    }

    toJSON() {
        return {
            id: this.id,
            name: this.name,
            description: this.description,
            type: this.type,
            category: this.category,
            format: this.format,
            settings: this.settings,
            criteria: this.criteria,
            metrics: this.metrics,
            dimensions: this.dimensions,
            charts: this.charts,
            tables: this.tables,
            createdBy: this.createdBy,
            createdAt: this.createdAt,
            updatedAt: this.updatedAt,
            lastGeneratedAt: this.lastGeneratedAt,
            generationCount: this.generationCount,
            status: this.status,
            isPublic: this.isPublic,
            accessLevel: this.accessLevel,
            tags: this.tags,
            version: this.version,
            history: this.history,
        };
    }
}

export class PredefinedReport extends Report {
    constructor(data = {}) {
        super(data);
        this.type = "predefined";
        this.template = data.template || "default";

        this.templates = {
            userActivity: {
                name: "User Activity",
                description: "Track user engagement and session patterns",
                category: "users",
                metrics: [
                    { id: "totalUsers", name: "Total Users", type: "count" },
                    { id: "activeUsers", name: "Active Users", type: "count" },
                    { id: "newUsers", name: "New Users", type: "count" },
                    { id: "avgSessionTime", name: "Average Session Time", type: "duration" },
                    { id: "loginCount", name: "Login Count", type: "count" },
                ],
                dimensions: ["date", "userRole", "department"],
                charts: [
                    { type: "line", metric: "activeUsers", dimension: "date", title: "Active Users Trend" },
                    { type: "pie", metric: "totalUsers", dimension: "userRole", title: "Users by Role" },
                ],
                defaultFilters: {
                    dateRange: { type: "last30days" },
                },
            },
            systemPerformance: {
                name: "System Performance",
                description: "Monitor system responsiveness and reliability",
                category: "system",
                metrics: [
                    { id: "responseTime", name: "Response Time", type: "duration" },
                    { id: "cpuUsage", name: "CPU Usage", type: "percentage" },
                    { id: "memoryUsage", name: "Memory Usage", type: "percentage" },
                    { id: "errorRate", name: "Error Rate", type: "percentage" },
                    { id: "uptime", name: "Uptime", type: "duration" },
                ],
                dimensions: ["hour", "service", "server"],
                charts: [
                    { type: "line", metric: "responseTime", dimension: "hour", title: "Hourly Response Time" },
                    { type: "area", metric: "cpuUsage", dimension: "hour", title: "CPU Utilization" },
                ],
            },
            salesOverview: {
                name: "Sales Overview",
                description: "Track revenue and conversion performance",
                category: "sales",
                metrics: [
                    { id: "totalRevenue", name: "Total Revenue", type: "currency" },
                    { id: "ordersCount", name: "Orders Count", type: "count" },
                    { id: "avgOrderValue", name: "Average Order Value", type: "currency" },
                    { id: "conversionRate", name: "Conversion Rate", type: "percentage" },
                    { id: "refundRate", name: "Refund Rate", type: "percentage" },
                ],
                dimensions: ["date", "productCategory", "region"],
                charts: [
                    { type: "bar", metric: "totalRevenue", dimension: "date", title: "Revenue by Date" },
                    { type: "pie", metric: "totalRevenue", dimension: "productCategory", title: "Revenue by Category" },
                ],
            },
            shippingPerformance: {
                name: "Shipping Performance",
                description: "Measure delivery quality and shipment outcomes",
                category: "shipments",
                metrics: [
                    { id: "totalShipments", name: "Total Shipments", type: "count" },
                    { id: "onTimeDelivery", name: "On-Time Delivery", type: "percentage" },
                    { id: "avgDeliveryTime", name: "Average Delivery Time", type: "duration" },
                    { id: "damageRate", name: "Damage Rate", type: "percentage" },
                    { id: "customerSatisfaction", name: "Customer Satisfaction", type: "rating" },
                ],
                dimensions: ["carrier", "region", "serviceType"],
                charts: [
                    { type: "bar", metric: "onTimeDelivery", dimension: "carrier", title: "On-Time Delivery by Carrier" },
                    { type: "line", metric: "avgDeliveryTime", dimension: "date", title: "Delivery Time Trend" },
                ],
            },
        };

        if (this.templates[this.template]) {
            const template = this.templates[this.template];
            this.name = template.name;
            this.description = template.description;
            this.category = template.category;
            this.metrics = template.metrics;
            this.dimensions = template.dimensions;
            this.charts = template.charts;

            if (template.defaultFilters) {
                this.criteria.filters = { ...this.criteria.filters, ...template.defaultFilters };
            }
        }
    }
}
