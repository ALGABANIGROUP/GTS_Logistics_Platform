// frontend/src/pages/partner/PartnerPayoutsPage.jsx

import React, { useEffect, useState } from "react";
import {
    getPartnerPayouts,
    createPartnerPayoutRequest,
} from "../../services/partnerApi";

const PartnerPayoutsPage = () => {
    const [payouts, setPayouts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [requesting, setRequesting] = useState(false);
    const [error, setError] = useState(null);
    const [periodStart, setPeriodStart] = useState("");
    const [periodEnd, setPeriodEnd] = useState("");

    const load = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await getPartnerPayouts();
            setPayouts(res || []);
        } catch (err) {
            const msg =
                err?.response?.data?.detail ||
                err?.message ||
                "Failed to load payouts.";
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load();
    }, []);

    const handleRequestPayout = async (e) => {
        e.preventDefault();
        if (!periodStart || !periodEnd) {
            alert("Please select period start and end dates.");
            return;
        }

        try {
            setRequesting(true);
            await createPartnerPayoutRequest({
                periodStartDate: periodStart,
                periodEndDate: periodEnd,
            });
            await load();
            setPeriodStart("");
            setPeriodEnd("");
        } catch (err) {
            console.error("Failed to create payout request", err);
            alert(
                err?.response?.data?.detail ||
                err?.message ||
                "Failed to create payout request."
            );
        } finally {
            setRequesting(false);
        }
    };

    return (
        <div className="space-y-4">
            <div>
                <h1 className="text-2xl font-semibold text-gray-900">
                    Payouts
                </h1>
                <p className="text-sm text-gray-500">
                    View payout history and request a new payout for a period.
                </p>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-100 rounded-md px-3 py-2 text-sm text-red-700">
                    {error}
                </div>
            )}

            <form
                onSubmit={handleRequestPayout}
                className="bg-white border rounded-lg shadow-sm p-4 space-y-3 text-sm"
            >
                <h2 className="font-semibold text-gray-900">
                    Request payout
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
                    <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                            Period start
                        </label>
                        <input
                            type="date"
                            value={periodStart}
                            onChange={(e) => setPeriodStart(e.target.value)}
                            className="w-full border rounded-md px-2 py-1 text-sm"
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                            Period end
                        </label>
                        <input
                            type="date"
                            value={periodEnd}
                            onChange={(e) => setPeriodEnd(e.target.value)}
                            className="w-full border rounded-md px-2 py-1 text-sm"
                        />
                    </div>
                    <div>
                        <button
                            type="submit"
                            disabled={requesting}
                            className="px-3 py-2 rounded-md bg-emerald-600 text-white text-sm mt-5 w-full md:w-auto disabled:opacity-60"
                        >
                            {requesting ? "Submitting..." : "Request payout"}
                        </button>
                    </div>
                </div>
            </form>

            <div className="bg-white border rounded-lg shadow-sm p-4 text-sm">
                <h2 className="font-semibold text-gray-900 mb-2">
                    Payout history
                </h2>
                {loading ? (
                    <div className="text-gray-500 text-sm">
                        Loading payout history...
                    </div>
                ) : payouts.length === 0 ? (
                    <div className="text-gray-500 text-sm">
                        No payouts recorded yet.
                    </div>
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

export default PartnerPayoutsPage;
