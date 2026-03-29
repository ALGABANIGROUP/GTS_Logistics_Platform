// frontend/src/stores/useRealDataStore.js
/**
 * Store for Real Data from Backend API
 * Fetches actual data from database instead of mock data
 * Includes market intelligence and analytics
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { API_BASE_URL } from "../config/env";

const API_ROOT = String(API_BASE_URL || "").replace(/\/+$/, "");

export const useRealDataStore = create(
    persist(
        (set, get) => ({
            // Real Reports Data
            realReports: [],
            reportAnalytics: null,
            shipmentIntelligence: null,

            // Loading states
            loadingReports: false,
            loadingAnalytics: false,
            loadingIntelligence: false,

            // Errors
            error: null,

            /**
             * Fetch real reports from API
             */
            fetchRealReports: async () => {
                set({ loadingReports: true, error: null });
                try {
                    const token = localStorage.getItem("access_token");
                    const response = await fetch(`${API_ROOT}/api/v1/reports/real-data`, {
                        headers: {
                            "Authorization": `Bearer ${token || ""}`,
                            "Content-Type": "application/json",
                        },
                    });

                    if (!response.ok) {
                        throw new Error(`Failed to fetch reports: ${response.statusText}`);
                    }

                    const reports = await response.json();
                    set({ realReports: reports });
                    return reports;
                } catch (error) {
                    console.error("Error fetching real reports:", error);
                    set({ error: error.message });
                    return [];
                } finally {
                    set({ loadingReports: false });
                }
            },

            /**
             * Fetch analytics data
             */
            fetchReportAnalytics: async () => {
                set({ loadingAnalytics: true, error: null });
                try {
                    const token = localStorage.getItem("access_token");
                    const response = await fetch(`${API_ROOT}/api/v1/reports/analytics`, {
                        headers: {
                            "Authorization": `Bearer ${token || ""}`,
                            "Content-Type": "application/json",
                        },
                    });

                    if (!response.ok) {
                        // Return default empty analytics on error
                        const defaultAnalytics = {
                            total: 0,
                            active: 0,
                            draft: 0,
                            archived: 0,
                            byCategory: { users: 0, system: 0, shipments: 0, finance: 0, support: 0 }
                        };
                        set({ reportAnalytics: defaultAnalytics });
                        return defaultAnalytics;
                    }

                    const analytics = await response.json();
                    set({ reportAnalytics: analytics });
                    return analytics;
                } catch (error) {
                    // Silently handle error and return defaults
                    const defaultAnalytics = {
                        total: 0,
                        active: 0,
                        draft: 0,
                        archived: 0,
                        byCategory: { users: 0, system: 0, shipments: 0, finance: 0, support: 0 }
                    };
                    set({ reportAnalytics: defaultAnalytics, error: null });
                    return defaultAnalytics;
                } finally {
                    set({ loadingAnalytics: false });
                }
            },

            /**
             * Fetch market intelligence for shipments
             * Includes PayByCanada insights and AI analysis
             */
            fetchShipmentIntelligence: async () => {
                set({ loadingIntelligence: true, error: null });
                try {
                    const token = localStorage.getItem("access_token");
                    const response = await fetch(`${API_ROOT}/api/v1/reports/shipments-market-intelligence`, {
                        headers: {
                            "Authorization": `Bearer ${token || ""}`,
                            "Content-Type": "application/json",
                        },
                    });

                    if (!response.ok) {
                        throw new Error(`Failed to fetch market intelligence: ${response.statusText}`);
                    }

                    const intelligence = await response.json();
                    set({ shipmentIntelligence: intelligence });
                    return intelligence;
                } catch (error) {
                    console.error("Error fetching market intelligence:", error);
                    set({ error: error.message });
                    return null;
                } finally {
                    set({ loadingIntelligence: false });
                }
            },

            /**
             * Fetch all real data at once
             */
            fetchAllRealData: async () => {
                try {
                    await Promise.all([
                        get().fetchRealReports(),
                        get().fetchReportAnalytics(),
                        get().fetchShipmentIntelligence(),
                    ]);
                } catch (error) {
                    console.error("Error fetching all real data:", error);
                    set({ error: error.message });
                }
            },

            /**
             * Get real reports grouped by category
             */
            getRealReportsByCategory: (category) => {
                return get().realReports.filter((r) => r.category === category);
            },

            /**
             * Clear all real data
             */
            clearRealData: () => {
                set({
                    realReports: [],
                    reportAnalytics: null,
                    shipmentIntelligence: null,
                    error: null,
                });
            },
        }),
        {
            name: "real-data-store",
            version: 1,
        }
    )
);

export default useRealDataStore;
