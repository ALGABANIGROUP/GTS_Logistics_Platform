import React, { useEffect, useMemo, useRef, useState } from "react";
import { Search, SlidersHorizontal, Filter, X, Sparkles, Clock, Flame } from "lucide-react";
import { useSearchStore } from "../../stores/useSearchStore";

export default function SmartSearchBar() {
    const containerRef = useRef(null);
    const inputRef = useRef(null);

    const search = useSearchStore((state) => state.search);
    const smartSearch = useSearchStore((state) => state.smartSearch);
    const advancedSearch = useSearchStore((state) => state.advancedSearch);
    const rebuildAllIndices = useSearchStore((state) => state.rebuildAllIndices);
    const updateSettings = useSearchStore((state) => state.updateSettings);
    const settings = useSearchStore((state) => state.settings);
    const loading = useSearchStore((state) => state.loading);
    const currentResults = useSearchStore((state) => state.currentResults);
    const lastSearch = useSearchStore((state) => state.lastSearch);
    const searchHistory = useSearchStore((state) => state.searchHistory);
    const popularQueries = useSearchStore((state) => state.stats.popularQueries || []);
    const getQuickCommands = useSearchStore((state) => state.getQuickCommands);
    const getSearchSuggestions = useSearchStore((state) => state.getSearchSuggestions);

    const [query, setQuery] = useState("");
    const [showPanel, setShowPanel] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [selectedIndices, setSelectedIndices] = useState(["users", "roles", "reports", "notifications", "shipments"]);
    const [advancedFilters, setAdvancedFilters] = useState({
        category: "",
        status: "",
        dateRange: { start: "", end: "" },
    });
    const [sortBy, setSortBy] = useState("relevance");

    useEffect(() => {
        rebuildAllIndices();
    }, [rebuildAllIndices]);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (containerRef.current && !containerRef.current.contains(event.target)) {
                setShowPanel(false);
                setShowSettings(false);
                setShowAdvanced(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const suggestions = useMemo(() => getSearchSuggestions(query), [getSearchSuggestions, query]);
    const quickCommands = useMemo(() => getQuickCommands(query), [getQuickCommands, query]);

    const groupedResults = useMemo(() => {
        if (!currentResults?.results?.length) return {};
        return currentResults.results.reduce((acc, result) => {
            const key = result.sources?.[0] || result.source || "general";
            if (!acc[key]) acc[key] = [];
            acc[key].push(result);
            return acc;
        }, {});
    }, [currentResults]);

    const performSearch = async () => {
        if (!query.trim()) return;
        setShowPanel(true);
        await search(query, {
            indices: selectedIndices,
            sortBy,
        });
    };

    const performSmartSearch = async () => {
        if (!query.trim()) return;
        setShowPanel(true);
        await smartSearch(query);
    };

    const performAdvancedSearch = async () => {
        setShowPanel(true);
        setShowAdvanced(false);
        const filters = {};
        if (advancedFilters.category) filters.category = advancedFilters.category;
        if (advancedFilters.status) filters.status = advancedFilters.status;
        if (advancedFilters.dateRange.start) filters.dateRange = advancedFilters.dateRange;

        await advancedSearch({
            query: query || " ",
            filters,
            indices: selectedIndices,
            sortBy,
            maxResults: settings.maxResults,
        });
    };

    const handleQueryChange = (value) => {
        setQuery(value);
        if (!value) {
            setShowPanel(false);
            return;
        }
        setShowPanel(true);
    };

    const handleKeyDown = (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            performSearch();
        }
        if (event.key === "Escape") {
            setShowPanel(false);
            inputRef.current?.blur();
        }
    };

    const applySettings = () => {
        updateSettings(settings);
        setShowSettings(false);
        if (query.trim()) performSearch();
    };

    const getHighlightTokens = (highlights = {}) =>
        Object.values(highlights)
            .flat()
            .map((item) => item?.token)
            .filter(Boolean);

    const renderHighlightedText = (text, highlights = {}, className = "") => {
        const safeText = String(text || "");
        const tokens = getHighlightTokens(highlights);

        if (!tokens.length) {
            return <span className={className}>{safeText}</span>;
        }

        const regex = new RegExp(
            `(${tokens
                .map((token) => token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
                .join("|")})`,
            "gi"
        );

        const segments = safeText.split(regex);
        return (
            <span className={className}>
                {segments.map((segment, index) => {
                    const matched = tokens.some(
                        (token) => segment.toLowerCase() === token.toLowerCase()
                    );
                    return matched ? <mark key={index}>{segment}</mark> : <React.Fragment key={index}>{segment}</React.Fragment>;
                })}
            </span>
        );
    };

    const renderSuggestions = () => {
        if (!query || query.length < 2) {
            return null;
        }

        const historyMatches = suggestions?.historyMatches || [];
        const popularMatches = suggestions?.popularMatches || [];

        return (
            <div className="space-y-4">
                {historyMatches.length > 0 && (
                    <div>
                        <div className="mb-2 flex items-center gap-2 text-xs text-slate-300">
                            <Clock className="h-3 w-3" />
                            Recent Searches
                        </div>
                        <div className="space-y-1">
                            {historyMatches.map((item) => (
                                <button
                                    key={item.id}
                                    onClick={() => {
                                        setQuery(item.query);
                                        performSearch();
                                    }}
                                    className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-right text-sm text-slate-200 transition hover:bg-white/10"
                                >
                                    <span>{item.query}</span>
                                    <span className="text-xs text-slate-400">{item.count}x</span>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {popularMatches.length > 0 && (
                    <div>
                        <div className="mb-2 flex items-center gap-2 text-xs text-slate-300">
                            <Flame className="h-3 w-3" />
                            Popular Searches
                        </div>
                        <div className="space-y-1">
                            {popularMatches.map((item) => (
                                <button
                                    key={item.query}
                                    onClick={() => {
                                        setQuery(item.query);
                                        performSearch();
                                    }}
                                    className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-right text-sm text-slate-200 transition hover:bg-white/10"
                                >
                                    <span>{item.query}</span>
                                    <span className="text-xs text-slate-400">{item.count}x</span>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {quickCommands.length > 0 && (
                    <div>
                        <div className="mb-2 flex items-center gap-2 text-xs text-slate-300">
                            <Sparkles className="h-3 w-3" />
                            Quick Commands
                        </div>
                        <div className="space-y-1">
                            {quickCommands.map((command) => (
                                <button
                                    key={command.command}
                                    onClick={() => {
                                        setQuery(command.command);
                                        performSearch();
                                    }}
                                    className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-right text-sm text-slate-200 transition hover:bg-white/10"
                                >
                                    <span>{command.description}</span>
                                    <span className="text-xs text-slate-400">{command.command}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        );
    };

    const renderResults = () => {
        if (!currentResults) return null;

        if (currentResults.total === 0) {
            return (
                <div className="rounded-xl border border-white/10 bg-white/5 p-6 text-center text-sm text-slate-300">
                    No results found for your search
                </div>
            );
        }

        return (
            <div className="space-y-4">
                {Object.entries(groupedResults).map(([groupName, items]) => (
                    <div key={groupName} className="rounded-xl border border-white/10 bg-white/5 p-4">
                        <div className="mb-3 flex items-center justify-between text-xs text-slate-400">
                            <span>{groupName}</span>
                            <span>{items.length} results</span>
                        </div>
                        <div className="space-y-2">
                            {items.map((result) => (
                                <div key={result.document?.id} className="rounded-lg border border-white/5 bg-slate-950/40 p-3">
                                    {renderHighlightedText(
                                        result.document?.name || result.document?.title || "",
                                        result.highlights,
                                        "text-sm font-semibold text-white"
                                    )}
                                    {renderHighlightedText(
                                        result.document?.description || "",
                                        result.highlights,
                                        "mt-1 text-xs text-slate-400"
                                    )}
                                    <div className="mt-2 flex flex-wrap gap-2 text-[10px] text-slate-400">
                                        {result.document?.category && (
                                            <span className="rounded-full border border-white/10 px-2 py-0.5">{result.document.category}</span>
                                        )}
                                        <span className="rounded-full border border-white/10 px-2 py-0.5">
                                            Relevance {Math.round(result.totalScore * 10) / 10}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <div ref={containerRef} className="relative w-full max-w-xl">
            <div className="flex items-center gap-2 rounded-full border border-white/10 bg-slate-950/50 px-4 py-2 text-slate-200 shadow-lg">
                <Search className="h-4 w-4 text-slate-400" />
                <input
                    ref={inputRef}
                    value={query}
                    onChange={(event) => handleQueryChange(event.target.value)}
                    onFocus={() => setShowPanel(true)}
                    onKeyDown={handleKeyDown}
                    placeholder="Search the system..."
                    className="w-full bg-transparent text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none"
                />
                <button
                    type="button"
                    onClick={() => setShowSettings((prev) => !prev)}
                    className={`rounded-full p-1 transition ${showSettings ? "bg-white/10" : "hover:bg-white/10"}`}
                >
                    <SlidersHorizontal className="h-4 w-4" />
                </button>
                <button
                    type="button"
                    onClick={() => setShowAdvanced((prev) => !prev)}
                    className={`rounded-full p-1 transition ${showAdvanced ? "bg-white/10" : "hover:bg-white/10"}`}
                >
                    <Filter className="h-4 w-4" />
                </button>
                <button
                    type="button"
                    onClick={performSmartSearch}
                    className="rounded-full bg-blue-500/20 px-2 py-1 text-xs text-blue-200 hover:bg-blue-500/30"
                >
                    Smart
                </button>
                <button
                    type="button"
                    onClick={performSearch}
                    className="rounded-full bg-emerald-500/20 px-2 py-1 text-xs text-emerald-200 hover:bg-emerald-500/30"
                >
                    Search
                </button>
                {query && (
                    <button
                        type="button"
                        onClick={() => {
                            setQuery("");
                            setShowPanel(false);
                        }}
                        className="rounded-full p-1 text-slate-400 hover:bg-white/10"
                    >
                        <X className="h-4 w-4" />
                    </button>
                )}
            </div>

            {showSettings && (
                <div className="absolute right-0 mt-2 w-72 rounded-xl border border-white/10 bg-slate-950/90 p-4 text-xs text-slate-200 shadow-xl">
                    <div className="mb-3 font-semibold">Search Settings</div>
                    <label className="flex items-center justify-between gap-2 py-1">
                        <span>Fuzzy Search</span>
                        <input
                            type="checkbox"
                            checked={settings.enableFuzzySearch}
                            onChange={(event) => updateSettings({ enableFuzzySearch: event.target.checked })}
                        />
                    </label>
                    <label className="flex items-center justify-between gap-2 py-1">
                        <span>Highlight Results</span>
                        <input
                            type="checkbox"
                            checked={settings.highlightMatches}
                            onChange={(event) => updateSettings({ highlightMatches: event.target.checked })}
                        />
                    </label>
                    <label className="flex items-center justify-between gap-2 py-1">
                        <span>Save History</span>
                        <input
                            type="checkbox"
                            checked={settings.saveHistory}
                            onChange={(event) => updateSettings({ saveHistory: event.target.checked })}
                        />
                    </label>
                    <div className="mt-3">
                        <div className="mb-1 text-[11px] text-slate-400">Search Depth</div>
                        <select
                            value={settings.searchDepth}
                            onChange={(event) => updateSettings({ searchDepth: event.target.value })}
                            className="w-full rounded-lg border border-white/10 bg-slate-900 px-2 py-1 text-xs"
                        >
                            <option value="quick">Quick</option>
                            <option value="deep">Deep</option>
                            <option value="exhaustive">Exhaustive</option>
                        </select>
                    </div>
                    <div className="mt-3">
                        <div className="mb-1 text-[11px] text-slate-400">Max Results</div>
                        <input
                            type="number"
                            min={10}
                            max={200}
                            value={settings.maxResults}
                            onChange={(event) => updateSettings({ maxResults: Number(event.target.value) })}
                            className="w-full rounded-lg border border-white/10 bg-slate-900 px-2 py-1 text-xs"
                        />
                    </div>
                    <button
                        type="button"
                        onClick={applySettings}
                        className="mt-3 w-full rounded-lg bg-blue-500/20 py-1 text-xs text-blue-200"
                    >
                        Apply
                    </button>
                </div>
            )}

            {showAdvanced && (
                <div className="absolute right-0 mt-2 w-80 rounded-xl border border-white/10 bg-slate-950/90 p-4 text-xs text-slate-200 shadow-xl">
                    <div className="mb-3 font-semibold">Advanced Search</div>
                    <div className="space-y-3">
                        <label className="flex flex-col gap-1">
                            <span className="text-[11px] text-slate-400">Category</span>
                            <input
                                value={advancedFilters.category}
                                onChange={(event) => setAdvancedFilters((prev) => ({ ...prev, category: event.target.value }))}
                                className="rounded-lg border border-white/10 bg-slate-900 px-2 py-1"
                                placeholder="e.g., users / system"
                            />
                        </label>
                        <label className="flex flex-col gap-1">
                            <span className="text-[11px] text-slate-400">Status</span>
                            <input
                                value={advancedFilters.status}
                                onChange={(event) => setAdvancedFilters((prev) => ({ ...prev, status: event.target.value }))}
                                className="rounded-lg border border-white/10 bg-slate-900 px-2 py-1"
                                placeholder="active / archived"
                            />
                        </label>
                        <label className="flex flex-col gap-1">
                            <span className="text-[11px] text-slate-400">Date Range</span>
                            <div className="flex gap-2">
                                <input
                                    type="date"
                                    value={advancedFilters.dateRange.start}
                                    onChange={(event) =>
                                        setAdvancedFilters((prev) => ({
                                            ...prev,
                                            dateRange: { ...prev.dateRange, start: event.target.value },
                                        }))
                                    }
                                    className="flex-1 rounded-lg border border-white/10 bg-slate-900 px-2 py-1"
                                />
                                <input
                                    type="date"
                                    value={advancedFilters.dateRange.end}
                                    onChange={(event) =>
                                        setAdvancedFilters((prev) => ({
                                            ...prev,
                                            dateRange: { ...prev.dateRange, end: event.target.value },
                                        }))
                                    }
                                    className="flex-1 rounded-lg border border-white/10 bg-slate-900 px-2 py-1"
                                />
                            </div>
                        </label>
                        <label className="flex flex-col gap-1">
                            <span className="text-[11px] text-slate-400">Sort By</span>
                            <select
                                value={sortBy}
                                onChange={(event) => setSortBy(event.target.value)}
                                className="rounded-lg border border-white/10 bg-slate-900 px-2 py-1"
                            >
                                <option value="relevance">Relevance</option>
                                <option value="date">Date</option>
                                <option value="name">Name</option>
                                <option value="category">Category</option>
                            </select>
                        </label>
                        <div>
                            <div className="mb-1 text-[11px] text-slate-400">Indices</div>
                            <div className="flex flex-wrap gap-2">
                                {["users", "roles", "reports", "notifications", "shipments"].map((index) => (
                                    <button
                                        key={index}
                                        type="button"
                                        onClick={() =>
                                            setSelectedIndices((prev) =>
                                                prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
                                            )
                                        }
                                        className={`rounded-full border px-3 py-1 ${selectedIndices.includes(index)
                                            ? "border-emerald-400/60 bg-emerald-500/20 text-emerald-200"
                                            : "border-white/10 text-slate-400"
                                            }`}
                                    >
                                        {index}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                    <button
                        type="button"
                        onClick={performAdvancedSearch}
                        className="mt-4 w-full rounded-lg bg-emerald-500/20 py-1 text-xs text-emerald-200"
                    >
                        Execute Advanced Search
                    </button>
                </div>
            )}

            {showPanel && (
                <div className="absolute right-0 mt-3 w-full rounded-2xl border border-white/10 bg-slate-950/95 p-4 text-sm text-slate-200 shadow-2xl">
                    <div className="mb-3 flex items-center justify-between text-xs text-slate-400">
                        <span>Search Results</span>
                        <span>{loading ? "..." : `${currentResults?.total || 0} results`}</span>
                    </div>

                    {loading && (
                        <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-center text-xs text-slate-300">
                            Searching...
                        </div>
                    )}

                    {!loading && (!currentResults || currentResults.total === 0) && renderSuggestions()}
                    {!loading && currentResults?.total > 0 && renderResults()}

                    {lastSearch?.time && (
                        <div className="mt-3 text-[10px] text-slate-500">
                            Last search took {lastSearch.time}ms
                        </div>
                    )}
                </div>
            )}

            <div className="mt-2 flex flex-wrap items-center gap-2 text-[10px] text-slate-400">
                <span>Recent Searches:</span>
                {searchHistory.slice(0, 3).map((item) => (
                    <button
                        key={item.id}
                        onClick={() => {
                            setQuery(item.query);
                            performSearch();
                        }}
                        className="rounded-full border border-white/10 px-2 py-0.5"
                    >
                        {item.query}
                    </button>
                ))}
                {popularQueries.slice(0, 1).map((item) => (
                    <span key={item.query} className="rounded-full border border-white/10 px-2 py-0.5">
                        Most Popular: {item.query}
                    </span>
                ))}
            </div>
        </div>
    );
}
