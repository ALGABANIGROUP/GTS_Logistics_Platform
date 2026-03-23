import React, { useEffect, useMemo, useState } from "react";
import { FINANCE_ZERO_MODE } from "../../../../config/financeConstants";
import financeApi from "../../../../services/financeApi";

const initialForm = {
    date: new Date().toISOString().split("T")[0],
    category: "fuel",
    description: "",
    vendor: "",
    amount: "",
    status: "PENDING",
};

const formatCurrency = (amount) =>
    new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 2,
    }).format(Number(amount || 0));

export default function ExpenseTracker({ zeroMode = FINANCE_ZERO_MODE }) {
    const [filter, setFilter] = useState("all");
    const [showExpenseModal, setShowExpenseModal] = useState(false);
    const [expenseList, setExpenseList] = useState([]);
    const [form, setForm] = useState(initialForm);
    const [submitting, setSubmitting] = useState(false);
    const [loading, setLoading] = useState(!zeroMode);
    const [error, setError] = useState("");

    const loadExpenses = async () => {
        if (zeroMode) return;
        setLoading(true);
        setError("");
        try {
            const response = await financeApi.getExpenses();
            setExpenseList(response?.items || []);
        } catch (err) {
            setError(err?.response?.data?.detail || err?.message || "Failed to load expenses.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadExpenses();
    }, [zeroMode]);

    const filteredExpenses = useMemo(() => {
        return expenseList.filter((expense) => {
            if (filter === "all") return true;
            return String(expense.status || "").toLowerCase() === filter;
        });
    }, [expenseList, filter]);

    const handleSubmitExpense = async (event) => {
        event.preventDefault();
        setSubmitting(true);
        setError("");
        try {
            const result = await financeApi.createExpense({
                category: form.category,
                amount: Number(form.amount),
                description: form.description,
                vendor: form.vendor,
                created_at: form.date,
                status: form.status,
            });
            if (result?.success) {
                setShowExpenseModal(false);
                setForm(initialForm);
                await loadExpenses();
            }
        } catch (err) {
            setError(err?.response?.data?.detail || err?.message || "Failed to record expense.");
        } finally {
            setSubmitting(false);
        }
    };

    const handlePayExpense = async (expense) => {
        const confirmed = window.confirm(`Record supplier payout for ${expense.vendor || "supplier"} (${formatCurrency(expense.amount)})?`);
        if (!confirmed) return;
        try {
            await financeApi.payExpense(expense.id, Number(expense.amount || 0), expense.vendor || "Supplier", "sudapay");
            await loadExpenses();
        } catch (err) {
            setError(err?.response?.data?.detail || err?.message || "Failed to record supplier payout.");
        }
    };

    return (
        <div className="fin-section">
            <div className="fin-card-title">Expense Control</div>

            <div className="fin-row fin-gap-sm">
                <button className={`fin-btn ${filter === "pending" ? "primary" : ""}`} onClick={() => setFilter("pending")}>
                    Pending
                </button>
                <button className={`fin-btn ${filter === "paid" ? "primary" : ""}`} onClick={() => setFilter("paid")}>
                    Paid
                </button>
                <button className={`fin-btn ${filter === "all" ? "primary" : ""}`} onClick={() => setFilter("all")}>
                    All
                </button>
                <button className="fin-btn" onClick={loadExpenses} disabled={zeroMode || loading}>Refresh</button>
                <button className="fin-btn" disabled={zeroMode} onClick={() => setShowExpenseModal(true)}>Record Expense</button>
            </div>

            {error ? <div className="fin-card" style={{ color: "#fca5a5" }}>{String(error)}</div> : null}

            {showExpenseModal && (
                <div className="fin-modal-overlay" onClick={() => setShowExpenseModal(false)}>
                    <div className="fin-modal" onClick={(e) => e.stopPropagation()}>
                        <h3>Record New Expense</h3>
                        <form onSubmit={handleSubmitExpense}>
                            <label>Date</label>
                            <input type="date" value={form.date} onChange={(e) => setForm((current) => ({ ...current, date: e.target.value }))} required />
                            <label>Category</label>
                            <select value={form.category} onChange={(e) => setForm((current) => ({ ...current, category: e.target.value }))} required>
                                <option value="fuel">Fuel</option>
                                <option value="maintenance">Maintenance</option>
                                <option value="office">Office</option>
                                <option value="travel">Travel</option>
                                <option value="other">Other</option>
                            </select>
                            <label>Description</label>
                            <input type="text" value={form.description} onChange={(e) => setForm((current) => ({ ...current, description: e.target.value }))} required placeholder="Expense description" />
                            <label>Vendor</label>
                            <input type="text" value={form.vendor} onChange={(e) => setForm((current) => ({ ...current, vendor: e.target.value }))} required placeholder="Vendor name" />
                            <label>Amount (USD)</label>
                            <input type="number" value={form.amount} onChange={(e) => setForm((current) => ({ ...current, amount: e.target.value }))} required min="0" step="0.01" />
                            <label>Status</label>
                            <select value={form.status} onChange={(e) => setForm((current) => ({ ...current, status: e.target.value }))}>
                                <option value="PENDING">Pending</option>
                                <option value="PAID">Paid</option>
                            </select>
                            <div className="fin-modal-actions">
                                <button type="button" className="fin-btn" onClick={() => setShowExpenseModal(false)}>Cancel</button>
                                <button type="submit" className="fin-btn primary" disabled={submitting}>
                                    {submitting ? "Submitting..." : "Submit"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <div className="fin-card">
                <div className="fin-table-wrapper">
                    {loading ? (
                        <div style={{ padding: "16px", color: "#9fb2d3" }}>Loading expenses...</div>
                    ) : filteredExpenses.length === 0 ? (
                        <div style={{ padding: "16px", color: "#9fb2d3" }}>No expenses available.</div>
                    ) : (
                        <table className="fin-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Category</th>
                                    <th>Description</th>
                                    <th>Vendor</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredExpenses.map((expense) => {
                                    const normalizedStatus = String(expense.status || "").toLowerCase();
                                    return (
                                        <tr key={expense.id}>
                                            <td>{String(expense.created_at || expense.date || "").slice(0, 10)}</td>
                                            <td><span className={`fin-badge ${expense.category}`}>{expense.category}</span></td>
                                            <td>{expense.description}</td>
                                            <td>{expense.vendor || "-"}</td>
                                            <td className="fin-neg">-{formatCurrency(expense.amount)}</td>
                                            <td><span className={`fin-status ${normalizedStatus}`}>{normalizedStatus}</span></td>
                                            <td>
                                                {normalizedStatus !== "paid" ? (
                                                    <button className="glass-btn-primary glass-btn-sm" onClick={() => handlePayExpense(expense)}>
                                                        Pay Supplier
                                                    </button>
                                                ) : (
                                                    <span style={{ color: "#86efac" }}>Settled</span>
                                                )}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}
