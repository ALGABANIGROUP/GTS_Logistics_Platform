import { create } from "zustand";
import axiosClient from "../api/axiosClient";

export const usePlatformStore = create((set, get) => ({
    // Platform settings
    platformName: "Gabani Transport Solutions",
    platformLogo: "",
    tenantId: null,
    isLoading: false,
    error: null,

    // Actions
    fetchPlatformSettings: async () => {
        set({ isLoading: true, error: null });
        try {
            let data = {};
            try {
                const response = await axiosClient.get("/api/v1/admin/platform-settings/branding");
                data = response.data || {};
            } catch (_authScopedError) {
                const response = await axiosClient.get("/api/v1/platform-settings/branding");
                data = response.data || {};
            }

            set({
                platformName: data.platformName || "Gabani Transport Solutions",
                platformLogo: data.platformLogo || "",
                tenantId: data.tenantId || null,
                isLoading: false
            });
        } catch (error) {
            console.error("Error fetching platform settings:", error);
            set({
                error: "Failed to load platform settings",
                isLoading: false
            });
        }
    },

    updatePlatformSettings: (settings) => {
        set({
            platformName: settings.platformName || get().platformName,
            platformLogo: settings.platformLogo || get().platformLogo,
            tenantId: settings.tenantId || get().tenantId
        });
    }
}));
