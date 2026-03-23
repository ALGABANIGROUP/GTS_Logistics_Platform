// frontend/src/pages/EditDocument.jsx
import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axiosClient from "../api/axiosClient";

const EditDocument = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [doc, setDoc] = useState(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const loadDocument = async () => {
    setLoading(true);
    setMessage("");

    try {
      const res = await axiosClient.get(`/documents/${id}`);
      setDoc(res.data);
    } catch (err) {
      console.error(err);
      setMessage("Failed to load document.");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!doc) return;
    setSaving(true);
    setMessage("");

    try {
      const payload = {
        title: doc.title,
        file_url: doc.file_url,
        file_type: doc.file_type || null,
        expires_at: doc.expires_at
          ? new Date(doc.expires_at).toISOString()
          : null,
        notify_before_days: Number(doc.notify_before_days) || 7,
        owner_id: doc.owner_id || 1,
      };

      const res = await axiosClient.put(`/documents/${id}`, payload);
      if (res.status < 200 || res.status >= 300) {
        throw new Error("Save failed");
      }

      setMessage("✅ Document saved successfully.");
      setTimeout(() => navigate("/documents"), 700);
    } catch (err) {
      console.error(err);
      setMessage(`❌ ${String(err.message || err)}`);
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    loadDocument();
  }, [id]);

  if (loading) {
    return <div className="p-6 text-sm text-slate-600">Loading…</div>;
  }

  if (!doc) {
    return (
      <div className="p-6 text-sm text-rose-700">
        Failed to load document.
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-4">
      <h2 className="text-xl font-bold text-slate-900">
        Edit Document #{id}
      </h2>

      <div className="space-y-3 bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
        <div className="space-y-1">
          <label className="text-xs font-medium text-slate-700">Title</label>
          <input
            className="border border-slate-300 rounded-lg p-2 w-full text-sm focus:outline-none focus:ring-1 focus:ring-sky-500"
            value={doc.title || ""}
            onChange={(e) => setDoc({ ...doc, title: e.target.value })}
          />
        </div>

        <div className="space-y-1">
          <label className="text-xs font-medium text-slate-700">
            File URL
          </label>
          <input
            className="border border-slate-300 rounded-lg p-2 w-full text-sm focus:outline-none focus:ring-1 focus:ring-sky-500"
            value={doc.file_url || ""}
            onChange={(e) => setDoc({ ...doc, file_url: e.target.value })}
          />
        </div>

        <div className="flex gap-3">
          <div className="flex-1 space-y-1">
            <label className="text-xs font-medium text-slate-700">
              File type
            </label>
            <input
              className="border border-slate-300 rounded-lg p-2 w-full text-sm focus:outline-none focus:ring-1 focus:ring-sky-500"
              placeholder="pdf / jpg / png / etc."
              value={doc.file_type || ""}
              onChange={(e) =>
                setDoc({ ...doc, file_type: e.target.value })
              }
            />
          </div>

          <div className="flex-1 space-y-1">
            <label className="text-xs font-medium text-slate-700">
              Expiry date
            </label>
            <input
              className="border border-slate-300 rounded-lg p-2 w-full text-sm focus:outline-none focus:ring-1 focus:ring-sky-500"
              type="date"
              value={doc.expires_at ? String(doc.expires_at).slice(0, 10) : ""}
              onChange={(e) =>
                setDoc({ ...doc, expires_at: e.target.value })
              }
            />
          </div>

          <div className="w-32 space-y-1">
            <label className="text-xs font-medium text-slate-700">
              Notify (days)
            </label>
            <input
              className="border border-slate-300 rounded-lg p-2 w-full text-sm focus:outline-none focus:ring-1 focus:ring-sky-500"
              type="number"
              value={doc.notify_before_days || 7}
              onChange={(e) =>
                setDoc({
                  ...doc,
                  notify_before_days: e.target.value,
                })
              }
            />
          </div>
        </div>
      </div>

      <div className="flex gap-2">
        <button
          className="bg-sky-700 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-sky-800 disabled:opacity-60 transition"
          disabled={saving}
          onClick={handleSave}
        >
          {saving ? "Saving…" : "Save"}
        </button>
        <button
          className="px-4 py-2 rounded-lg border border-slate-300 text-sm hover:bg-slate-50"
          onClick={() => navigate(-1)}
        >
          Cancel
        </button>
      </div>

      {message && (
        <div className="text-xs text-slate-700 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
          {message}
        </div>
      )}
    </div>
  );
};

export default EditDocument;
