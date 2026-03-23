// frontend/src/components/memory/SharedMemoryDashboard.jsx
import React, { useState, useEffect } from 'react';

const SharedMemoryDashboard = () => {
    const [memoryStats, setMemoryStats] = useState({});
    const [recentActivity, setRecentActivity] = useState([]);

    useEffect(() => {
        const updateStats = () => {
            const stats = window.sharedMemorySystem?.getStats();
            setMemoryStats(stats || {});
        };

        const interval = setInterval(updateStats, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl shadow-lg">
            <h3 className="text-2xl font-bold mb-6">💾 Smart Shared Memory</h3>

            <div className="grid grid-cols-4 gap-4 mb-6">
                <div className="bg-white p-4 rounded-lg shadow">
                    <div className="text-2xl font-bold text-blue-600">
                        {memoryStats.totalItems || 0}
                    </div>
                    <div className="text-sm text-gray-600">Items in Memory</div>
                </div>

                <div className="bg-white p-4 rounded-lg shadow">
                    <div className="text-2xl font-bold text-green-600">
                        {memoryStats.activeSubscriptions || 0}
                    </div>
                    <div className="text-sm text-gray-600">Active Subscriptions</div>
                </div>

                <div className="bg-white p-4 rounded-lg shadow">
                    <div className="text-2xl font-bold text-purple-600">
                        {memoryStats.memoryUsage || '0'}%
                    </div>
                    <div className="text-sm text-gray-600">Memory Usage</div>
                </div>

                <div className="bg-white p-4 rounded-lg shadow">
                    <div className="text-2xl font-bold text-orange-600">
                        {memoryStats.historySize || 0}
                    </div>
                    <div className="text-sm text-gray-600">Change Log</div>
                </div>
            </div>

            <div className="bg-white rounded-lg shadow p-4">
                <h4 className="font-semibold mb-3">📊 Recent Activity</h4>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                    {recentActivity.map((activity, index) => (
                        <div key={index} className="flex justify-between items-center p-2 border-b">
                            <div>
                                <span className="font-medium">{activity.key}</span>
                                <span className="text-xs text-gray-500 ml-2">{activity.action}</span>
                            </div>
                            <span className="text-xs text-gray-400">
                                {new Date(activity.timestamp).toLocaleTimeString()}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default SharedMemoryDashboard;
