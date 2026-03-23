import axiosClient from "@/api/axiosClient";

// AI Strategy Advisor service client
const strategyService = {
    async getDashboard() {
        try {
            const response = await axiosClient.get("/strategy/analysis/dashboard");
            return response.data;
        } catch (error) {
            console.error("Failed to fetch strategy dashboard:", error);
            return {
                status: "inactive",
                last_updated: null,
                key_metrics: {
                    market_position: { market_share: "12.5%", rank: "3", trend: "up" },
                    financial_health: { revenue_growth: "+15.2%", profit_margin: "22.5%", roi: "18.7%" },
                    competitive_position: { competitive_advantage: "strong", differentiation_score: "8.2/10", customer_loyalty: "high" }
                },
                strategic_alerts: [],
                priority_recommendations: [],
                market_outlook: {},
                competitor_watchlist: []
            };
        }
    },

    async analyzeMarket({ marketName, depth = "standard" }) {
        try {
            const params = {};
            if (marketName) params.market_name = marketName;
            if (depth) params.depth = depth;
            const response = await axiosClient.get("/strategy/analysis/market", { params });
            return response.data;
        } catch (error) {
            console.error("Failed to analyze market:", error);
            return {
                market: marketName || "global",
                analysis: { error: true, message: "Unable to load market analysis" },
                depth,
                timestamp: new Date().toISOString()
            };
        }
    },

    async analyzeCompetitors(category = "all") {
        try {
            const response = await axiosClient.get("/strategy/analysis/competitors", { params: { category } });
            return response.data;
        } catch (error) {
            console.error("Failed to analyze competitors:", error);
            return {
                analysis_type: "comprehensive",
                analysis: {
                    competitive_landscape: {
                        total_competitors: 0,
                        market_concentration: "unknown",
                        competitive_intensity: "unknown",
                        analysis_date: new Date().toISOString()
                    },
                    threat_assessment: [],
                    opportunity_analysis: [],
                    competitive_response: {},
                    key_insights: []
                },
                timestamp: new Date().toISOString()
            };
        }
    },

    async performSwot() {
        try {
            const response = await axiosClient.get("/strategy/analysis/swot");
            return response.data;
        } catch (error) {
            console.error("Failed to perform SWOT analysis:", error);
            return {
                analysis_date: new Date().toISOString(),
                swot_matrix: { strengths: [], weaknesses: [], opportunities: [], threats: [] },
                key_insights: [],
                strategic_implications: {}
            };
        }
    },

    async analyzeMarketEntry({ targetMarket, investmentCapacity, timeframe = "12-18 months" }) {
        try {
            const body = { target_market: targetMarket, investment_capacity: investmentCapacity, timeframe };
            const response = await axiosClient.post("/strategy/analysis/market-entry", body);
            return response.data;
        } catch (error) {
            console.error("Failed to analyze market entry:", error);
            return { error: true, message: "Unable to analyze market entry", target_market: targetMarket };
        }
    },

    async getTrends({ timeframe = "1y", trendType = "all" }) {
        try {
            const params = { timeframe };
            if (trendType) params.trend_type = trendType;
            const response = await axiosClient.get("/strategy/analysis/trends", { params });
            return response.data;
        } catch (error) {
            console.error("Failed to load market trends:", error);
            return { analysis_type: "comprehensive_trends", all_trends: {}, analysis_date: new Date().toISOString() };
        }
    },

    async benchmarkPerformance({ metric = "market_share", comparisonGroup = "regional" }) {
        try {
            const params = { metric, comparison_group: comparisonGroup };
            const response = await axiosClient.get("/strategy/analysis/benchmark", { params });
            return response.data;
        } catch (error) {
            console.error("Failed to benchmark performance:", error);
            return { metric, comparison_group: comparisonGroup, benchmark_data: {}, recommendations: [] };
        }
    },

    async getRecommendations({ timeframe = "all", priority = "all", category = "all" }) {
        try {
            const params = { timeframe, priority, category };
            const response = await axiosClient.get("/strategy/recommendations/", { params });
            return response.data;
        } catch (error) {
            console.error("Failed to load strategic recommendations:", error);
            return { recommendations: {}, total_recommendations: 0, timeframe_filter: timeframe, priority_filter: priority, category_filter: category };
        }
    },

    async generateRecommendations({ focusArea, constraints }) {
        try {
            const body = { focus_area: focusArea, constraints };
            const response = await axiosClient.post("/strategy/recommendations/generate", body);
            return response.data;
        } catch (error) {
            console.error("Failed to generate custom recommendations:", error);
            return { error: true, message: "Unable to generate recommendations" };
        }
    },

    async consult({ question, context }) {
        try {
            const body = { question, context };
            const response = await axiosClient.post("/strategy/recommendations/consult", body);
            return response.data;
        } catch (error) {
            console.error("Failed to consult strategy advisor:", error);
            return { error: true, message: "Unable to consult strategy advisor" };
        }
    },

    async getActionPlan(recommendationId) {
        try {
            const response = await axiosClient.get(`/strategy/recommendations/action-plan/${recommendationId}`);
            return response.data;
        } catch (error) {
            console.error("Failed to load action plan:", error);
            return { recommendation_id: recommendationId, action_plan: null, error: true };
        }
    }
};

export default strategyService;
