import React, { useEffect, useMemo, useState } from "react";
import { FINANCE_ZERO_MODE } from "../../../../config/financeConstants";


const safeDivide = (numerator, denominator, fallback = 0) => {
    if (!denominator || Number.isNaN(denominator)) {
        return fallback;
    }
    const result = numerator / denominator;
    return Number.isFinite(result) ? result : fallback;
};

const safePercentage = (numerator, denominator, fallback = 0) => {
    const pct = safeDivide(numerator, denominator, fallback) * 100;
    return Number.isFinite(pct) ? pct : fallback;
};

const LaneProfitability = ({ zeroMode = FINANCE_ZERO_MODE }) => {
    const [selectedPeriod, setSelectedPeriod] = useState("month");
    const [sortBy, setSortBy] = useState("margin_desc");
    const [filterStatus, setFilterStatus] = useState("all");
    const [lanes, setLanes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        let isMounted = true;
        const load = async () => {
            setLoading(true);
            setError(null);
            try {
                if (zeroMode) {
                    if (isMounted) {
                        setLanes([]);
                    }
                    return;
                }

                // Live data only: keep empty until backend integration
                if (isMounted) {
                    setLanes([]);
                }
            } catch (err) {
                console.error("Lane profitability load failed", err);
                if (isMounted) {
                    setError("Failed to load lane profitability data.");
                    setLanes([]);
                }
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        };

        load();
        return () => {
            isMounted = false;
        };
    }, [selectedPeriod, zeroMode]);

    const sortedLanes = useMemo(() => {
        const filtered = lanes.filter((lane) => {
            const profit = (lane.revenue || 0) - (lane.directCosts || 0);
            if (filterStatus === "profitable") {
                return profit > 0;
            }
            if (filterStatus === "unprofitable") {
                return profit <= 0;
            }
            return true;
        });

        const sorted = [...filtered];
        switch (sortBy) {
            case "margin_desc":
                return sorted.sort((a, b) => (b.margin || 0) - (a.margin || 0));
            case "margin_percent_desc":
                return sorted.sort((a, b) => (b.marginPercent || 0) - (a.marginPercent || 0));
            case "revenue_desc":
                return sorted.sort((a, b) => (b.revenue || 0) - (a.revenue || 0));
            case "shipments_desc":
                return sorted.sort((a, b) => (b.shipments || 0) - (a.shipments || 0));
            default:
                return sorted;
        }
    }, [lanes, sortBy, filterStatus]);

    const totals = useMemo(() => {
        const totalRevenue = lanes.reduce((sum, lane) => sum + (lane.revenue || 0), 0);
        const totalCosts = lanes.reduce((sum, lane) => sum + (lane.directCosts || 0), 0);
        const totalMargin = lanes.reduce((sum, lane) => sum + ((lane.revenue || 0) - (lane.directCosts || 0)), 0);
        const totalShipments = lanes.reduce((sum, lane) => sum + (lane.shipments || 0), 0);
        const avgMarginPercent = lanes.length === 0
            ? 0
            : safeDivide(
                lanes.reduce((sum, lane) => sum + (lane.marginPercent || 0), 0),
                lanes.length,
                0,
            );

        return {
            totalRevenue,
            totalCosts,
            totalMargin,
            totalShipments,
            avgMarginPercent,
            profitableLanes: lanes.filter((lane) => (lane.revenue || 0) - (lane.directCosts || 0) > 0).length,
        };
    }, [lanes]);

    const getTrendIndicator = (trend) => {
        if (trend > 0) {
            return <span style={{ color: "#198754" }}> {trend.toFixed(1)}%</span>;
        }
        if (trend < 0) {
            return <span style={{ color: "#dc3545" }}> {Math.abs(trend).toFixed(1)}%</span>;
        }
        return <span style={{ color: "#6c757d" }}> 0%</span>;
    };

    const getMarginColor = (marginPercent) => {
        if (marginPercent >= 25) return "#198754";
        if (marginPercent >= 20) return "#ffc107";
        return "#dc3545";
    };

    const isEmpty = sortedLanes.length === 0;

    if (loading) {
        return (
            <div className="fin-lane-profitability glass-page">
                <div className="glass-panel fin-empty" style={{ padding: "20px", color: "#9fb2d3" }}>
                    Loading lane profitability...
                </div>
            </div>
        );
    }

    return (
        <div className="fin-lane-profitability glass-page">
            {zeroMode && (
                <div className="glass-panel" style={{ marginBottom: "12px", padding: "12px", display: "flex", gap: "8px", alignItems: "center" }}>
                    <span role="img" aria-label="info"></span>
                    <span>Connect your TMS to see lane profitability data.</span>
                </div>
            )}

            {error && (
                <div className="glass-panel" style={{ marginBottom: "12px", padding: "12px", border: "1px solid #dc3545", color: "#dc3545" }}>
                    {error}
                </div>
            )}

            <div className="fin-filters glass-panel" style={{ marginBottom: "16px", display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
                <label style={{ fontWeight: "600" }}>Period:</label>
                <select
                    value={selectedPeriod}
                    onChange={(e) => setSelectedPeriod(e.target.value)}
                    className="glass-select"
                    style={{ minWidth: "160px" }}
                    disabled={zeroMode || isEmpty}
                >
                    <option value="week">This Week</option>
                    <option value="month">This Month</option>
                    <option value="quarter">This Quarter</option>
                    <option value="year">This Year</option>
                </select>

                <label style={{ fontWeight: "600", marginLeft: "24px" }}>Filter:</label>
                <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="glass-select"
                    style={{ minWidth: "180px" }}
                    disabled={zeroMode || isEmpty}
                >
                    <option value="all">All Lanes</option>
                    <option value="profitable">Profitable</option>
                    <option value="unprofitable">Unprofitable</option>
                </select>

                <label style={{ fontWeight: "600", marginLeft: "24px" }}>Sort By:</label>
                <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="glass-select"
                    style={{ minWidth: "200px" }}
                    disabled={zeroMode || isEmpty}
                >
                    <option value="margin_desc">Highest Margin ($)</option>
                    <option value="margin_percent_desc">Highest Margin (%)</option>
                    <option value="revenue_desc">Highest Revenue</option>
                    <option value="shipments_desc">Most Shipments</option>
                </select>

                <div style={{ marginLeft: "auto" }}>
                    <button className="fin-btn" disabled={zeroMode || isEmpty}>Export CSV</button>
                </div>
            </div>

            {isEmpty ? (
                <div className="glass-panel fin-empty" style={{ padding: "20px", color: "#9fb2d3", textAlign: "center" }}>
                    <div style={{ fontSize: "20px", marginBottom: "6px" }}> No lane profitability data</div>
                    <div>{zeroMode ? "Connect to your TMS to view live profitability." : "Add shipments to see profitability by lane."}</div>
                </div>
            ) : (
                <>
                    <div className="fin-grid fin-grid-compact" style={{ marginBottom: "16px" }}>
                        <div className="fin-card glass-panel">
                            <div className="fin-label">Total Revenue</div>
                            <div className="fin-metric">${totals.totalRevenue.toLocaleString()}</div>
                            <div className="fin-subtext">Across {totals.totalShipments} shipments</div>
                        </div>
                        <div className="fin-card glass-panel">
                            <div className="fin-label">Total Profit</div>
                            <div className="fin-metric" style={{ color: totals.totalMargin >= 0 ? "#198754" : "#dc3545" }}>${totals.totalMargin.toLocaleString()}</div>
                            <div className="fin-subtext">Net after direct costs</div>
                        </div>
                        <div className="fin-card glass-panel">
                            <div className="fin-label">Direct Costs</div>
                            <div className="fin-metric" style={{ color: "#dc3545" }}>${totals.totalCosts.toLocaleString()}</div>
                            <div className="fin-subtext">Fuel, linehaul, accessorials</div>
                        </div>
                        <div className="fin-card glass-panel">
                            <div className="fin-label">Avg Margin %</div>
                            <div className="fin-metric">{totals.avgMarginPercent.toFixed(1)}%</div>
                            <div className="fin-subtext">Weighted across all lanes</div>
                        </div>
                        <div className="fin-card glass-panel">
                            <div className="fin-label">Profitable Lanes</div>
                            <div className="fin-metric">{totals.profitableLanes} / {lanes.length}</div>
                            <div className="fin-subtext">{safePercentage(totals.profitableLanes, lanes.length, 0).toFixed(1)}% success</div>
                        </div>
                        <div className="fin-card glass-panel">
                            <div className="fin-label">Avg Profit per Lane</div>
                            <div className="fin-metric">${safeDivide(totals.totalMargin, lanes.length || 1, 0).toLocaleString()}</div>
                            <div className="fin-subtext">Aggregate view</div>
                        </div>
                    </div>

                    <div className="fin-table-container glass-panel">
                        <table className="fin-table">
                            <thead>
                                <tr>
                                    <th>Lane (Route)</th>
                                    <th>Distance</th>
                                    <th>Shipments</th>
                                    <th>Revenue</th>
                                    <th>Direct Costs</th>
                                    <th>Margin ($)</th>
                                    <th>Margin (%)</th>
                                    <th>Trend</th>
                                    <th>Top Customer</th>
                                    <th>Avg Delivery</th>
                                </tr>
                            </thead>
                            <tbody>
                                {sortedLanes.map((lane) => {
                                    const margin = (lane.revenue || 0) - (lane.directCosts || 0);
                                    const marginPct = safePercentage(margin, lane.revenue || 0, 0);
                                    return (
                                        <tr key={lane.id}>
                                            <td>
                                                <div style={{ fontWeight: "600" }}>{lane.origin}</div>
                                                <div style={{ fontSize: "12px", color: "#6c757d" }}> {lane.destination}</div>
                                            </td>
                                            <td>{(lane.distance || 0).toLocaleString()} km</td>
                                            <td style={{ fontWeight: "600" }}>{lane.shipments || 0}</td>
                                            <td style={{ fontWeight: "600" }}>${(lane.revenue || 0).toLocaleString()}</td>
                                            <td style={{ color: "#dc3545" }}>${(lane.directCosts || 0).toLocaleString()}</td>
                                            <td style={{ fontWeight: "600", color: margin >= 0 ? "#198754" : "#dc3545" }}>
                                                ${margin.toLocaleString()}
                                            </td>
                                            <td>
                                                <span
                                                    style={{
                                                        padding: "4px 10px",
                                                        borderRadius: "12px",
                                                        backgroundColor: `${getMarginColor(marginPct)}20`,
                                                        color: getMarginColor(marginPct),
                                                        fontWeight: 600,
                                                        fontSize: "13px",
                                                    }}
                                                >
                                                    {marginPct.toFixed(1)}%
                                                </span>
                                            </td>
                                            <td style={{ fontSize: "13px", fontWeight: "600" }}>{getTrendIndicator(lane.trend || 0)}</td>
                                            <td>
                                                <div style={{ fontSize: "13px" }}>{lane.topCustomer}</div>
                                                <div style={{ fontSize: "11px", color: "#6c757d" }}>
                                                    ({lane.topCustomerShipments || 0} shipments)
                                                </div>
                                            </td>
                                            <td>{(lane.avgDaysToDeliver || 0).toFixed(1)} days</td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>

                    <div style={{ marginTop: "24px" }}>
                        <h3 style={{ marginBottom: "12px" }}>Lane Insights & Recommendations</h3>
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "16px" }}>
                            <div className="fin-card glass-panel" style={{ borderLeft: "4px solid #198754" }}>
                                <h4 style={{ color: "#198754", marginBottom: "6px" }}> Top Performer</h4>
                                <div style={{ fontWeight: "600", marginBottom: "4px" }}>Toronto, ON  Montreal, QC</div>
                                <div style={{ fontSize: "14px", color: "#6c757d", marginBottom: "8px" }}>
                                    30% margin  42 shipments  +8.1% trend
                                </div>
                                <div className="glass-subpanel" style={{ fontSize: "13px" }}>
                                    <strong>Action:</strong> Prioritize this lane; expand commitments with existing shippers.
                                </div>
                            </div>

                            <div className="fin-card glass-panel" style={{ borderLeft: "4px solid #dc3545" }}>
                                <h4 style={{ color: "#dc3545", marginBottom: "6px" }}> Needs Attention</h4>
                                <div style={{ fontWeight: "600", marginBottom: "4px" }}>Vancouver, BC  Toronto, ON</div>
                                <div style={{ fontSize: "14px", color: "#6c757d", marginBottom: "8px" }}>
                                    17.5% margin  19 shipments  -5.2% trend
                                </div>
                                <div className="glass-subpanel" style={{ fontSize: "13px" }}>
                                    <strong>Action:</strong> Re-price lane and renegotiate carrier linehaul; watch accessorial leakage.
                                </div>
                            </div>

                            <div className="fin-card glass-panel" style={{ borderLeft: "4px solid #0dcaf0" }}>
                                <h4 style={{ color: "#0dcaf0", marginBottom: "6px" }}> Growth Opportunity</h4>
                                <div style={{ fontWeight: "600", marginBottom: "4px" }}>Montreal, QC  Calgary, AB</div>
                                <div style={{ fontSize: "14px", color: "#6c757d", marginBottom: "8px" }}>
                                    25% margin  18 shipments  +3.5% trend
                                </div>
                                <div className="glass-subpanel" style={{ fontSize: "13px" }}>
                                    <strong>Action:</strong> Promote with target accounts; lock capacity with top carriers.
                                </div>
                            </div>
                        </div>
                    </div>

                    <div style={{ marginTop: "24px" }}>
                        <h3 style={{ marginBottom: "12px" }}>Carrier Efficiency by Lane</h3>
                        <div className="fin-table-container glass-panel">
                            <table className="fin-table">
                                <thead>
                                    <tr>
                                        <th>Lane</th>
                                        <th>Carriers Used</th>
                                        <th>Best Performer</th>
                                        <th>Avg Cost/km</th>
                                        <th>On-Time %</th>
                                        <th>Recommendation</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Toronto  Vancouver</td>
                                        <td>3 carriers</td>
                                        <td>FastTrack Logistics</td>
                                        <td>$0.12</td>
                                        <td>96%</td>
                                        <td style={{ color: "#198754" }}>Keep FastTrack as primary</td>
                                    </tr>
                                    <tr>
                                        <td>Montreal  Calgary</td>
                                        <td>2 carriers</td>
                                        <td>Reliable Transport</td>
                                        <td>$0.11</td>
                                        <td>89%</td>
                                        <td style={{ color: "#ffc107" }}>Add backup for surge weeks</td>
                                    </tr>
                                    <tr>
                                        <td>Vancouver  Toronto</td>
                                        <td>4 carriers</td>
                                        <td>Express Freight</td>
                                        <td>$0.15</td>
                                        <td>72%</td>
                                        <td style={{ color: "#dc3545" }}>Review carrier mix and OTIF</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}

            <div className="fin-row fin-justify-end fin-gap-sm" style={{ marginTop: "16px" }}>
                <button className="fin-btn" disabled={zeroMode || isEmpty}>Export CSV</button>
                <button className="fin-btn primary" disabled={zeroMode || isEmpty}>Sync Lane Data</button>
            </div>
        </div>
    );
};

export default LaneProfitability;
