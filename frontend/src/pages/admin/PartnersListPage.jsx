import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listPartners, updatePartnerStatus } from "../../services/partnerApi";

const STATUS_OPTIONS = ["all", "pending", "active", "suspended", "closed"];

function formatMoney(value) {
  return Number(value || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export default function PartnersListPage() {
  const [partners, setPartners] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  const [updatingId, setUpdatingId] = useState("");

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        setLoading(true);
        setError("");
        const response = await listPartners({
          page: 1,
          pageSize: 100,
          status: status === "all" ? undefined : status,
          search: search.trim() || undefined,
        });
        if (!active) return;
        setPartners(Array.isArray(response.items) ? response.items : []);
      } catch (err) {
        if (!active) return;
        setPartners([]);
        setError(
          err?.response?.data?.detail ||
            err?.message ||
            "Failed to load partners."
        );
      } finally {
        if (active) setLoading(false);
      }
    };

    load();
    return () => {
      active = false;
    };
  }, [search, status]);

  const handleStatusChange = async (partnerId, nextStatus) => {
    const previous = partners;
    setUpdatingId(partnerId);
    setPartners((current) =>
      current.map((partner) =>
        partner.id === partnerId ? { ...partner, status: nextStatus } : partner
      )
    );

    try {
      const updated = await updatePartnerStatus(partnerId, nextStatus);
      setPartners((current) =>
        current.map((partner) =>
          partner.id === partnerId ? updated : partner
        )
      );
    } catch (err) {
      setPartners(previous);
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Failed to update partner status."
      );
    } finally {
      setUpdatingId("");
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">
              Partners
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Review partner accounts, revenue, and payout readiness.
            </p>
          </div>
          <div className="text-sm text-slate-500">
            {loading ? "Loading..." : `${partners.length} partner records`}
          </div>
        </div>

        <div className="flex flex-col gap-3 md:flex-row">
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by name, code, or email"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none ring-0 focus:border-sky-500"
          />
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value)}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-sky-500"
          >
            {STATUS_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option === "all" ? "All statuses" : option}
              </option>
            ))}
          </select>
        </div>

        {error ? (
          <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
            {error}
          </div>
        ) : null}
      </div>

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        {loading ? (
          <div className="p-6 text-sm text-slate-500">Loading partner records...</div>
        ) : partners.length === 0 ? (
          <div className="p-6 text-sm text-slate-500">No partners matched the current filters.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-slate-500">
                <tr>
                  <th className="px-4 py-3 text-left font-medium">Partner</th>
                  <th className="px-4 py-3 text-left font-medium">Type</th>
                  <th className="px-4 py-3 text-left font-medium">Status</th>
                  <th className="px-4 py-3 text-right font-medium">Revenue</th>
                  <th className="px-4 py-3 text-left font-medium">Joined</th>
                  <th className="px-4 py-3 text-left font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {partners.map((partner) => (
                  <tr key={partner.id} className="border-t border-slate-100">
                    <td className="px-4 py-3">
                      <div className="font-medium text-slate-900">{partner.name}</div>
                      <div className="text-xs text-slate-500">{partner.code}</div>
                      <div className="text-xs text-slate-500">{partner.email}</div>
                    </td>
                    <td className="px-4 py-3 capitalize text-slate-700">
                      {partner.partnerType || "-"}
                    </td>
                    <td className="px-4 py-3">
                      <select
                        value={partner.status}
                        onChange={(event) =>
                          handleStatusChange(partner.id, event.target.value)
                        }
                        disabled={updatingId === partner.id}
                        className="rounded-md border border-slate-300 px-2 py-1 text-xs capitalize outline-none focus:border-sky-500"
                      >
                        {STATUS_OPTIONS.filter((option) => option !== "all").map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-slate-700">
                      {formatMoney(partner.revenueTotal)}
                    </td>
                    <td className="px-4 py-3 text-slate-700">
                      {partner.joinedAt ? String(partner.joinedAt).slice(0, 10) : "-"}
                    </td>
                    <td className="px-4 py-3">
                      <Link
                        to={`/admin/partners/${partner.id}`}
                        className="inline-flex rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                      >
                        View details
                      </Link>
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
}
