import React, { useEffect, useMemo, useState } from "react";

const API_BASE = typeof window !== "undefined" ? "" : "http://localhost:8000";

export default function DocumentIntelligenceDashboard() {
  const [summary, setSummary] = useState({
    expired: 0,
    expiring_soon: 0,
    valid: 0,
  });
  const [expiring, setExpiring] = useState([]);
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const safeJson = async (res) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : null;
    } catch {
      return null;
    }
  };

  const loadData = async () => {
    setLoading(true);
    setError("");
    setMsg("");

    try {
      const [sRes, eRes] = await Promise.all([
        fetch(`${API_BASE}/ai/documents/status`),
        fetch(`${API_BASE}/ai/documents/expiring`),
      ]);

      if (!sRes.ok) {
        const jd = await safeJson(sRes);
        throw new Error(jd?.detail || jd?.message || "Failed to load status.");
      }
      if (!eRes.ok) {
        const jd = await safeJson(eRes);
        throw new Error(jd?.detail || jd?.message || "Failed to load expiring list.");
      }

      const s = await safeJson(sRes);
      const e = await safeJson(eRes);

      setSummary({
        expired: Number(s?.expired || 0),
        expiring_soon: Number(s?.expiring_soon || 0),
        valid: Number(s?.valid || 0),
      });

      setExpiring(Array.isArray(e) ? e : []);
    } catch (err) {
      setSummary({ expired: 0, expiring_soon: 0, valid: 0 });
      setExpiring([]);
      setError(String(err?.message || err || "Failed to load data."));
    } finally {
      setLoading(false);
    }
  };

  const notifyNow = async () => {
    setMsg("");
    setError("");

    try {
      const r = await fetch(`${API_BASE}/documents/notify-expiring/`, {
        method: "POST",
      });

      const jd = await safeJson(r);

      if (!r.ok) {
        throw new Error(jd?.detail || jd?.message || "Failed to trigger notification.");
      }

      setMsg(jd?.message || "Notification triggered.");
    } catch (err) {
      setError(String(err?.message || err || "Failed to trigger notification."));
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const counts = useMemo(
    () => ({
      expired: Number(summary?.expired || 0),
      expiring_soon: Number(summary?.expiring_soon || 0),
      valid: Number(summary?.valid || 0),
    }),
    [summary]
  );

  return (
    <div className="px-8 py-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-white">
            Documents Intelligence
          </h1>
          <p className="text-sm text-slate-200 mt-1 max-w-2xl">
            Status overview and expiring list driven by AI endpoints.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={loadData}
            disabled={loading}
            className="px-3 py-2 rounded-lg text-xs font-medium border border-slate-600 text-slate-100 hover:bg-white/10 disabled:opacity-60"
          >
            {loading ? "Refreshing…" : "Refresh"}
          </button>
          <button
            type="button"
            onClick={notifyNow}
            className="px-3 py-2 rounded-lg text-xs font-medium bg-sky-600 text-white hover:bg-sky-700 shadow-sm"
          >
            Notify Now
          </button>
        </div>
      </div>

      {/* Summary tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
        <Tile
          title="Expired"
          value={counts.expired}
          loading={loading}
          tone="danger"
        />
        <Tile
          title="Expiring (30d)"
          value={counts.expiring_soon}
          loading={loading}
          tone="warning"
        />
        <Tile
          title="Valid"
          value={counts.valid}
          loading={loading}
          tone="success"
        />
      </div>

      {/* Error / Message */}
      {error && (
        <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      )}

      {msg && !error && (
        <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          {msg}
        </div>
      )}

      {/* Expiring list */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between gap-3 px-5 py-4 border-b border-slate-200">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">
              Expiring / Expired
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Documents returned by the expiring endpoint.
            </p>
          </div>

          <span className="text-[11px] text-slate-500">
            Total: {Array.isArray(expiring) ? expiring.length : 0}
          </span>
        </div>

        <div className="p-5">
          {loading ? (
            <div className="text-sm text-slate-500">Loading…</div>
          ) : expiring.length === 0 ? (
            <div className="text-sm text-slate-500">
              No expiring documents.
            </div>
          ) : (
            <ul className="space-y-3">
              {expiring.map((d) => {
                const fileName = d?.file_url
                  ? String(d.file_url).split("/").pop()
                  : "";
                const status = String(d?.status || "").toLowerCase();
                const pill = statusPill(status);

                return (
                  <li
                    key={d.id}
                    className="border border-slate-200 rounded-xl p-4 hover:bg-slate-50 transition"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-slate-700">
                            #{d.id}
                          </span>
                          <span className="text-sm font-semibold text-slate-900">
                            {d.title || "Untitled document"}
                          </span>
                          {pill}
                        </div>

                        {fileName ? (
                          <div className="text-xs text-slate-500 mt-1">
                            File:{" "}
                            <span className="font-mono text-[11px] text-slate-600">
                              {fileName}
                            </span>
                          </div>
                        ) : null}

                        <div className="text-xs text-slate-600 mt-2">
                          {d.expires_at ? (
                            <>
                              Expires:{" "}
                              <span className="font-mono text-[11px]">
                                {String(d.expires_at).slice(0, 10)}
                              </span>
                            </>
                          ) : (
                            <span className="text-slate-500">No expiry date</span>
                          )}
                        </div>
                      </div>

                      {d.file_url ? (
                        <a
                          href={d.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs font-medium text-sky-700 hover:text-sky-800 underline"
                        >
                          Open
                        </a>
                      ) : null}
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

function Tile({ title, value, loading, tone }) {
  const meta = toneMeta(tone);

  return (
    <div className={`rounded-xl border shadow-sm px-4 py-3 ${meta.box}`}>
      <p className={`text-xs mb-1 ${meta.label}`}>{title}</p>
      <p className={`text-2xl font-semibold ${meta.value}`}>
        {loading ? "…" : value}
      </p>
    </div>
  );
}

function toneMeta(tone) {
  if (tone === "danger") {
    return {
      box: "bg-rose-50 border-rose-100",
      label: "text-rose-700",
      value: "text-rose-800",
    };
  }
  if (tone === "warning") {
    return {
      box: "bg-amber-50 border-amber-100",
      label: "text-amber-700",
      value: "text-amber-800",
    };
  }
  return {
    box: "bg-emerald-50 border-emerald-100",
    label: "text-emerald-700",
    value: "text-emerald-800",
  };
}

function statusPill(status) {
  if (status.includes("expired")) {
    return (
      <span className="px-2 py-0.5 rounded-full text-[11px] bg-rose-100 text-rose-700">
        Expired
      </span>
    );
  }
  if (status.includes("near") || status.includes("soon") || status.includes("expiring")) {
    return (
      <span className="px-2 py-0.5 rounded-full text-[11px] bg-amber-100 text-amber-700">
        Expiring
      </span>
    );
  }
  if (status.includes("valid")) {
    return (
      <span className="px-2 py-0.5 rounded-full text-[11px] bg-emerald-100 text-emerald-700">
        Valid
      </span>
    );
  }
  if (!status) {
    return (
      <span className="px-2 py-0.5 rounded-full text-[11px] bg-slate-100 text-slate-600">
        Unknown
      </span>
    );
  }
  return (
    <span className="px-2 py-0.5 rounded-full text-[11px] bg-slate-100 text-slate-600">
      {status}
    </span>
  );
}
