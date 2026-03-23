import React, { useEffect, useMemo, useState } from "react";
import { FINANCE_ZERO_MODE } from "../../../../config/financeConstants";
import financeApi from "../../../../services/financeApi";

const formatCurrency = (amount) =>
    new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 2,
    }).format(Number(amount || 0));

export default function LedgerManager({ zeroMode = FINANCE_ZERO_MODE }) {
    const [selected, setSelected] = useState(null);
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(!zeroMode);
    const [error, setError] = useState("");
    const [asOfDate, setAsOfDate] = useState(new Date().toISOString().split("T")[0]);

    useEffect(() => {
        let mounted = true;

        const load = async () => {
            if (zeroMode) return;
            setLoading(true);
            setError("");
            try {
                const result = await financeApi.getTrialBalance(asOfDate);
                if (!mounted) return;
                setReport(result);
            } catch (err) {
                if (!mounted) return;
                setError(err?.response?.data?.detail || err?.message || "Failed to load ledger data.");
            } finally {
                if (mounted) setLoading(false);
            }
        };

        load();
        return () => {
            mounted = false;
        };
    }, [zeroMode, asOfDate]);

    const accounts = useMemo(() => {
        const rows = report?.trial_balance || [];
        return rows.map((row) => ({
            code: row.account_code,
            name: row.account_name,
            type: Number(row.debit_balance || 0) > 0 ? "asset" : "liability",
            balance: Number(row.debit_balance || row.credit_balance || 0),
        }));
    }, [report]);

    const ledgerEntries = useMemo(() => {
        const rows = report?.trial_balance || [];
        return rows.map((row) => ({
            id: `${row.account_code}-${row.account_name}`,
            date: report?.as_of_date || asOfDate,
            desc: row.account_name,
            debit: Number(row.debit_balance || 0) > 0 ? row.account_code : "-",
            credit: Number(row.credit_balance || 0) > 0 ? row.account_code : "-",
            amount: Number(row.debit_balance || row.credit_balance || 0),
            ref: row.account_code,
        }));
    }, [report, asOfDate]);

    const handleExport = () => {
        const csvContent = "Date,Description,Debit,Credit,Amount,Reference\n" +
            ledgerEntries.map((entry) => `${entry.date},${entry.desc},${entry.debit},${entry.credit},${entry.amount},${entry.ref}`).join("\n");
        const blob = new Blob([csvContent], { type: "text/csv" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `ledger_${asOfDate}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    };

    return (
        <div className="fin-section">
            <div className="fin-card-title">General Ledger</div>
            <div className="fin-row fin-gap-sm">
                <input type="date" value={asOfDate} onChange={(e) => setAsOfDate(e.target.value)} className="fin-select" />
                <button className="fin-btn" onClick={handleExport} disabled={zeroMode || loading || ledgerEntries.length === 0}>Export Ledger</button>
            </div>

            {error ? <div className="fin-card" style={{ color: "#fca5a5" }}>{String(error)}</div> : null}

            <div className="fin-grid fin-grid-compact">
                {accounts.length === 0 ? (
                    <div style={{ padding: "16px", color: "#9fb2d3" }}>{loading ? "Loading accounts..." : "No accounts available."}</div>
                ) : (
                    accounts.map((acc) => (
                        <div
                            key={acc.code}
                            className={`fin-card fin-account ${selected === acc.code ? "selected" : ""}`}
                            onClick={() => setSelected(acc.code)}
                        >
                            <div className="fin-account-head">
                                <span className="fin-account-code">{acc.code}</span>
                                <span className={`fin-badge ${acc.type}`}>{acc.type}</span>
                            </div>
                            <div className="fin-account-name">{acc.name}</div>
                            <div className="fin-account-balance">{formatCurrency(acc.balance)}</div>
                        </div>
                    ))
                )}
            </div>

            <div className="fin-card">
                <div className="fin-card-title">Trial Balance Entries</div>
                <div className="fin-table-wrapper">
                    {ledgerEntries.length === 0 ? (
                        <div style={{ padding: "16px", color: "#9fb2d3" }}>{loading ? "Loading ledger entries..." : "No ledger entries available."}</div>
                    ) : (
                        <table className="fin-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Description</th>
                                    <th>Debit</th>
                                    <th>Credit</th>
                                    <th>Amount</th>
                                    <th>Ref</th>
                                </tr>
                            </thead>
                            <tbody>
                                {ledgerEntries.map((entry) => (
                                    <tr key={entry.id}>
                                        <td>{entry.date}</td>
                                        <td>{entry.desc}</td>
                                        <td>{entry.debit}</td>
                                        <td>{entry.credit}</td>
                                        <td className="fin-pos">{formatCurrency(entry.amount)}</td>
                                        <td>{entry.ref}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
                {report ? (
                    <div className="fin-row fin-gap-sm">
                        <span className="fin-status completed">Balanced: {report.is_balanced ? "Yes" : "No"}</span>
                        <span>Total Debit {formatCurrency(report.total_debit)}</span>
                        <span>Total Credit {formatCurrency(report.total_credit)}</span>
                    </div>
                ) : null}
            </div>
        </div>
    );
}
