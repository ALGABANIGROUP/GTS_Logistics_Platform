import React, { useEffect, useMemo, useState } from "react";
import { FINANCE_ZERO_MODE } from "../../../../config/financeConstants";
import financeApi from "../../../../services/financeApi";

const formatCurrency = (amount) =>
    new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 2,
    }).format(Number(amount || 0));

export default function FinanceDashboard({ zeroMode = FINANCE_ZERO_MODE }) {
    const [range, setRange] = useState("month");
    const [dashboard, setDashboard] = useState(null);
    const [payments, setPayments] = useState([]);
    const [loading, setLoading] = useState(!zeroMode);
    const [error, setError] = useState("");

    useEffect(() => {
        let mounted = true;

        const load = async () => {
            if (zeroMode) return;
            setLoading(true);
            setError("");
            try {
                const [dashboardData, paymentData] = await Promise.all([
                    financeApi.getDashboardStats(),
                    financeApi.getPayments(),
                ]);
                if (!mounted) return;
                setDashboard(dashboardData);
                setPayments(paymentData?.items || []);
            } catch (err) {
                if (!mounted) return;
                setError(err?.response?.data?.detail || err?.message || "Failed to load finance dashboard.");
            } finally {
                if (mounted) setLoading(false);
            }
        };

        load();
        return () => {
            mounted = false;
        };
    }, [zeroMode, range]);

    const metrics = useMemo(() => {
        if (zeroMode || !dashboard) {
            return [
                { label: "Total Revenue", value: "$0.00", trend: "No data", tone: "neutral" },
                { label: "Total Expenses", value: "$0.00", trend: "No data", tone: "neutral" },
                { label: "Net Profit", value: "$0.00", trend: "No data", tone: "neutral" },
                { label: "Pending Invoices", value: "0", trend: "No data", tone: "neutral" },
            ];
        }

        return [
            { label: "Total Revenue", value: formatCurrency(dashboard.total_revenue), trend: "Unified finance API", tone: "up" },
            { label: "Total Expenses", value: formatCurrency(dashboard.total_expenses), trend: "Unified finance API", tone: "down" },
            {
                label: "Net Profit",
                value: formatCurrency(dashboard.net_profit),
                trend: `Margin ${Number(dashboard.net_margin || 0).toFixed(2)}%`,
                tone: dashboard.net_profit >= 0 ? "up" : "warn",
            },
            {
                label: "Pending Invoices",
                value: String(dashboard.pending_invoices || 0),
                trend: `${formatCurrency(dashboard.pending_payments)} outstanding`,
                tone: "warn",
            },
        ];
    }, [dashboard, zeroMode]);

    const arAp = useMemo(() => {
        if (zeroMode || !dashboard) return [];
        return [
            { label: "Accounts Receivable", value: formatCurrency(dashboard.pending_payments), tone: "up" },
            { label: "Collected Payments", value: String(dashboard.paid_invoices || 0), tone: "neutral" },
            { label: "Invoice Count", value: String(dashboard.total_invoices || 0), tone: "up" },
        ];
    }, [dashboard, zeroMode]);

    const transactions = useMemo(() => {
        if (zeroMode) return [];
        return payments.slice(0, 8).map((payment) => ({
            id: payment.id,
            date: payment.payment_date || payment.created_at || "-",
            desc: payment.reference_id,
            type: payment.payment_type || "payment",
            amount: Number(payment.amount || 0),
            status: String(payment.status || "").toLowerCase(),
        }));
    }, [payments, zeroMode]);

    const invoiceSnapshot = useMemo(() => {
        if (zeroMode || !dashboard?.recent_invoices?.length) return [];
        return dashboard.recent_invoices.slice(0, 4).map((invoice) => ({
            category: invoice.number,
            allocated: Number(invoice.amount_usd || 0),
            spent: ["paid"].includes(String(invoice.status || "").toLowerCase()) ? Number(invoice.amount_usd || 0) : 0,
        }));
    }, [dashboard, zeroMode]);

    return (
        <div className="fin-section">
            <div className="fin-section-header">
                <div>
                    <div className="fin-section-title">Financial Dashboard</div>
                    <div className="fin-section-sub">Unified Finance API</div>
                </div>
                <div className="fin-row">
                    <select className="fin-select" value={range} onChange={(e) => setRange(e.target.value)}>
                        <option value="week">This Week</option>
                        <option value="month">This Month</option>
                        <option value="quarter">This Quarter</option>
                        <option value="year">This Year</option>
                    </select>
                    <button className="fin-btn ghost" onClick={() => window.location.reload()} disabled={zeroMode || loading}>
                        Refresh
                    </button>
                </div>
            </div>

            {error ? <div className="fin-card" style={{ color: "#fca5a5" }}>{String(error)}</div> : null}

            <div className="fin-grid fin-grid-metrics">
                {metrics.map((metric) => (
                    <div key={metric.label} className="fin-card fin-metric">
                        <div className="fin-metric-label">{metric.label}</div>
                        <div className="fin-metric-value">{loading ? "..." : metric.value}</div>
                        <div className={`fin-metric-trend ${metric.tone}`}>{metric.trend}</div>
                    </div>
                ))}
            </div>

            <div className="fin-card">
                <div className="fin-card-title">Receivables / Collections</div>
                <div className="fin-grid fin-grid-compact">
                    {arAp.length === 0 ? (
                        <div style={{ padding: "16px", color: "#9fb2d3" }}>{loading ? "Loading finance summary..." : "No receivables/payables yet."}</div>
                    ) : (
                        arAp.map((item) => (
                            <div key={item.label} className="fin-chip">
                                <div className="fin-chip-label">{item.label}</div>
                                <div className="fin-chip-value">{item.value}</div>
                                <div className={`fin-chip-trend ${item.tone}`}>{item.tone === "neutral" ? "-" : item.tone === "up" ? "+" : ""}</div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            <div className="fin-card">
                <div className="fin-card-title">Recent Payments</div>
                <div className="fin-table-wrapper">
                    {transactions.length === 0 ? (
                        <div style={{ padding: "24px", color: "#9fb2d3" }}>{loading ? "Loading payments..." : "No payments available."}</div>
                    ) : (
                        <table className="fin-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Reference</th>
                                    <th>Type</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {transactions.map((tx) => (
                                    <tr key={tx.id}>
                                        <td>{String(tx.date).slice(0, 10)}</td>
                                        <td>{tx.desc}</td>
                                        <td><span className={`fin-badge ${tx.type}`}>{tx.type}</span></td>
                                        <td className={tx.type === "expense" ? "fin-neg" : "fin-pos"}>{formatCurrency(tx.amount)}</td>
                                        <td><span className={`fin-status ${tx.status}`}>{tx.status}</span></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>

            <div className="fin-card">
                <div className="fin-card-title">Recent Invoice Snapshot</div>
                <div className="fin-grid fin-grid-compact">
                    {invoiceSnapshot.length === 0 ? (
                        <div style={{ padding: "16px", color: "#9fb2d3" }}>{loading ? "Loading invoice snapshot..." : "No invoices available."}</div>
                    ) : (
                        invoiceSnapshot.map((item) => {
                            const pct = item.allocated > 0 ? Math.min((item.spent / item.allocated) * 100, 100) : 0;
                            return (
                                <div key={item.category} className="fin-budget">
                                    <div className="fin-budget-header">
                                        <span>{item.category}</span>
                                        <span className={`fin-budget-flag ${pct >= 100 ? "ok" : "warn"}`}>{pct >= 100 ? "Paid" : "Pending"}</span>
                                    </div>
                                    <div className="fin-progress">
                                        <div className="fin-progress-bar" style={{ width: `${pct}%`, backgroundColor: pct >= 100 ? "#10b981" : "#f59e0b" }} />
                                    </div>
                                    <div className="fin-budget-meta">
                                        <span>Collected {formatCurrency(item.spent)}</span>
                                        <span>Total {formatCurrency(item.allocated)}</span>
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>
            </div>
        </div>
    );
}
