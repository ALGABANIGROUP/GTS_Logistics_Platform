import React, { useMemo, useState } from "react";
import { FINANCE_ZERO_MODE } from "../../../../config/financeConstants";

export default function TaxManager({ zeroMode = FINANCE_ZERO_MODE }) {
    const [filter, setFilter] = useState("all");

    const handleCalculate = () => {
        alert('Calculating tax obligations based on current financial data...');
        setTimeout(() => {
            alert('Tax calculation complete! Estimated liability: $42,500');
        }, 1000);
    };

    const handleFileReturn = () => {
        const confirmed = window.confirm('Are you sure you want to file tax return for Q4 2023?');
        if (confirmed) {
            alert('Tax return filing initiated. Reference: TR-2024-001');
        }
    };

    const handlePayNow = () => {
        const amount = prompt('Enter payment amount:', '28500');
        if (amount) {
            alert(`Tax payment of $${parseFloat(amount).toLocaleString()} processed successfully!`);
        }
    };

    const liabilities = useMemo(() => (
        zeroMode
            ? []
            : [
                { id: 1, type: "income", period: "Q4 2023", amount: 28500, due: "2024-01-31", status: "pending" },
                { id: 2, type: "sales", period: "Dec 2023", amount: 12500, due: "2024-01-20", status: "paid" },
                { id: 3, type: "payroll", period: "Dec 2023", amount: 8500, due: "2024-01-15", status: "paid" },
                { id: 4, type: "income", period: "Q1 2024", amount: 32000, due: "2024-04-30", status: "estimated" },
            ]
    ), [zeroMode]);

    const payments = useMemo(() => (
        zeroMode
            ? []
            : [
                { id: 1, date: "2024-01-15", type: "sales", amount: 12500, ref: "TAX-789", method: "EFT" },
                { id: 2, date: "2023-12-20", type: "income", amount: 25000, ref: "TAX-456", method: "Transfer" },
            ]
    ), [zeroMode]);

    return (
        <div className="fin-section">
            <div className="fin-card-title">Tax Management</div>

            <div className="fin-row fin-justify-between fin-align-center fin-gap-sm">
                <div className="fin-row fin-gap-sm">
                    <select className="fin-select" value={filter} onChange={(e) => setFilter(e.target.value)}>
                        <option value="all">All</option>
                        <option value="income">Income</option>
                        <option value="sales">Sales</option>
                        <option value="payroll">Payroll</option>
                    </select>
                    <button className="fin-btn" disabled={zeroMode} onClick={handleCalculate}>Calculate</button>
                </div>
                <div className="fin-row fin-gap-sm">
                    <button className="fin-btn" disabled={zeroMode} onClick={handleFileReturn}>File Return</button>
                    <button className="fin-btn primary" disabled={zeroMode} onClick={handlePayNow}>Pay Now</button>
                </div>
            </div>

            <div className="fin-card">
                <div className="fin-card-title">Liabilities</div>
                <div className="fin-table-wrapper">
                    {liabilities.filter((l) => filter === "all" || l.type === filter).length === 0 ? (
                        <div style={{ padding: "16px", color: "#9fb2d3" }}>No tax liabilities available.</div>
                    ) : (
                        <table className="fin-table">
                            <thead>
                                <tr>
                                    <th>Type</th>
                                    <th>Period</th>
                                    <th>Amount</th>
                                    <th>Due Date</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {liabilities
                                    .filter((l) => filter === "all" || l.type === filter)
                                    .map((l) => (
                                        <tr key={l.id}>
                                            <td><span className={`fin-badge ${l.type}`}>{l.type}</span></td>
                                            <td>{l.period}</td>
                                            <td className="fin-pos">${l.amount.toLocaleString()}</td>
                                            <td>{l.due}</td>
                                            <td><span className={`fin-status ${l.status}`}>{l.status}</span></td>
                                        </tr>
                                    ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>

            <div className="fin-card">
                <div className="fin-card-title">Payments</div>
                <div className="fin-table-wrapper">
                    {payments.length === 0 ? (
                        <div style={{ padding: "16px", color: "#9fb2d3" }}>No tax payments recorded.</div>
                    ) : (
                        <table className="fin-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Type</th>
                                    <th>Amount</th>
                                    <th>Reference</th>
                                    <th>Method</th>
                                </tr>
                            </thead>
                            <tbody>
                                {payments.map((p) => (
                                    <tr key={p.id}>
                                        <td>{p.date}</td>
                                        <td>{p.type}</td>
                                        <td className="fin-pos">${p.amount.toLocaleString()}</td>
                                        <td>{p.ref}</td>
                                        <td>{p.method}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}
