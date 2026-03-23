// frontend/src/pages/partner/PartnerRevenuePage.jsx

import React, { useEffect, useState } from "react";
import { getPartnerRevenue } from "../../services/partnerApi";

const PartnerRevenuePage = () => {
    const [rows, setRows] = useState([]);
    const [page, setPage] = useState(1);
    const [pageSize] = useState(50);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const load = async (targetPage = page) => {
        setLoading(true);
        setError(null);
        try {
            const res = await getPartnerRevenue(targetPage, pageSize);
            setRows(res.items || []);
            setTotal(res.total || 0);
            setPage(res.page || targetPage);
        } catch (err) {
            const msg =
                err?.response?.data?.detail ||
                err?.message ||
                "Failed to load revenue.";
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load(1);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const totalPages = Math.max(1, Math.ceil(total / pageSize));

    const summary = rows.reduce(
        (acc, r) => {
            acc.totalNet += Number(r.netProfitAmount || 0);
            acc.totalPartner += Number(r.partnerAmount || 0);
            acc.totalGts += Number(r.gtsAmount || 0);
            return acc;
        },
        { totalNet: 0, totalPartner: 0, totalGts: 0 }
    );

    return (
        <div className="space-y-4">
            <div>
                <h1 className="text-2xl font-semibold text-gray-900">
                    Revenue
                </h1>
                <p className="text-sm text-gray-500">
                    Revenue rows and partner shares from completed orders.
                </p>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-100 rounded-md px-3 py-2 text-sm text-red-700">
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white border rounded-lg shadow-sm p-4 text-sm">
                    <p className="text-gray-500 text-xs mb-1">
                        Net profit (this page)
                    </p>
                    <div className="text-xl font-mono text-gray-900">
                        {summary.totalNet.toLocaleString(undefined, {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                        })}
                    </div>
                </div>
                <div className="bg-white border rounded-lg shadow-sm p-4 text-sm">
                    <p className="text-gray-500 text-xs mb-1">
                        Partner share (this page)
                    </p>
                    <div className="text-xl font-mono text-emerald-700">
                        {summary.totalPartner.toLocaleString(undefined, {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                        })}
                    </div>
                </div>
                <div className="bg-white border rounded-lg shadow-sm p-4 text-sm">
                    <p className="text-gray-500 text-xs mb-1">
                        GTS share (this page)
                    </p>
                    <div className="text-xl font-mono text-blue-700">
                        {summary.totalGts.toLocaleString(undefined, {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                        })}
                    </div>
                </div>
            </div>

            <div className="bg-white border rounded-lg shadow-sm overflow-x-auto">
                <table className="min-w-full text-xs">
                    <thead className="bg-gray-50 border-b">
                        <tr>
                            <th className="px-3 py-2 text-left font-medium text-gray-500">
                                Order
                            </th>
                            <th className="px-3 py-2 text-left font-medium text-gray-500">
                                Service
                            </th>
                            <th className="px-3 py-2 text-right font-medium text-gray-500">
                                Net profit
                            </th>
                            <th className="px-3 py-2 text-right font-medium text-gray-500">
                                Partner share
                            </th>
                            <th className="px-3 py-2 text-right font-medium text-gray-500">
                                GTS share
                            </th>
                            <th className="px-3 py-2 text-right font-medium text-gray-500">
                                Share %
                            </th>
                            <th className="px-3 py-2 text-left font-medium text-gray-500">
                                Period
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading && (
                            <tr>
                                <td
                                    colSpan={7}
                                    className="px-3 py-4 text-center text-gray-500"
                                >
                                    Loading revenue rows...
                                </td>
                            </tr>
                        )}

                        {!loading && rows.length === 0 && (
                            <tr>
                                <td
                                    colSpan={7}
                                    className="px-3 py-4 text-center text-gray-500"
                                >
                                    No revenue rows found.
                                </td>
                            </tr>
                        )}

                        {!loading &&
                            rows.map((r) => (
                                <tr key={r.id} className="border-t hover:bg-gray-50">
                                    <td className="px-3 py-2">
                                        <div className="font-medium text-gray-900">
                                            {r.orderId || r.id}
                                        </div>
                                        <div className="text-[10px] text-gray-500">
                                            Client: {r.clientId || "-"}
                                        </div>
                                    </td>
                                    <td className="px-3 py-2 text-xs">
                                        {r.serviceType || "-"}
                                    </td>
                                    <td className="px-3 py-2 text-right font-mono">
                                        {Number(r.netProfitAmount || 0).toLocaleString(undefined, {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2,
                                        })}
                                    </td>
                                    <td className="px-3 py-2 text-right font-mono">
                                        {Number(r.partnerAmount || 0).toLocaleString(undefined, {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2,
                                        })}
                                    </td>
                                    <td className="px-3 py-2 text-right font-mono">
                                        {Number(r.gtsAmount || 0).toLocaleString(undefined, {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2,
                                        })}
                                    </td>
                                    <td className="px-3 py-2 text-right text-gray-700">
                                        {r.partnerSharePercent != null
                                            ? `${r.partnerSharePercent.toFixed(1)}%`
                                            : "-"}
                                    </td>
                                    <td className="px-3 py-2 text-xs text-gray-600">
                                        {r.periodYear && r.periodMonth
                                            ? `${r.periodYear}-${String(r.periodMonth).padStart(
                                                2,
                                                "0"
                                            )}`
                                            : "-"}
                                    </td>
                                </tr>
                            ))}
                    </tbody>
                </table>
            </div>

            {/* pagination */}
            <div className="flex items-center justify-between text-xs text-gray-600">
                <div>
                    Showing page {page} of {totalPages} ({total} rows)
                </div>
                <div className="space-x-1">
                    <button
                        onClick={() => load(Math.max(1, page - 1))}
                        disabled={page <= 1 || loading}
                        className="px-2 py-1 border rounded-md disabled:opacity-50"
                    >
                        Prev
                    </button>
                    <button
                        onClick={() => load(page + 1)}
                        disabled={page >= totalPages || loading}
                        className="px-2 py-1 border rounded-md disabled:opacity-50"
                    >
                        Next
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PartnerRevenuePage;
