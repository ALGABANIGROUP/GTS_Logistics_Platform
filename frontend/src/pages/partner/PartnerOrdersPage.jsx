// frontend/src/pages/partner/PartnerOrdersPage.jsx

import React, { useEffect, useState } from "react";
import { getPartnerOrders } from "../../services/partnerApi";

const PartnerOrdersPage = () => {
    const [items, setItems] = useState([]);
    const [statusFilter, setStatusFilter] = useState("");
    const [page, setPage] = useState(1);
    const [pageSize] = useState(20);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const load = async (targetPage = page) => {
        setLoading(true);
        setError(null);
        try {
            const res = await getPartnerOrders({
                page: targetPage,
                pageSize,
                status: statusFilter || undefined,
            });
            setItems(res.items || []);
            setTotal(res.total || 0);
            setPage(res.page || targetPage);
        } catch (err) {
            const msg =
                err?.response?.data?.detail ||
                err?.message ||
                "Failed to load orders.";
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

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between gap-3">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900">
                        My Orders
                    </h1>
                    <p className="text-sm text-gray-500">
                        Orders generated through your partner channel.
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    <select
                        value={statusFilter}
                        onChange={(e) => {
                            setStatusFilter(e.target.value);
                            load(1);
                        }}
                        className="border rounded-md px-2 py-1 text-sm"
                    >
                        <option value="">All statuses</option>
                        <option value="pending">Pending</option>
                        <option value="in_progress">In progress</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                    </select>

                    <button
                        onClick={() => load(1)}
                        className="px-3 py-1.5 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-700"
                    >
                        Refresh
                    </button>
                </div>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-100 rounded-md px-3 py-2 text-sm text-red-700">
                    {error}
                </div>
            )}

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
                                Partner amount
                            </th>
                            <th className="px-3 py-2 text-right font-medium text-gray-500">
                                GTS amount
                            </th>
                            <th className="px-3 py-2 text-left font-medium text-gray-500">
                                Status
                            </th>
                            <th className="px-3 py-2 text-left font-medium text-gray-500">
                                Date
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
                                    Loading orders...
                                </td>
                            </tr>
                        )}

                        {!loading && items.length === 0 && (
                            <tr>
                                <td
                                    colSpan={7}
                                    className="px-3 py-4 text-center text-gray-500"
                                >
                                    No orders found.
                                </td>
                            </tr>
                        )}

                        {!loading &&
                            items.map((o) => (
                                <tr key={o.id} className="border-t hover:bg-gray-50">
                                    <td className="px-3 py-2">
                                        <div className="font-medium text-gray-900">
                                            {o.orderId || o.id}
                                        </div>
                                        <div className="text-[10px] text-gray-500">
                                            Client: {o.clientId || "-"}
                                        </div>
                                    </td>
                                    <td className="px-3 py-2 text-xs">
                                        {o.serviceType || "-"}
                                    </td>
                                    <td className="px-3 py-2 text-right font-mono">
                                        {Number(o.netProfitAmount || 0).toLocaleString(undefined, {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2,
                                        })}
                                    </td>
                                    <td className="px-3 py-2 text-right font-mono">
                                        {Number(o.partnerAmount || 0).toLocaleString(undefined, {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2,
                                        })}
                                    </td>
                                    <td className="px-3 py-2 text-right font-mono">
                                        {Number(o.gtsAmount || 0).toLocaleString(undefined, {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2,
                                        })}
                                    </td>
                                    <td className="px-3 py-2 text-xs capitalize">
                                        {o.status || "-"}
                                    </td>
                                    <td className="px-3 py-2 text-xs text-gray-600">
                                        {o.createdAt ? o.createdAt.slice(0, 10) : "-"}
                                    </td>
                                </tr>
                            ))}
                    </tbody>
                </table>
            </div>

            {/* pagination */}
            <div className="flex items-center justify-between text-xs text-gray-600">
                <div>
                    Showing page {page} of {totalPages} ({total} orders)
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

export default PartnerOrdersPage;
