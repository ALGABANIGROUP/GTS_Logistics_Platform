
import React, { useEffect, useState } from "react";
import axiosClient from "../../api/axiosClient";

export default function PortalRequests() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [status, setStatus] = useState("pending");
    const [limit, setLimit] = useState(100);
    const [denyTarget, setDenyTarget] = useState(null);
    const [denyCode, setDenyCode] = useState("");
    const [denyMessage, setDenyMessage] = useState("");
    const [deletingId, setDeletingId] = useState(null);
    const [confirmDeleteId, setConfirmDeleteId] = useState(null);
    const [notice, setNotice] = useState("");

    const deleteRequest = async (id) => {
        setDeletingId(id);
        setError("");
        try {
            await axiosClient.delete(`/api/v1/admin/portal/requests/${id}`);
            setNotice("Request deleted successfully.");
            await fetchItems();
        } catch (e) {
            setError(e?.response?.data?.detail || e.message || "Delete failed");
        } finally {
            setDeletingId(null);
            setConfirmDeleteId(null);
        }
    };

    const fetchItems = async () => {
        setLoading(true);
        setError("");
        try {
            const res = await axiosClient.get("/api/v1/admin/portal/requests", {
                params: { status, limit },
            });
            setItems(res.data || []);
        } catch (e) {
            setError(e?.response?.data?.detail || e.message || "Failed to load requests");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchItems();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [status, limit]);

    const approve = async (id) => {
        try {
            await axiosClient.post(`/api/v1/admin/portal/requests/${id}/approve`);
            setNotice("Request approved successfully.");
            await fetchItems();
        } catch (e) {
            setError(e?.response?.data?.detail || e.message || "Approve failed");
        }
    };

    const openDeny = (item) => {
        setDenyTarget(item);
        setDenyCode("");
        setDenyMessage("");
    };

    const closeDeny = () => {
        setDenyTarget(null);
        setDenyCode("");
        setDenyMessage("");
    };

    const confirmDeny = async () => {
        if (!denyTarget) return;
        try {
            await axiosClient.post(`/api/v1/admin/portal/requests/${denyTarget.id}/deny`, {
                rejection_code: denyCode || null,
                rejection_message: denyMessage || null,
            });
            setNotice("Request denied successfully.");
            closeDeny();
            await fetchItems();
        } catch (e) {
            setError(e?.response?.data?.detail || e.message || "Deny failed");
        }
    };


    // Bulk approve/deny handlers
    const handleBulkApprove = async () => {
        try {
            const ids = items.filter(item => item.status === "pending").map(item => item.id);
            await Promise.all(ids.map((id) => axiosClient.post(`/api/v1/admin/portal/requests/${id}/approve`)));
            setNotice(`${ids.length} request(s) approved successfully.`);
            fetchItems();
        } catch (e) {
            setError(e?.response?.data?.detail || e.message || "Bulk approve failed");
        }
    };

    const handleBulkDeny = async () => {
        try {
            const ids = items.filter(item => item.status === "pending").map(item => item.id);
            await Promise.all(ids.map((id) => axiosClient.post(`/api/v1/admin/portal/requests/${id}/deny`, {
                rejection_message: "Bulk rejection from admin panel",
            })));
            setNotice(`${ids.length} request(s) denied successfully.`);
            fetchItems();
        } catch (e) {
            setError(e?.response?.data?.detail || e.message || "Bulk deny failed");
        }
    };

    return (
        <div className="space-y-4">
            <div className="glass-panel rounded-xl p-4">
                <div className="flex items-center justify-between gap-4">
                    <h1 className="text-xl font-semibold text-slate-100">Portal Access Requests</h1>
                    <div className="flex flex-wrap items-center gap-2">
                        <select
                            value={status}
                            onChange={(e) => setStatus(e.target.value)}
                            className="glass-select text-sm"
                            title="Filter by status"
                        >
                            <option value="">All</option>
                            <option value="pending">Pending</option>
                            <option value="approved">Approved</option>
                            <option value="rejected">Rejected</option>
                        </select>
                        <select
                            value={limit}
                            onChange={(e) => setLimit(Number(e.target.value))}
                            className="glass-select text-sm"
                            title="Rows"
                        >
                            <option value={25}>25</option>
                            <option value={50}>50</option>
                            <option value={100}>100</option>
                        </select>
                        <button
                            onClick={fetchItems}
                            className="glass-btn-secondary glass-btn-sm"
                        >
                            Refresh
                        </button>
                        {/* Bulk actions for pending requests */}
                        {status === "pending" && (
                            <>
                                <button
                                    onClick={handleBulkApprove}
                                    className="glass-btn-success glass-btn-sm"
                                >
                                    Approve All
                                </button>
                                <button
                                    onClick={handleBulkDeny}
                                    className="glass-btn-danger glass-btn-sm"
                                >
                                    Deny All
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {error && (
                <div className="mb-3 rounded border border-rose-400/40 bg-rose-500/10 px-3 py-2 text-rose-200 text-sm">
                    {error}
                </div>
            )}

            {notice && (
                <div className="mb-3 rounded border border-emerald-400/40 bg-emerald-500/10 px-3 py-2 text-emerald-200 text-sm flex items-center justify-between gap-3">
                    <span>{notice}</span>
                    <button type="button" onClick={() => setNotice("")} className="text-emerald-100/80 hover:text-emerald-100">
                        Dismiss
                    </button>
                </div>
            )}

            {loading ? (
                <div className="text-sm text-slate-500">Loading...</div>
            ) : items.length === 0 ? (
                <div className="text-sm text-slate-500">No requests found.</div>
            ) : (
                <div className="space-y-3">
                    {items.map((x) => (
                        <div
                            key={x.id}
                            className="glass-panel rounded-xl p-3 flex items-center justify-between"
                        >
                            <div className="text-sm">
                                <div className="font-medium text-white">
                                    {x.full_name} — {x.company}
                                </div>
                                <div className="text-slate-300">
                                    {x.email} | {x.mobile} | {x.country} | {x.user_type}
                                </div>
                                <div className="text-slate-400 text-xs">
                                    Request ID: {x.request_id || x.id}
                                </div>
                                <div className="text-slate-400 text-xs">
                                    System: {x.system || "standard"} • Document: {x.document_name || "-"}
                                </div>
                                <div className="mt-1">
                                    <span
                                        className={
                                            "inline-flex items-center text-[11px] px-2 py-0.5 rounded " +
                                            (x.status === "approved"
                                                ? "bg-emerald-500/15 text-emerald-300 border border-emerald-400/30"
                                                : x.status === "rejected"
                                                    ? "bg-rose-500/15 text-rose-300 border border-rose-400/30"
                                                    : "bg-amber-500/15 text-amber-300 border border-amber-400/30")
                                        }
                                    >
                                        {x.status || "unknown"}
                                    </span>
                                </div>
                                {x.rejection_message ? (
                                    <div className="mt-2 text-xs text-rose-200">
                                        Reason: {x.rejection_message}
                                    </div>
                                ) : null}
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => approve(x.id)}
                                    className="glass-btn-success glass-btn-sm"
                                >
                                    Approve
                                </button>
                                <button
                                    onClick={() => openDeny(x)}
                                    className="glass-btn-danger glass-btn-sm"
                                >
                                    Deny
                                </button>
                                <button
                                    onClick={() => setConfirmDeleteId(x.id)}
                                    className="glass-btn-secondary glass-btn-sm"
                                    disabled={deletingId === x.id}
                                    title="Delete request permanently"
                                >
                                    {deletingId === x.id ? "Deleting..." : "Delete"}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {denyTarget ? (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
                    <div className="glass-modal w-full max-w-md p-4">
                        <div className="mb-3 text-sm font-semibold text-white">
                            Reject Request
                        </div>
                        <div className="space-y-3">
                            <div>
                                <label className="text-xs text-slate-300">Reason code</label>
                                <input
                                    value={denyCode}
                                    onChange={(e) => setDenyCode(e.target.value)}
                                    className="mt-1 w-full rounded-md border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white"
                                    placeholder="e.g. incomplete_docs"
                                />
                            </div>
                            <div>
                                <label className="text-xs text-slate-300">Reason message</label>
                                <textarea
                                    value={denyMessage}
                                    onChange={(e) => setDenyMessage(e.target.value)}
                                    className="mt-1 w-full rounded-md border border-white/10 bg-slate-900 px-3 py-2 text-sm text-white"
                                    rows={3}
                                    placeholder="Explain why the request was rejected"
                                />
                            </div>
                        </div>
                        <div className="mt-4 flex justify-end gap-2">
                            <button
                                onClick={closeDeny}
                                className="rounded-md border border-white/10 px-3 py-1.5 text-sm text-slate-200"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmDeny}
                                className="rounded-md bg-rose-600 px-3 py-1.5 text-sm text-white hover:bg-rose-500"
                            >
                                Confirm deny
                            </button>
                        </div>
                    </div>
                </div>
            ) : null}

            {confirmDeleteId ? (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
                    <div className="glass-modal w-full max-w-md p-4">
                        <div className="mb-2 text-sm font-semibold text-white">Delete Request</div>
                        <p className="text-sm text-slate-300">
                            This action cannot be undone. The request will be removed permanently.
                        </p>
                        <div className="mt-4 flex justify-end gap-2">
                            <button
                                onClick={() => setConfirmDeleteId(null)}
                                className="rounded-md border border-white/10 px-3 py-1.5 text-sm text-slate-200"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => deleteRequest(confirmDeleteId)}
                                className="rounded-md bg-rose-600 px-3 py-1.5 text-sm text-white hover:bg-rose-500"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            ) : null}
        </div>
    );
}
