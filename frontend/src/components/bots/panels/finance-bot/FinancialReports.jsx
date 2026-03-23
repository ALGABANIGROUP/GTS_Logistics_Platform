import React, { useMemo, useState } from "react";
import { FINANCE_ZERO_MODE } from "../../../../config/financeConstants";
import financeApi from "../../../../services/financeApi";

export default function FinancialReports({ zeroMode = FINANCE_ZERO_MODE }) {
    const [reportType, setReportType] = useState("income-statement");
    const [period, setPeriod] = useState("monthly");
    const [generatedReports, setGeneratedReports] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const types = useMemo(() => ([
        { id: "income-statement", name: "Income Statement" },
        { id: "balance-sheet", name: "Balance Sheet" },
        { id: "trial-balance", name: "Trial Balance" },
    ]), []);

    const handleGenerate = async () => {
        const today = new Date();
        const endDate = today.toISOString().split("T")[0];
        const startDate = new Date(today);
        if (period === "monthly") startDate.setMonth(today.getMonth() - 1);
        if (period === "quarterly") startDate.setMonth(today.getMonth() - 3);
        if (period === "yearly") startDate.setFullYear(today.getFullYear() - 1);

        setLoading(true);
        setError("");
        try {
            let payload;
            if (reportType === "trial-balance") {
                payload = await financeApi.getTrialBalance(endDate);
            } else if (reportType === "balance-sheet") {
                payload = await financeApi.getBalanceSheet(endDate);
            } else {
                payload = await financeApi.getIncomeStatement(startDate.toISOString().split("T")[0], endDate);
            }

            const typeName = types.find((item) => item.id === reportType)?.name || reportType;
            const newReport = {
                id: Date.now(),
                type: reportType,
                name: typeName,
                period: `${period} ending ${endDate}`,
                generated: new Date().toLocaleDateString(),
                status: "generated",
                payload,
            };
            setGeneratedReports((current) => [newReport, ...current]);
        } catch (err) {
            setError(err?.response?.data?.detail || err?.message || "Failed to generate report.");
        } finally {
            setLoading(false);
        }
    };

    const exportReport = (report) => {
        const dataStr = JSON.stringify(report.payload, null, 2);
        const blob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = `${report.type}_${new Date().toISOString().split("T")[0]}.json`;
        anchor.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="fin-section">
            <div className="fin-card-title">Financial Reports</div>

            <div className="fin-grid fin-grid-compact">
                <div className="fin-card">
                    <div className="fin-card-title">Generate</div>
                    <div className="fin-row fin-gap-sm">
                        <select className="fin-select" value={reportType} onChange={(e) => setReportType(e.target.value)}>
                            {types.map((type) => (
                                <option key={type.id} value={type.id}>{type.name}</option>
                            ))}
                        </select>
                        <select className="fin-select" value={period} onChange={(e) => setPeriod(e.target.value)}>
                            <option value="monthly">Monthly</option>
                            <option value="quarterly">Quarterly</option>
                            <option value="yearly">Yearly</option>
                        </select>
                        <button className="fin-btn primary" disabled={zeroMode || loading} onClick={handleGenerate}>
                            {loading ? "Generating..." : "Generate"}
                        </button>
                    </div>
                    <div className="fin-card-sub">Source: /api/v1/finance/ledger/*</div>
                    {error ? <div style={{ marginTop: "12px", color: "#fca5a5" }}>{String(error)}</div> : null}
                </div>

                <div className="fin-card">
                    <div className="fin-card-title">Available Reports</div>
                    <div className="fin-table-wrapper">
                        {generatedReports.length === 0 ? (
                            <div style={{ padding: "16px", color: "#9fb2d3" }}>No reports generated yet.</div>
                        ) : (
                            <table className="fin-table">
                                <thead>
                                    <tr>
                                        <th>Type</th>
                                        <th>Period</th>
                                        <th>Generated</th>
                                        <th>Status</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {generatedReports.map((report) => (
                                        <tr key={report.id}>
                                            <td>{report.name}</td>
                                            <td>{report.period}</td>
                                            <td>{report.generated}</td>
                                            <td><span className={`fin-status ${report.status}`}>{report.status}</span></td>
                                            <td>
                                                <button className="glass-btn-secondary glass-btn-sm" onClick={() => exportReport(report)}>
                                                    Export
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
