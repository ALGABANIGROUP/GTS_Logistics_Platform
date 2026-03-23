import React, { useEffect, useMemo, useState } from "react";
import { FaCheckCircle, FaDollarSign, FaExclamationTriangle, FaExternalLinkAlt, FaFileInvoiceDollar } from "react-icons/fa";
import financeApi from "../../services/financeApi";

const cardStyle = {
    background: "rgba(15, 23, 42, 0.72)",
    border: "1px solid rgba(148, 163, 184, 0.18)",
    borderRadius: "18px",
    backdropFilter: "blur(16px)",
};

const ShippersInvoices = () => {
    const [invoices, setInvoices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadInvoices = async () => {
        try {
            setLoading(true);
            setError("");
            const response = await financeApi.getInvoices();
            setInvoices(response.items || []);
        } catch (err) {
            console.error("Failed to load invoices:", err);
            setError("Failed to load Finance Bot invoices.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadInvoices();
    }, []);

    const summary = useMemo(() => {
        const pending = invoices.filter((invoice) => ["pending", "sent", "overdue"].includes(String(invoice.status || "").toLowerCase()));
        const paid = invoices.filter((invoice) => String(invoice.status || "").toLowerCase() === "paid");
        const overdue = invoices.filter((invoice) => String(invoice.status || "").toLowerCase() === "overdue");
        return {
            total: invoices.length,
            pending: pending.length,
            paid: paid.length,
            overdue: overdue.length,
            totalAmount: invoices.reduce((sum, invoice) => sum + Number(invoice.amount_usd || 0), 0),
        };
    }, [invoices]);

    const handleStatusUpdate = async (invoiceId, nextStatus) => {
        try {
            await financeApi.updateInvoiceStatus(invoiceId, nextStatus);
            await loadInvoices();
        } catch (err) {
            console.error("Failed to update invoice status:", err);
            setError("Failed to update invoice status through Finance Bot.");
        }
    };

    return (
        <div style={{ padding: "24px", color: "white" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
                <div>
                    <h1 style={{ fontSize: "28px", margin: 0 }}>Shipper Invoices</h1>
                    <p style={{ color: "#94a3b8", marginTop: "8px" }}>
                        Billing and payment actions are managed by the Finance Bot.
                    </p>
                </div>
                <a
                    href="/ai-bots/finance_bot"
                    style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "8px",
                        padding: "12px 16px",
                        borderRadius: "10px",
                        background: "#16a34a",
                        color: "white",
                        textDecoration: "none",
                        fontWeight: 600,
                    }}
                >
                    Open Finance Bot
                    <FaExternalLinkAlt size={12} />
                </a>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: "16px", marginBottom: "24px" }}>
                <div style={{ ...cardStyle, padding: "18px" }}>
                    <div style={{ color: "#94a3b8", fontSize: "12px" }}>Total Invoices</div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "10px" }}>
                        <span style={{ fontSize: "28px", fontWeight: 700 }}>{summary.total}</span>
                        <FaFileInvoiceDollar style={{ color: "#60a5fa", fontSize: "24px" }} />
                    </div>
                </div>
                <div style={{ ...cardStyle, padding: "18px" }}>
                    <div style={{ color: "#94a3b8", fontSize: "12px" }}>Pending or Sent</div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "10px" }}>
                        <span style={{ fontSize: "28px", fontWeight: 700 }}>{summary.pending}</span>
                        <FaDollarSign style={{ color: "#f59e0b", fontSize: "24px" }} />
                    </div>
                </div>
                <div style={{ ...cardStyle, padding: "18px" }}>
                    <div style={{ color: "#94a3b8", fontSize: "12px" }}>Paid</div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "10px" }}>
                        <span style={{ fontSize: "28px", fontWeight: 700 }}>{summary.paid}</span>
                        <FaCheckCircle style={{ color: "#22c55e", fontSize: "24px" }} />
                    </div>
                </div>
                <div style={{ ...cardStyle, padding: "18px" }}>
                    <div style={{ color: "#94a3b8", fontSize: "12px" }}>Overdue</div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "10px" }}>
                        <span style={{ fontSize: "28px", fontWeight: 700 }}>{summary.overdue}</span>
                        <FaExclamationTriangle style={{ color: "#f87171", fontSize: "24px" }} />
                    </div>
                </div>
            </div>

            <div style={{ ...cardStyle, padding: "18px", marginBottom: "18px", color: "#cbd5e1" }}>
                Total invoice value in the current Finance Bot feed: <strong style={{ color: "white" }}>${summary.totalAmount.toLocaleString()}</strong>
            </div>

            {error ? (
                <div style={{ marginBottom: "18px", color: "#fecaca", background: "rgba(127, 29, 29, 0.35)", border: "1px solid rgba(248, 113, 113, 0.3)", padding: "12px 14px", borderRadius: "12px" }}>
                    {error}
                </div>
            ) : null}

            <div style={{ ...cardStyle, overflow: "hidden" }}>
                <div style={{ padding: "18px 20px", borderBottom: "1px solid rgba(51, 65, 85, 1)" }}>
                    <div style={{ fontSize: "18px", fontWeight: 700 }}>Finance Bot Invoice Feed</div>
                </div>

                {loading ? (
                    <div style={{ padding: "32px 20px", color: "#cbd5e1" }}>Loading invoices...</div>
                ) : invoices.length === 0 ? (
                    <div style={{ padding: "32px 20px", color: "#94a3b8" }}>No invoices are available.</div>
                ) : (
                    <div style={{ overflowX: "auto" }}>
                        <table style={{ width: "100%", borderCollapse: "collapse" }}>
                            <thead>
                                <tr style={{ borderBottom: "1px solid #334155", color: "#94a3b8", background: "#0f172a" }}>
                                    <th style={{ padding: "14px 16px", textAlign: "left" }}>Invoice</th>
                                    <th style={{ padding: "14px 16px", textAlign: "left" }}>Date</th>
                                    <th style={{ padding: "14px 16px", textAlign: "left" }}>Shipment ID</th>
                                    <th style={{ padding: "14px 16px", textAlign: "left" }}>Amount</th>
                                    <th style={{ padding: "14px 16px", textAlign: "left" }}>Status</th>
                                    <th style={{ padding: "14px 16px", textAlign: "left" }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {invoices.map((invoice) => (
                                    <tr key={invoice.id} style={{ borderBottom: "1px solid #334155" }}>
                                        <td style={{ padding: "14px 16px", color: "white", fontWeight: 600 }}>{invoice.number}</td>
                                        <td style={{ padding: "14px 16px", color: "#cbd5e1" }}>{invoice.date}</td>
                                        <td style={{ padding: "14px 16px", color: "#94a3b8" }}>{invoice.shipment_id || "N/A"}</td>
                                        <td style={{ padding: "14px 16px", color: "#e2e8f0" }}>${Number(invoice.amount_usd || 0).toLocaleString()}</td>
                                        <td style={{ padding: "14px 16px" }}>
                                            <span
                                                style={{
                                                    padding: "4px 10px",
                                                    borderRadius: "999px",
                                                    background:
                                                        String(invoice.status).toLowerCase() === "paid"
                                                            ? "rgba(16, 185, 129, 0.18)"
                                                            : String(invoice.status).toLowerCase() === "overdue"
                                                                ? "rgba(239, 68, 68, 0.18)"
                                                                : "rgba(245, 158, 11, 0.18)",
                                                    color:
                                                        String(invoice.status).toLowerCase() === "paid"
                                                            ? "#34d399"
                                                            : String(invoice.status).toLowerCase() === "overdue"
                                                                ? "#f87171"
                                                                : "#fbbf24",
                                                    fontSize: "12px",
                                                    fontWeight: 600,
                                                }}
                                            >
                                                {invoice.status}
                                            </span>
                                        </td>
                                        <td style={{ padding: "14px 16px" }}>
                                            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                                                {String(invoice.status).toLowerCase() !== "paid" ? (
                                                    <button
                                                        onClick={() => handleStatusUpdate(invoice.id, "paid")}
                                                        style={{ padding: "8px 10px", borderRadius: "8px", border: "none", background: "#16a34a", color: "white", cursor: "pointer" }}
                                                    >
                                                        Mark Paid
                                                    </button>
                                                ) : null}
                                                {String(invoice.status).toLowerCase() !== "overdue" ? (
                                                    <button
                                                        onClick={() => handleStatusUpdate(invoice.id, "overdue")}
                                                        style={{ padding: "8px 10px", borderRadius: "8px", border: "none", background: "#b91c1c", color: "white", cursor: "pointer" }}
                                                    >
                                                        Mark Overdue
                                                    </button>
                                                ) : null}
                                            </div>
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

export default ShippersInvoices;
