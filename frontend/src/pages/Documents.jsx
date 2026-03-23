// frontend/src/pages/Documents.jsx
import React, { useEffect, useMemo, useState } from "react";
import axiosClient from "../api/axiosClient";
import { Link } from "react-router-dom";

const getStatus = (expiresAt) => {
  if (!expiresAt) return "no-expiry";

  const now = new Date();
  const expiry = new Date(expiresAt);
  const diffDays = (expiry - now) / (1000 * 60 * 60 * 24);

  if (Number.isNaN(diffDays)) return "no-expiry";
  if (diffDays < 0) return "expired";
  if (diffDays <= 15) return "near";
  return "valid";
};

const statusMeta = {
  all: { label: "All", badgeClass: "bg-slate-200 text-slate-800" },
  valid: { label: "Valid", badgeClass: "bg-emerald-100 text-emerald-800" },
  near: { label: "Expiring Soon", badgeClass: "bg-amber-100 text-amber-800" },
  expired: { label: "Expired", badgeClass: "bg-rose-100 text-rose-800" },
  "no-expiry": {
    label: "No Expiry",
    badgeClass: "bg-sky-100 text-sky-800",
  },
};

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadDocuments = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await axiosClient.get("/documents/");
      let data = res.data;

      let list = [];
      if (Array.isArray(data)) {
        list = data;
      } else if (Array.isArray(data.items)) {
        list = data.items;
      } else {
        console.error("Unexpected documents payload:", data);
        throw new Error("Invalid documents payload from server.");
      }

      setDocuments(list);
    } catch (err) {
      console.error(err);
      setError("Failed to load documents. Please try again later.");
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const filteredDocuments = useMemo(() => {
    if (!Array.isArray(documents)) return [];
    if (filter === "all") return documents;

    return documents.filter((doc) => {
      const status = getStatus(doc.expires_at);
      return status === filter;
    });
  }, [documents, filter]);

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <span>Document Center</span>
            <span className="text-xl">📁</span>
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Smart tracking for all compliance and operational documents.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadDocuments}
            className="px-3 py-2 text-xs rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 transition"
          >
            Refresh
          </button>
          <Link
            to="/documents/upload"
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-sky-700 text-white hover:bg-sky-800 transition shadow-sm"
          >
            Upload New Document
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        {Object.entries(statusMeta).map(([key, meta]) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`px-3 py-1 rounded-full border text-xs transition ${filter === key
                ? "border-sky-600 bg-sky-50 text-sky-800"
                : "border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
              }`}
          >
            {meta.label}
          </button>
        ))}
        <span className="ml-auto text-[11px] text-slate-500">
          Total: {Array.isArray(documents) ? documents.length : 0}
        </span>
      </div>

      {/* Error / Loading / Empty */}
      {loading && (
        <div className="text-sm text-slate-600">Loading documents…</div>
      )}

      {error && (
        <div className="text-sm text-rose-700 bg-rose-50 border border-rose-200 rounded-lg px-3 py-2">
          {error}
        </div>
      )}

      {!loading && !error && filteredDocuments.length === 0 && (
        <div className="text-sm text-slate-500 border border-dashed border-slate-300 rounded-lg px-4 py-6 text-center">
          No documents found for this filter.
        </div>
      )}

      {/* List */}
      {!loading && !error && filteredDocuments.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredDocuments.map((doc) => {
            const status = getStatus(doc.expires_at);
            const meta = statusMeta[status] || statusMeta["no-expiry"];

            return (
              <div
                key={doc.id}
                className="border border-slate-200 rounded-xl bg-white shadow-sm p-4 flex flex-col gap-2"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="font-semibold text-slate-900 line-clamp-2">
                      {doc.title || "Untitled document"}
                    </div>
                    <div className="text-[11px] text-slate-500 mt-1">
                      {doc.file_type?.toUpperCase() || "Unknown type"}
                    </div>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${meta.badgeClass}`}
                  >
                    {meta.label}
                  </span>
                </div>

                {doc.expires_at && (
                  <div className="text-[11px] text-slate-600">
                    Expires on:{" "}
                    <span className="font-mono">
                      {new Date(doc.expires_at).toLocaleDateString()}
                    </span>
                  </div>
                )}

                <div className="mt-2 flex items-center gap-2 text-xs">
                  {doc.file_url && (
                    <a
                      href={doc.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-2 py-1 rounded-md border border-slate-300 hover:bg-slate-50 text-slate-700 transition"
                    >
                      Open
                    </a>
                  )}
                  <Link
                    to={`/documents/${doc.id}/edit`}
                    className="px-2 py-1 rounded-md border border-slate-300 hover:bg-slate-50 text-slate-700 transition"
                  >
                    Edit
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Documents;
