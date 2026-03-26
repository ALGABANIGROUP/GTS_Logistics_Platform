import { create } from "zustand";
import { persist } from "zustand/middleware";
import { SearchEngine, SearchIndex } from "../models/Search";
import { useReportsStore } from "./useReportsStore";

const createIndices = () => ({
    users: new SearchIndex("users", {
        fields: ["name", "email", "phone", "role", "department"],
        weights: { name: 2, email: 1.5 },
    }),
    roles: new SearchIndex("roles", {
        fields: ["name", "description", "permissions"],
        weights: { name: 2 },
    }),
    reports: new SearchIndex("reports", {
        fields: ["name", "description", "category", "tags"],
        weights: { name: 2, category: 1.2 },
    }),
    notifications: new SearchIndex("notifications", {
        fields: ["title", "message", "category"],
        weights: { title: 1.6 },
    }),
    shipments: new SearchIndex("shipments", {
        fields: ["reference", "status", "origin", "destination", "carrier"],
        weights: { reference: 2 },
    }),
});

const DEFAULT_SETTINGS = {
    enableFuzzySearch: true,
    enableSynonyms: true,
    enableAutocomplete: true,
    searchDepth: "deep",
    maxResults: 50,
    highlightMatches: true,
    saveHistory: true,
    historyDays: 30,
    language: "ar",
};

const deterministicOffsetMs = (index, windowDays) => {
    const hours = ((index * 7 + 11) % (windowDays * 24));
    return hours * 60 * 60 * 1000;
};

const deterministicIdSuffix = (seed) => `k${(seed * 2654435761 >>> 0).toString(36)}`;

const buildSeedUsers = (count = 50) =>
    Array.from({ length: count }, (_, i) => ({
        id: `user_${i + 1}`,
        name: `User ${i + 1}`,
        email: `user${i + 1}@example.com`,
        role: i % 5 === 0 ? "admin" : "user",
        department: i % 3 === 0 ? "Operations" : i % 3 === 1 ? "Sales" : "Support",
        status: i % 10 === 0 ? "inactive" : "active",
        createdAt: new Date(Date.now() - deterministicOffsetMs(i + 1, 360)).toISOString(),
    }));

const buildSeedRoles = (count = 10) => {
    const roles = ["admin", "user", "manager", "viewer", "editor"];
    return Array.from({ length: count }, (_, i) => ({
        id: `role_${i + 1}`,
        name: roles[i % roles.length],
        description: `Role profile: ${roles[i % roles.length]}`,
        permissions: ["read", "write"].slice(0, (i % 2) + 1),
        createdAt: new Date(Date.now() - deterministicOffsetMs(i + 1, 30)).toISOString(),
    }));
};

const buildSeedNotifications = (count = 100) => {
    const categories = ["system", "user", "security", "update"];
    return Array.from({ length: count }, (_, i) => ({
        id: `notification_${i + 1}`,
        title: `Notification: ${categories[i % categories.length]}`,
        message: `System notification ${i + 1}`,
        category: categories[i % categories.length],
        read: i % 3 === 0,
        createdAt: new Date(Date.now() - deterministicOffsetMs(i + 1, 3)).toISOString(),
    }));
};

const buildSeedShipments = (count = 80) => {
    const statuses = ["in_transit", "delivered", "pending", "cancelled"];
    const cities = ["Toronto", "Montreal", "Vancouver", "Calgary", "Ottawa"];
    return Array.from({ length: count }, (_, i) => ({
        id: `shipment_${i + 1}`,
        reference: `SHP-${1000 + i}`,
        status: statuses[i % statuses.length],
        origin: cities[i % cities.length],
        destination: cities[(i + 2) % cities.length],
        carrier: `Carrier ${i % 6}`,
        createdAt: new Date(Date.now() - deterministicOffsetMs(i + 1, 14)).toISOString(),
    }));
};

const buildSeedReports = (count = 30) => {
    const categories = ["users", "system", "sales", "shipments"];
    return Array.from({ length: count }, (_, i) => ({
        id: `report_${i + 1}`,
        name: `Report ${categories[i % categories.length]} ${i + 1}`,
        description: `Analytics report for ${categories[i % categories.length]}`,
        category: categories[i % categories.length],
        tags: ["monthly", "analysis"].slice(0, (i % 2) + 1),
        createdAt: new Date(Date.now() - deterministicOffsetMs(i + 1, 7)).toISOString(),
        updatedAt: new Date(Date.now() - deterministicOffsetMs(i + 3, 1)).toISOString(),
    }));
};
export const useSearchStore = create(
    persist(
        (set, get) => ({
            indices: createIndices(),
            searchHistory: [],
            savedSearches: [],
            settings: DEFAULT_SETTINGS,
            stats: {
                totalSearches: 0,
                successfulSearches: 0,
                averageResponseTime: 0,
                popularQueries: [],
                searchTrends: {},
            },
            loading: false,
            error: null,
            lastSearch: null,
            currentResults: null,

            search: async (query, options = {}) => {
                set({ loading: true, error: null });
                const startTime = Date.now();

                try {
                    const searchOptions = { ...get().settings, ...options };
                    const engine = new SearchEngine(get().indices, searchOptions);
                    const results = await engine.search(query, searchOptions);
                    get().updateSearchStats(query, results, Date.now() - startTime);

                    if (get().settings.saveHistory) {
                        get().addToHistory(query, results);
                    }

                    const lastSearch = {
                        query,
                        results,
                        timestamp: new Date().toISOString(),
                        options: searchOptions,
                        time: results.time,
                    };

                    set({ currentResults: results, lastSearch });
                    return results;
                } catch (error) {
                    const message = error?.message || "Search failed";
                    set({ error: message });
                    throw error;
                } finally {
                    set({ loading: false });
                }
            },

            searchIn: async (indexName, query, options = {}) => {
                return get().search(query, {
                    ...options,
                    indices: [indexName],
                    maxResults: options.maxResults || 20,
                });
            },

            advancedSearch: async (criteria) => {
                const options = {
                    searchDepth: "exhaustive",
                    enableFuzzySearch: Boolean(criteria?.fuzzy),
                    enableSynonyms: criteria?.synonyms !== false,
                    filters: criteria?.filters || {},
                    sortBy: criteria?.sortBy || "relevance",
                    indices: criteria?.indices,
                    maxResults: criteria?.maxResults || 100,
                };
                return get().search(criteria?.query || "", options);
            },

            smartSearch: async (query) => {
                const intent = get().analyzeIntent(query);
                const criteria = get().buildCriteriaFromIntent(intent, query);
                return get().advancedSearch(criteria);
            },

            updateSettings: (updates) => set((state) => ({ settings: { ...state.settings, ...updates } })),

            updateIndex: async (indexName, data) => {
                const indices = { ...get().indices };
                const index = indices[indexName];
                if (!index) throw new Error(`Index ${indexName} not found`);
                index.update(data);
                set({ indices });
            },

            rebuildAllIndices: async () => {
                set({ loading: true, error: null });
                try {
                    const reports = useReportsStore.getState?.().reports || [];

                    await Promise.all([
                        get().updateIndex("users", buildSeedUsers(80)),
                        get().updateIndex("roles", buildSeedRoles(12)),
                        get().updateIndex(
                            "reports",
                            reports.length > 0
                                ? reports.map((report) => ({
                                    id: report.id,
                                    name: report.name,
                                    description: report.description,
                                    category: report.category,
                                    tags: report.tags || [],
                                    createdAt: report.createdAt,
                                    updatedAt: report.updatedAt,
                                }))
                                : buildSeedReports(40)
                        ),
                        get().updateIndex("notifications", buildSeedNotifications(120)),
                        get().updateIndex("shipments", buildSeedShipments(60)),
                    ]);
                } catch (error) {
                    set({ error: error?.message || "Failed to rebuild indices" });
                    throw error;
                } finally {
                    set({ loading: false });
                }
            },

            saveSearch: async (name, query, criteria = {}) => {
                const savedSearch = {
                    id: `search_${Date.now()}_${deterministicIdSuffix((get().stats.totalSearches || 0) + 1)}`,
                    name,
                    query,
                    criteria,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    usageCount: 0,
                    isFavorite: false,
                    tags: ["saved"],
                };
                set((state) => ({ savedSearches: [savedSearch, ...state.savedSearches] }));
                return savedSearch;
            },

            deleteSavedSearch: async (searchId) =>
                set((state) => ({ savedSearches: state.savedSearches.filter((s) => s.id !== searchId) })),

            getQuickCommands: (query = "") => {
                const commands = [
                    { command: "user:active", description: "Show active users", icon: "fas fa-user-check" },
                    { command: "role:admin", description: "Filter by admin role", icon: "fas fa-user-tag" },
                    { command: "report:today", description: "Open today's reports", icon: "fas fa-chart-bar" },
                    { command: "notification:unread", description: "Show unread notifications", icon: "fas fa-bell" },
                    { command: "shipment:delivered", description: "Show delivered shipments", icon: "fas fa-truck" },
                ];

                if (!query) return commands;
                const lower = query.toLowerCase();
                return commands.filter(
                    (cmd) => cmd.command.includes(lower) || cmd.description.includes(query)
                );
            },

            getSearchSuggestions: (query) => {
                if (!query || query.length < 2) return [];
                const lower = query.toLowerCase();
                const historyMatches = (get().searchHistory || [])
                    .filter((item) => item.query.toLowerCase().includes(lower))
                    .slice(0, 5);

                const popularMatches = (get().stats.popularQueries || [])
                    .filter((item) => item.query.toLowerCase().includes(lower))
                    .slice(0, 5);

                const quickCommands = get().getQuickCommands(query);
                return { historyMatches, popularMatches, quickCommands };
            },

            updateSearchStats: (query, results, responseTime) => {
                set((state) => {
                    const totalSearches = state.stats.totalSearches + 1;
                    const successfulSearches =
                        state.stats.successfulSearches + (results.total > 0 ? 1 : 0);
                    const averageResponseTime =
                        (state.stats.averageResponseTime * (totalSearches - 1) + responseTime) /
                        totalSearches;

                    const popularQueries = [...state.stats.popularQueries];
                    const existing = popularQueries.find((q) => q.query === query);
                    if (existing) {
                        existing.count += 1;
                        existing.lastUsed = Date.now();
                        existing.totalResults += results.total;
                    } else {
                        popularQueries.push({
                            query,
                            count: 1,
                            lastUsed: Date.now(),
                            totalResults: results.total,
                            firstUsed: Date.now(),
                        });
                    }
                    popularQueries.sort((a, b) => b.count - a.count);

                    const searchTrends = { ...state.stats.searchTrends };
                    const now = new Date();
                    const day = now.toDateString();
                    const hour = now.getHours();
                    if (!searchTrends[day]) searchTrends[day] = Array(24).fill(0);
                    searchTrends[day][hour] += 1;

                    return {
                        stats: {
                            totalSearches,
                            successfulSearches,
                            averageResponseTime,
                            popularQueries: popularQueries.slice(0, 20),
                            searchTrends,
                        },
                    };
                });
            },

            addToHistory: (query, results) => {
                set((state) => {
                    const history = [...state.searchHistory];
                    const existing = history.find((item) => item.query === query);
                    if (existing) {
                        existing.count += 1;
                        existing.timestamp = Date.now();
                        existing.lastResults = results.total;
                    } else {
                        history.unshift({
                            id: `hist_${Date.now()}`,
                            query,
                            count: 1,
                            timestamp: Date.now(),
                            firstSearched: Date.now(),
                            lastResults: results.total,
                        });
                    }
                    return { searchHistory: history.slice(0, 100) };
                });
                get().cleanupOldHistory();
            },

            cleanupOldHistory: () => {
                const cutoff = Date.now() - get().settings.historyDays * 24 * 60 * 60 * 1000;
                set((state) => ({
                    searchHistory: state.searchHistory.filter((h) => h.timestamp > cutoff),
                }));
            },

            clearSearchHistory: () => set({ searchHistory: [] }),

            analyzeIntent: (query) => {
                const queryLower = query.toLowerCase();
                const patterns = {
                    user: [/user/i, /account/i, /member/i, /@/],
                    role: [/role/i, /permission/i, /access/i],
                    report: [/report/i, /analytics/i, /dashboard/i],
                    notification: [/notification/i, /alert/i, /message/i],
                    shipment: [/shipment/i, /delivery/i, /carrier/i],
                };

                const intent = { type: "general", confidence: 0.5, entities: [], filters: {} };
                Object.entries(patterns).forEach(([type, regexes]) => {
                    if (regexes.some((regex) => regex.test(queryLower))) {
                        intent.type = type;
                        intent.confidence = Math.min(intent.confidence + 0.3, 1.0);
                    }
                });

                return intent;
            },

            buildCriteriaFromIntent: (intent, originalQuery) => {
                const criteria = {
                    query: originalQuery,
                    filters: { ...intent.filters },
                    sortBy: "relevance",
                    maxResults: 50,
                };

                switch (intent.type) {
                    case "user":
                        criteria.indices = ["users"];
                        criteria.sortBy = "name";
                        break;
                    case "role":
                        criteria.indices = ["roles"];
                        criteria.sortBy = "name";
                        break;
                    case "report":
                        criteria.indices = ["reports"];
                        criteria.sortBy = "date";
                        break;
                    case "notification":
                        criteria.indices = ["notifications"];
                        criteria.sortBy = "date";
                        break;
                    case "shipment":
                        criteria.indices = ["shipments"];
                        criteria.sortBy = "date";
                        break;
                    default:
                        break;
                }

                return criteria;
            },
        }),
        {
            name: "search-store",
            partialize: (state) => ({
                searchHistory: state.searchHistory,
                savedSearches: state.savedSearches,
                settings: state.settings,
                stats: state.stats,
            }),
        }
    )
);
