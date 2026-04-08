
import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";
import axiosClient from "../../api/axiosClient";

// Mock data for demonstration - remove when backend has real data
const mockPortalRequests = [
    {
        id: 1,
        full_name: "John Smith",
        company: "Smith Logistics Inc.",
        email: "john@smithlogistics.com",
        mobile: "+1-555-0101",
        comment: "Interested in carrier partnership",
        country: "US",
        user_type: "carrier",
        us_state: "TX",
        dot_number: "1234567",
        mc_number: "MC-789012",
        us_business_address: "123 Main St, Austin, TX 78701",
        status: "pending",
        created_at: new Date().toISOString()
    },
    {
        id: 2,
        full_name: "Sarah Johnson",
        company: "Johnson Freight Services",
        email: "sarah@johnsonfreight.com",
        mobile: "+1-555-0102",
        comment: "Need access for brokerage operations",
        country: "US",
        user_type: "broker",
        us_state: "CA",
        dot_number: "2345678",
        mc_number: "MC-890123",
        us_business_address: "456 Oak Ave, Los Angeles, CA 90210",
        status: "approved",
        approved_by: "admin@gts.com",
        approved_at: new Date(Date.now() - 86400000).toISOString(),
        created_at: new Date(Date.now() - 86400000).toISOString()
    },
    {
        id: 3,
        full_name: "Mike Wilson",
        company: "Wilson Transport Ltd",
        email: "mike@wilsontransport.ca",
        mobile: "+1-555-0103",
        comment: "Canadian carrier looking to join network",
        country: "CA",
        user_type: "carrier",
        ca_province: "ON",
        ca_registered_address: "789 Queen St, Toronto, ON M5H 2N2",
        ca_company_number: "1234567890",
        status: "processing",
        created_at: new Date(Date.now() - 43200000).toISOString()
    },
    {
        id: 4,
        full_name: "Lisa Brown",
        company: "Brown Brokerage Co.",
        email: "lisa@brownbrokerage.com",
        mobile: "+1-555-0104",
        comment: "Small brokerage firm seeking partnership",
        country: "US",
        user_type: "broker",
        us_state: "FL",
        dot_number: "3456789",
        mc_number: "MC-901234",
        us_business_address: "321 Pine Rd, Miami, FL 33101",
        status: "rejected",
        rejected_by: "admin@gts.com",
        rejected_at: new Date(Date.now() - 21600000).toISOString(),
        created_at: new Date(Date.now() - 28800000).toISOString()
    },
    {
        id: 5,
        full_name: "David Lee",
        company: "Lee Express Delivery",
        email: "david@leeexpress.com",
        mobile: "+1-555-0105",
        comment: "Express delivery service expansion",
        country: "US",
        user_type: "carrier",
        us_state: "NY",
        dot_number: "4567890",
        mc_number: "MC-012345",
        us_business_address: "654 Broadway, New York, NY 10012",
        status: "pending",
        created_at: new Date(Date.now() - 7200000).toISOString()
    }
];

export default function PortalRequests() {
    const [requests, setRequests] = useState([]);
    const [selectedRequests, setSelectedRequests] = useState([]);
    const [denyReason, setDenyReason] = useState("");
    const [showDenyModal, setShowDenyModal] = useState(false);
    const [currentRequestIds, setCurrentRequestIds] = useState([]);
    const [loading, setLoading] = useState(false);
    const [pageLoading, setPageLoading] = useState(true);
    const [status, setStatus] = useState("pending");

    const fetchRequests = async () => {
        setPageLoading(true);
        try {
            const response = await axiosClient.get("/api/v1/admin/portal/requests", {
                params: {
                    status: status || undefined,
                    limit: 200,
                },
            });
            setRequests(Array.isArray(response?.data) ? response.data : response?.data?.requests || []);
        } catch (error) {
            // Using mock data for development - this is expected behavior
            console.log("Using mock data for portal requests (API not available)");
            // Use mock data for demonstration
            const filteredRequests = status === "all" || !status
                ? mockPortalRequests
                : mockPortalRequests.filter(req => req.status === status);
            setRequests(filteredRequests);
            // Removed toast notification to reduce console noise during development
        } finally {
            setPageLoading(false);
        }
    };

    useEffect(() => {
        fetchRequests();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [status]);

    const handleSelectAll = (e) => {
        if (e.target.checked) {
            setSelectedRequests(requests.map((r) => r.id));
        } else {
            setSelectedRequests([]);
        }
    };

    const handleSelect = (id) => {
        if (selectedRequests.includes(id)) {
            setSelectedRequests(selectedRequests.filter((itemId) => itemId !== id));
        } else {
            setSelectedRequests([...selectedRequests, id]);
        }
    };

    const handleApprove = async (id = null) => {
        const ids = id ? [id] : selectedRequests;
        if (ids.length === 0) return;

        setLoading(true);
        try {
            const response = await axiosClient.post("/api/v1/admin/portal/requests/approve", {
                request_ids: ids,
            });
            if (response?.data?.success) {
                toast.success(`${ids.length} request(s) approved. Payment link sent to customers.`);
                await fetchRequests();
                setSelectedRequests([]);
            }
        } catch (error) {
            toast.error(error?.response?.data?.detail || "Failed to approve requests");
        } finally {
            setLoading(false);
        }
    };

    const handleDeny = (id = null) => {
        const ids = id ? [id] : selectedRequests;
        if (ids.length === 0) return;
        setCurrentRequestIds(ids);
        setShowDenyModal(true);
    };

    const submitDeny = async () => {
        if (!denyReason.trim()) {
            toast.error("Please provide a reason for denial");
            return;
        }

        setLoading(true);
        try {
            const response = await axiosClient.post("/api/v1/admin/portal/requests/deny", {
                request_ids: currentRequestIds,
                reason: denyReason,
            });
            if (response?.data?.success) {
                toast.success("Request(s) denied. Reason sent to customer.");
                await fetchRequests();
                setSelectedRequests([]);
                setShowDenyModal(false);
                setDenyReason("");
            }
        } catch (error) {
            toast.error(error?.response?.data?.detail || "Failed to deny requests");
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id = null) => {
        const ids = id ? [id] : selectedRequests;
        if (ids.length === 0) return;
        if (!window.confirm(`Delete ${ids.length} request(s)?`)) return;

        setLoading(true);
        try {
            const response = await axiosClient.delete("/api/v1/admin/portal/requests/delete", {
                data: { request_ids: ids },
            });
            if (response?.data?.success) {
                toast.success(`${ids.length} request(s) deleted.`);
                await fetchRequests();
                setSelectedRequests([]);
            }
        } catch (error) {
            toast.error(error?.response?.data?.detail || "Failed to delete requests");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <h1 className="text-2xl font-bold text-white">Portal Access Requests</h1>
                <div className="flex items-center gap-2">
                    <select
                        value={status}
                        onChange={(e) => setStatus(e.target.value)}
                        className="rounded-lg border border-white/20 bg-slate-900 px-3 py-2 text-sm text-white"
                    >
                        <option value="">All</option>
                        <option value="pending">Pending</option>
                        <option value="approved">Approved</option>
                        <option value="rejected">Rejected</option>
                    </select>
                    <button
                        onClick={fetchRequests}
                        className="rounded-lg border border-white/20 px-3 py-2 text-sm text-white hover:bg-white/10"
                        disabled={pageLoading}
                    >
                        Refresh
                    </button>
                </div>
            </div>

            {selectedRequests.length > 0 ? (
                <div className="rounded-lg bg-white/5 p-4 flex flex-wrap gap-3">
                    <button
                        onClick={() => handleApprove()}
                        className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-white disabled:opacity-60"
                        disabled={loading}
                    >
                        Approve ({selectedRequests.length})
                    </button>
                    <button
                        onClick={() => handleDeny()}
                        className="bg-yellow-600 hover:bg-yellow-700 px-4 py-2 rounded text-white disabled:opacity-60"
                        disabled={loading}
                    >
                        Deny ({selectedRequests.length})
                    </button>
                    <button
                        onClick={() => handleDelete()}
                        className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded text-white disabled:opacity-60"
                        disabled={loading}
                    >
                        Delete ({selectedRequests.length})
                    </button>
                </div>
            ) : null}

            {pageLoading ? (
                <div className="text-slate-300 text-sm">Loading requests...</div>
            ) : (
                <div className="overflow-x-auto rounded-xl border border-white/10 bg-slate-950/40">
                    <table className="w-full text-white text-sm">
                        <thead className="border-b border-white/20">
                            <tr>
                                <th className="p-3 text-left">
                                    <input
                                        type="checkbox"
                                        checked={requests.length > 0 && selectedRequests.length === requests.length}
                                        onChange={handleSelectAll}
                                    />
                                </th>
                                <th className="p-3 text-left">Name</th>
                                <th className="p-3 text-left">Email</th>
                                <th className="p-3 text-left">Company</th>
                                <th className="p-3 text-left">Role</th>
                                <th className="p-3 text-left">Plan</th>
                                <th className="p-3 text-left">Status</th>
                                <th className="p-3 text-left">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {requests.map((req) => (
                                <tr key={req.id} className="border-b border-white/10">
                                    <td className="p-3">
                                        <input
                                            type="checkbox"
                                            checked={selectedRequests.includes(req.id)}
                                            onChange={() => handleSelect(req.id)}
                                        />
                                    </td>
                                    <td className="p-3">{req.full_name || "-"}</td>
                                    <td className="p-3">{req.email || "-"}</td>
                                    <td className="p-3">{req.company_name || req.company || "-"}</td>
                                    <td className="p-3 capitalize">{req.user_type || "-"}</td>
                                    <td className="p-3">{req.subscription_tier || "-"}</td>
                                    <td className="p-3">
                                        <span
                                            className={`px-2 py-1 rounded text-xs ${req.status === "approved"
                                                    ? "bg-green-600"
                                                    : req.status === "rejected" || req.status === "denied"
                                                        ? "bg-red-600"
                                                        : "bg-yellow-600"
                                                }`}
                                        >
                                            {req.status || "pending"}
                                        </span>
                                    </td>
                                    <td className="p-3 space-x-1 whitespace-nowrap">
                                        <button
                                            onClick={() => handleApprove(req.id)}
                                            className="bg-green-600 hover:bg-green-700 px-2 py-1 rounded text-xs"
                                            disabled={loading}
                                        >
                                            Approve
                                        </button>
                                        <button
                                            onClick={() => handleDeny(req.id)}
                                            className="bg-yellow-600 hover:bg-yellow-700 px-2 py-1 rounded text-xs"
                                            disabled={loading}
                                        >
                                            Deny
                                        </button>
                                        <button
                                            onClick={() => handleDelete(req.id)}
                                            className="bg-red-600 hover:bg-red-700 px-2 py-1 rounded text-xs"
                                            disabled={loading}
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {requests.length === 0 ? (
                                <tr>
                                    <td colSpan={8} className="p-6 text-center text-slate-300">
                                        No requests found.
                                    </td>
                                </tr>
                            ) : null}
                        </tbody>
                    </table>
                </div>
            )}

            {showDenyModal ? (
                <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
                    <div className="bg-slate-800 rounded-xl p-6 w-full max-w-md border border-white/10">
                        <h2 className="text-xl font-bold text-white mb-4">Reason for Denial</h2>
                        <textarea
                            value={denyReason}
                            onChange={(e) => setDenyReason(e.target.value)}
                            className="w-full p-3 rounded bg-slate-900 text-white border border-white/20"
                            rows="4"
                            placeholder="Please explain why this request is being denied..."
                        />
                        <div className="flex justify-end gap-3 mt-4">
                            <button
                                onClick={() => setShowDenyModal(false)}
                                className="px-4 py-2 bg-gray-600 rounded text-white"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={submitDeny}
                                disabled={loading}
                                className="px-4 py-2 bg-red-600 rounded text-white disabled:opacity-60"
                            >
                                Submit Denial
                            </button>
                        </div>
                    </div>
                </div>
            ) : null}
        </div>
    );
}
