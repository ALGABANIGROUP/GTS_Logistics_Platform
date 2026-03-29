import React, { useState, useRef } from "react";
import InvoiceAIUpload from "../components/InvoiceAIUpload";
import { API_BASE_URL } from "../config/env";

const API_ROOT = String(API_BASE_URL || "").replace(/\/+$/, "");

const getToken = () =>
  (typeof window !== "undefined" && (localStorage.getItem("gts_token") || localStorage.getItem("access_token"))) || "";

const authHeaders = () => {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
};

export default function DocumentUpload() {
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);
  const [expiresAt, setExpiresAt] = useState("");
  const [notifyDays, setNotifyDays] = useState(7);
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState("");
  const fileInputRef = useRef(null);

  const inputBase =
    "w-full p-2 border border-slate-300 rounded-lg bg-white text-slate-900 " +
    "placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-sky-500";

  const labelBase = "block text-sm mb-1 text-slate-200";

  const fileInputClass =
    "w-full p-2 border border-slate-300 rounded-lg bg-white text-slate-900 " +
    "file:text-slate-700 file:bg-slate-100 file:border-0 file:px-3 file:py-1 " +
    "file:rounded-md file:mr-3 cursor-pointer " +
    "focus:outline-none focus:ring-1 focus:ring-sky-500";

  const uploadFile = async () => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(`${API_ROOT}/documents/upload-file/`, {
      method: "POST",
      headers: { ...authHeaders() },
      body: fd,
    });
    const jd = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(jd?.detail || "Upload failed");
    return jd;
  };

  const createDoc = async (fileUrl, fileType) => {
    // Get owner_id from current user if available
    let owner_id;
    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      owner_id = user?.id;
    } catch { owner_id = undefined; }
    const payload = {
      title,
      file_url: fileUrl,
      file_type: fileType || undefined,
      expires_at: expiresAt ? new Date(expiresAt).toISOString() : undefined,
      notify_before_days: Number(notifyDays) || 7,
      ...(owner_id ? { owner_id } : {}),
    };
    const res = await fetch(`${API_ROOT}/documents/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify(payload),
    });
    const jd = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(jd?.detail || "Create failed");
    return jd;
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMsg("");

    try {
      if (!file) throw new Error("Please choose a file");
      const ext = file.name.split(".").pop()?.toLowerCase();
      const { file_url } = await uploadFile();
      const created = await createDoc(file_url, ext);
      setMsg(`✅ Uploaded & created: #${created.id}`);
      setTitle("");
      setFile(null);
      setExpiresAt("");
      setNotifyDays(7);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) {
      setMsg(`❌ ${String(err.message || err)}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h2 className="text-xl font-bold mb-4 text-white">Upload Document</h2>

      <form className="space-y-3" onSubmit={onSubmit}>
        <input
          className={inputBase}
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />

        <input
          ref={fileInputRef}
          className={fileInputClass}
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          required
        />

        <div className="flex gap-3">
          <div className="flex-1">
            <label className={labelBase}>Expiry Date</label>
            <input
              className={inputBase}
              type="date"
              value={expiresAt}
              onChange={(e) => setExpiresAt(e.target.value)}
            />
          </div>

          <div className="w-40">
            <label className={labelBase}>Notify (days)</label>
            <input
              className={inputBase}
              type="number"
              min="0"
              value={notifyDays}
              onChange={(e) => setNotifyDays(e.target.value)}
            />
          </div>
        </div>

        <button
          disabled={submitting}
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-60"
        >
          {submitting ? "Uploading..." : "Upload & Create"}
        </button>
      </form>

      {msg && <p className="mt-3 text-sm text-white">{msg}</p>}

      <div className="my-8">
        <InvoiceAIUpload />
      </div>
    </div>
  );
}
