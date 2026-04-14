import { create } from "zustand";
import axiosClient from "../api/axiosClient";

const normalizeErrorMessage = (error, fallback) => {
    const normalized = error?.normalized?.detail;
    if (typeof normalized === "string" && normalized.trim()) return normalized;

    const detail = error?.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) return detail;
    if (Array.isArray(detail)) {
        return detail
            .map((item) => {
                if (typeof item === "string") return item;
                if (item?.msg) return item.msg;
                if (item?.message) return item.message;
                return null;
            })
            .filter(Boolean)
            .join(", ");
    }

    if (detail && typeof detail === "object") {
        if (typeof detail.msg === "string" && detail.msg.trim()) return detail.msg;
        if (typeof detail.message === "string" && detail.message.trim()) return detail.message;
    }

    if (typeof error?.message === "string" && error.message.trim()) return error.message;
    return fallback;
};

export const useSettingsStore = create((set, get) => ({
    // Social Media Links
    socialMediaLinks: {},
    branding: {
        logo: "",
        favicon: "",
        primaryColor: "#1E40AF",
        secondaryColor: "#3B82F6",
        companyName: "Gabani Logistics",
        companyEmail: "support@gabanilogistics.com",
        companyPhone: "+966 123 456 789",
        companyAddress: "Riyadh, Saudi Arabia",
    },

    // State
    isLoading: false,
    error: null,
    success: null,

    // Actions
    fetchSocialMediaLinks: async () => {
        set({ isLoading: true, error: null });
        try {
            const response = await axiosClient.get("/api/v1/admin/social-media/settings/platform-social-links");
            const links = response?.data && typeof response.data === "object" ? response.data : {};
            set({ socialMediaLinks: links });
            return links;
        } catch (error) {
            const message = normalizeErrorMessage(error, "Failed to load social media links");
            set({ error: message });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    saveSocialMediaLinks: async (links) => {
        set({ isLoading: true, error: null, success: null });
        try {
            const payload = Object.entries(links || {}).reduce((acc, [platform, url]) => {
                acc[platform] = typeof url === "string" ? url : "";
                return acc;
            }, {});

            await axiosClient.put("/api/v1/admin/social-media/settings/platform-social-links", payload);

            set({
                socialMediaLinks: payload,
                success: "Social media links saved successfully"
            });

            // Clear success message after 3 seconds
            setTimeout(() => set({ success: null }), 3000);

            return payload;
        } catch (error) {
            const message = normalizeErrorMessage(error, "Failed to save social media links");
            set({ error: message });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    fetchBrandingSettings: async () => {
        set({ isLoading: true, error: null });
        try {
            // This would be implemented when branding API is ready
            const branding = get().branding;
            set({ branding });
            return branding;
        } catch (error) {
            set({ error: "Failed to load branding settings" });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    saveBrandingSettings: async (settings) => {
        set({ isLoading: true, error: null, success: null });
        try {
            // This would be implemented when branding API is ready
            set({
                branding: { ...get().branding, ...settings },
                success: "Branding settings saved successfully"
            });
            return settings;
        } catch (error) {
            set({ error: "Failed to save branding settings" });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    clearMessages: () => set({ error: null, success: null }),

    // Getters
    getActiveSocialLinks: () => {
        const links = get().socialMediaLinks;
        return Object.entries(links)
            .filter(([_, url]) => url && url.trim() !== "")
            .reduce((acc, [platform, url]) => {
                acc[platform] = url;
                return acc;
            }, {});
    },
}));
