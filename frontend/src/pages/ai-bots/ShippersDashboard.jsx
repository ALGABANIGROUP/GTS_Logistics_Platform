import React, { useEffect, useState } from "react";
import { FaBox, FaChartLine, FaMoneyBillWave, FaUsers } from "react-icons/fa";
import { getRecentShippers, getShipperStats } from "../../services/shippersApi";
import financeApi from "../../services/financeApi";
import freightBrokerApi from "../../services/freightBrokerApi";

const ShippersDashboard = () => {
    const [stats, setStats] = useState({
        totalShippers: 0,
        activeShippers: 0,
        brokerShipments: 0,
        pendingInvoices: 0,
    });
    const [recentShippers, setRecentShippers] = useState([]);
    const [recentShipments, setRecentShipments] = useState([]);
    const [pendingInvoices, setPendingInvoices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            setError(null);

            const [statsResponse, recentResponse, shipmentsResponse, invoicesResponse] = await Promise.all([
                getShipperStats(),
                getRecentShippers(5),
                freightBrokerApi.getRecentShipments(5),
                financeApi.getPendingInvoices(5),
            ]);

            setStats({
                totalShippers: statsResponse.total_shippers || 0,
                activeShippers: statsResponse.active_shippers || 0,
                brokerShipments: shipmentsResponse.total || shipmentsResponse.items?.length || 0,
                pendingInvoices: invoicesResponse.total || invoicesResponse.items?.length || 0,
            });

            setRecentShippers(recentResponse.items || []);
            setRecentShipments(shipmentsResponse.items || []);
            setPendingInvoices(invoicesResponse.items || []);
        } catch (err) {
            console.error("Error fetching dashboard data:", err);
            setError("Failed to load dashboard data. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboardData();
    }, []);

    if (loading) {
        return (
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
                <div className="loading">Loading dashboard...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", flexDirection: "column" }}>
                <div style={{ color: "#ef4444", fontSize: "16px", marginBottom: "16px" }}>{error}</div>
                <button
                    onClick={fetchDashboardData}
                    style={{
                        padding: "10px 20px",
                        background: "#3b82f6",
                        border: "none",
                        borderRadius: "8px",
                        color: "white",
                        cursor: "pointer",
                    }}
                >
                    Try Again
                </button>
            </div>
        );
    }

    return (
        <div style={{ padding: "24px" }}>
            <div style={{ marginBottom: "32px" }}>
                <h1 style={{ color: "white", fontSize: "28px", marginBottom: "8px" }}>Shippers Dashboard</h1>
                <p style={{ color: "#94a3b8" }}>Shipper records stay here, while shipments and billing are fed by Freight Broker and Finance Bot.</p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "20px", marginBottom: "32px" }}>
                <div style={{ background: "#1e293b", borderRadius: "16px", padding: "20px", border: "1px solid #334155" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                        <FaUsers style={{ fontSize: "28px", color: "#f59e0b" }} />
                        <span style={{ fontSize: "28px", fontWeight: "bold", color: "white" }}>{stats.totalShippers}</span>
                    </div>
                    <div style={{ color: "#94a3b8", fontSize: "14px" }}>Total Shippers</div>
                    <div style={{ fontSize: "12px", color: "#10b981", marginTop: "8px" }}>+{stats.activeShippers} active</div>
                </div>

                <div style={{ background: "#1e293b", borderRadius: "16px", padding: "20px", border: "1px solid #334155" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                        <FaBox style={{ fontSize: "28px", color: "#3b82f6" }} />
                        <span style={{ fontSize: "28px", fontWeight: "bold", color: "white" }}>{stats.brokerShipments}</span>
                    </div>
                    <div style={{ color: "#94a3b8", fontSize: "14px" }}>Freight Broker Shipments</div>
                    <div style={{ fontSize: "12px", color: "#60a5fa", marginTop: "8px" }}>Live operations feed</div>
                </div>

                <div style={{ background: "#1e293b", borderRadius: "16px", padding: "20px", border: "1px solid #334155" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                        <FaMoneyBillWave style={{ fontSize: "28px", color: "#10b981" }} />
                        <span style={{ fontSize: "28px", fontWeight: "bold", color: "white" }}>{stats.pendingInvoices}</span>
                    </div>
                    <div style={{ color: "#94a3b8", fontSize: "14px" }}>Pending Finance Invoices</div>
                    <div style={{ fontSize: "12px", color: "#10b981", marginTop: "8px" }}>Managed by Finance Bot</div>
                </div>

                <div style={{ background: "#1e293b", borderRadius: "16px", padding: "20px", border: "1px solid #334155" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                        <FaChartLine style={{ fontSize: "28px", color: "#f97316" }} />
                        <span style={{ fontSize: "28px", fontWeight: "bold", color: "white" }}>{recentShippers.length}</span>
                    </div>
                    <div style={{ color: "#94a3b8", fontSize: "14px" }}>Recent Shipper Records</div>
                    <div style={{ fontSize: "12px", color: "#f59e0b", marginTop: "8px" }}>Latest workspace snapshot</div>
                </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
                <div style={{ background: "#1e293b", borderRadius: "16px", border: "1px solid #334155", overflow: "hidden" }}>
                    <div style={{ padding: "20px", borderBottom: "1px solid #334155" }}>
                        <h3 style={{ color: "white", margin: 0 }}>Recent Shippers</h3>
                    </div>
                    <div style={{ overflowX: "auto" }}>
                        <table style={{ width: "100%", borderCollapse: "collapse" }}>
                            <thead>
                                <tr style={{ borderBottom: "1px solid #334155", color: "#94a3b8" }}>
                                    <th style={{ padding: "16px", textAlign: "right" }}>Shipper</th>
                                    <th style={{ padding: "16px", textAlign: "right" }}>Industry</th>
                                    <th style={{ padding: "16px", textAlign: "right" }}>Contact</th>
                                    <th style={{ padding: "16px", textAlign: "right" }}>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recentShippers.map((shipper) => (
                                    <tr key={shipper.id} style={{ borderBottom: "1px solid #334155" }}>
                                        <td style={{ padding: "16px", color: "white" }}>{shipper.name}</td>
                                        <td style={{ padding: "16px", color: "#94a3b8" }}>{shipper.industry_type || "N/A"}</td>
                                        <td style={{ padding: "16px", color: "#cbd5e1" }}>{shipper.contact_person || shipper.email || "N/A"}</td>
                                        <td style={{ padding: "16px", color: shipper.is_active ? "#10b981" : "#ef4444" }}>{shipper.is_active ? "Active" : "Inactive"}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div style={{ background: "#1e293b", borderRadius: "16px", border: "1px solid #334155", overflow: "hidden" }}>
                    <div style={{ padding: "20px", borderBottom: "1px solid #334155" }}>
                        <h3 style={{ color: "white", margin: 0 }}>Operations and Finance Snapshot</h3>
                    </div>
                    <div style={{ padding: "18px", display: "grid", gap: "16px" }}>
                        <div>
                            <div style={{ color: "#60a5fa", fontWeight: 600, marginBottom: "10px" }}>Freight Broker Shipments</div>
                            {recentShipments.length === 0 ? (
                                <div style={{ color: "#94a3b8" }}>No recent shipments found.</div>
                            ) : (
                                recentShipments.map((shipment) => (
                                    <div key={shipment.id || shipment.shipment_number} style={{ padding: "10px 0", borderBottom: "1px solid #334155", color: "#cbd5e1" }}>
                                        <div style={{ color: "white" }}>{shipment.shipment_number || `Shipment #${shipment.id}`}</div>
                                        <div style={{ fontSize: "13px", color: "#94a3b8" }}>
                                            {shipment.origin_city || "N/A"} to {shipment.destination_city || "N/A"} · {shipment.status || "unknown"}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>

                        <div>
                            <div style={{ color: "#10b981", fontWeight: 600, marginBottom: "10px" }}>Finance Bot Invoices</div>
                            {pendingInvoices.length === 0 ? (
                                <div style={{ color: "#94a3b8" }}>No pending invoices found.</div>
                            ) : (
                                pendingInvoices.map((invoice) => (
                                    <div key={invoice.id} style={{ padding: "10px 0", borderBottom: "1px solid #334155", color: "#cbd5e1" }}>
                                        <div style={{ color: "white" }}>{invoice.number}</div>
                                        <div style={{ fontSize: "13px", color: "#94a3b8" }}>
                                            ${Number(invoice.amount_usd || 0).toLocaleString()} · {invoice.status}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <style>{`
                .loading {
                    color: #94a3b8;
                    font-size: 16px;
                }
                .loading::after {
                    content: '';
                    display: inline-block;
                    width: 20px;
                    height: 20px;
                    border: 2px solid #f59e0b;
                    border-top-color: transparent;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-right: 8px;
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
};

export default ShippersDashboard;
