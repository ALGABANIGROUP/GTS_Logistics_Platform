// frontend/src/pages/MarketIntelligenceDashboard.jsx
/**
 * Market Intelligence Dashboard
 * AI-powered insights for shipments market
 * PayByCanada integration and market trends
 */

import React, { useEffect, useState } from "react";
import { useRealDataStore } from "../stores/useRealDataStore";
import { useEntitlements } from "../stores/useEntitlements";
import { TrendingUp, TrendingDown, AlertCircle, Activity, DollarSign, Truck } from "lucide-react";

export default function MarketIntelligenceDashboard() {
  const { shipmentIntelligence, reportAnalytics, loadingIntelligence, loadingAnalytics, fetchShipmentIntelligence, fetchReportAnalytics } = useRealDataStore();
  const hasPermission = useEntitlements((state) => state.hasPermission);
  const isSuperAdmin = useEntitlements((state) => state.isSuperAdmin);
  const canViewIntelligence = Boolean(isSuperAdmin?.() || hasPermission?.("reports.analytics"));

  const [selectedMetric, setSelectedMetric] = useState("market_health");

  useEffect(() => {
    fetchShipmentIntelligence();
    fetchReportAnalytics();
  }, [fetchShipmentIntelligence, fetchReportAnalytics]);

  if (!canViewIntelligence) {
    return (
      <div className="glass-card p-8 text-center text-yellow-200">
        <AlertCircle className="inline w-8 h-8 mr-2" />
        You don't have permission to view market intelligence
      </div>
    );
  }

  const loading = loadingIntelligence || loadingAnalytics;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Market Intelligence</h1>
        <p className="text-slate-400">AI-powered insights for shipment market and PayByCanada integration</p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="glass-card p-8 text-center">
          <Activity className="inline w-8 h-8 mr-2 animate-spin text-blue-400" />
          <span className="text-slate-300">Loading market intelligence...</span>
        </div>
      )}

      {!loading && shipmentIntelligence && (
        <>
          {/* Market Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Total Shipments */}
            <div className="glass-card p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Total Shipments Analyzed</span>
                <Truck className="w-5 h-5 text-orange-400" />
              </div>
              <div className="text-2xl font-bold text-white">{shipmentIntelligence.market_overview?.total_shipments_analyzed || 0}</div>
              <div className="text-xs text-slate-500">{shipmentIntelligence.market_overview?.analysis_period}</div>
            </div>

            {/* Market Health */}
            <div className="glass-card p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Market Health</span>
                <Activity className="w-5 h-5 text-green-400" />
              </div>
              <div className="text-2xl font-bold text-white capitalize">{shipmentIntelligence.market_overview?.market_health || "N/A"}</div>
              <div className="text-xs text-green-400">Healthy trend detected</div>
            </div>

            {/* PayByCanada Status */}
            <div className="glass-card p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">PayByCanada</span>
                <DollarSign className="w-5 h-5 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold text-emerald-400">
                {shipmentIntelligence.payment_integration?.paybycanada_enabled ? "Active" : "Inactive"}
              </div>
              <div className="text-xs text-slate-500">
                {shipmentIntelligence.payment_integration?.supported_currencies?.join(", ")}
              </div>
            </div>

            {/* Total Reports */}
            {reportAnalytics && (
              <div className="glass-card p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Total Reports</span>
                  <TrendingUp className="w-5 h-5 text-blue-400" />
                </div>
                <div className="text-2xl font-bold text-white">{reportAnalytics.total || 0}</div>
                <div className="text-xs text-slate-500">{reportAnalytics.active || 0} active</div>
              </div>
            )}
          </div>

          {/* Status Distribution */}
          {shipmentIntelligence.status_distribution && (
            <div className="glass-card p-6 space-y-4">
              <h2 className="text-lg font-semibold text-white">Shipment Status Distribution</h2>
              <div className="space-y-3">
                {Object.entries(shipmentIntelligence.status_distribution).map(([status, count]) => (
                  <div key={status} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400 capitalize">{status.replace(/_/g, " ")}</span>
                      <span className="text-white font-semibold">{count}</span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full"
                        style={{
                          width: `${(count / (shipmentIntelligence.market_overview?.total_shipments_analyzed || 1)) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Top Routes */}
          {shipmentIntelligence.top_routes && shipmentIntelligence.top_routes.length > 0 && (
            <div className="glass-card p-6 space-y-4">
              <h2 className="text-lg font-semibold text-white">Top Shipping Routes</h2>
              <div className="space-y-2">
                {shipmentIntelligence.top_routes.map(([route, count], idx) => (
                  <div key={route} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-sm font-semibold text-blue-400">#{idx + 1}</span>
                      <span className="text-white">{route}</span>
                    </div>
                    <span className="text-orange-400 font-semibold">{count} shipments</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Recommendations */}
          {shipmentIntelligence.ai_recommendations && shipmentIntelligence.ai_recommendations.length > 0 && (
            <div className="glass-card p-6 space-y-4">
              <h2 className="text-lg font-semibold text-white">AI Recommendations</h2>
              <div className="space-y-3">
                {shipmentIntelligence.ai_recommendations.map((recommendation, idx) => (
                  <div key={idx} className="flex items-start space-x-3 p-3 bg-slate-800/50 rounded-lg border border-cyan-500/20">
                    <TrendingUp className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                    <p className="text-slate-300">{recommendation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analytics Overview */}
          {reportAnalytics && (
            <div className="glass-card p-6 space-y-4">
              <h2 className="text-lg font-semibold text-white">Reports Analytics</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-3 bg-slate-800/50 rounded-lg">
                  <div className="text-sm text-slate-400">Total</div>
                  <div className="text-2xl font-bold text-white">{reportAnalytics.total}</div>
                </div>
                <div className="p-3 bg-slate-800/50 rounded-lg">
                  <div className="text-sm text-slate-400">Active</div>
                  <div className="text-2xl font-bold text-green-400">{reportAnalytics.active}</div>
                </div>
                <div className="p-3 bg-slate-800/50 rounded-lg">
                  <div className="text-sm text-slate-400">Draft</div>
                  <div className="text-2xl font-bold text-yellow-400">{reportAnalytics.draft}</div>
                </div>
                <div className="p-3 bg-slate-800/50 rounded-lg">
                  <div className="text-sm text-slate-400">Archived</div>
                  <div className="text-2xl font-bold text-slate-400">{reportAnalytics.archived}</div>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {!loading && !shipmentIntelligence && (
        <div className="glass-card p-8 text-center text-slate-400">
          <AlertCircle className="inline w-8 h-8 mr-2" />
          No market intelligence data available
        </div>
      )}
    </div>
  );
}
