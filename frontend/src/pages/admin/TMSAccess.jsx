import React, { useEffect, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";
import RequireAuth from "../../components/RequireAuth.jsx";
import { formatTierLabel } from "../../utils/tierUtils";

const LIST_ENDPOINT = "/api/v1/admin/tms-requests/list";
const STATS_ENDPOINT = "/api/v1/admin/tms-requests/stats";

export default function TMSAccess() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <TMSAccessContent />
    </RequireAuth>
  );
}

function TMSAccessContent() {
  const [items, setItems] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [rejectTarget, setRejectTarget] = useState(null);
  const [rejectReason, setRejectReason] = useState("Insufficient verification data");

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const [listRes, statsRes] = await Promise.all([
        axiosClient.get(LIST_ENDPOINT, {
          params: {
            limit: 100,
            ...(statusFilter ? { status_filter: statusFilter } : {}),
          },
        }),
        axiosClient.get(STATS_ENDPOINT),
      ]);
      setItems(listRes.data?.requests || []);
      setStats(statsRes.data?.stats || null);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to load TMS requests");
      setItems([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [statusFilter]);

  const approve = async (requestId) => {
    setActionLoading(requestId);
    setError("");
    try {
      await axiosClient.post(`/api/v1/admin/tms-requests/${requestId}/approve`, { notes: "Approved from admin panel" });
      setNotice("TMS request approved successfully.");
      await fetchData();
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Approval failed");
    } finally {
      setActionLoading("");
    }
  };

  const reject = async (requestId, reason) => {
    if (!reason?.trim()) return;
    setActionLoading(requestId);
    setError("");
    try {
      await axiosClient.post(`/api/v1/admin/tms-requests/${requestId}/reject`, { rejection_reason: reason });
      setNotice("TMS request rejected successfully.");
      await fetchData();
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Rejection failed");
    } finally {
      setActionLoading("");
    }
  };

  const statCards = useMemo(() => {
    const current = stats || {};
    return [
      { label: "Pending", value: current.pending ?? 0 },
      { label: "Approved", value: current.approved ?? 0 },
      { label: "Rejected", value: current.rejected ?? 0 },
      { label: "Total", value: current.total ?? 0 },
    ];
  }, [stats]);

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-100">TMS Access Requests</h1>
          <p className="text-sm text-slate-400">Review and decide pending TMS registration requests.</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
            className="rounded border border-white/15 bg-slate-900/60 px-3 py-2 text-sm text-slate-100"
          >
            <option value="">All</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          <button
            onClick={fetchData}
            className="rounded bg-blue-600 px-3 py-2 text-sm text-white hover:bg-blue-500"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {statCards.map((card) => (
          <div key={card.label} className="rounded-xl border border-white/15 bg-white/5 p-4">
            <div className="text-xs uppercase tracking-wide text-slate-400">{card.label}</div>
            <div className="mt-2 text-2xl font-semibold text-slate-100">{card.value}</div>
          </div>
        ))}
      </div>

      {error ? (
        <div className="rounded border border-rose-400/40 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">
          {error}
        </div>
      ) : null}

      {notice ? (
        <div className="rounded border border-emerald-400/40 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-200 flex items-center justify-between gap-3">
          <span>{notice}</span>
          <button type="button" onClick={() => setNotice("")} className="text-emerald-100/80 hover:text-emerald-100">
            Dismiss
          </button>
        </div>
      ) : null}

      {loading ? (
        <div className="text-sm text-slate-400">Loading...</div>
      ) : items.length === 0 ? (
        <div className="text-sm text-slate-400">No TMS requests found for the current filter.</div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.id}
              className="flex flex-col gap-3 rounded-xl border border-white/15 bg-white/5 p-4 md:flex-row md:items-center md:justify-between"
            >
              <div className="text-sm">
                <div className="font-medium text-white">{item.company_name}</div>
                <div className="text-slate-300">
                  {item.contact_name} | {item.contact_email} | {item.country_code || "-"} | {formatTierLabel(item.requested_plan)}
                </div>
                <div className="text-xs text-slate-400">
                  {item.industry_type || "-"} | Submitted {item.created_at || "unknown"}
                </div>
                {item.rejection_reason ? (
                  <div className="mt-1 text-xs text-rose-200">Reason: {item.rejection_reason}</div>
                ) : null}
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`inline-flex rounded px-2 py-1 text-[11px] uppercase tracking-wide ${item.status === "approved"
                      ? "border border-emerald-400/30 bg-emerald-500/15 text-emerald-300"
                      : item.status === "rejected"
                        ? "border border-rose-400/30 bg-rose-500/15 text-rose-300"
                        : "border border-amber-400/30 bg-amber-500/15 text-amber-300"
                    }`}
                >
                  {item.status}
                </span>
                {item.status === "pending" ? (
                  <>
                    <button
                      onClick={() => approve(item.id)}
                      disabled={actionLoading === item.id}
                      className="rounded bg-emerald-600 px-3 py-1.5 text-xs text-white hover:bg-emerald-500 disabled:bg-slate-600"
                    >
                      {actionLoading === item.id ? "Working..." : "Approve"}
                    </button>
                    <button
                      onClick={() => {
                        setRejectTarget(item);
                        setRejectReason("Insufficient verification data");
                      }}
                      disabled={actionLoading === item.id}
                      className="rounded bg-rose-600 px-3 py-1.5 text-xs text-white hover:bg-rose-500 disabled:bg-slate-600"
                    >
                      Reject
                    </button>
                  </>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      )}

      {rejectTarget ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-xl border border-white/15 bg-slate-900 p-4">
            <h2 className="text-base font-semibold text-white">Reject TMS Request</h2>
            <p className="mt-1 text-sm text-slate-400">
              Provide a rejection reason for {rejectTarget.company_name || "this request"}.
            </p>
            <textarea
              value={rejectReason}
              onChange={(event) => setRejectReason(event.target.value)}
              rows={4}
              className="mt-3 w-full rounded border border-white/15 bg-white/5 px-3 py-2 text-sm text-white"
            />
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setRejectTarget(null)}
                className="rounded border border-white/15 px-3 py-1.5 text-sm text-slate-200"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={async () => {
                  const current = rejectTarget;
                  setRejectTarget(null);
                  await reject(current.id, rejectReason);
                }}
                className="rounded bg-rose-600 px-3 py-1.5 text-sm text-white hover:bg-rose-500"
              >
                Confirm Reject
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
