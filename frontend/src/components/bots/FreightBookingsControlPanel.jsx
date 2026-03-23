/**
 * FreightBookingsControlPanel.jsx
 * Integrated freight bookings control panel
 * Comprehensive Freight Bookings Bot Control Panel
 */

import React, { useState, useEffect, useCallback } from 'react';
import axiosClient from '../../api/axiosClient';

const BOT_KEY = 'freight_bookings';

// ==================== TAB COMPONENTS ====================

// Tab 1: Load Management
const LoadManagementTab = ({ panelData, onAction }) => {
    const [newLoad, setNewLoad] = useState({
        origin: '',
        destination: '',
        weight: '',
        equipment: 'DryVan',
        rate: '',
        pickupDate: '',
        deliveryDate: ''
    });

    const activeLoads = panelData?.loads?.active || [];
    const pendingLoads = panelData?.loads?.pending || [];

    const handleCreateLoad = () => {
        if (newLoad.origin && newLoad.destination) {
            onAction('create_load', newLoad);
            setNewLoad({
                origin: '',
                destination: '',
                weight: '',
                equipment: 'DryVan',
                rate: '',
                pickupDate: '',
                deliveryDate: ''
            });
        }
    };

    return (
        <div className="space-y-6">
            {/* Create New Load Form */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Create New Load
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Origin</label>
                        <input
                            type="text"
                            value={newLoad.origin}
                            onChange={(e) => setNewLoad({ ...newLoad, origin: e.target.value })}
                            placeholder="City, State"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Destination</label>
                        <input
                            type="text"
                            value={newLoad.destination}
                            onChange={(e) => setNewLoad({ ...newLoad, destination: e.target.value })}
                            placeholder="City, State"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Weight (lbs)</label>
                        <input
                            type="number"
                            value={newLoad.weight}
                            onChange={(e) => setNewLoad({ ...newLoad, weight: e.target.value })}
                            placeholder="45000"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Equipment</label>
                        <select
                            value={newLoad.equipment}
                            onChange={(e) => setNewLoad({ ...newLoad, equipment: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="DryVan">Dry Van</option>
                            <option value="Reefer">Reefer</option>
                            <option value="Flatbed">Flatbed</option>
                            <option value="StepDeck">Step Deck</option>
                            <option value="Tanker">Tanker</option>
                            <option value="Hotshot">Hotshot</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Rate ($)</label>
                        <input
                            type="number"
                            value={newLoad.rate}
                            onChange={(e) => setNewLoad({ ...newLoad, rate: e.target.value })}
                            placeholder="2500"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Pickup Date</label>
                        <input
                            type="date"
                            value={newLoad.pickupDate}
                            onChange={(e) => setNewLoad({ ...newLoad, pickupDate: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                </div>

                <button
                    onClick={handleCreateLoad}
                    className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                    <span></span> Create Load
                </button>
            </div>

            {/* Active Loads */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Active Loads ({activeLoads.length})
                </h3>

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-900">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Load ID</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Route</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Carrier</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Rate</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {activeLoads.length > 0 ? activeLoads.map((load, idx) => (
                                <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                    <td className="px-4 py-3 text-sm font-medium text-blue-600">{load.id || `LD-${1000 + idx}`}</td>
                                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{load.origin}  {load.destination}</td>
                                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{load.carrier || 'Assigned'}</td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded-full ${load.status === 'In Transit' ? 'bg-blue-100 text-blue-800' :
                                            load.status === 'Delivered' ? 'bg-green-100 text-green-800' :
                                                'bg-yellow-100 text-yellow-800'
                                            }`}>
                                            {load.status || 'In Transit'}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm font-medium text-green-600">${load.rate?.toLocaleString() || '0'}</td>
                                    <td className="px-4 py-3">
                                        <button
                                            onClick={() => onAction('track_load', { loadId: load.id })}
                                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                        >
                                            Track
                                        </button>
                                    </td>
                                </tr>
                            )) : (
                                <tr>
                                    <td colSpan="6" className="px-4 py-8 text-center text-gray-500">No active loads</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Pending Loads */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Pending Bookings ({pendingLoads.length})
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {pendingLoads.length > 0 ? pendingLoads.map((load, idx) => (
                        <div key={idx} className="p-4 border border-yellow-200 dark:border-yellow-800 rounded-lg bg-yellow-50 dark:bg-yellow-900/20">
                            <div className="flex justify-between items-start mb-2">
                                <span className="font-medium text-gray-900 dark:text-white">{load.origin}  {load.destination}</span>
                                <span className="text-xs bg-yellow-200 text-yellow-800 px-2 py-1 rounded">Pending</span>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Equipment: {load.equipment}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Rate: ${load.rate?.toLocaleString()}</p>
                            <div className="mt-3 flex gap-2">
                                <button
                                    onClick={() => onAction('confirm_load', { loadId: load.id })}
                                    className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded"
                                >
                                    Confirm
                                </button>
                                <button
                                    onClick={() => onAction('cancel_load', { loadId: load.id })}
                                    className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    )) : (
                        <p className="text-gray-500 col-span-full text-center py-4">No pending bookings</p>
                    )}
                </div>
            </div>
        </div>
    );
};

// Tab 2: Carrier Coordination
const CarrierCoordinationTab = ({ panelData, onAction }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const carriers = panelData?.carriers || [];
    const availableCarriers = panelData?.availableCarriers || [];

    const filteredCarriers = carriers.filter(c =>
        c.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.mc?.includes(searchTerm)
    );

    return (
        <div className="space-y-6">
            {/* Carrier Search */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Carrier Search & Assignment
                </h3>

                <div className="flex gap-4 mb-4">
                    <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Search by name or MC#..."
                        className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                        onClick={() => onAction('search_carriers', { query: searchTerm })}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
                    >
                        Search
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {(filteredCarriers.length > 0 ? filteredCarriers : availableCarriers).slice(0, 6).map((carrier, idx) => (
                        <div key={idx} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start mb-2">
                                <h4 className="font-medium text-gray-900 dark:text-white">{carrier.name || `Carrier ${idx + 1}`}</h4>
                                <span className={`px-2 py-1 text-xs rounded ${carrier.status === 'Available' ? 'bg-green-100 text-green-800' :
                                    carrier.status === 'Busy' ? 'bg-yellow-100 text-yellow-800' :
                                        'bg-gray-100 text-gray-800'
                                    }`}>
                                    {carrier.status || 'Available'}
                                </span>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">MC# {carrier.mc || '123456'}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Rating:  {carrier.rating || '4.5'}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Equipment: {carrier.equipment || 'Dry Van, Reefer'}</p>
                            <button
                                onClick={() => onAction('assign_carrier', { carrierId: carrier.id })}
                                className="mt-3 w-full px-3 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg"
                            >
                                Assign to Load
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Carrier Performance */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Carrier Performance Dashboard
                </h3>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-center">
                        <p className="text-3xl font-bold text-blue-600">{panelData?.carrierStats?.total || 150}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Total Carriers</p>
                    </div>
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg text-center">
                        <p className="text-3xl font-bold text-green-600">{panelData?.carrierStats?.active || 85}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Active Now</p>
                    </div>
                    <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg text-center">
                        <p className="text-3xl font-bold text-yellow-600">{panelData?.carrierStats?.onTime || '94%'}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">On-Time Rate</p>
                    </div>
                    <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg text-center">
                        <p className="text-3xl font-bold text-purple-600">{panelData?.carrierStats?.avgRating || '4.6'}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Avg Rating</p>
                    </div>
                </div>

                {/* Top Performers */}
                <h4 className="font-medium text-gray-800 dark:text-white mb-3">Top Performing Carriers</h4>
                <div className="space-y-2">
                    {(panelData?.topCarriers || [
                        { name: 'Swift Transport', loads: 45, rating: 4.9 },
                        { name: 'Prime Logistics', loads: 38, rating: 4.8 },
                        { name: 'Eagle Freight', loads: 32, rating: 4.7 }
                    ]).map((carrier, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                            <div className="flex items-center gap-3">
                                <span className="text-xl">{idx === 0 ? '' : idx === 1 ? '' : ''}</span>
                                <span className="font-medium text-gray-900 dark:text-white">{carrier.name}</span>
                            </div>
                            <div className="flex items-center gap-4">
                                <span className="text-sm text-gray-600 dark:text-gray-400">{carrier.loads} loads</span>
                                <span className="text-sm text-yellow-600"> {carrier.rating}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Communication Center */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Communication Center
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button
                        onClick={() => onAction('send_rate_confirmation', {})}
                        className="p-4 border-2 border-dashed border-blue-300 dark:border-blue-600 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors text-center"
                    >
                        <span className="text-3xl block mb-2"></span>
                        <span className="font-medium text-gray-900 dark:text-white">Send Rate Confirmation</span>
                    </button>

                    <button
                        onClick={() => onAction('request_pod', {})}
                        className="p-4 border-2 border-dashed border-green-300 dark:border-green-600 rounded-lg hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors text-center"
                    >
                        <span className="text-3xl block mb-2"></span>
                        <span className="font-medium text-gray-900 dark:text-white">Request POD</span>
                    </button>

                    <button
                        onClick={() => onAction('send_dispatch_sheet', {})}
                        className="p-4 border-2 border-dashed border-purple-300 dark:border-purple-600 rounded-lg hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors text-center"
                    >
                        <span className="text-3xl block mb-2"></span>
                        <span className="font-medium text-gray-900 dark:text-white">Send Dispatch Sheet</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

// Tab 3: Booking Queue
const BookingQueueTab = ({ panelData, onAction }) => {
    const [filter, setFilter] = useState('all');
    const bookings = panelData?.bookings || [];

    const filteredBookings = bookings.filter(b =>
        filter === 'all' || b.status?.toLowerCase() === filter
    );

    return (
        <div className="space-y-6">
            {/* Queue Stats */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {[
                    { label: 'Total', value: panelData?.queueStats?.total || 45, color: 'blue', filter: 'all' },
                    { label: 'New', value: panelData?.queueStats?.new || 12, color: 'green', filter: 'new' },
                    { label: 'Processing', value: panelData?.queueStats?.processing || 18, color: 'yellow', filter: 'processing' },
                    { label: 'Confirmed', value: panelData?.queueStats?.confirmed || 10, color: 'purple', filter: 'confirmed' },
                    { label: 'Urgent', value: panelData?.queueStats?.urgent || 5, color: 'red', filter: 'urgent' }
                ].map((stat, idx) => (
                    <button
                        key={idx}
                        onClick={() => setFilter(stat.filter)}
                        className={`p-4 rounded-xl text-center transition-all ${filter === stat.filter
                            ? `bg-${stat.color}-600 text-white shadow-lg`
                            : `bg-${stat.color}-50 dark:bg-${stat.color}-900/20 hover:shadow-md`
                            }`}
                    >
                        <p className={`text-3xl font-bold ${filter === stat.filter ? 'text-white' : `text-${stat.color}-600`}`}>
                            {stat.value}
                        </p>
                        <p className={`text-sm ${filter === stat.filter ? 'text-white/80' : 'text-gray-600 dark:text-gray-400'}`}>
                            {stat.label}
                        </p>
                    </button>
                ))}
            </div>

            {/* Booking Queue List */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="text-2xl"></span>
                        Booking Queue
                    </h3>
                    <button
                        onClick={() => onAction('process_all_bookings', {})}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium"
                    >
                        Process All
                    </button>
                </div>

                <div className="space-y-3">
                    {(filteredBookings.length > 0 ? filteredBookings : [
                        { id: 'BK-001', shipper: 'ABC Corp', route: 'Chicago, IL  Dallas, TX', equipment: 'Dry Van', rate: 2500, status: 'New', priority: 'High' },
                        { id: 'BK-002', shipper: 'XYZ Inc', route: 'Atlanta, GA  Miami, FL', equipment: 'Reefer', rate: 1800, status: 'Processing', priority: 'Medium' },
                        { id: 'BK-003', shipper: 'Global Trade', route: 'Los Angeles, CA  Phoenix, AZ', equipment: 'Flatbed', rate: 2200, status: 'Confirmed', priority: 'Normal' }
                    ]).map((booking, idx) => (
                        <div key={idx} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow">
                            <div className="flex flex-wrap items-center justify-between gap-4">
                                <div className="flex items-center gap-4">
                                    <div>
                                        <span className="font-bold text-blue-600">{booking.id}</span>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">{booking.shipper}</p>
                                    </div>
                                    <div>
                                        <p className="font-medium text-gray-900 dark:text-white">{booking.route}</p>
                                        <p className="text-sm text-gray-500">{booking.equipment}</p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-4">
                                    <span className="text-lg font-bold text-green-600">${booking.rate?.toLocaleString()}</span>

                                    <span className={`px-3 py-1 text-xs rounded-full ${booking.status === 'New' ? 'bg-green-100 text-green-800' :
                                        booking.status === 'Processing' ? 'bg-yellow-100 text-yellow-800' :
                                            booking.status === 'Confirmed' ? 'bg-purple-100 text-purple-800' :
                                                'bg-gray-100 text-gray-800'
                                        }`}>
                                        {booking.status}
                                    </span>

                                    <span className={`px-2 py-1 text-xs rounded ${booking.priority === 'High' ? 'bg-red-100 text-red-800' :
                                        booking.priority === 'Medium' ? 'bg-orange-100 text-orange-800' :
                                            'bg-gray-100 text-gray-800'
                                        }`}>
                                        {booking.priority}
                                    </span>

                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => onAction('process_booking', { bookingId: booking.id })}
                                            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded"
                                        >
                                            Process
                                        </button>
                                        <button
                                            onClick={() => onAction('view_booking', { bookingId: booking.id })}
                                            className="px-3 py-1 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm rounded"
                                        >
                                            View
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Tab 4: Rate Management
const RateManagementTab = ({ panelData, onAction }) => {
    const [rateSettings, setRateSettings] = useState({
        baseRate: panelData?.rateSettings?.baseRate || 2.50,
        fuelSurcharge: panelData?.rateSettings?.fuelSurcharge || 15,
        detentionRate: panelData?.rateSettings?.detentionRate || 75,
        layoverRate: panelData?.rateSettings?.layoverRate || 350
    });

    return (
        <div className="space-y-6">
            {/* Rate Calculator */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Rate Calculator
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Base Rate ($/mile)</label>
                        <input
                            type="number"
                            step="0.01"
                            value={rateSettings.baseRate}
                            onChange={(e) => setRateSettings({ ...rateSettings, baseRate: parseFloat(e.target.value) })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fuel Surcharge (%)</label>
                        <input
                            type="number"
                            value={rateSettings.fuelSurcharge}
                            onChange={(e) => setRateSettings({ ...rateSettings, fuelSurcharge: parseInt(e.target.value) })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Detention Rate ($/hr)</label>
                        <input
                            type="number"
                            value={rateSettings.detentionRate}
                            onChange={(e) => setRateSettings({ ...rateSettings, detentionRate: parseInt(e.target.value) })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Layover Rate ($/day)</label>
                        <input
                            type="number"
                            value={rateSettings.layoverRate}
                            onChange={(e) => setRateSettings({ ...rateSettings, layoverRate: parseInt(e.target.value) })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                    </div>
                </div>

                <button
                    onClick={() => onAction('update_rate_settings', rateSettings)}
                    className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
                >
                    Update Rate Settings
                </button>
            </div>

            {/* Market Rate Analysis */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Market Rate Analysis
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[
                        { lane: 'Chicago  Dallas', avgRate: '$2.35/mi', trend: '+5%', volume: 'High' },
                        { lane: 'LA  Phoenix', avgRate: '$2.80/mi', trend: '+12%', volume: 'Medium' },
                        { lane: 'Atlanta  Miami', avgRate: '$2.15/mi', trend: '-3%', volume: 'High' }
                    ].map((lane, idx) => (
                        <div key={idx} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                            <h4 className="font-medium text-gray-900 dark:text-white mb-2">{lane.lane}</h4>
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-sm text-gray-600 dark:text-gray-400">Avg Rate</span>
                                    <span className="font-medium text-blue-600">{lane.avgRate}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-sm text-gray-600 dark:text-gray-400">Trend</span>
                                    <span className={`font-medium ${lane.trend.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                                        {lane.trend}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-sm text-gray-600 dark:text-gray-400">Volume</span>
                                    <span className="font-medium text-gray-900 dark:text-white">{lane.volume}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Rate History */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl"></span>
                    Recent Rate History
                </h3>

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-900">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lane</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Equipment</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rate</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Miles</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">RPM</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {(panelData?.rateHistory || [
                                { date: '2025-01-15', lane: 'Chicago  Dallas', equipment: 'Dry Van', rate: 2500, miles: 920, rpm: 2.72 },
                                { date: '2025-01-14', lane: 'LA  Phoenix', equipment: 'Reefer', rate: 1200, miles: 370, rpm: 3.24 },
                                { date: '2025-01-14', lane: 'Atlanta  Miami', equipment: 'Dry Van', rate: 1400, miles: 660, rpm: 2.12 }
                            ]).map((rate, idx) => (
                                <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{rate.date}</td>
                                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{rate.lane}</td>
                                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{rate.equipment}</td>
                                    <td className="px-4 py-3 text-sm font-medium text-green-600">${rate.rate?.toLocaleString()}</td>
                                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{rate.miles}</td>
                                    <td className="px-4 py-3 text-sm font-medium text-blue-600">${rate.rpm?.toFixed(2)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

// ==================== MAIN COMPONENT ====================

const FreightBookingsControlPanel = () => {
    const [activeTab, setActiveTab] = useState('loads');
    const [panelData, setPanelData] = useState({});
    const [connected, setConnected] = useState(false);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [actionLog, setActionLog] = useState([]);

    // Fetch panel data
    const fetchPanelData = useCallback(async () => {
        try {
            const response = await axiosClient.get(`/api/v1/ai/bots/available/${BOT_KEY}/status`);
            setPanelData(response.data || {});
            setConnected(true);
            setLastUpdate(new Date());
        } catch (error) {
            console.error('Failed to fetch panel data:', error);
            setConnected(false);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchPanelData();
        const interval = setInterval(fetchPanelData, 30000);
        return () => clearInterval(interval);
    }, [fetchPanelData]);

    // Handle actions
    const handleAction = async (action, params = {}) => {
        const logEntry = {
            id: Date.now(),
            action,
            params,
            timestamp: new Date().toISOString(),
            status: 'pending'
        };
        setActionLog(prev => [logEntry, ...prev.slice(0, 19)]);

        try {
            const response = await axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
                action,
                ...params
            });

            setActionLog(prev => prev.map(log =>
                log.id === logEntry.id ? { ...log, status: 'success', result: response.data } : log
            ));

            fetchPanelData();
            return response.data;
        } catch (error) {
            setActionLog(prev => prev.map(log =>
                log.id === logEntry.id ? { ...log, status: 'error', error: error.message } : log
            ));
            throw error;
        }
    };

    const tabs = [
        { id: 'loads', label: 'Load Management', icon: '', component: LoadManagementTab },
        { id: 'carriers', label: 'Carrier Coordination', icon: '', component: CarrierCoordinationTab },
        { id: 'queue', label: 'Booking Queue', icon: '', component: BookingQueueTab },
        { id: 'rates', label: 'Rate Management', icon: '', component: RateManagementTab }
    ];

    const ActiveTabComponent = tabs.find(t => t.id === activeTab)?.component || LoadManagementTab;

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">Loading Freight Bookings Control Panel...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
            {/* Header */}
            <div className="bg-white dark:bg-gray-800 shadow-lg border-b border-gray-200 dark:border-gray-700">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-xl shadow-lg">
                                <span className="text-3xl"></span>
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                                    Freight Bookings Control Panel
                                </h1>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Load & Booking Management System
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            {/* Quick Stats */}
                            <div className="hidden md:flex items-center gap-4">
                                <div className="text-center px-4 py-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-blue-600">{panelData?.stats?.activeLoads || 25}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Active Loads</p>
                                </div>
                                <div className="text-center px-4 py-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-green-600">{panelData?.stats?.todayBookings || 12}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Today's Bookings</p>
                                </div>
                                <div className="text-center px-4 py-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                    <p className="text-xl font-bold text-purple-600">${panelData?.stats?.revenue?.toLocaleString() || '45,200'}</p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Revenue Today</p>
                                </div>
                            </div>

                            {/* Connection Status */}
                            <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                }`}>
                                <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></span>
                                <span className="text-sm font-medium">{connected ? 'Connected' : 'Disconnected'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="flex overflow-x-auto">
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center gap-2 px-6 py-4 border-b-2 transition-colors whitespace-nowrap ${activeTab === tab.id
                                    ? 'border-blue-600 text-blue-600 bg-blue-50 dark:bg-blue-900/20'
                                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                                    }`}
                            >
                                <span className="text-xl">{tab.icon}</span>
                                <span className="font-medium">{tab.label}</span>
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-4 py-6">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* Main Panel */}
                    <div className="lg:col-span-3">
                        <ActiveTabComponent panelData={panelData} onAction={handleAction} />
                    </div>

                    {/* Sidebar */}
                    <div className="lg:col-span-1 space-y-6">
                        {/* Quick Actions */}
                        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700">
                            <h3 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                <span></span> Quick Actions
                            </h3>
                            <div className="space-y-2">
                                <button
                                    onClick={() => handleAction('sync_load_boards', {})}
                                    className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Sync Load Boards
                                </button>
                                <button
                                    onClick={() => handleAction('auto_match_carriers', {})}
                                    className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Auto-Match Carriers
                                </button>
                                <button
                                    onClick={() => handleAction('generate_rate_quotes', {})}
                                    className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Generate Rate Quotes
                                </button>
                                <button
                                    onClick={() => handleAction('export_bookings', {})}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <span></span> Export Report
                                </button>
                            </div>
                        </div>

                        {/* Activity Log */}
                        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700">
                            <h3 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                <span></span> Activity Log
                            </h3>
                            <div className="space-y-2 max-h-64 overflow-y-auto">
                                {actionLog.length > 0 ? actionLog.slice(0, 5).map(log => (
                                    <div key={log.id} className="p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
                                        <div className="flex items-center justify-between">
                                            <span className="font-medium text-gray-900 dark:text-white">{log.action}</span>
                                            <span className={`text-xs px-2 py-0.5 rounded ${log.status === 'success' ? 'bg-green-100 text-green-800' :
                                                log.status === 'error' ? 'bg-red-100 text-red-800' :
                                                    'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                {log.status}
                                            </span>
                                        </div>
                                        <p className="text-xs text-gray-500 mt-1">
                                            {new Date(log.timestamp).toLocaleTimeString()}
                                        </p>
                                    </div>
                                )) : (
                                    <p className="text-sm text-gray-500 text-center py-4">No recent activity</p>
                                )}
                            </div>
                        </div>

                        {/* System Status */}
                        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700">
                            <h3 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                <span></span> System Status
                            </h3>
                            <div className="space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-gray-600 dark:text-gray-400">Load Board API</span>
                                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Online</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-gray-600 dark:text-gray-400">Carrier Database</span>
                                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Synced</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-gray-600 dark:text-gray-400">Rate Engine</span>
                                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Active</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-gray-600 dark:text-gray-400">Last Update</span>
                                    <span className="text-xs text-gray-500">
                                        {lastUpdate?.toLocaleTimeString() || 'N/A'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-6">
                <div className="max-w-7xl mx-auto px-4 py-3">
                    <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <span>Freight Bookings Control Panel v2.0</span>
                        <span>Last sync: {lastUpdate?.toLocaleString() || 'Never'}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FreightBookingsControlPanel;
