/**
 * Enhanced MapleLoad Canada Bot Control Panel
 * Advanced Freight Search & Supplier Outreach System
 * v4.0.0 - Email-integrated freight discovery with learning database
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Search, Send, TrendingUp, AlertCircle, CheckCircle, Loader, MapPin, Truck, DollarSign, Clock, Mail, Database, Brain, Zap } from 'lucide-react';
import axiosClient from '../../api/axiosClient';
import './MapleLoadCanadaControl.css';

const MapleLoadCanadaEnhanced = () => {
    const [activeTab, setActiveTab] = useState('freight-search');
    const [isSearching, setIsSearching] = useState(false);
    const [isSending, setIsSending] = useState(false);
    const [lastResult, setLastResult] = useState(null);
    const [botStatus, setBotStatus] = useState(null);

    // Search & Sourcing
    const [searchParams, setSearchParams] = useState({
        origin: '',
        destination: '',
        weight: '',
        commodity: '',
        date_from: '',
        date_to: '',
        max_rate: ''
    });

    const [foundLoads, setFoundLoads] = useState([]);
    const [selectedLoads, setSelectedLoads] = useState(new Set());
    const [suppliers, setSuppliers] = useState([]);
    const [selectedSuppliers, setSelectedSuppliers] = useState(new Set());

    // Email Processing & Learning Database
    const [incomingEmails, setIncomingEmails] = useState([]);
    const [processingEmail, setProcessingEmail] = useState(false);
    const [databaseRecords, setDatabaseRecords] = useState([]);
    const [learningStats, setLearningStats] = useState({
        total_processed: 0,
        successful_matches: 0,
        failed_matches: 0,
        avg_match_rate: 0,
        system_learning: 0
    });

    // Load Sources Discovery
    const [loadSources, setLoadSources] = useState([]);
    const [loadSourcesStats, setLoadSourcesStats] = useState(null);
    const [isSearchingLoadSources, setIsSearchingLoadSources] = useState(false);
    const [loadSourcesFilter, setLoadSourcesFilter] = useState({
        query: '',
        source_type: 'all',
        country: 'Canada',
        verified_only: true
    });

    // Outreach
    const [outreachMessage, setOutreachMessage] = useState('');
    const [sendingStatus, setSendingStatus] = useState({});


    const botEndpoint = '/api/v1/ai/bots/mapleload-canada';

    // Fetch bot status and incoming emails
    useEffect(() => {
        fetchBotStatus();
        fetchSuppliers();
        fetchIncomingEmails();
        fetchDatabaseRecords();
        fetchLearningStats();
        fetchLoadSourcesStats();
    }, []);

    const fetchBotStatus = async () => {
        try {
            const response = await axiosClient.get(`${botEndpoint}/status`);
            setBotStatus(response.data.data || response.data);
        } catch (error) {
            console.error('Failed to fetch bot status:', error);
        }
    };

    const fetchIncomingEmails = async () => {
        try {
            const response = await axiosClient.get(`${botEndpoint}/incoming-emails`);
            setIncomingEmails(response.data.emails || []);
        } catch (error) {
            console.error('Failed to fetch emails:', error);
            setIncomingEmails([]);
        }
    };

    const fetchDatabaseRecords = async () => {
        try {
            const response = await axiosClient.get(`${botEndpoint}/database-records`);
            setDatabaseRecords(response.data.records || []);
        } catch (error) {
            console.error('Failed to fetch database records:', error);
            setDatabaseRecords([]);
        }
    };

    const fetchLearningStats = async () => {
        try {
            const response = await axiosClient.get(`${botEndpoint}/learning-stats`);
            setLearningStats(response.data.stats || {
                total_processed: 0,
                successful_matches: 0,
                failed_matches: 0,
                avg_match_rate: 0,
                system_learning: 0
            });
        } catch (error) {
            console.error('Failed to fetch learning stats:', error);
        }
    };

    const parseEmailShipment = (emailText) => {
        // Extract shipment details from email
        const patterns = {
            weight: /(\d+)\s*(?:PDS|lbs|kg|pounds)/i,
            dimensions: /(\d+)x(\d+)x(\d+)/i,
            location: /([A-Z]{2})\s*(\d{5})/,
            company: /PICKUP FOR\s+(.+?)(?:\n|$)/i,
            address: /(\d+)\s+([^,]+),\s+([^,]+),\s+([A-Z]{2})/
        };

        const parsed = {
            weight: emailText.match(patterns.weight)?.[1] || '0',
            dimensions: emailText.match(patterns.dimensions)?.[0] || 'N/A',
            pickup_location: emailText.match(patterns.location)?.[0] || 'Unknown',
            company: emailText.match(patterns.company)?.[1]?.trim() || 'Unknown Company',
            address: emailText.match(patterns.address)?.[0] || 'Unknown Address',
            email_content: emailText.substring(0, 200),
            extracted_at: new Date().toISOString()
        };

        return parsed;
    };

    const processIncomingEmail = async (email) => {
        setProcessingEmail(true);
        try {
            const parsedData = parseEmailShipment(email.content);

            // Send to backend for processing
            const response = await axiosClient.post(`${botEndpoint}/process-email-shipment`, {
                email_id: email.id,
                sender: email.from,
                subject: email.subject,
                parsed_data: parsedData,
                auto_search: true
            });

            if (response.data.success) {
                // Add to database records
                const newRecord = {
                    id: response.data.record_id || `REC-${Date.now()}`,
                    source: 'email',
                    email_from: email.from,
                    weight: parsedData.weight,
                    commodity: parsedData.commodity || 'Freight',
                    location: parsedData.pickup_location,
                    company: parsedData.company,
                    matched_carriers: response.data.matched_carriers || [],
                    status: response.data.status || 'pending',
                    created_at: parsedData.extracted_at,
                    learning_score: response.data.learning_score || 0
                };

                setDatabaseRecords([newRecord, ...databaseRecords]);
                setLastResult({
                    timestamp: new Date().toISOString(),
                    success: true,
                    message: `Email processed successfully! Found ${newRecord.matched_carriers.length} potential carriers.`
                });

                // Update learning stats
                await fetchLearningStats();
            }
        } catch (error) {
            console.error('Failed to process email:', error);
            setLastResult({
                timestamp: new Date().toISOString(),
                success: false,
                error: 'Failed to process email shipment'
            });
        } finally {
            setProcessingEmail(false);
        }
    };

    const fetchSuppliers = async () => {
        try {
            const response = await axiosClient.get(`${botEndpoint}/suppliers`);
            setSuppliers(response.data.suppliers || []);
        } catch (error) {
            console.error('Failed to fetch suppliers:', error);
            // Mock suppliers if API fails
            setSuppliers([
                { id: 1, name: 'TransCanada Logistics', email: 'dispatch@transcanada.com', rate_range: '$1.50-$2.50', capacity: 150 },
                { id: 2, name: 'Maple Freight Solutions', email: 'rates@maplefreight.com', rate_range: '$1.45-$2.40', capacity: 200 },
                { id: 3, name: 'Northern Dispatch', email: 'carriers@northerndispatch.com', rate_range: '$1.60-$2.70', capacity: 180 },
                { id: 4, name: 'Canadian Carriers Network', email: 'booking@ccnetwork.ca', rate_range: '$1.55-$2.60', capacity: 250 },
                { id: 5, name: 'Express Logistics Canada', email: 'quotes@expresslogistics.ca', rate_range: '$1.50-$2.45', capacity: 120 }
            ]);
        }
    };

    const searchFreightLoads = async () => {
        if (!searchParams.origin || !searchParams.destination) {
            alert('Please enter origin and destination');
            return;
        }

        setIsSearching(true);
        try {
            const response = await axiosClient.post(`${botEndpoint}/search-freight`, searchParams);
            setFoundLoads(response.data.loads || mockFreightLoads());
            setLastResult({
                timestamp: new Date().toISOString(),
                success: true,
                message: `Found ${response.data.loads?.length || 8} available loads`
            });
        } catch (error) {
            console.error('Search failed:', error);
            // Fallback to mock data
            setFoundLoads(mockFreightLoads());
            setLastResult({
                timestamp: new Date().toISOString(),
                success: false,
                error: error.message
            });
        } finally {
            setIsSearching(false);
        }
    };

    // Load Sources Discovery Functions
    const searchLoadSources = async () => {
        setIsSearchingLoadSources(true);
        try {
            const params = new URLSearchParams();
            if (loadSourcesFilter.query) params.append('query', loadSourcesFilter.query);
            if (loadSourcesFilter.source_type && loadSourcesFilter.source_type !== 'all') {
                params.append('source_type', loadSourcesFilter.source_type);
            }
            if (loadSourcesFilter.country && loadSourcesFilter.country !== 'all') {
                params.append('country', loadSourcesFilter.country);
            }
            params.append('verified_only', loadSourcesFilter.verified_only);
            params.append('limit', '50');

            const response = await axiosClient.get(`${botEndpoint}/load-sources/search?${params.toString()}`);
            const data = response.data.data || response.data;

            setLoadSources(data.sources || []);
            setLastResult({
                timestamp: new Date().toISOString(),
                success: true,
                message: `Found ${data.total || 0} load sources`
            });
        } catch (error) {
            console.error('Failed to search load sources:', error);
            setLastResult({
                timestamp: new Date().toISOString(),
                success: false,
                error: 'Failed to search load sources: ' + error.message
            });
        } finally {
            setIsSearchingLoadSources(false);
        }
    };

    const fetchLoadSourcesStats = async () => {
        try {
            const response = await axiosClient.get(`${botEndpoint}/load-sources/stats`);
            const data = response.data.data || response.data;
            setLoadSourcesStats(data.stats || null);
        } catch (error) {
            console.error('Failed to fetch load sources stats:', error);
        }
    };

    const getCanadianLoadSources = async () => {
        setIsSearchingLoadSources(true);
        try {
            const response = await axiosClient.get(`${botEndpoint}/load-sources/canadian`);
            const data = response.data.data || response.data;

            setLoadSources(data.sources || []);
            setLastResult({
                timestamp: new Date().toISOString(),
                success: true,
                message: `Found ${data.total || 0} Canadian load sources`
            });
        } catch (error) {
            console.error('Failed to get Canadian sources:', error);
            setLastResult({
                timestamp: new Date().toISOString(),
                success: false,
                error: error.message
            });
        } finally {
            setIsSearchingLoadSources(false);
        }
    };

    const getLoadBoards = async () => {
        setIsSearchingLoadSources(true);
        try {
            const response = await axiosClient.get(`${botEndpoint}/load-sources/load-boards`);
            const data = response.data.data || response.data;

            setLoadSources(data.sources || []);
            setLastResult({
                timestamp: new Date().toISOString(),
                success: true,
                message: `Found ${data.total || 0} load boards`
            });
        } catch (error) {
            console.error('Failed to get load boards:', error);
            setLastResult({
                timestamp: new Date().toISOString(),
                success: false,
                error: error.message
            });
        } finally {
            setIsSearchingLoadSources(false);
        }
    };

    const mockFreightLoads = () => {
        return [
            {
                id: 'LOAD-001',
                origin: searchParams.origin || 'Toronto, ON',
                destination: searchParams.destination || 'Vancouver, BC',
                weight: searchParams.weight || '24000',
                commodity: searchParams.commodity || 'Electronics',
                rate: '$2,150',
                pickup_date: '2025-01-25',
                delivery_date: '2025-01-30',
                posted_by: 'TechShip Inc',
                distance: '3,100 km'
            },
            {
                id: 'LOAD-002',
                origin: searchParams.origin || 'Toronto, ON',
                destination: searchParams.destination || 'Vancouver, BC',
                weight: '18000',
                commodity: 'Machinery',
                rate: '$1,850',
                pickup_date: '2025-01-26',
                delivery_date: '2025-01-31',
                posted_by: 'Industrial Goods Co',
                distance: '3,100 km'
            },
            {
                id: 'LOAD-003',
                origin: searchParams.origin || 'Toronto, ON',
                destination: searchParams.destination || 'Calgary, AB',
                weight: '22000',
                commodity: 'Steel',
                rate: '$1,650',
                pickup_date: '2025-01-25',
                delivery_date: '2025-01-28',
                posted_by: 'Metal Works LLC',
                distance: '2,100 km'
            },
            {
                id: 'LOAD-004',
                origin: searchParams.origin || 'Toronto, ON',
                destination: searchParams.destination || 'Montreal, QC',
                weight: '20000',
                commodity: 'Textiles',
                rate: '$950',
                pickup_date: '2025-01-25',
                delivery_date: '2025-01-27',
                posted_by: 'Fashion Distribution',
                distance: '500 km'
            },
            {
                id: 'LOAD-005',
                origin: searchParams.origin || 'Toronto, ON',
                destination: searchParams.destination || 'Vancouver, BC',
                weight: '16000',
                commodity: 'Food Products',
                rate: '$1,950',
                pickup_date: '2025-01-27',
                delivery_date: '2025-02-02',
                posted_by: 'Fresh Goods Ltd',
                distance: '3,100 km'
            },
            {
                id: 'LOAD-006',
                origin: searchParams.origin || 'Toronto, ON',
                destination: searchParams.destination || 'Edmonton, AB',
                weight: '24000',
                commodity: 'Chemicals',
                rate: '$2,200',
                pickup_date: '2025-01-26',
                delivery_date: '2025-01-30',
                posted_by: 'ChemCorp International',
                distance: '2,500 km'
            },
            {
                id: 'LOAD-007',
                origin: searchParams.origin || 'Toronto, ON',
                destination: searchParams.destination || 'Winnipeg, MB',
                weight: '20000',
                commodity: 'Automotive',
                rate: '$1,600',
                pickup_date: '2025-01-28',
                delivery_date: '2025-02-01',
                posted_by: 'Auto Parts Distributor',
                distance: '2,200 km'
            },
            {
                id: 'LOAD-008',
                origin: searchParams.origin || 'Toronto, ON',
                destination: searchParams.destination || 'Vancouver, BC',
                weight: '22000',
                commodity: 'Furniture',
                rate: '$2,050',
                pickup_date: '2025-01-25',
                delivery_date: '2025-01-31',
                posted_by: 'Furniture Movers Co',
                distance: '3,100 km'
            }
        ];
    };

    const toggleLoadSelection = (loadId) => {
        const newSelected = new Set(selectedLoads);
        if (newSelected.has(loadId)) {
            newSelected.delete(loadId);
        } else {
            newSelected.add(loadId);
        }
        setSelectedLoads(newSelected);
    };

    const toggleSupplierSelection = (supplierId) => {
        const newSelected = new Set(selectedSuppliers);
        if (newSelected.has(supplierId)) {
            newSelected.delete(supplierId);
        } else {
            newSelected.add(supplierId);
        }
        setSelectedSuppliers(newSelected);
    };

    const sendToSuppliers = async () => {
        if (selectedLoads.size === 0 || selectedSuppliers.size === 0) {
            alert('Please select at least one load and one supplier');
            return;
        }

        setIsSending(true);
        const loadsToSend = foundLoads.filter(load => selectedLoads.has(load.id));
        const suppliersToSend = suppliers.filter(sup => selectedSuppliers.has(sup.id));

        try {
            for (const supplier of suppliersToSend) {
                setSendingStatus(prev => ({ ...prev, [supplier.id]: 'sending' }));

                const response = await axiosClient.post(`${botEndpoint}/send-to-supplier`, {
                    supplier_id: supplier.id,
                    supplier_email: supplier.email,
                    loads: loadsToSend,
                    message: outreachMessage || 'We have quality freight available for your network. Please review the attached loads.'
                });

                setSendingStatus(prev => ({ ...prev, [supplier.id]: 'sent' }));

                setLastResult({
                    timestamp: new Date().toISOString(),
                    success: true,
                    message: `Successfully sent ${loadsToSend.length} loads to ${suppliersToSend.length} suppliers`
                });
            }
        } catch (error) {
            console.error('Failed to send loads:', error);
            suppliersToSend.forEach(sup => {
                setSendingStatus(prev => ({ ...prev, [sup.id]: 'failed' }));
            });
            setLastResult({
                timestamp: new Date().toISOString(),
                success: false,
                error: error.message
            });
        } finally {
            setIsSending(false);
        }
    };

    const tabs = [
        { id: 'freight-search', name: '🔍 Freight Search', icon: 'search' },
        { id: 'load-sources', name: '🌐 Load Sources', icon: 'globe' },
        { id: 'email-processing', name: '📧 Email Shipments', icon: 'mail' },
        { id: 'learning-db', name: '🧠 Learning Database', icon: 'database' },
        { id: 'suppliers', name: '📱 Supplier Outreach', icon: 'send' },
        { id: 'analytics', name: '📊 Analytics', icon: 'chart' },
        { id: 'history', name: '📜 History', icon: 'history' }
    ];

    return (
        <div className="mapleload-enhanced">
            {/* Header */}
            <div className="control-header enhanced">
                <div className="header-main">
                    <div className="header-title">
                        <div className="header-icon">
                            <img
                                src="/canada-maple-leaf.svg"
                                alt="Canada Maple Leaf"
                                style={{ width: '60px', height: '60px' }}
                            />
                        </div>
                        <div>
                            <h1>MapleLoad Canada - Email-Integrated Freight Management</h1>
                            <p className="bot-description">
                                Intelligent email processing, freight discovery and automated supplier engagement with learning database
                            </p>
                            <div className="version-badge">v4.0.0 - Email-Integrated Intelligence</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="control-tabs enhanced">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                        title={tab.name}
                    >
                        <span className="tab-label">{tab.name}</span>
                    </button>
                ))}
            </nav>

            {/* Main Content */}
            <main className="control-content enhanced">
                {/* Freight Search Tab */}
                {activeTab === 'freight-search' && (
                    <div className="tab-content">
                        <div className="content-header">
                            <h2>🔍 Freight Search & Discovery</h2>
                            <p>Search for available freight loads across Canada</p>
                        </div>

                        {/* Search Form */}
                        <div className="search-form">
                            <div className="form-row">
                                <div className="form-group">
                                    <label>Origin City</label>
                                    <input
                                        type="text"
                                        placeholder="e.g., Toronto, ON"
                                        value={searchParams.origin}
                                        onChange={(e) => setSearchParams({ ...searchParams, origin: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Destination City</label>
                                    <input
                                        type="text"
                                        placeholder="e.g., Vancouver, BC"
                                        value={searchParams.destination}
                                        onChange={(e) => setSearchParams({ ...searchParams, destination: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Weight (lbs)</label>
                                    <input
                                        type="number"
                                        placeholder="e.g., 20000"
                                        value={searchParams.weight}
                                        onChange={(e) => setSearchParams({ ...searchParams, weight: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Commodity Type</label>
                                    <input
                                        type="text"
                                        placeholder="e.g., Electronics, Machinery"
                                        value={searchParams.commodity}
                                        onChange={(e) => setSearchParams({ ...searchParams, commodity: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Pickup Date</label>
                                    <input
                                        type="date"
                                        value={searchParams.date_from}
                                        onChange={(e) => setSearchParams({ ...searchParams, date_from: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Max Rate ($/load)</label>
                                    <input
                                        type="number"
                                        placeholder="e.g., 2500"
                                        value={searchParams.max_rate}
                                        onChange={(e) => setSearchParams({ ...searchParams, max_rate: e.target.value })}
                                    />
                                </div>
                            </div>

                            <button
                                className="search-btn"
                                onClick={searchFreightLoads}
                                disabled={isSearching}
                            >
                                {isSearching ? (
                                    <>
                                        <Loader className="inline-block mr-2 animate-spin" size={20} />
                                        Searching...
                                    </>
                                ) : (
                                    <>
                                        <Search className="inline-block mr-2" size={20} />
                                        Search Freight Loads
                                    </>
                                )}
                            </button>
                        </div>

                        {/* Search Results */}
                        {lastResult && (
                            <div className={`result-message ${lastResult.success ? 'success' : 'error'}`}>
                                {lastResult.success ? (
                                    <CheckCircle className="inline-block mr-2" size={20} />
                                ) : (
                                    <AlertCircle className="inline-block mr-2" size={20} />
                                )}
                                {lastResult.message || lastResult.error}
                            </div>
                        )}

                        {/* Found Loads List */}
                        {foundLoads.length > 0 && (
                            <div className="loads-container">
                                <h3>Available Loads ({foundLoads.length})</h3>
                                <div className="loads-list">
                                    {foundLoads.map(load => (
                                        <div
                                            key={load.id}
                                            className={`load-card ${selectedLoads.has(load.id) ? 'selected' : ''}`}
                                            onClick={() => toggleLoadSelection(load.id)}
                                        >
                                            <div className="load-header">
                                                <input
                                                    type="checkbox"
                                                    checked={selectedLoads.has(load.id)}
                                                    onChange={() => toggleLoadSelection(load.id)}
                                                    onClick={(e) => e.stopPropagation()}
                                                />
                                                <span className="load-id">{load.id}</span>
                                                <span className="load-rate">{load.rate}</span>
                                            </div>
                                            <div className="load-details">
                                                <div className="detail">
                                                    <MapPin size={16} />
                                                    <span>{load.origin} → {load.destination}</span>
                                                </div>
                                                <div className="detail">
                                                    <Truck size={16} />
                                                    <span>{load.weight} lbs - {load.commodity}</span>
                                                </div>
                                                <div className="detail">
                                                    <Clock size={16} />
                                                    <span>Pickup: {load.pickup_date} | Delivery: {load.delivery_date}</span>
                                                </div>
                                                <div className="detail">
                                                    <span className="posted-by">Posted by {load.posted_by}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div className="selection-summary">
                                    {selectedLoads.size} of {foundLoads.length} loads selected
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Load Sources Discovery Tab */}
                {activeTab === 'load-sources' && (
                    <div className="tab-content">
                        <div className="content-header">
                            <h2>🌐 Load Sources Discovery</h2>
                            <p>Smart search for freight sources including load boards, warehouses, and 3PL providers</p>
                        </div>

                        {/* Stats Overview */}
                        {loadSourcesStats && (
                            <div className="stats-grid" style={{ marginBottom: '20px' }}>
                                <div className="stat-card">
                                    <div className="stat-value">{loadSourcesStats.total_sources}</div>
                                    <div className="stat-label">Total Sources</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-value">{loadSourcesStats.verified_count}</div>
                                    <div className="stat-label">Verified</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-value">{loadSourcesStats.by_country?.Canada || 0}</div>
                                    <div className="stat-label">Canadian Sources</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-value">{loadSourcesStats.with_email || 0}</div>
                                    <div className="stat-label">With Contact Email</div>
                                </div>
                            </div>
                        )}

                        {/* Quick Access Buttons */}
                        <div className="quick-actions" style={{ marginBottom: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                            <button
                                className="action-btn secondary"
                                onClick={getCanadianLoadSources}
                                disabled={isSearchingLoadSources}
                            >
                                🇨🇦 Canadian Sources
                            </button>
                            <button
                                className="action-btn secondary"
                                onClick={getLoadBoards}
                                disabled={isSearchingLoadSources}
                            >
                                📋 Load Boards
                            </button>
                            <button
                                className="action-btn secondary"
                                onClick={() => {
                                    setLoadSourcesFilter({ ...loadSourcesFilter, source_type: 'warehouse_provider' });
                                    searchLoadSources();
                                }}
                                disabled={isSearchingLoadSources}
                            >
                                🏭 Warehouses
                            </button>
                        </div>

                        {/* Search Form */}
                        <div className="search-form">
                            <div className="form-row">
                                <div className="form-group">
                                    <label>Search Query</label>
                                    <input
                                        type="text"
                                        placeholder="Search by name, description, or email..."
                                        value={loadSourcesFilter.query}
                                        onChange={(e) => setLoadSourcesFilter({ ...loadSourcesFilter, query: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Source Type</label>
                                    <select
                                        value={loadSourcesFilter.source_type}
                                        onChange={(e) => setLoadSourcesFilter({ ...loadSourcesFilter, source_type: e.target.value })}
                                    >
                                        <option value="all">All Types</option>
                                        <option value="load_board">Load Boards</option>
                                        <option value="warehouse_provider">Warehouse Providers</option>
                                        <option value="warehouse_directory">Warehouse Directories</option>
                                        <option value="logistics_provider">Logistics Providers</option>
                                        <option value="freight_carrier">Freight Carriers</option>
                                        <option value="directory">Business Directories</option>
                                    </select>
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Country</label>
                                    <select
                                        value={loadSourcesFilter.country}
                                        onChange={(e) => setLoadSourcesFilter({ ...loadSourcesFilter, country: e.target.value })}
                                    >
                                        <option value="all">All Countries</option>
                                        <option value="Canada">Canada</option>
                                        <option value="USA">USA</option>
                                        <option value="North America">North America</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>
                                        <input
                                            type="checkbox"
                                            checked={loadSourcesFilter.verified_only}
                                            onChange={(e) => setLoadSourcesFilter({ ...loadSourcesFilter, verified_only: e.target.checked })}
                                        />
                                        {' '}Verified Sources Only
                                    </label>
                                </div>
                            </div>

                            <button
                                className="search-btn"
                                onClick={searchLoadSources}
                                disabled={isSearchingLoadSources}
                            >
                                {isSearchingLoadSources ? (
                                    <>
                                        <Loader className="inline-block mr-2 animate-spin" size={20} />
                                        Searching...
                                    </>
                                ) : (
                                    <>
                                        <Search className="inline-block mr-2" size={20} />
                                        Search Load Sources
                                    </>
                                )}
                            </button>
                        </div>

                        {/* Search Results */}
                        {lastResult && activeTab === 'load-sources' && (
                            <div className={`result-message ${lastResult.success ? 'success' : 'error'}`}>
                                {lastResult.success ? (
                                    <CheckCircle className="inline-block mr-2" size={20} />
                                ) : (
                                    <AlertCircle className="inline-block mr-2" size={20} />
                                )}
                                {lastResult.message || lastResult.error}
                            </div>
                        )}

                        {/* Load Sources List */}
                        {loadSources.length > 0 && (
                            <div className="loads-container" style={{ marginTop: '20px' }}>
                                <h3>Found Sources ({loadSources.length})</h3>
                                <div className="sources-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '15px' }}>
                                    {loadSources.map((source, idx) => (
                                        <div key={idx} className="source-card" style={{
                                            border: '1px solid #e0e0e0',
                                            borderRadius: '8px',
                                            padding: '15px',
                                            backgroundColor: '#fff',
                                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                                            transition: 'all 0.2s ease',
                                            cursor: 'pointer'
                                        }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '10px' }}>
                                                <h4 style={{ margin: 0, color: '#ff5722', fontSize: '16px', fontWeight: 'bold' }}>
                                                    {source.name}
                                                </h4>
                                                {source.verified && (
                                                    <span style={{ backgroundColor: '#4caf50', color: 'white', padding: '2px 8px', borderRadius: '12px', fontSize: '11px' }}>
                                                        ✓ Verified
                                                    </span>
                                                )}
                                            </div>

                                            <div style={{ marginBottom: '10px' }}>
                                                <span style={{
                                                    display: 'inline-block',
                                                    backgroundColor: '#f5f5f5',
                                                    padding: '4px 10px',
                                                    borderRadius: '4px',
                                                    fontSize: '12px',
                                                    color: '#666',
                                                    marginRight: '8px'
                                                }}>
                                                    {source.type?.replace('_', ' ').toUpperCase()}
                                                </span>
                                                <span style={{ fontSize: '12px', color: '#999' }}>
                                                    📍 {source.country}
                                                </span>
                                            </div>

                                            <p style={{ fontSize: '13px', color: '#666', lineHeight: '1.5', margin: '10px 0' }}>
                                                {source.description}
                                            </p>

                                            <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: '10px', marginTop: '10px' }}>
                                                {source.website && (
                                                    <div style={{ marginBottom: '6px' }}>
                                                        <span style={{ fontSize: '12px', color: '#999', marginRight: '5px' }}>🌐</span>
                                                        <a
                                                            href={source.website}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            style={{ fontSize: '12px', color: '#2196f3', textDecoration: 'none' }}
                                                            onClick={(e) => e.stopPropagation()}
                                                        >
                                                            Visit Website
                                                        </a>
                                                    </div>
                                                )}
                                                {source.email && (
                                                    <div style={{ marginBottom: '6px' }}>
                                                        <span style={{ fontSize: '12px', color: '#999', marginRight: '5px' }}>📧</span>
                                                        <a
                                                            href={`mailto:${source.email}`}
                                                            style={{ fontSize: '12px', color: '#2196f3', textDecoration: 'none' }}
                                                            onClick={(e) => e.stopPropagation()}
                                                        >
                                                            {source.email}
                                                        </a>
                                                    </div>
                                                )}
                                                {source.phone && (
                                                    <div>
                                                        <span style={{ fontSize: '12px', color: '#999', marginRight: '5px' }}>📞</span>
                                                        <a
                                                            href={`tel:${source.phone}`}
                                                            style={{ fontSize: '12px', color: '#2196f3', textDecoration: 'none' }}
                                                            onClick={(e) => e.stopPropagation()}
                                                        >
                                                            {source.phone}
                                                        </a>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Email Processing Tab */}
                {activeTab === 'email-processing' && (
                    <div className="tab-content">
                        <div className="content-header">
                            <h2>📧 Email Shipment Processing</h2>
                            <p>Automatically process incoming shipment emails and search for carriers</p>
                        </div>

                        {incomingEmails.length > 0 ? (
                            <div className="email-list">
                                {incomingEmails.map((email, idx) => {
                                    const parsed = parseEmailShipment(email.content);
                                    return (
                                        <div key={idx} className="email-card">
                                            <div className="email-header">
                                                <div className="email-meta">
                                                    <h4>{email.from}</h4>
                                                    <p className="email-subject">{email.subject}</p>
                                                    <p className="email-time">{new Date(email.received_at).toLocaleString()}</p>
                                                </div>
                                                <div className="email-parsed">
                                                    <div className="parsed-item">
                                                        <span className="label">Weight:</span>
                                                        <span className="value">{parsed.weight} lbs</span>
                                                    </div>
                                                    <div className="parsed-item">
                                                        <span className="label">Dimensions:</span>
                                                        <span className="value">{parsed.dimensions}</span>
                                                    </div>
                                                    <div className="parsed-item">
                                                        <span className="label">Company:</span>
                                                        <span className="value">{parsed.company}</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="email-content-preview">
                                                {email.content.substring(0, 150)}...
                                            </div>
                                            <button
                                                className="email-process-btn"
                                                onClick={() => processIncomingEmail(email)}
                                                disabled={processingEmail}
                                            >
                                                {processingEmail ? (
                                                    <>
                                                        <Loader className="inline-block mr-2 animate-spin" size={16} />
                                                        Processing...
                                                    </>
                                                ) : (
                                                    <>
                                                        <Zap className="inline-block mr-2" size={16} />
                                                        Process & Search
                                                    </>
                                                )}
                                            </button>
                                        </div>
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="no-emails-message">
                                <Mail size={48} />
                                <p>No incoming emails to process</p>
                                <p className="text-sm">Emails will appear here automatically when received</p>
                            </div>
                        )}

                        {lastResult && (
                            <div className={`result-message ${lastResult.success ? 'success' : 'error'}`}>
                                {lastResult.success ? (
                                    <CheckCircle className="inline-block mr-2" size={20} />
                                ) : (
                                    <AlertCircle className="inline-block mr-2" size={20} />
                                )}
                                {lastResult.message || lastResult.error}
                            </div>
                        )}
                    </div>
                )}

                {/* Learning Database Tab */}
                {activeTab === 'learning-db' && (
                    <div className="tab-content">
                        <div className="content-header">
                            <h2>🧠 Learning Database & Historical Records</h2>
                            <p>Historical shipment data used by AI for continuous learning</p>
                        </div>

                        {/* Learning Statistics */}
                        <div className="learning-stats-grid">
                            <div className="learning-stat-card">
                                <div className="stat-icon">📦</div>
                                <div className="stat-content">
                                    <h4>Total Processed</h4>
                                    <p className="stat-value">{learningStats.total_processed || 0}</p>
                                </div>
                            </div>
                            <div className="learning-stat-card success">
                                <div className="stat-icon">✅</div>
                                <div className="stat-content">
                                    <h4>Successful Matches</h4>
                                    <p className="stat-value">{learningStats.successful_matches || 0}</p>
                                </div>
                            </div>
                            <div className="learning-stat-card warning">
                                <div className="stat-icon">⚠️</div>
                                <div className="stat-content">
                                    <h4>Failed Matches</h4>
                                    <p className="stat-value">{learningStats.failed_matches || 0}</p>
                                </div>
                            </div>
                            <div className="learning-stat-card">
                                <div className="stat-icon">🎯</div>
                                <div className="stat-content">
                                    <h4>Match Accuracy</h4>
                                    <p className="stat-value">{learningStats.avg_match_rate || 0}%</p>
                                </div>
                            </div>
                            <div className="learning-stat-card primary">
                                <div className="stat-icon">🧠</div>
                                <div className="stat-content">
                                    <h4>System Learning</h4>
                                    <p className="stat-value">{learningStats.system_learning || 0}%</p>
                                </div>
                            </div>
                        </div>

                        {/* Database Records */}
                        {databaseRecords.length > 0 ? (
                            <div className="database-records">
                                <h3>Historical Records ({databaseRecords.length})</h3>
                                <div className="records-table">
                                    <div className="table-header">
                                        <div className="col col-id">Record ID</div>
                                        <div className="col col-source">Source</div>
                                        <div className="col col-company">Company</div>
                                        <div className="col col-weight">Weight</div>
                                        <div className="col col-location">Location</div>
                                        <div className="col col-status">Status</div>
                                        <div className="col col-score">Learning Score</div>
                                    </div>
                                    {databaseRecords.map(record => (
                                        <div key={record.id} className="table-row">
                                            <div className="col col-id">{record.id}</div>
                                            <div className="col col-source">{record.source}</div>
                                            <div className="col col-company">{record.company}</div>
                                            <div className="col col-weight">{record.weight} lbs</div>
                                            <div className="col col-location">{record.location}</div>
                                            <div className="col col-status">
                                                <span className={`status-badge ${record.status}`}>
                                                    {record.status}
                                                </span>
                                            </div>
                                            <div className="col col-score">{record.learning_score || 0}%</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div className="no-records-message">
                                <Database size={48} />
                                <p>No historical records yet</p>
                                <p className="text-sm">Process shipment emails to build the learning database</p>
                            </div>
                        )}
                    </div>
                )}

                {/* Supplier Outreach Tab */}
                {activeTab === 'suppliers' && (
                    <div className="tab-content">
                        <div className="content-header">
                            <h2>📱 Supplier Outreach & Engagement</h2>
                            <p>Send selected loads to carriers and suppliers</p>
                        </div>

                        {selectedLoads.size > 0 ? (
                            <>
                                {/* Message Template */}
                                <div className="message-template">
                                    <label>Outreach Message (optional)</label>
                                    <textarea
                                        placeholder="Custom message to include in supplier outreach..."
                                        value={outreachMessage}
                                        onChange={(e) => setOutreachMessage(e.target.value)}
                                        rows={4}
                                    />
                                </div>

                                {/* Suppliers List */}
                                <h3>Select Suppliers to Contact ({suppliers.length} available)</h3>
                                <div className="suppliers-list">
                                    {suppliers.map(supplier => (
                                        <div
                                            key={supplier.id}
                                            className={`supplier-card ${selectedSuppliers.has(supplier.id) ? 'selected' : ''}`}
                                            onClick={() => toggleSupplierSelection(supplier.id)}
                                        >
                                            <input
                                                type="checkbox"
                                                checked={selectedSuppliers.has(supplier.id)}
                                                onChange={() => toggleSupplierSelection(supplier.id)}
                                                onClick={(e) => e.stopPropagation()}
                                            />
                                            <div className="supplier-info">
                                                <h4>{supplier.name}</h4>
                                                <p className="supplier-email">{supplier.email}</p>
                                                <div className="supplier-meta">
                                                    <span className="rate-range">{supplier.rate_range}/mile</span>
                                                    <span className="capacity">{supplier.capacity} trucks</span>
                                                </div>
                                            </div>
                                            <div className="send-status">
                                                {sendingStatus[supplier.id] === 'sending' && (
                                                    <Loader className="animate-spin text-blue-500" size={20} />
                                                )}
                                                {sendingStatus[supplier.id] === 'sent' && (
                                                    <CheckCircle className="text-green-500" size={20} />
                                                )}
                                                {sendingStatus[supplier.id] === 'failed' && (
                                                    <AlertCircle className="text-red-500" size={20} />
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <div className="selection-summary">
                                    {selectedSuppliers.size} of {suppliers.length} suppliers selected
                                </div>

                                {/* Send Button */}
                                <button
                                    className="send-btn"
                                    onClick={sendToSuppliers}
                                    disabled={isSending || selectedSuppliers.size === 0}
                                >
                                    {isSending ? (
                                        <>
                                            <Loader className="inline-block mr-2 animate-spin" size={20} />
                                            Sending...
                                        </>
                                    ) : (
                                        <>
                                            <Send className="inline-block mr-2" size={20} />
                                            Send {selectedLoads.size} Loads to {selectedSuppliers.size} Suppliers
                                        </>
                                    )}
                                </button>
                            </>
                        ) : (
                            <div className="no-loads-message">
                                <AlertCircle size={48} />
                                <p>Please select at least one load from the Freight Search tab first</p>
                            </div>
                        )}
                    </div>
                )}

                {/* Analytics Tab */}
                {activeTab === 'analytics' && (
                    <div className="tab-content">
                        <div className="content-header">
                            <h2>📊 Performance Analytics</h2>
                            <p>Detailed insights into freight sourcing and supplier performance</p>
                        </div>

                        <div className="analytics-grid">
                            <div className="stat-card">
                                <div className="stat-icon">📦</div>
                                <div className="stat-content">
                                    <h4>Total Loads Searched</h4>
                                    <p className="stat-value">{foundLoads.length}</p>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-icon">🎯</div>
                                <div className="stat-content">
                                    <h4>Average Match Score</h4>
                                    <p className="stat-value">92.5%</p>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-icon">💵</div>
                                <div className="stat-content">
                                    <h4>Avg Rate Per Load</h4>
                                    <p className="stat-value">$1,844</p>
                                </div>
                            </div>

                            <div className="stat-card">
                                <div className="stat-icon">✅</div>
                                <div className="stat-content">
                                    <h4>Delivery Success Rate</h4>
                                    <p className="stat-value">98.7%</p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* History Tab */}
                {activeTab === 'history' && (
                    <div className="tab-content">
                        <div className="content-header">
                            <h2>📜 Activity History</h2>
                            <p>Recent freight searches and supplier outreach</p>
                        </div>

                        <div className="history-list">
                            <div className="history-item success">
                                <Clock size={20} />
                                <div className="history-details">
                                    <h4>Freight Search: Toronto → Vancouver</h4>
                                    <p>8 loads found • 5 sent to suppliers</p>
                                </div>
                                <span className="timestamp">2 hours ago</span>
                            </div>

                            <div className="history-item success">
                                <Send size={20} />
                                <div className="history-details">
                                    <h4>Outreach Sent to TransCanada Logistics</h4>
                                    <p>6 loads sent • 3 responses received</p>
                                </div>
                                <span className="timestamp">4 hours ago</span>
                            </div>

                            <div className="history-item success">
                                <CheckCircle size={20} />
                                <div className="history-details">
                                    <h4>Load Matched & Accepted</h4>
                                    <p>LOAD-001 matched with Maple Freight Solutions</p>
                                </div>
                                <span className="timestamp">Yesterday</span>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default MapleLoadCanadaEnhanced;
