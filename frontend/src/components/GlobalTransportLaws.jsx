import React, { useState, useEffect, useMemo } from 'react';
import axiosClient from '../api/axiosClient';

const GlobalTransportLaws = () => {
    const [laws, setLaws] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCountry, setSelectedCountry] = useState('all');
    const [selectedType, setSelectedType] = useState('all');
    const [selectedYear, setSelectedYear] = useState('all');
    const [selectedSafety, setSelectedSafety] = useState('all');
    const [upcomingUpdates, setUpcomingUpdates] = useState([]);
    const [comparisonMode, setComparisonMode] = useState(false);
    const [selectedForComparison, setSelectedForComparison] = useState([]);
    const [error, setError] = useState(null);

    const COUNTRIES = [
        { code: 'all', name: 'All Countries' },
        { code: 'US', name: 'United States' },
        { code: 'SA', name: 'Saudi Arabia' },
        { code: 'AE', name: 'UAE' },
        { code: 'CA', name: 'Canada' },
        { code: 'GB', name: 'UK' },
        { code: 'JP', name: 'Japan' },
        { code: 'DE', name: 'Germany' },
        { code: 'FR', name: 'France' },
        { code: 'CN', name: 'China' },
        { code: 'IN', name: 'India' },
        { code: 'AU', name: 'Australia' },
        { code: 'BR', name: 'Brazil' },
    ];

    const TRANSPORT_TYPES = [
        { value: 'all', label: 'All Types' },
        { value: 'road', label: 'Road Transport' },
        { value: 'air', label: 'Air Transport' },
        { value: 'sea', label: 'Sea Transport' },
        { value: 'rail', label: 'Rail Transport' },
        { value: 'multimodal', label: 'Multimodal' },
    ];

    const SAFETY_LEVELS = [
        { value: 'all', label: 'All Safety Levels' },
        { value: 'low', label: 'Low' },
        { value: 'medium', label: 'Medium' },
        { value: 'high', label: 'High' },
        { value: 'critical', label: 'Critical' },
    ];

    useEffect(() => {
        fetchLaws();
        fetchUpcomingUpdates();
    }, []);

    const fetchLaws = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await axiosClient.get('/api/transport-laws/');
            setLaws(response.data);
        } catch (err) {
            console.error('Error fetching laws:', err);
            setError('Failed to load transport laws');
        }
        setLoading(false);
    };

    const fetchUpcomingUpdates = async () => {
        try {
            const response = await axiosClient.get('/api/transport-laws/schedule/upcoming');
            setUpcomingUpdates(response.data);
        } catch (err) {
            console.error('Error fetching updates:', err);
        }
    };

    const filteredLaws = useMemo(() => {
        return laws.filter((law) => {
            const matchesSearch =
                searchTerm === '' ||
                law.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                law.country_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                law.tags.some((tag) =>
                    tag.toLowerCase().includes(searchTerm.toLowerCase())
                );

            const matchesCountry =
                selectedCountry === 'all' || law.country_code === selectedCountry;
            const matchesType =
                selectedType === 'all' || law.transport_type === selectedType;
            const matchesYear =
                selectedYear === 'all' || law.year.toString() === selectedYear;
            const matchesSafety =
                selectedSafety === 'all' || law.safety_standards === selectedSafety;

            return (
                matchesSearch &&
                matchesCountry &&
                matchesType &&
                matchesYear &&
                matchesSafety
            );
        });
    }, [laws, searchTerm, selectedCountry, selectedType, selectedYear, selectedSafety]);

    const years = useMemo(() => {
        const uniqueYears = [...new Set(laws.map((law) => law.year))];
        return uniqueYears.sort((a, b) => b - a);
    }, [laws]);

    const toggleComparisonSelection = (lawId) => {
        setSelectedForComparison((prev) => {
            if (prev.includes(lawId)) {
                return prev.filter((id) => id !== lawId);
            } else if (prev.length < 4) {
                return [...prev, lawId];
            }
            return prev;
        });
    };

    const compareLaws = async () => {
        if (selectedForComparison.length < 2) return;

        try {
            const response = await axiosClient.get(
                `/api/transport-laws/compare/${selectedForComparison.join(',')}`
            );
            console.log('Comparison result:', response.data);
            alert(
                `Comparing ${selectedForComparison.length} laws. Check console for details.`
            );
        } catch (err) {
            console.error('Error comparing laws:', err);
        }
    };

    const downloadLaw = (law) => {
        const lawData = {
            ...law,
            download_date: new Date().toISOString(),
            source: 'Global Transport Laws System',
        };

        const dataStr = JSON.stringify(lawData, null, 2);
        const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(
            dataStr
        )}`;
        const fileName = `transport-law-${law.country_code}-${law.year}.json`;

        const link = document.createElement('a');
        link.setAttribute('href', dataUri);
        link.setAttribute('download', fileName);
        link.click();
    };

    const getSafetyColor = (level) => {
        switch (level) {
            case 'critical':
                return 'bg-red-500';
            case 'high':
                return 'bg-orange-500';
            case 'medium':
                return 'bg-yellow-500';
            case 'low':
                return 'bg-green-500';
            default:
                return 'bg-gray-500';
        }
    };

    if (loading) {
        return <div className="text-center py-8 text-white">Loading transport laws...</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-white">Global Transport Laws</h1>
                    <p className="text-gray-400">
                        Comprehensive database of road, air, sea, rail, and multimodal
                        regulations
                    </p>
                </div>
                <div className="flex items-center space-x-4">
                    <button
                        className={`px-4 py-2 rounded-lg ${comparisonMode ? 'bg-blue-600' : 'bg-gray-700'
                            } text-white`}
                        onClick={() => setComparisonMode(!comparisonMode)}
                    >
                        {comparisonMode ? 'Exit Comparison' : 'Compare Laws'}
                    </button>
                    <button
                        className="px-4 py-2 bg-green-600 rounded-lg text-white hover:bg-green-700"
                        onClick={fetchUpcomingUpdates}
                    >
                        Check Updates
                    </button>
                </div>
            </div>

            {error && (
                <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 text-red-100">
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <input
                    type="text"
                    placeholder="Search transport laws..."
                    className="px-4 py-2 bg-gray-800 rounded-lg text-white border border-gray-700"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />

                <select
                    className="px-4 py-2 bg-gray-800 rounded-lg text-white border border-gray-700"
                    value={selectedCountry}
                    onChange={(e) => setSelectedCountry(e.target.value)}
                >
                    {COUNTRIES.map((country) => (
                        <option key={country.code} value={country.code}>
                            {country.name}
                        </option>
                    ))}
                </select>

                <select
                    className="px-4 py-2 bg-gray-800 rounded-lg text-white border border-gray-700"
                    value={selectedType}
                    onChange={(e) => setSelectedType(e.target.value)}
                >
                    {TRANSPORT_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>
                            {type.label}
                        </option>
                    ))}
                </select>

                <select
                    className="px-4 py-2 bg-gray-800 rounded-lg text-white border border-gray-700"
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(e.target.value)}
                >
                    <option value="all">All Years</option>
                    {years.map((year) => (
                        <option key={year} value={year}>
                            {year}
                        </option>
                    ))}
                </select>

                <select
                    className="px-4 py-2 bg-gray-800 rounded-lg text-white border border-gray-700"
                    value={selectedSafety}
                    onChange={(e) => setSelectedSafety(e.target.value)}
                >
                    {SAFETY_LEVELS.map((level) => (
                        <option key={level.value} value={level.value}>
                            {level.label}
                        </option>
                    ))}
                </select>
            </div>

            {comparisonMode && (
                <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
                    <div className="flex justify-between items-center">
                        <div>
                            <span className="font-semibold text-white">Comparison Mode Active</span>
                            <p className="text-sm text-gray-400">
                                Select up to 4 laws to compare. Selected: {selectedForComparison.length}
                            </p>
                        </div>
                        <div className="flex space-x-2">
                            <button
                                className="px-4 py-2 bg-blue-600 rounded-lg text-white hover:bg-blue-700 disabled:opacity-50"
                                onClick={compareLaws}
                                disabled={selectedForComparison.length < 2}
                            >
                                Compare ({selectedForComparison.length})
                            </button>
                            <button
                                className="px-4 py-2 bg-gray-700 rounded-lg text-white hover:bg-gray-600"
                                onClick={() => setSelectedForComparison([])}
                            >
                                Clear Selection
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {upcomingUpdates.length > 0 && (
                <div className="bg-amber-900/20 border border-amber-700 rounded-lg p-4">
                    <h3 className="font-semibold text-amber-300">⚠️ Upcoming Law Updates</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mt-2">
                        {upcomingUpdates.slice(0, 3).map((update) => (
                            <div key={update.law.id} className="bg-gray-800/50 rounded p-3">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <span className="font-medium text-white">
                                            {update.law.country_name}
                                        </span>
                                        <p className="text-sm text-gray-400 truncate">
                                            {update.law.title}
                                        </p>
                                    </div>
                                    <span
                                        className={`px-2 py-1 rounded text-xs ${update.priority === 'URGENT' ? 'bg-red-600' : 'bg-amber-600'
                                            } text-white`}
                                    >
                                        {update.priority}
                                    </span>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">
                                    Due in {update.days_until} days
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredLaws.map((law) => (
                    <div
                        key={law.id}
                        className={`bg-gray-800/50 rounded-xl p-4 border ${selectedForComparison.includes(law.id)
                            ? 'border-blue-500'
                            : 'border-gray-700'
                            }`}
                    >
                        {comparisonMode && (
                            <div className="flex justify-end mb-2">
                                <input
                                    type="checkbox"
                                    checked={selectedForComparison.includes(law.id)}
                                    onChange={() => toggleComparisonSelection(law.id)}
                                    className="h-5 w-5"
                                />
                            </div>
                        )}

                        <div className="flex justify-between items-start mb-3">
                            <div>
                                <div className="flex items-center space-x-2">
                                    <span className="text-lg font-semibold text-white">
                                        {law.country_name}
                                    </span>
                                    <span className="text-xs bg-gray-700 px-2 py-1 rounded text-gray-100">
                                        {law.country_code}
                                    </span>
                                </div>
                                <div className="flex items-center space-x-2 mt-1">
                                    <span
                                        className={`px-2 py-1 rounded text-xs text-white ${getSafetyColor(
                                            law.safety_standards
                                        )}`}
                                    >
                                        {law.safety_standards.toUpperCase()} Safety
                                    </span>
                                    <span className="text-xs bg-gray-700 px-2 py-1 rounded text-gray-100">
                                        {law.transport_type.toUpperCase()}
                                    </span>
                                </div>
                            </div>
                            <span className="text-gray-400">{law.year}</span>
                        </div>

                        <h4 className="font-medium text-lg text-white mb-2">{law.title}</h4>
                        <p className="text-gray-400 text-sm mb-4">{law.description}</p>

                        <div className="flex flex-wrap gap-2 mb-4">
                            {law.tags.map((tag) => (
                                <span
                                    key={tag}
                                    className="text-xs bg-gray-900 px-2 py-1 rounded text-gray-300"
                                >
                                    {tag}
                                </span>
                            ))}
                        </div>

                        <div className="text-xs text-gray-500 mb-4">
                            <div>
                                Last Updated:{' '}
                                {new Date(law.last_updated).toLocaleDateString()}
                            </div>
                            <div>
                                Next Update: {new Date(law.next_update_due).toLocaleDateString()}
                            </div>
                        </div>

                        <div className="flex justify-between gap-2">
                            <button
                                className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm text-white flex-1"
                                onClick={() => downloadLaw(law)}
                            >
                                Download
                            </button>
                            <button
                                className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm text-white flex-1"
                                onClick={() =>
                                    alert(`View details for ${law.title}`)
                                }
                            >
                                View Details
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {filteredLaws.length === 0 && (
                <div className="text-center py-12">
                    <div className="text-gray-500 text-lg">No transport laws found</div>
                    <p className="text-gray-600">Try adjusting your search filters</p>
                </div>
            )}

            <div className="bg-gray-800/30 rounded-xl p-4 mt-6">
                <h3 className="font-semibold text-white mb-3">System Statistics</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                        <div className="text-2xl font-bold text-white">{laws.length}</div>
                        <div className="text-sm text-gray-400">Total Laws</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-white">
                            {[...new Set(laws.map((l) => l.country_code))].length}
                        </div>
                        <div className="text-sm text-gray-400">Countries</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-white">
                            {upcomingUpdates.length}
                        </div>
                        <div className="text-sm text-gray-400">Pending Updates</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-white">
                            {laws.filter((l) => l.safety_standards === 'critical').length}
                        </div>
                        <div className="text-sm text-gray-400">Critical Safety</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default GlobalTransportLaws;
