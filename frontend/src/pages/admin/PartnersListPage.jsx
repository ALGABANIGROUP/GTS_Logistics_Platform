// frontend/src/pages/admin/PartnerDetailsPage.jsx

import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
    getPartnerById,
    getPartnerRevenueSummaryAdmin,
    getPartnerPayoutsAdmin,
} from "../../services/partnerApi";
import { format } from "date-fns";

const PartnerDetailsPage = () => {
    const { id } = useParams();
    const [partner, setPartner] = useState(null);
    const [revenueSummary, setRevenueSummary] = useState(null);
    const [payouts, setPayouts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let isMounted = true;

        const load = async () => {
            setLoading(true);
            setError(null);
            try {
                const [p, rev, po] = await Promise.all([
                    getPartnerById(id),
                    getPartnerRevenueSummaryAdmin(id),
                    getPartnerPayoutsAdmin(id),
                ]);

                if (!isMounted) return;
                setPartner(p);
                setRevenueSummary(rev);
                setPayouts(po || []);
            } catch (err) {
                if (!isMounted) return;
                const msg =
                    err?.response?.data?.detail ||
                    err?.message ||
                    "Failed to load partner details.";
                setError(msg);
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        };

        if (id) {
            load();
        }

        return () => {
            isMounted = false;
        };
    }, [id]);

    if (loading) {
        return (
            <div className="p-4 text-sm text-gray-600">
                Loading partner details...
            </div>
        );
    }

    if (error) {
        return (
            <div className="space-y-3">
                <div className="bg-red-50 border border-red-100 rounded-md px-3 py-2 text-sm text-red-700">
                    {error}
                </div>
                <Link
                    to="/admin/partners"
                    className="inline-flex items-center px-3 py-1.5 text-xs rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50"
                >
                    Back to partners
                </Link>
            </div>
        );
    }

    if (!partner) {
        return (
            <div className="space-y-3">
                <div className="p-4 text-sm text-gray-600">
                    Partner record is unavailable.
                </div>
                <Link
                    to="/admin/partners"
                    className="inline-flex items-center px-3 py-1.5 text-xs rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50"
                >
                    Back to partners
                </Link>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between gap-3">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900">
                        {partner.name}
                    </h1>
                    <p className="text-sm text-gray-500">
                        Code: {partner.code} · Type: {partner.partnerType} · Status:{" "}
                        <span className="font-medium">{partner.status}</span>
                    </p>
                </div>
                <Link
                    to="/admin/partners"
                    className="inline-flex items-center px-3 py-1.5 text-xs rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50"
                >
                    Back to partners
                </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white border rounded-lg shadow-sm p-4 text-sm">
                    <h2 className="font-semibold text-gray-900 mb-2">
                        Contact
                    </h2>
                    <p className="text-gray-700">{partner.email}</p>
                    {partner.phone && (
                        <p className="text-gray-700 mt-1">{partner.phone}</p>
                    )}
                    {partner.addressText && (
                        <p className="text-gray-500 text-xs mt-2 whitespace-pre-line">
                            {partner.addressText}
                        </p>
                    )}
                </div>

                <div className="bg-white border rounded-lg shadow-sm p-4 text-sm">
                    <h2 className="font-semibold text-gray-900 mb-2">
                        Revenue summary
                    </h2>
                    {revenueSummary ? (
                        <div className="space-y-1">
                            <p>
                                Total:{" "}
                                <span className="font-mono">
                                    {Number(
                                        revenueSummary.totalRevenue || 0
                                    ).toLocaleString(undefined, {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2,
                                    })}
                                </span>
                            </p>
                            <p>
                                Pending:{" "}
                                <span className="font-mono text-amber-700">
                                    {Number(
                                        revenueSummary.pendingRevenue || 0
                                    ).toLocaleString(undefined, {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2,
                                    })}
                                </span>
                            </p>
                            <p>
                                Paid:{" "}
                                <span className="font-mono text-emerald-700">
                                    {Number(
                                        revenueSummary.paidRevenue || 0
                                    ).toLocaleString(undefined, {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2,
                                    })}
                                </span>
                            </p>
                        </div>
                    ) : (
                        <p className="text-gray-500">No revenue summary.</p>
                    )}
                </div>

                <div className="bg-white border rounded-lg shadow-sm p-4 text-sm">
                    <h2 className="font-semibold text-gray-900 mb-2">
                        Meta
                    </h2>
                    <p>
                        Joined:{" "}
                        {partner.joinedAt
                            ? format(new Date(partner.joinedAt), "yyyy-MM-dd")
                            : "-"}
                    </p>
                    <p>
                        Last login:{" "}
                        {partner.lastLoginAt
                            ? format(new Date(partner.lastLoginAt), "yyyy-MM-dd HH:mm")
                            : "-"}
                    </p>
                </div>
            </div>

            <div className="bg-white border rounded-lg shadow-sm p-4 text-sm">
                <h2 className="font-semibold text-gray-900 mb-2">
                    Payouts
                </h2>
                {payouts.length === 0 ? (
                    <p className="text-gray-500">No payouts recorded yet.</p>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full text-xs">
                            <thead className="bg-gray-50 border-b">
                                <tr>
                                    <th className="px-2 py-1 text-left font-medium text-gray-500">
                                        Period
                                    </th>
                                    <th className="px-2 py-1 text-right font-medium text-gray-500">
                                        Net amount
                                    </th>
                                    <th className="px-2 py-1 text-left font-medium text-gray-500">
                                        Status
                                    </th>
                                    <th className="px-2 py-1 text-left font-medium text-gray-500">
                                        Requested
                                    </th>
                                    <th className="px-2 py-1 text-left font-medium text-gray-500">
                                        Paid
                                    </th>
                                    <th className="px-2 py-1 text-left font-medium text-gray-500">
                                        Reference
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {payouts.map((p) => (
                                    <tr key={p.id} className="border-t">
                                        <td className="px-2 py-1">
                                            {p.periodStartDate} – {p.periodEndDate}
                                        </td>
                                        <td className="px-2 py-1 text-right font-mono">
                                            {Number(p.netAmount || 0).toLocaleString(undefined, {
                                                minimumFractionDigits: 2,
                                                maximumFractionDigits: 2,
                                            })}
                                        </td>
                                        <td className="px-2 py-1 capitalize">{p.status}</td>
                                        <td className="px-2 py-1">
                                            {p.requestedAt || "-"}
                                        </td>
                                        <td className="px-2 py-1">
                                            {p.paidAt || "-"}
                                        </td>
                                        <td className="px-2 py-1">
                                            {p.paymentReference || "-"}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PartnerDetailsPage;
