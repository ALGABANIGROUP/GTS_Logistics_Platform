// frontend/src/pages/partner/PartnerClientsPage.jsx

import React, { useEffect, useState } from "react";
import { getPartnerClients } from "../../services/partnerApi";

const PartnerClientsPage = () => {
    const [items, setItems] = useState([]);
    const [page, setPage] = useState(1);
    const [pageSize] = useState(20);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const load = async (targetPage = page) => {
        setLoading(true);
        setError(null);
        try {
            const res = await getPartnerClients(targetPage, pageSize);
            setItems(res.items || []);
            setTotal(res.total || 0);
            setPage(res.page || targetPage);
        } catch (err) {
            const msg =
                err?.response?.data?.detail ||
                err?.message ||
                "Failed to load partner clients.";
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
            <div>
                <h1 className="text-2xl font-semibold text-gray-900">
                    My Clients
                </h1>
                <p className="text-sm text-gray-500">
                    Clients associated with your partner account.
                </p>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-100 rounded-md px-3 py-2 text-sm text-red-700">
                    {error}
                </div>
            )}

            <div className="bg-white border rounded-lg shadow-sm overflow-hidden">
                <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 border-b">
                        <tr>
                            <th className="px-3 py-2 text-left font-medium text-gray-500">
                                Client
                            </th>
                            <th className="px-3 py-2 text-left font-medium text-gray-500">
                                Email
                            </th>
                            <th className="px-3 py-2 text-left font-medium text-gray-500">
                                Active
                            </th>
                            <th className="px-3 py-2 text-right font-medium text-gray-500">
                                Orders
                            </th>
                            <th className="px-3 py-2 text-right font-medium text-gray-500">
                                Revenue
                            </th>
                            <th className="px-3 py-2 text-left font-medium text-gray-500">
                                Since
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading && (
                            <tr>
                                <td
                                    colSpan={6}
                                    className="px-3 py-4 text-center text-gray-500"
                                >
                                    Loading clients...
                                </td>
                            </tr>
                        )}

                        {!loading && items.length === 0 && (
                            <tr>
                                <td
                                    colSpan={6}
                                    className="px-3 py-4 text-center text-gray-500"
                                >
                                    No clients found.
                                </td>
                            </tr>
                        )}

                        {!loading &&
                            items.map((c) => (
                                <tr key={c.id} className="border-t hover:bg-gray-50">
                                    <td className="px-3 py-2">
                                        <div className="font-medium text-gray-900">
                                            {c.name}
                                        </div>
                                        <div className="text-xs text-gray-500">
                                            {c.clientId}
                                        </div>
                                    </td>
                                    <td className="px-3 py-2 text-xs text-gray-700">
                                        {c.email}
                                    </td>
                                    <td className="px-3 py-2 text-xs">
                                        {c.isActive ? (
                                            <span className="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">
                                                Active
                                            </span>
                                        ) : (
                                            <span className="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                                                Inactive
                                            </span>
                                        )}
                                    </td>
                                    <td className="px-3 py-2 text-right text-xs font-mono">
                                        {c.totalOrders ?? 0}
                                    </td>
                                    <td className="px-3 py-2 text-right text-xs font-mono">
                                        {Number(c.totalRevenue || 0).toLocaleString(undefined, {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2,
                                        })}
                                    </td>
                                    <td className="px-3 py-2 text-xs text-gray-600">
                                        {c.relationshipStartedAt
                                            ? c.relationshipStartedAt.slice(0, 10)
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
                    Showing page {page} of {totalPages} ({total} clients)
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

export default PartnerClientsPage;
