import React, { useEffect, useMemo, useState } from "react";
import { FaExternalLinkAlt, FaFilter, FaSearch, FaSyncAlt } from "react-icons/fa";
import freightBrokerApi from "../../services/freightBrokerApi";
import { listShippers } from "../../services/shippersApi";

const filtersCard = {
    background: "rgba(15, 23, 42, 0.72)",
    border: "1px solid rgba(148, 163, 184, 0.18)",
    borderRadius: "18px",
    backdropFilter: "blur(16px)",
};

const inputStyle = {
    width: "100%",
    padding: "12px 14px",
    background: "#0f172a",
    border: "1px solid #334155",
    borderRadius: "10px",
    color: "white",
    fontSize: "14px",
};

const normalizeShipmentText = (shipment) =>
    [
        shipment.shipment_number,
        shipment.origin_city,
        shipment.destination_city,
        shipment.customer_name,
        shipment.shipper_name,
        shipment.status,
    ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

const shipmentMatchesShipper = (shipment, shipper) => {
    if (!shipper) return true;

    const shipperId = String(shipper.id);
    const candidateIds = [shipment.shipper_id, shipment.customer_id, shipment.user_id]
        .filter((value) => value !== undefined && value !== null)
        .map(String);

    if (candidateIds.includes(shipperId)) return true;

    const shipperName = String(shipper.name || "").toLowerCase();
    const shipmentNames = [shipment.shipper_name, shipment.customer_name, shipment.client_name]
        .filter(Boolean)
        .map((value) => String(value).toLowerCase());

    return shipperName ? shipmentNames.includes(shipperName) : false;
};

const ShippersShipments = () => {
    const [shipments, setShipments] = useState([]);
    const [shippers, setShippers] = useState([]);
    const [selectedShipperId, setSelectedShipperId] = useState("");
    const [statusFilter, setStatusFilter] = useState("");
    const [searchTerm, setSearchTerm] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const [shipmentResponse, shipperResponse] = await Promise.all([
                freightBrokerApi.getShipments({ limit: 100 }),
                listShippers({ per_page: 100 }),
            ]);
            setShipments(shipmentResponse.items || []);
            setShippers(shipperResponse.items || []);
        } catch (err) {
            console.error("Failed to load shipper shipments page:", err);
            setError("Failed to load shipment data from Freight Broker.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const selectedShipper = useMemo(
        () => shippers.find((item) => String(item.id) === String(selectedShipperId)) || null,
        [shippers, selectedShipperId]
    );

    const filteredShipments = useMemo(() => {
        return shipments.filter((shipment) => {
            const matchesSearch = !searchTerm || normalizeShipmentText(shipment).includes(searchTerm.toLowerCase());
            const matchesStatus = !statusFilter || String(shipment.status || "").toLowerCase() === statusFilter.toLowerCase();
            const matchesShipper = shipmentMatchesShipper(shipment, selectedShipper);
            return matchesSearch && matchesStatus && matchesShipper;
        });
    }, [shipments, searchTerm, statusFilter, selectedShipper]);

    return (
        <div style={{ padding: "24px", color: "white" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
                <div>
                    <h1 style={{ fontSize: "28px", margin: 0 }}>Shipper Shipments</h1>
                    <p style={{ color: "#94a3b8", marginTop: "8px" }}>
                        Operational shipment data is managed by the AI Freight Broker.
                    </p>
                </div>
                <a
                    href="/ai-bots/freight_broker/shipments"
                    style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "8px",
                        padding: "12px 16px",
                        borderRadius: "10px",
                        background: "#2563eb",
                        color: "white",
                        textDecoration: "none",
                        fontWeight: 600,
                    }}
                >
                    Open Freight Broker
                    <FaExternalLinkAlt size={12} />
                </a>
            </div>

            <div style={{ ...filtersCard, padding: "20px", marginBottom: "24px" }}>
                <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.8fr 1fr auto", gap: "16px", alignItems: "end" }}>
                    <div>
                        <div style={{ color: "#cbd5e1", marginBottom: "8px", fontSize: "13px" }}>Shipper</div>
                        <select value={selectedShipperId} onChange={(e) => setSelectedShipperId(e.target.value)} style={inputStyle}>
                            <option value="">All shippers</option>
                            {shippers.map((shipper) => (
                                <option key={shipper.id} value={shipper.id}>
                                    {shipper.name}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <div style={{ color: "#cbd5e1", marginBottom: "8px", fontSize: "13px" }}>Status</div>
                        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={inputStyle}>
                            <option value="">All statuses</option>
                            <option value="pending">Pending</option>
                            <option value="assigned">Assigned</option>
                            <option value="in_transit">In Transit</option>
                            <option value="delivered">Delivered</option>
                            <option value="cancelled">Cancelled</option>
                        </select>
                    </div>
                    <div>
                        <div style={{ color: "#cbd5e1", marginBottom: "8px", fontSize: "13px" }}>Search</div>
                        <div style={{ position: "relative" }}>
                            <FaSearch style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "#64748b" }} />
                            <input
                                type="text"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                placeholder="Shipment number, city, customer..."
                                style={{ ...inputStyle, paddingLeft: "38px" }}
                            />
                        </div>
                    </div>
                    <button
                        onClick={loadData}
                        style={{
                            padding: "12px 16px",
                            background: "#334155",
                            border: "none",
                            borderRadius: "10px",
                            color: "white",
                            cursor: "pointer",
                        }}
                    >
                        <FaSyncAlt />
                    </button>
                </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: "16px", marginBottom: "24px" }}>
                <div style={{ ...filtersCard, padding: "18px" }}>
                    <div style={{ color: "#94a3b8", fontSize: "12px" }}>Filtered Shipments</div>
                    <div style={{ fontSize: "28px", fontWeight: 700, marginTop: "8px" }}>{filteredShipments.length}</div>
                </div>
                <div style={{ ...filtersCard, padding: "18px" }}>
                    <div style={{ color: "#94a3b8", fontSize: "12px" }}>In Transit</div>
                    <div style={{ fontSize: "28px", fontWeight: 700, marginTop: "8px" }}>
                        {filteredShipments.filter((shipment) => String(shipment.status).toLowerCase() === "in_transit").length}
                    </div>
                </div>
                <div style={{ ...filtersCard, padding: "18px" }}>
                    <div style={{ color: "#94a3b8", fontSize: "12px" }}>Delivered</div>
                    <div style={{ fontSize: "28px", fontWeight: 700, marginTop: "8px" }}>
                        {filteredShipments.filter((shipment) => String(shipment.status).toLowerCase() === "delivered").length}
                    </div>
                </div>
            </div>

            {error ? (
                <div style={{ marginBottom: "18px", color: "#fecaca", background: "rgba(127, 29, 29, 0.35)", border: "1px solid rgba(248, 113, 113, 0.3)", padding: "12px 14px", borderRadius: "12px" }}>
                    {error}
                </div>
            ) : null}

            <div style={{ ...filtersCard, overflow: "hidden" }}>
                <div style={{ padding: "18px 20px", borderBottom: "1px solid rgba(51, 65, 85, 1)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                        <div style={{ fontSize: "18px", fontWeight: 700 }}>Shipment Feed</div>
                        <div style={{ color: "#94a3b8", fontSize: "13px", marginTop: "4px" }}>
                            {selectedShipper ? `Filtered for ${selectedShipper.name}` : "Showing all available Freight Broker shipments"}
                        </div>
                    </div>
                    <FaFilter style={{ color: "#94a3b8" }} />
                </div>

                {loading ? (
                    <div style={{ padding: "32px 20px", color: "#cbd5e1" }}>Loading shipments...</div>
                ) : filteredShipments.length === 0 ? (
                    <div style={{ padding: "32px 20px", color: "#94a3b8" }}>No shipments match the current filters.</div>
                ) : (
                    <div style={{ overflowX: "auto" }}>
                        <table style={{ width: "100%", borderCollapse: "collapse" }}>
                            <thead>
                                <tr style={{ borderBottom: "1px solid #334155", color: "#94a3b8", background: "#0f172a" }}>
                                    <th style={{ padding: "14px 16px", textAlign: "left" }}>Shipment</th>
                                    <th style={{ padding: "14px 16px", textAlign: "left" }}>Route</th>
                                    <th style={{ padding: "14px 16px", textAlign: "left" }}>Date</th>
                                    <th style={{ padding: "14px 16px", textAlign: "left" }}>Status</th>
                                    <th style={{ padding: "14px 16px", textAlign: "left" }}>Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredShipments.map((shipment) => (
                                    <tr key={shipment.id || shipment.shipment_number} style={{ borderBottom: "1px solid #334155" }}>
                                        <td style={{ padding: "14px 16px" }}>
                                            <div style={{ color: "white", fontWeight: 600 }}>
                                                {shipment.shipment_number || `Shipment #${shipment.id}`}
                                            </div>
                                            <div style={{ color: "#94a3b8", fontSize: "12px", marginTop: "4px" }}>
                                                {shipment.shipper_name || shipment.customer_name || "Freight Broker feed"}
                                            </div>
                                        </td>
                                        <td style={{ padding: "14px 16px", color: "#cbd5e1" }}>
                                            {shipment.origin_city || "N/A"} to {shipment.destination_city || "N/A"}
                                        </td>
                                        <td style={{ padding: "14px 16px", color: "#94a3b8" }}>
                                            {shipment.shipment_date || shipment.created_at || "N/A"}
                                        </td>
                                        <td style={{ padding: "14px 16px" }}>
                                            <span
                                                style={{
                                                    padding: "4px 10px",
                                                    borderRadius: "999px",
                                                    background:
                                                        String(shipment.status).toLowerCase() === "delivered"
                                                            ? "rgba(16, 185, 129, 0.18)"
                                                            : String(shipment.status).toLowerCase() === "in_transit"
                                                                ? "rgba(59, 130, 246, 0.18)"
                                                                : "rgba(245, 158, 11, 0.18)",
                                                    color:
                                                        String(shipment.status).toLowerCase() === "delivered"
                                                            ? "#34d399"
                                                            : String(shipment.status).toLowerCase() === "in_transit"
                                                                ? "#60a5fa"
                                                                : "#fbbf24",
                                                    fontSize: "12px",
                                                    fontWeight: 600,
                                                }}
                                            >
                                                {shipment.status || "unknown"}
                                            </span>
                                        </td>
                                        <td style={{ padding: "14px 16px", color: "#e2e8f0" }}>
                                            {shipment.amount || shipment.total_amount || shipment.price || "N/A"}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ShippersShipments;
