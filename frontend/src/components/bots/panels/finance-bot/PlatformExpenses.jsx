import React, { useEffect, useMemo, useState } from "react";
import axiosClient from "../../../../api/axiosClient";

function formatDate(dateStr) {
    if (!dateStr) return "";
    const d = new Date(dateStr);
    if (!isNaN(d)) return d.toISOString().slice(0, 10);
    const match = dateStr.match(/([A-Za-z]+) (\d{1,2}), (\d{4})/);
    if (match) {
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const monthIdx = months.findIndex((m) => match[1].toLowerCase().startsWith(m.toLowerCase()));
        if (monthIdx >= 0) {
            const mm = String(monthIdx + 1).padStart(2, "0");
            return `${match[3]}-${mm}-${match[2].padStart(2, "0")}`;
        }
    }
    return dateStr;
}

export default function PlatformExpenses() {
    const [expenses, setExpenses] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [uploading, setUploading] = useState(false);

    const loadExpenses = async () => {
        setLoading(true);
        setError("");
        try {
            const res = await axiosClient.get("/finance/expenses");
            const raw = res?.data;
            const items = Array.isArray(raw?.items)
                ? raw.items
                : Array.isArray(raw)
                    ? raw
                    : [];

            const mapped = items.map((item, idx) => ({
                id: item?.id ?? idx,
                invoiceNumber: item?.invoice_number || item?.filename || item?.invoiceNumber || "-",
                date: item?.issue_date ? formatDate(item.issue_date) : "-",
                amount: item?.amount ?? "-",
                vendor: item?.vendor || "-",
                fileName: item?.filename || item?.invoice_file || "-",
                url: item?.url || item?.download_url || "",
            }));

            setExpenses(mapped);
        } catch (err) {
            setError("Failed to load platform invoices.");
            setExpenses([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadExpenses();
    }, []);

    const totalAmount = useMemo(() => {
        return expenses.reduce((sum, item) => sum + Number(item?.amount || 0), 0);
    }, [expenses]);

    const latestMonth = useMemo(() => {
        const months = expenses
            .map((item) => (item?.date && item.date !== "-" ? item.date.slice(0, 7) : ""))
            .filter(Boolean)
            .sort();
        return months.length ? months[months.length - 1] : "-";
    }, [expenses]);

    const latestMonthTotal = useMemo(() => {
        if (latestMonth === "-") return 0;
        return expenses.reduce((sum, item) => {
            const month = item?.date && item.date !== "-" ? item.date.slice(0, 7) : "";
            return month === latestMonth ? sum + Number(item?.amount || 0) : sum;
        }, 0);
    }, [expenses, latestMonth]);

    const handleMultiUpload = async (e) => {
        const files = Array.from(e.target.files || []).slice(0, 30);
        if (!files.length) return;

        setUploading(true);
        try {
            const newExpenses = await Promise.all(
                files.map(async (file) => {
                    const formData = new FormData();
                    formData.append("file", file);
                    try {
                        const res = await axiosClient.post("/api/v1/ocr/ocr-invoice-extract", formData, {
                            headers: { "Content-Type": "multipart/form-data" },
                        });
                        const fields = res?.data?.fields || {};
                        return {
                            id: Date.now() + Math.random(),
                            invoiceNumber: fields.invoice_number || file.name,
                            date: fields.issue_date ? formatDate(fields.issue_date) : new Date().toISOString().slice(0, 10),
                            amount: fields.amount || 0,
                            vendor: fields.vendor || "-",
                            fileName: file.name,
                            url: "",
                        };
                    } catch (err) {
                        return {
                            id: Date.now() + Math.random(),
                            invoiceNumber: file.name,
                            date: new Date().toISOString().slice(0, 10),
                            amount: 0,
                            vendor: "-",
                            fileName: file.name,
                            url: "",
                        };
                    }
                })
            );
            setExpenses((prev) => [...newExpenses, ...prev]);
        } finally {
            setUploading(false);
            e.target.value = null;
        }
    };

    return (
        <div className="fin-section">
            <div className="fin-section-header">
                <div>
                    <div className="fin-section-title">Platform Expenses</div>
                    <div className="fin-section-sub">Invoices pulled from the platform finance service.</div>
                </div>
                <div className="fin-row fin-gap-sm">
                    <label className={`fin-btn ${uploading ? "primary" : ""}`}>
                        <input
                            type="file"
                            multiple
                            onChange={handleMultiUpload}
                            disabled={uploading}
                            style={{ display: "none" }}
                        />
                        {uploading ? "Uploading..." : "Upload invoices"}
                    </label>
                    <button className="fin-btn" onClick={loadExpenses} disabled={loading}>
                        {loading ? "Loading..." : "Refresh"}
                    </button>
                </div>
            </div>

            {error ? (
                <div className="fin-card">
                    <div className="fin-card-title">Load Error</div>
                    <div className="fin-card-sub">{error}</div>
                </div>
            ) : null}

            <div className="fin-grid fin-grid-metrics">
                <div className="fin-card fin-metric">
                    <span className="fin-metric-label">Records</span>
                    <span className="fin-metric-value">{loading ? "..." : expenses.length}</span>
                </div>
                <div className="fin-card fin-metric">
                    <span className="fin-metric-label">Total Amount</span>
                    <span className="fin-metric-value">${loading ? "..." : totalAmount.toLocaleString()}</span>
                </div>
                <div className="fin-card fin-metric">
                    <span className="fin-metric-label">Latest Month</span>
                    <span className="fin-metric-value">{loading ? "..." : latestMonth}</span>
                </div>
                <div className="fin-card fin-metric">
                    <span className="fin-metric-label">Latest Month Total</span>
                    <span className="fin-metric-value">${loading ? "..." : latestMonthTotal.toLocaleString()}</span>
                </div>
            </div>

            <div className="fin-card">
                <div className="fin-table-wrapper">
                    {loading ? (
                        <div style={{ padding: "16px", color: "#9fb2d3" }}>Loading platform invoices...</div>
                    ) : expenses.length === 0 ? (
                        <div style={{ padding: "16px", color: "#9fb2d3" }}>No platform invoices found.</div>
                    ) : (
                        <table className="fin-table">
                            <thead>
                                <tr>
                                    <th>Invoice File</th>
                                    <th>Date</th>
                                    <th>Vendor</th>
                                    <th>Amount</th>
                                    <th>Download</th>
                                </tr>
                            </thead>
                            <tbody>
                                {expenses.map((item) => (
                                    <tr key={item.id}>
                                        <td>{item.invoiceNumber || item.fileName}</td>
                                        <td>{item.date || "-"}</td>
                                        <td>{item.vendor || "-"}</td>
                                        <td>{Number(item.amount || 0).toLocaleString()}</td>
                                        <td>
                                            {item.url ? (
                                                <a
                                                    href={item.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="fin-btn primary"
                                                >
                                                    Download
                                                </a>
                                            ) : (
                                                "-"
                                            )}
                                        </td>
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
