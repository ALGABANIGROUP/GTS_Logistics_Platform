// src/services/socialMediaService.js
import axiosClient from "../api/axiosClient";

const API_BASE = "/api/v1";
const SOCIAL_API = `${API_BASE}/social-media`;

export const socialMediaAPI = {
    // ==================== Platform Connection ====================
    connectPlatform: async (platformId) => {
        try {
            const response = await axiosClient.post(
                `${SOCIAL_API}/platforms/${platformId}/connect`,
                {}
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to connect ${platformId}:`, error);
            throw error;
        }
    },

    disconnectPlatform: async (platformId) => {
        try {
            const response = await axiosClient.post(
                `${SOCIAL_API}/platforms/${platformId}/disconnect`,
                {}
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to disconnect ${platformId}:`, error);
            throw error;
        }
    },

    getPlatformStatus: async (platformId) => {
        try {
            const response = await axiosClient.get(
                `${SOCIAL_API}/platforms/${platformId}/status`
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to get platform status:`, error);
            throw error;
        }
    },

    // ==================== Campaign Management ====================
    getCampaigns: async (filters = {}) => {
        try {
            const response = await axiosClient.get(`${SOCIAL_API}/campaigns`, {
                params: filters,
            });
            return response.data.campaigns || [];
        } catch (error) {
            console.error("Failed to fetch campaigns:", error);
            return [];
        }
    },

    getCampaignById: async (campaignId) => {
        try {
            const response = await axiosClient.get(
                `${SOCIAL_API}/campaigns/${campaignId}`
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to fetch campaign ${campaignId}:`, error);
            throw error;
        }
    },

    createCampaign: async (campaignData) => {
        try {
            const response = await axiosClient.post(
                `${SOCIAL_API}/campaigns`,
                campaignData
            );
            return response.data.campaign;
        } catch (error) {
            console.error("Failed to create campaign:", error);
            throw error;
        }
    },

    updateCampaign: async (campaignId, updates) => {
        try {
            const response = await axiosClient.put(
                `${SOCIAL_API}/campaigns/${campaignId}`,
                updates
            );
            return response.data.campaign;
        } catch (error) {
            console.error(`Failed to update campaign ${campaignId}:`, error);
            throw error;
        }
    },

    deleteCampaign: async (campaignId) => {
        try {
            await axiosClient.delete(`${SOCIAL_API}/campaigns/${campaignId}`);
            return { success: true };
        } catch (error) {
            console.error(`Failed to delete campaign ${campaignId}:`, error);
            throw error;
        }
    },

    // ==================== Campaign Publishing ====================
    publishCampaign: async (campaignId) => {
        try {
            const response = await axiosClient.post(
                `${SOCIAL_API}/campaigns/${campaignId}/publish`,
                {}
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to publish campaign ${campaignId}:`, error);
            throw error;
        }
    },

    scheduleCampaign: async (campaignId, schedule) => {
        try {
            const response = await axiosClient.post(
                `${SOCIAL_API}/campaigns/${campaignId}/schedule`,
                { schedule }
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to schedule campaign ${campaignId}:`, error);
            throw error;
        }
    },

    pauseCampaign: async (campaignId) => {
        try {
            const response = await axiosClient.post(
                `${SOCIAL_API}/campaigns/${campaignId}/pause`,
                {}
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to pause campaign ${campaignId}:`, error);
            throw error;
        }
    },

    resumeCampaign: async (campaignId) => {
        try {
            const response = await axiosClient.post(
                `${SOCIAL_API}/campaigns/${campaignId}/resume`,
                {}
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to resume campaign ${campaignId}:`, error);
            throw error;
        }
    },

    // ==================== Analytics & Performance ====================
    getAnalytics: async (campaignId = null) => {
        try {
            const url = campaignId
                ? `${SOCIAL_API}/campaigns/${campaignId}/analytics`
                : `${SOCIAL_API}/analytics`;
            const response = await axiosClient.get(url);
            return response.data;
        } catch (error) {
            console.error("Failed to fetch analytics:", error);
            return {
                totalReach: 0,
                engagements: 0,
                clicks: 0,
                conversions: 0,
                roi: "0%",
            };
        }
    },

    getCampaignStats: async (campaignId) => {
        try {
            const response = await axiosClient.get(
                `${SOCIAL_API}/campaigns/${campaignId}/stats`
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to fetch campaign stats:`, error);
            throw error;
        }
    },

    getPerformanceByPlatform: async () => {
        try {
            const response = await axiosClient.get(
                `${SOCIAL_API}/analytics/by-platform`
            );
            return response.data;
        } catch (error) {
            console.error("Failed to fetch platform performance:", error);
            return {};
        }
    },

    // ==================== Content Management ====================
    uploadMedia: async (file, campaignId = null) => {
        try {
            const formData = new FormData();
            formData.append("file", file);
            if (campaignId) {
                formData.append("campaign_id", campaignId);
            }

            const response = await axiosClient.post(
                `${SOCIAL_API}/media/upload`,
                formData,
                {
                    headers: { "Content-Type": "multipart/form-data" },
                }
            );
            return response.data;
        } catch (error) {
            console.error("Failed to upload media:", error);
            throw error;
        }
    },

    deleteMedia: async (mediaId) => {
        try {
            await axiosClient.delete(`${SOCIAL_API}/media/${mediaId}`);
            return { success: true };
        } catch (error) {
            console.error(`Failed to delete media ${mediaId}:`, error);
            throw error;
        }
    },

    getContentTemplates: async () => {
        try {
            const response = await axiosClient.get(`${SOCIAL_API}/templates`);
            return response.data.templates || [];
        } catch (error) {
            console.error("Failed to fetch templates:", error);
            return [];
        }
    },

    // ==================== Audience Management ====================
    getAudiences: async () => {
        try {
            const response = await axiosClient.get(`${SOCIAL_API}/audiences`);
            return response.data.audiences || [];
        } catch (error) {
            console.error("Failed to fetch audiences:", error);
            return [];
        }
    },

    createAudience: async (audienceData) => {
        try {
            const response = await axiosClient.post(
                `${SOCIAL_API}/audiences`,
                audienceData
            );
            return response.data.audience;
        } catch (error) {
            console.error("Failed to create audience:", error);
            throw error;
        }
    },

    updateAudience: async (audienceId, updates) => {
        try {
            const response = await axiosClient.put(
                `${SOCIAL_API}/audiences/${audienceId}`,
                updates
            );
            return response.data.audience;
        } catch (error) {
            console.error(`Failed to update audience ${audienceId}:`, error);
            throw error;
        }
    },

    // ==================== Campaign Boost & Optimization ====================
    boostCampaign: async (campaignId, boostData) => {
        try {
            const response = await axiosClient.post(
                `${SOCIAL_API}/campaigns/${campaignId}/boost`,
                boostData
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to boost campaign ${campaignId}:`, error);
            throw error;
        }
    },

    runABTest: async (campaignId, variants) => {
        try {
            const response = await axiosClient.post(
                `${SOCIAL_API}/campaigns/${campaignId}/ab-test`,
                { variants }
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to run A/B test:`, error);
            throw error;
        }
    },

    getABTestResults: async (campaignId) => {
        try {
            const response = await axiosClient.get(
                `${SOCIAL_API}/campaigns/${campaignId}/ab-test-results`
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to fetch A/B test results:`, error);
            throw error;
        }
    },

    // ==================== Comments & Engagement ====================
    getCampaignComments: async (campaignId) => {
        try {
            const response = await axiosClient.get(
                `${SOCIAL_API}/campaigns/${campaignId}/comments`
            );
            return response.data.comments || [];
        } catch (error) {
            console.error(`Failed to fetch comments:`, error);
            return [];
        }
    },

    respondToComment: async (campaignId, commentId, response) => {
        try {
            await axiosClient.post(
                `${SOCIAL_API}/campaigns/${campaignId}/comments/${commentId}/respond`,
                { response }
            );
            return { success: true };
        } catch (error) {
            console.error(`Failed to respond to comment:`, error);
            throw error;
        }
    },

    // ==================== Reports ====================
    generateReport: async (campaignId, reportType = "summary") => {
        try {
            const response = await axiosClient.get(
                `${SOCIAL_API}/campaigns/${campaignId}/report`,
                {
                    params: { type: reportType },
                }
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to generate report:`, error);
            throw error;
        }
    },

    exportCampaignData: async (campaignId, format = "csv") => {
        try {
            const response = await axiosClient.get(
                `${SOCIAL_API}/campaigns/${campaignId}/export`,
                {
                    params: { format },
                    responseType: format === "pdf" ? "blob" : "json",
                }
            );
            return response.data;
        } catch (error) {
            console.error(`Failed to export data:`, error);
            throw error;
        }
    },
};
