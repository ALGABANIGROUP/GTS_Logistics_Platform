import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './SearchInterface.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Main Search Interface Component
 * Provides search functionality with autocomplete, filters, and results
 */
export default function SearchInterface() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const [totalResults, setTotalResults] = useState(0);
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [filters, setFilters] = useState({
        content_type: '',
        section: ''
    });
    const [stats, setStats] = useState(null);
    const suggestionsRef = useRef(null);

    // Fetch stats on mount
    useEffect(() => {
        fetchStats();
    }, []);

    // Fetch suggestions as user types
    useEffect(() => {
        if (query.length > 1) {
            fetchSuggestions(query);
        } else {
            setSuggestions([]);
            setShowSuggestions(false);
        }
    }, [query]);

    // Fetch search results when query or filters change
    useEffect(() => {
        if (query.trim()) {
            setPage(1);
            fetchResults(query, 1, filters);
        }
    }, [filters]);

    // Fetch results
    const fetchResults = async (searchQuery, pageNum, filtersObj) => {
        setLoading(true);
        setError(null);

        try {
            const params = new URLSearchParams({
                q: searchQuery,
                page: pageNum,
                size: 10
            });

            if (filtersObj.content_type) {
                params.append('content_type', filtersObj.content_type);
            }
            if (filtersObj.section) {
                params.append('section', filtersObj.section);
            }

            const response = await axios.get(
                `${API_BASE_URL}/api/search?${params}`
            );

            if (response.data.success) {
                setResults(response.data.results || []);
                setTotalResults(response.data.total);
                setTotalPages(response.data.total_pages);
                setPage(pageNum);
            } else {
                setError('Failed to fetch results');
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Search failed');
            setResults([]);
        } finally {
            setLoading(false);
            setShowSuggestions(false);
        }
    };

    // Fetch autocomplete suggestions
    const fetchSuggestions = async (prefix) => {
        try {
            const response = await axios.get(
                `${API_BASE_URL}/api/autocomplete?prefix=${encodeURIComponent(prefix)}`
            );
            setSuggestions(response.data.suggestions || []);
            setShowSuggestions(true);
        } catch (err) {
            console.error('Autocomplete error:', err);
        }
    };

    // Fetch stats
    const fetchStats = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/stats`);
            if (response.data.success) {
                setStats(response.data);
            }
        } catch (err) {
            console.error('Stats fetch error:', err);
        }
    };

    // Handle search submission
    const handleSearch = (e) => {
        e.preventDefault();
        if (query.trim()) {
            fetchResults(query, 1, filters);
        }
    };

    // Handle suggestion click
    const handleSuggestionClick = (suggestion) => {
        setQuery(suggestion.text);
        setShowSuggestions(false);
        setTimeout(() => {
            fetchResults(suggestion.text, 1, filters);
        }, 0);
    };

    // Handle filter change
    const handleFilterChange = (filterName, value) => {
        const newFilters = { ...filters, [filterName]: value };
        setFilters(newFilters);
    };

    // Handle pagination
    const handlePageChange = (newPage) => {
        if (newPage > 0 && newPage <= totalPages) {
            fetchResults(query, newPage, filters);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    return (
        <div className="search-interface">
            {/* Header */}
            <div className="search-header">
                <h1>GTS Search Engine</h1>
                <p>Search across all GTS content and documentation</p>
            </div>

            {/* Search Form */}
            <form onSubmit={handleSearch} className="search-form">
                <div className="search-input-wrapper">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search GTS Dispatcher, freight, logistics, routes..."
                        className="search-input"
                        autoComplete="off"
                    />
                    <button type="submit" className="search-button" disabled={loading}>
                        {loading ? 'Searching...' : 'Search'}
                    </button>

                    {/* Suggestions Dropdown */}
                    {showSuggestions && suggestions.length > 0 && (
                        <div className="suggestions-dropdown" ref={suggestionsRef}>
                            <div className="suggestions-list">
                                {suggestions.map((suggestion, idx) => (
                                    <button
                                        key={idx}
                                        className="suggestion-item"
                                        onClick={() => handleSuggestionClick(suggestion)}
                                        type="button"
                                    >
                                        <span className="suggestion-text">{suggestion.text}</span>
                                        <span className="suggestion-arrow">→</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Filters */}
                <div className="search-filters">
                    <div className="filter-group">
                        <label htmlFor="content-type">Content Type:</label>
                        <select
                            id="content-type"
                            value={filters.content_type}
                            onChange={(e) => handleFilterChange('content_type', e.target.value)}
                            className="filter-select"
                        >
                            <option value="">All Types</option>
                            <option value="blog">Blog Post</option>
                            <option value="service">Service</option>
                            <option value="documentation">Documentation</option>
                            <option value="page">Web Page</option>
                            <option value="platform">Platform</option>
                        </select>
                    </div>

                    <div className="filter-group">
                        <label htmlFor="section">Section:</label>
                        <select
                            id="section"
                            value={filters.section}
                            onChange={(e) => handleFilterChange('section', e.target.value)}
                            className="filter-select"
                        >
                            <option value="">All Sections</option>
                            <option value="platform">GTS Platform</option>
                            <option value="marketing">Marketing Site</option>
                        </select>
                    </div>

                    {/* Stats */}
                    {stats && (
                        <div className="filter-stats">
                            <span className="stat-item">
                                📊 {stats.total_documents} total documents indexed
                            </span>
                            <span className="stat-item">
                                ⚡ {stats.avg_word_count} avg. word count
                            </span>
                        </div>
                    )}
                </div>
            </form>

            {/* Error Message */}
            {error && (
                <div className="error-message">
                    <strong>Error:</strong> {error}
                </div>
            )}

            {/* Results Section */}
            {results.length > 0 && (
                <div className="search-results">
                    <div className="results-header">
                        <h2>Results</h2>
                        <span className="result-count">
                            Found {totalResults} result{totalResults !== 1 ? 's' : ''} in {results[0]?.took_ms || 0}ms
                        </span>
                    </div>

                    <div className="results-list">
                        {results.map((result, idx) => (
                            <div key={idx} className="result-item">
                                <div className="result-rank">{result.rank}</div>
                                <div className="result-content">
                                    <a href={result.url} target="_blank" rel="noopener noreferrer" className="result-title">
                                        {result.title}
                                    </a>
                                    <p className="result-url">{result.url}</p>

                                    {/* Highlights */}
                                    {result.highlight && (
                                        <div className="result-highlight">
                                            {result.highlight.content_text && (
                                                <p
                                                    dangerouslySetInnerHTML={{
                                                        __html: `... ${result.highlight.content_text[0]} ...`
                                                    }}
                                                />
                                            )}
                                            {!result.highlight.content_text && result.meta_description && (
                                                <p>{result.meta_description}</p>
                                            )}
                                        </div>
                                    )}

                                    {/* Metadata */}
                                    <div className="result-meta">
                                        <span className={`content-type ${result.content_type}`}>
                                            {result.content_type}
                                        </span>
                                        {result.platform_section && (
                                            <span className="platform-section">{result.platform_section}</span>
                                        )}
                                        {result.word_count && (
                                            <span className="word-count">{result.word_count} words</span>
                                        )}
                                        <span className="score">Score: {result.score?.toFixed(2)}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="pagination">
                            <button
                                onClick={() => handlePageChange(page - 1)}
                                disabled={page === 1}
                                className="pagination-button"
                            >
                                ← Previous
                            </button>

                            <div className="pagination-info">
                                Page {page} of {totalPages}
                            </div>

                            <button
                                onClick={() => handlePageChange(page + 1)}
                                disabled={page === totalPages}
                                className="pagination-button"
                            >
                                Next →
                            </button>
                        </div>
                    )}
                </div>
            )}

            {/* Empty State */}
            {!loading && query.trim() && results.length === 0 && !error && (
                <div className="empty-state">
                    <div className="empty-icon">🔍</div>
                    <h3>No results found</h3>
                    <p>Try different keywords or check your filters</p>
                </div>
            )}

            {/* Initial State */}
            {!loading && !query.trim() && results.length === 0 && (
                <div className="initial-state">
                    <div className="initial-icon">✨</div>
                    <h3>Start searching</h3>
                    <p>Search across GTS Dispatcher and Gabani Logistics content</p>

                    {stats && (
                        <div className="initial-stats">
                            <p>📚 {stats.total_documents} documents available</p>
                            <div className="content-types">
                                {Object.entries(stats.content_distribution).map(([type, count]) => (
                                    <span key={type} className="stat-badge">
                                        {type}: {count}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Loading State */}
            {loading && (
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Searching...</p>
                </div>
            )}
        </div>
    );
}
