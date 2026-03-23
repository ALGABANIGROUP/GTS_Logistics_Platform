import React, { useEffect, useMemo, useRef, useState } from "react";
import Papa from "papaparse";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import axiosClient from "../api/axiosClient";
import { useCurrencyStore } from "../stores/useCurrencyStore";
import CurrencyConverter from "../components/CurrencyConverter";

const Finance = () => {
  const { currencySymbol, formatCurrency, currency } = useCurrencyStore();
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState({
    total_expenses: 0,
    total_revenue: 0,
    net_profit: 0,
  });

  const [csvFile, setCsvFile] = useState(null);
  const [csvData, setCsvData] = useState([]);
  const [taxStatus, setTaxStatus] = useState(null);
  const [taxPlanning, setTaxPlanning] = useState(null);

  const [loadingSummary, setLoadingSummary] = useState(false);
  const [loadingExpenses, setLoadingExpenses] = useState(false);

  const tableRef = useRef(null);

  const cardClass =
    "bg-white rounded-xl border border-slate-200 shadow-sm p-5 text-slate-900";
  const cardTitleClass = "text-sm font-semibold text-slate-900 mb-2";
  const labelClass = "text-sm text-slate-600";
  const valueClass = "text-sm font-semibold text-slate-900";

  const fileInputClass =
    "w-full p-2 border border-slate-300 rounded-lg bg-white text-slate-900 " +
    "file:text-slate-700 file:bg-slate-100 file:border-0 " +
    "file:px-3 file:py-1 file:rounded-md file:mr-3";

  const buttonPrimary =
    "bg-sky-700 text-white px-4 py-2 rounded-lg hover:bg-sky-800 transition";
  const buttonGhost =
    "px-3 py-2 rounded-lg text-xs font-medium border border-slate-600 text-slate-100 hover:bg-white/10 transition";

  useEffect(() => {
    fetchExpenses();
    fetchSummary();
    fetchTaxFiling();
    fetchTaxPlanning();
  }, []);

  // Reload data when currency changes
  useEffect(() => {
    const handleCurrencyChange = () => {
      fetchExpenses();
      fetchSummary();
    };

    window.addEventListener('currencyChanged', handleCurrencyChange);
    return () => window.removeEventListener('currencyChanged', handleCurrencyChange);
  }, []);

  const fetchExpenses = async () => {
    setLoadingExpenses(true);
    try {
      const res = await axiosClient.get("/finance/expenses");
      setExpenses(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error("Failed to fetch expenses", err);
      toast.error("Failed to fetch expenses");
      setExpenses([]);
    } finally {
      setLoadingExpenses(false);
    }
  };

  const fetchSummary = async () => {
    setLoadingSummary(true);
    try {
      const res = await axiosClient.get("/finance/summary");
      setSummary(res.data || { total_expenses: 0, total_revenue: 0, net_profit: 0 });
    } catch (err) {
      console.error("Failed to fetch summary", err);
      toast.error("Failed to fetch finance summary");
      setSummary({ total_expenses: 0, total_revenue: 0, net_profit: 0 });
    } finally {
      setLoadingSummary(false);
    }
  };

  const fetchTaxFiling = async () => {
    try {
      const res = await axiosClient.get("/financial/tax-filing");
      setTaxStatus(res.data || null);
    } catch (err) {
      // Non-blocking (endpoint may not exist in MVP)
      console.error("Failed to fetch tax filing status", err);
      setTaxStatus(null);
    }
  };

  const fetchTaxPlanning = async () => {
    try {
      const res = await axiosClient.get("/financial/tax-planning");
      setTaxPlanning(res.data || null);
    } catch (err) {
      // Non-blocking (endpoint may not exist in MVP)
      console.error("Failed to fetch tax planning", err);
      setTaxPlanning(null);
    }
  };

  const handleCSVUpload = () => {
    if (!csvFile) {
      toast.error("Please select a CSV file first");
      return;
    }

    Papa.parse(csvFile, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const rows = Array.isArray(results.data) ? results.data : [];
        setCsvData(rows);
        toast.success("CSV data loaded successfully");
        console.log("CSV Parsed Data:", rows);
      },
      error: (error) => {
        toast.error("Failed to parse CSV");
        console.error("CSV Parse Error:", error);
      },
    });
  };

  const totals = useMemo(() => {
    const te = Number(summary?.total_expenses || 0);
    const tr = Number(summary?.total_revenue || 0);
    const np = Number(summary?.net_profit || 0);
    return { te, tr, np };
  }, [summary]);

  return (
    <div className="px-8 py-6 max-w-7xl mx-auto">
      <ToastContainer />

      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-white">Finance Dashboard</h1>
          <p className="text-sm text-slate-200 mt-1">
            Central finance view for dashboards and platform expenses.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            className={buttonGhost}
            onClick={() => {
              fetchSummary();
              fetchExpenses();
            }}
            disabled={loadingSummary || loadingExpenses}
          >
            {(loadingSummary || loadingExpenses) ? "Refreshing…" : "Refresh"}
          </button>
        </div>
      </div>

      {/* Summary */}
      <div className={cardClass}>
        <h2 className={cardTitleClass}>Summary</h2>
        <div className="space-y-1">
          <p className={labelClass}>
            Total Expenses: <span className={valueClass}>${totals.te.toFixed(2)}</span>
          </p>
          <p className={labelClass}>
            Total Revenue: <span className={valueClass}>${totals.tr.toFixed(2)}</span>
          </p>
          <p className={labelClass}>
            Net Profit: <span className={valueClass}>${totals.np.toFixed(2)}</span>
          </p>
        </div>
      </div>

      {/* Currency Converter */}
      <div className="mt-6">
        <CurrencyConverter />
      </div>

      {/* Tax Filing Status */}
      {taxStatus && (
        <div className={`${cardClass} mt-4`}>
          <h2 className={cardTitleClass}>Tax Filing Status</h2>
          <div className="space-y-1">
            <p className={labelClass}>
              Business Filing:{" "}
              <span className={valueClass}>{taxStatus.business_tax_filing_status || "-"}</span>
            </p>
            <p className={labelClass}>
              Personal Filing:{" "}
              <span className={valueClass}>{taxStatus.personal_tax_filing_status || "-"}</span>
            </p>
            <p className={labelClass}>
              Next Deadline:{" "}
              <span className={valueClass}>{taxStatus.next_deadline || "-"}</span>
            </p>
          </div>
        </div>
      )}

      {/* Tax Planning Suggestions */}
      {taxPlanning && (
        <div className={`${cardClass} mt-4`}>
          <h2 className={cardTitleClass}>Tax Planning Suggestions</h2>
          <ul className="list-disc pl-5 text-sm text-slate-700">
            {Array.isArray(taxPlanning.recommended_deductions) &&
              taxPlanning.recommended_deductions.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
          </ul>
          <p className="mt-3 text-sm text-slate-600">
            Potential Savings:{" "}
            <span className="font-semibold text-slate-900">
              {taxPlanning.savings_potential || "-"}
            </span>
          </p>
        </div>
      )}

      {/* CSV Upload Section */}
      <div className={`${cardClass} mt-4`}>
        <h2 className={cardTitleClass}>Upload CSV File</h2>
        <div className="flex flex-col md:flex-row md:items-center gap-3">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
            className={fileInputClass}
          />
          <button onClick={handleCSVUpload} className={buttonPrimary}>
            Upload & Preview
          </button>
        </div>
      </div>

      {/* CSV Preview Table */}
      {csvData.length > 0 && (
        <div className={`${cardClass} mt-4`} ref={tableRef}>
          <h3 className={cardTitleClass}>Preview CSV Data</h3>

          <div className="overflow-x-auto">
            <table className="min-w-full table-auto border border-slate-200 text-sm">
              <thead className="bg-slate-50">
                <tr>
                  {Object.keys(csvData[0] || {}).map((key) => (
                    <th key={key} className="border-b border-slate-200 px-4 py-2 text-left text-xs text-slate-600">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {csvData.map((row, idx) => (
                  <tr key={idx} className="text-slate-700">
                    {Object.values(row || {}).map((value, i) => (
                      <td key={i} className="px-4 py-2">
                        {String(value ?? "")}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="mt-2 text-xs text-slate-500">
            Rows: {csvData.length}
          </p>
        </div>
      )}
    </div>
  );
};

export default Finance;
