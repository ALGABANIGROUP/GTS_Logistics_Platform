import React, { useEffect, useMemo, useState } from "react";
import { FINANCE_ZERO_MODE } from "../../../../config/financeConstants";
import financeApi from "../../../../services/financeApi";

const initialForm = {
    invoice_date: new Date().toISOString().split("T")[0],
    amount_usd: "",
    customer_name: "",
    status: "pending",
};

const formatCurrency = (amount) =>
    new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 2,
    }).format(Number(amount || 0));

const InvoiceManager = ({ zeroMode = FINANCE_ZERO_MODE }) => {
    const [filterStatus, setFilterStatus] = useState("all");
    const [selectedInvoice, setSelectedInvoice] = useState(null);
    const [showCreate, setShowCreate] = useState(false);
    const [form, setForm] = useState(initialForm);
    const [submitting, setSubmitting] = useState(false);
    const [loading, setLoading] = useState(!zeroMode);
    const [error, setError] = useState("");
    const [invoices, setInvoices] = useState([]);

    const loadInvoices = async () => {
        if (zeroMode) return;
        setLoading(true);
        setError("");
        try {
            const response = await financeApi.getInvoices();
            setInvoices(response?.items || []);
        } catch (err) {
            setError(err?.response?.data?.detail || err?.message || "Failed to load invoices.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadInvoices();
    }, [zeroMode]);

    const filteredInvoices = useMemo(() => {
        return invoices.filter((inv) => {
            if (filterStatus !== "all" && String(inv.status || "").toLowerCase() !== filterStatus) return false;
            return true;
        });
    }, [invoices, filterStatus]);

    const stats = useMemo(() => {
        if (filteredInvoices.length === 0) {
            return { total: 0, paid: 0, overdue: 0, outstanding: 0 };
        }
        const total = filteredInvoices.reduce((sum, inv) => sum + Number(inv.amount_usd || 0), 0);
        const paid = filteredInvoices
            .filter((inv) => String(inv.status || "").toLowerCase() === "paid")
            .reduce((sum, inv) => sum + Number(inv.amount_usd || 0), 0);
        const overdue = filteredInvoices
            .filter((inv) => String(inv.status || "").toLowerCase() === "overdue")
            .reduce((sum, inv) => sum + Number(inv.amount_usd || 0), 0);
        return { total, paid, overdue, outstanding: total - paid };
    }, [filteredInvoices]);

    const handleCreateInvoice = async (event) => {
        event.preventDefault();
        setSubmitting(true);
        setError("");
        try {
            const result = await financeApi.createInvoice({
                invoice_date: form.invoice_date,
                amount_usd: Number(form.amount_usd),
                customer_name: form.customer_name,
                status: form.status,
            });
            if (result?.success) {
                setShowCreate(false);
                setForm(initialForm);
                await loadInvoices();
            }
        } catch (err) {
            setError(err?.response?.data?.detail || err?.message || "Failed to create invoice.");
        } finally {
            setSubmitting(false);
        }
    };

    const handlePayInvoice = async (invoice) => {
        const confirmed = window.confirm(`Record payment for ${invoice.number} (${formatCurrency(invoice.amount_usd)})?`);
        if (!confirmed) return;
        try {
            await financeApi.payInvoice(invoice.id, Number(invoice.amount_usd || 0), "sudapay");
            await loadInvoices();
        } catch (err) {
            setError(err?.response?.data?.detail || err?.message || "Failed to record invoice payment.");
        }
    };

    return (
        <div className="fin-invoice-list glass-page">
            <div className="fin-stats-row" style={{ marginBottom: "24px" }}>
                <div className="fin-stat-card glass-panel">
                    <div className="fin-stat-label">Total Invoiced</div>
                    <div className="fin-stat-value">{formatCurrency(stats.total)}</div>
                </div>
                <div className="fin-stat-card glass-panel">
                    <div className="fin-stat-label">Collected</div>
                    <div className="fin-stat-value fin-text-positive">{formatCurrency(stats.paid)}</div>
                </div>
                <div className="fin-stat-card glass-panel">
                    <div className="fin-stat-label">Outstanding</div>
                    <div className="fin-stat-value fin-text-warn">{formatCurrency(stats.outstanding)}</div>
                </div>
                <div className="fin-stat-card glass-panel">
                    <div className="fin-stat-label">Overdue</div>
                    <div className="fin-stat-value fin-text-danger">{formatCurrency(stats.overdue)}</div>
                </div>
            </div>

            <div className="fin-filters" style={{ marginBottom: "16px", display: "flex", gap: "12px", alignItems: "center" }}>
                <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="glass-select" disabled={zeroMode}>
                    <option value="all">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="sent">Sent</option>
                    <option value="draft">Draft</option>
                    <option value="overdue">Overdue</option>
                    <option value="paid">Paid</option>
                </select>

                <button onClick={loadInvoices} className="glass-btn-secondary" disabled={zeroMode || loading}>
                    Refresh
                </button>

                <button
                    onClick={() => setShowCreate(true)}
                    className="glass-btn-primary"
                    style={{ marginLeft: "auto" }}
                    disabled={zeroMode}
                >
                    {zeroMode ? "Connect to create" : "+ Create Invoice"}
                </button>
            </div>

            {error ? <div className="glass-panel" style={{ marginBottom: "16px", padding: "16px", color: "#fca5a5" }}>{String(error)}</div> : null}

            <div className="fin-table-container glass-panel">
                {loading ? (
                    <div style={{ padding: "16px", color: "#9fb2d3" }}>Loading invoices...</div>
                ) : filteredInvoices.length === 0 ? (
                    <div style={{ padding: "16px", color: "#9fb2d3" }}>No invoices available.</div>
                ) : (
                    <table className="fin-table">
                        <thead>
                            <tr>
                                <th>Invoice #</th>
                                <th>Date</th>
                                <th>Customer</th>
                                <th>Amount</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredInvoices.map((invoice) => {
                                const normalizedStatus = String(invoice.status || "").toLowerCase();
                                return (
                                    <tr key={invoice.id}>
                                        <td style={{ fontWeight: "600", color: "#0d6efd" }}>{invoice.number}</td>
                                        <td>{invoice.date || "-"}</td>
                                        <td>{invoice.customer_name || "-"}</td>
                                        <td style={{ fontWeight: "600" }}>{formatCurrency(invoice.amount_usd)}</td>
                                        <td><span className={`fin-status ${normalizedStatus}`}>{normalizedStatus || "pending"}</span></td>
                                        <td>
                                            <div className="fin-row fin-gap-sm">
                                                {normalizedStatus !== "paid" ? (
                                                    <button onClick={() => handlePayInvoice(invoice)} className="glass-btn-primary glass-btn-sm">
                                                        Pay
                                                    </button>
                                                ) : null}
                                                <button onClick={() => setSelectedInvoice(invoice)} className="glass-btn-secondary glass-btn-sm">
                                                    View
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>

            {showCreate ? (
                <div className="fin-modal-overlay" onClick={() => setShowCreate(false)}>
                    <div className="fin-modal" onClick={(e) => e.stopPropagation()}>
                        <h3>Create Invoice</h3>
                        <form onSubmit={handleCreateInvoice}>
                            <label>Invoice Date</label>
                            <input
                                type="date"
                                value={form.invoice_date}
                                onChange={(e) => setForm((current) => ({ ...current, invoice_date: e.target.value }))}
                                required
                            />
                            <label>Customer Name</label>
                            <input
                                type="text"
                                value={form.customer_name}
                                onChange={(e) => setForm((current) => ({ ...current, customer_name: e.target.value }))}
                                placeholder="Acme Logistics"
                                required
                            />
                            <label>Amount (USD)</label>
                            <input
                                type="number"
                                min="0"
                                step="0.01"
                                value={form.amount_usd}
                                onChange={(e) => setForm((current) => ({ ...current, amount_usd: e.target.value }))}
                                required
                            />
                            <label>Status</label>
                            <select value={form.status} onChange={(e) => setForm((current) => ({ ...current, status: e.target.value }))}>
                                <option value="pending">Pending</option>
                                <option value="draft">Draft</option>
                                <option value="sent">Sent</option>
                            </select>
                            <div className="fin-modal-actions">
                                <button type="button" className="fin-btn" onClick={() => setShowCreate(false)}>Cancel</button>
                                <button type="submit" className="fin-btn primary" disabled={submitting}>
                                    {submitting ? "Creating..." : "Create Invoice"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            ) : null}

            {selectedInvoice ? (
                <div className="fin-modal-overlay" onClick={() => setSelectedInvoice(null)}>
                    <div className="fin-modal" onClick={(e) => e.stopPropagation()}>
                        <h3>{selectedInvoice.number}</h3>
                        <div className="fin-card-sub">Date: {selectedInvoice.date || "-"}</div>
                        <div className="fin-card-sub">Customer: {selectedInvoice.customer_name || "-"}</div>
                        <div className="fin-card-sub">Amount: {formatCurrency(selectedInvoice.amount_usd)}</div>
                        <div className="fin-card-sub">Status: {String(selectedInvoice.status || "").toLowerCase()}</div>
                        <div className="fin-modal-actions">
                            <button type="button" className="fin-btn" onClick={() => setSelectedInvoice(null)}>Close</button>
                        </div>
                    </div>
                </div>
            ) : null}
        </div>
    );
};

export default InvoiceManager;
