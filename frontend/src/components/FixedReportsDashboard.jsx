// frontend/src/pages/FixedReportsDashboard.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../api';

const FixedReportsDashboard = () => {
    const [reportData, setReportData] = useState(null);
    const [analysisData, setAnalysisData] = useState(null);
    const [loading, setLoading] = useState(true);

    const loadData = async () => {
        setLoading(true);

        try {
            const [reportResponse, analysisResponse] = await Promise.all([
                api.getWeeklyReports({ since_days: 7 }),
                api.getAiGeneralAnalysis({ from_month: '2025-11', to_month: '2025-11' })
            ]);

            setReportData(reportResponse);
            setAnalysisData(analysisResponse);

        } catch (error) {
            console.error('Error loading data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    if (loading) {
        return (
            <div className="p-6">
                <div className="animate-pulse space-y-4">
                    <div className="h-8 bg-gray-200 rounded w-1/3"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                    <div className="grid grid-cols-2 gap-4 mt-6">
                        <div className="h-24 bg-gray-200 rounded"></div>
                        <div className="h-24 bg-gray-200 rounded"></div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold">AI Reports Dashboard</h2>
                <button
                    onClick={loadData}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                    Refresh Data
                </button>
            </div>

            {/* Financial Summary */}
            {analysisData?.financial_analysis && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                        <div className="text-2xl font-bold text-green-700">
                            ${analysisData.financial_analysis.total_income?.toLocaleString()}
                        </div>
                        <div className="text-sm text-green-600">Total Income</div>
                    </div>
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <div className="text-2xl font-bold text-blue-700">
                            ${analysisData.financial_analysis.total_revenue?.toLocaleString()}
                        </div>
                        <div className="text-sm text-blue-600">Total Revenue</div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                        <div className="text-2xl font-bold text-purple-700">
                            ${analysisData.financial_analysis.profit?.toLocaleString()}
                        </div>
                        <div className="text-sm text-purple-600">Profit</div>
                    </div>
                    <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                        <div className="text-2xl font-bold text-orange-700">
                            {analysisData.financial_analysis.profit_margin}
                        </div>
                        <div className="text-sm text-orange-600">Profit Margin</div>
                    </div>
                </div>
            )}

            {/* Rest of your dashboard components... */}
        </div>
    );
};

export default FixedReportsDashboard;
