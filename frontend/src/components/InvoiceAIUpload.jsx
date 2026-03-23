import React, { useState } from "react";

export default function InvoiceAIUpload() {
    const [file, setFile] = useState(null);
    const [fields, setFields] = useState(null);
    const [rawText, setRawText] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setFields(null);
        setRawText("");
        setError("");
    };

    const handleExtract = async () => {
        if (!file) return;
        setLoading(true);
        setError("");
        setFields(null);
        setRawText("");
        try {
            const fd = new FormData();
            fd.append("file", file);
            const res = await fetch("/api/v1/invoice/extract-fields", {
                method: "POST",
                body: fd,
            });
            const jd = await res.json();
            if (!res.ok) throw new Error(jd?.detail || "Extraction failed");
            setFields(jd.fields);
            setRawText(jd.raw_text);
        } catch (err) {
            setError(err.message || "Unknown error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-slate-900 p-6 rounded-lg max-w-xl mx-auto mt-8 shadow-lg">
            <h2 className="text-xl font-bold mb-4 text-white">AI Invoice Field Extraction</h2>
            <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.xls,.xlsx"
                onChange={handleFileChange}
                className="mb-4 block w-full text-white"
            />
            <button
                onClick={handleExtract}
                disabled={!file || loading}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded disabled:opacity-50"
            >
                {loading ? "Extracting..." : "Extract Fields"}
            </button>
            {error && <div className="text-red-400 mt-2">{error}</div>}
            {fields && (
                <div className="mt-6 bg-slate-800 p-4 rounded">
                    <h3 className="text-lg font-semibold text-white mb-2">Extracted Fields:</h3>
                    <ul className="text-slate-200">
                        {Object.entries(fields).map(([k, v]) => (
                            <li key={k}><b>{k}:</b> {v}</li>
                        ))}
                    </ul>
                    <details className="mt-2">
                        <summary className="text-slate-400 cursor-pointer">Full Extracted Text</summary>
                        <pre className="text-xs text-slate-300 bg-slate-900 p-2 rounded overflow-x-auto max-h-40">{rawText}</pre>
                    </details>
                </div>
            )}
        </div>
    );
}
