import React, { useMemo, useState } from "react";
import { FINANCE_ZERO_MODE } from "../../../../config/financeConstants";

export default function RevenueManager({ zeroMode = FINANCE_ZERO_MODE }) {
    const [showInvoiceModal, setShowInvoiceModal] = useState(false);
    const [showPaymentModal, setShowPaymentModal] = useState(false);
    const [invoiceList, setInvoiceList] = useState([]);

    const streams = useMemo(() => (
        zeroMode
            ? []
            : [
                { id: "freight", name: "Freight Services", target: 150000, actual: 125000, trend: "+12%" },
                { id: "logistics", name: "Logistics Solutions", target: 80000, actual: 78500, trend: "+8%" },
                { id: "consulting", name: "Consulting", target: 50000, actual: 42300, trend: "+5%" },
            ]
    ), [zeroMode]);

    const baseInvoices = useMemo(() => [
        { id: "INV-001", client: "ABC Corp", date: "2024-01-15", due: "2024-02-14", amount: 25000, status: "paid", type: "freight" },
        { id: "INV-002", client: "XYZ Logistics", date: "2024-01-14", due: "2024-02-13", amount: 18500, status: "pending", type: "logistics" },
        { id: "INV-003", client: "Global Shipping", date: "2024-01-13", due: "2024-02-12", amount: 32000, status: "overdue", type: "freight" },
    ], []);

    const invoices = useMemo(() => (
        zeroMode ? [] : [...baseInvoices, ...invoiceList]
    ), [zeroMode, baseInvoices, invoiceList]);

    const handleNewInvoice = (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const newInvoice = {
            id: `INV-${String(Date.now()).slice(-3)}`,
            client: formData.get('client'),
            date: formData.get('date'),
            due: formData.get('due'),
            amount: parseFloat(formData.get('amount')),
            status: 'pending',
            type: formData.get('type')
        };
        setInvoiceList(prev => [...prev, newInvoice]);
        setShowInvoiceModal(false);
        alert(`Invoice ${newInvoice.id} created successfully!`);
    };

    const handleRecordPayment = (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const invoiceId = formData.get('invoiceId');
        const amount = formData.get('amount');
        setShowPaymentModal(false);
        alert(`Payment of $${amount} recorded for ${invoiceId}`);
    };

    return (
        <div className="fin-section">
            <div className="fin-card-title">Revenue Tracking</div>
            <div className="fin-grid fin-grid-compact">
                {streams.length === 0 ? (
                    <div style={{ padding: "16px", color: "#9fb2d3" }}>No revenue streams available.</div>
                ) : (
                    streams.map((s) => {
                        const pct = Math.min((s.actual / s.target) * 100, 120);
                        return (
                            <div key={s.id} className="fin-card fin-stream">
                                <div className="fin-stream-head">
                                    <span className="fin-stream-name">{s.name}</span>
                                    <span className="fin-stream-trend">{s.trend}</span>
                                </div>
                                <div className="fin-progress">
                                    <div className="fin-progress-bar" style={{ width: `${pct}%` }} />
                                </div>
                                <div className="fin-stream-meta">
                                    <span>Actual ${s.actual.toLocaleString()}</span>
                                    <span>Target ${s.target.toLocaleString()}</span>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            <div className="fin-card">
                <div className="fin-card-title">Invoices</div>
                <div className="fin-table-wrapper">
                    {invoices.length === 0 ? (
                        <div style={{ padding: "16px", color: "#9fb2d3" }}>No invoices available.</div>
                    ) : (
                        <table className="fin-table">
                            <thead>
                                <tr>
                                    <th>Invoice</th>
                                    <th>Client</th>
                                    <th>Issue Date</th>
                                    <th>Due Date</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {invoices.map((inv) => (
                                    <tr key={inv.id}>
                                        <td>{inv.id}</td>
                                        <td>{inv.client}</td>
                                        <td>{inv.date}</td>
                                        <td>{inv.due}</td>
                                        <td className="fin-pos">${inv.amount.toLocaleString()}</td>
                                        <td><span className={`fin-status ${inv.status}`}>{inv.status}</span></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
                <div className="fin-row fin-justify-end fin-gap-sm">
                    <button className="fin-btn" disabled={zeroMode} onClick={() => setShowPaymentModal(true)}>Record Payment</button>
                    <button className="fin-btn primary" disabled={zeroMode} onClick={() => setShowInvoiceModal(true)}>New Invoice</button>
                </div>
            </div>

            {showInvoiceModal && (
                <div className="fin-modal-overlay" onClick={() => setShowInvoiceModal(false)}>
                    <div className="fin-modal" onClick={(e) => e.stopPropagation()}>
                        <h3>Create New Invoice</h3>
                        <form onSubmit={handleNewInvoice}>
                            <label>Client Name</label>
                            <input type="text" name="client" required placeholder="Client Name" />
                            <label>Issue Date</label>
                            <input type="date" name="date" required />
                            <label>Due Date</label>
                            <input type="date" name="due" required />
                            <label>Amount ($)</label>
                            <input type="number" name="amount" required min="0" step="0.01" />
                            <label>Type</label>
                            <select name="type" required>
                                <option value="freight">Freight</option>
                                <option value="logistics">Logistics</option>
                                <option value="consulting">Consulting</option>
                            </select>
                            <div className="fin-modal-actions">
                                <button type="button" className="fin-btn" onClick={() => setShowInvoiceModal(false)}>Cancel</button>
                                <button type="submit" className="fin-btn primary">Create Invoice</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {showPaymentModal && (
                <div className="fin-modal-overlay" onClick={() => setShowPaymentModal(false)}>
                    <div className="fin-modal" onClick={(e) => e.stopPropagation()}>
                        <h3>Record Payment</h3>
                        <form onSubmit={handleRecordPayment}>
                            <label>Invoice ID</label>
                            <select name="invoiceId" required>
                                {invoices.filter(i => i.status !== 'paid').map(inv => (
                                    <option key={inv.id} value={inv.id}>{inv.id} - {inv.client} (${inv.amount.toLocaleString()})</option>
                                ))}
                            </select>
                            <label>Payment Amount ($)</label>
                            <input type="number" name="amount" required min="0" step="0.01" />
                            <label>Payment Date</label>
                            <input type="date" name="paymentDate" required />
                            <label>Payment Method</label>
                            <select name="method">
                                <option value="bank">Bank Transfer</option>
                                <option value="check">Check</option>
                                <option value="cash">Cash</option>
                                <option value="credit">Credit Card</option>
                            </select>
                            <div className="fin-modal-actions">
                                <button type="button" className="fin-btn" onClick={() => setShowPaymentModal(false)}>Cancel</button>
                                <button type="submit" className="fin-btn primary">Record Payment</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
