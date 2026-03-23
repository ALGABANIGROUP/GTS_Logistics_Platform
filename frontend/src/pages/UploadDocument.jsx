import React, { useState, useEffect, useMemo } from "react";
import axiosClient from "../api/axiosClient";

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

const getStatusColor = (status) => {
  switch (status) {
    case "expired":
      return "bg-rose-100 border-rose-200";
    case "near":
      return "bg-amber-100 border-amber-200";
    case "valid":
      return "bg-emerald-100 border-emerald-200";
    case "no-expiry":
    default:
      return "bg-slate-100 border-slate-200";
  }
};

const UploadDocument = () => {
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);
  const [expiresAt, setExpiresAt] = useState("");
  const [fileType, setFileType] = useState("");
  const [documents, setDocuments] = useState([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");

  const inputBase =
    "w-full p-2 border border-slate-300 rounded-lg bg-white text-slate-900 " +
    "placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-sky-500";

  const fileInputClass =
    "w-full p-2 border border-slate-300 rounded-lg bg-white text-slate-900 " +
    "file:text-slate-700 file:bg-slate-100 file:border-0 file:px-3 file:py-1 " +
    "file:rounded-md file:mr-3 cursor-pointer";

  const loadDocuments = async () => {
    setLoading(true);
    setMessage("");

    try {
      const res = await axiosClient.get("/documents/");
      const data = res.data;

      let list = [];
      if (Array.isArray(data)) {
        list = data;
      } else if (Array.isArray(data.items)) {
        list = data.items;
      } else {
        console.error("Unexpected documents payload:", data);
        throw new Error("Invalid documents payload");
      }

      setDocuments(list);
    } catch (err) {
      console.error(err);
      setMessage("Failed to load documents.");
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const getErrorMessage = (err, fallback = "Upload failed.") => {
    if (err.response?.data) {
      const d = err.response.data;
      return d.detail || d.error || d.message || fallback;
    }
    return err.message || fallback;
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    setMessage("");

    if (!file || !title) {
      setMessage("Title and file are required.");
      return;
    }

    setUploading(true);

    try {
      const fd = new FormData();
      fd.append("file", file);

      const uploadRes = await axiosClient.post("/documents/upload-file/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const fileUrl = uploadRes.data.file_url;
      if (!fileUrl) {
        throw new Error("Upload did not return file_url.");
      }

      const payload = {
        title,
        file_url: fileUrl,
        file_type: fileType || file.type,
        expires_at: expiresAt || null,
      };

      await axiosClient.post("/documents/", payload);

      setTitle("");
      setFile(null);
      setFileType("");
      setExpiresAt("");
      setMessage("Document uploaded successfully.");

      await loadDocuments();
    } catch (err) {
      console.error(err);
      setMessage(getErrorMessage(err, "Upload failed."));
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this document?")) {
      return;
    }

    try {
      await axiosClient.delete(`/documents/${id}`);
      await loadDocuments();
    } catch (err) {
      console.error(err);
      setMessage(getErrorMessage(err, "Failed to delete document."));
    }
  };

  const filteredDocuments = useMemo(() => {
    if (!Array.isArray(documents)) return [];
    if (filter === "all") return documents;

    return documents.filter((doc) => {
      const status = getStatus(doc.expires_at);
      return filter === status;
    });
  }, [documents, filter]);

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Upload New Document</h2>
        <p className="text-xs text-slate-200 mt-1">
          Quick upload and inline view for existing documents.
        </p>
      </div>

      <form
        onSubmit={handleUpload}
        className="space-y-4 bg-white border border-slate-200 rounded-xl p-4 shadow-sm"
      >
        <input
          type="text"
          placeholder="Document title"
          className={inputBase}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />

        <input
          type="date"
          className={inputBase}
          value={expiresAt}
          onChange={(e) => setExpiresAt(e.target.value)}
        />

        <input
          type="text"
          placeholder="File type (optional)"
          className={inputBase}
          value={fileType}
          onChange={(e) => setFileType(e.target.value)}
        />

        <input
          type="file"
          className={fileInputClass}
          onChange={(e) => setFile(e.target.files[0] || null)}
          required
        />

        <button
          type="submit"
          className="bg-sky-700 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-sky-800 disabled:opacity-60 transition"
          disabled={uploading}
        >
          {uploading ? "Uploading…" : "Upload Document"}
        </button>
      </form>

      {message && (
        <div className="text-xs text-slate-700 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
          {message}
        </div>
      )}

      <hr className="my-4" />

      <div className="flex items-center gap-2 mb-3 text-xs">
        <span className="font-medium text-slate-200">Filter:</span>
        <select
          className="p-2 border border-slate-300 rounded-lg text-xs bg-white text-slate-900"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">All</option>
          <option value="valid">Valid</option>
          <option value="near">Expiring Soon</option>
          <option value="expired">Expired</option>
          <option value="no-expiry">No Expiry</option>
        </select>

        <span className="ml-auto text-[11px] text-slate-300">
          Total: {Array.isArray(documents) ? documents.length : 0}
        </span>
      </div>

      {loading ? (
        <div className="text-sm text-slate-200">Loading documents…</div>
      ) : (
        <>
          <h3 className="text-sm font-semibold text-slate-200 mb-2">
            Existing Documents
          </h3>
          <ul className="space-y-2">
            {filteredDocuments.map((doc) => {
              const status = getStatus(doc.expires_at);
              const color = getStatusColor(status);
              return (
                <li
                  key={doc.id}
                  className={`border rounded-lg p-3 flex flex-col gap-1 text-sm ${color}`}
                >
                  <div className="flex justify-between items-center gap-2">
                    <a
                      href={doc.file_url}
                      download
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-semibold underline text-slate-900 line-clamp-1"
                    >
                      {doc.title}
                    </a>
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="bg-rose-600 text-white px-2 py-1 rounded text-xs hover:bg-rose-700"
                    >
                      Delete
                    </button>
                  </div>
                  <span className="text-[11px] text-slate-700">
                    {doc.file_type}
                  </span>
                  {doc.expires_at && (
                    <span className="text-[11px] text-slate-700">
                      Expires at:{" "}
                      {new Date(doc.expires_at).toLocaleDateString()}
                    </span>
                  )}
                </li>
              );
            })}
            {!loading && filteredDocuments.length === 0 && (
              <li className="text-xs text-slate-200">
                No documents for this filter.
              </li>
            )}
          </ul>
        </>
      )}
    </div>
  );
};

export default UploadDocument;
