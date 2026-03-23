import { useState } from "react";

export default function ReviewPanel({ service, disabled }) {
  const [title, setTitle] = useState("");
  const [documentType, setDocumentType] = useState("contract");
  const [jurisdiction, setJurisdiction] = useState("uae");
  const [content, setContent] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const runTextReview = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await service.reviewDocument({
        title: title || "Untitled",
        content,
        documentType,
        jurisdiction,
      });
      setResult(res);
    } catch (e) {
      setError("Failed to review document");
    } finally {
      setLoading(false);
    }
  };

  const runFileReview = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await service.uploadAndReview({
        file,
        documentType,
        jurisdiction,
      });
      setResult(res);
    } catch (e) {
      setError("Failed to upload & review");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="lc-card">
      <div className="lc-section-title">Document Review</div>
      <div className="lc-grid">
        <div className="lc-field">
          <label>Title</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div className="lc-field">
          <label>Type</label>
          <select value={documentType} onChange={(e) => setDocumentType(e.target.value)}>
            <option value="contract">Contract</option>
            <option value="policy">Policy</option>
            <option value="agreement">Agreement</option>
            <option value="notice">Notice</option>
          </select>
        </div>
        <div className="lc-field">
          <label>Jurisdiction</label>
          <select value={jurisdiction} onChange={(e) => setJurisdiction(e.target.value)}>
            <option value="uae">UAE</option>
            <option value="gcc">GCC</option>
            <option value="international">International</option>
          </select>
        </div>
      </div>

      <div className="lc-field">
        <label>Content</label>
        <textarea rows={6} value={content} onChange={(e) => setContent(e.target.value)} />
      </div>

      <div className="lc-actions">
        <button onClick={runTextReview} disabled={disabled || loading}>
          {loading ? "Analyzing..." : "Analyze Text"}
        </button>
        <label className="lc-file">
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          <span>{file ? file.name : "Choose file"}</span>
        </label>
        <button onClick={runFileReview} disabled={disabled || loading || !file}>
          {loading ? "Uploading..." : "Upload & Analyze"}
        </button>
      </div>

      {error ? <div className="lc-error">{error}</div> : null}
      {result ? (
        <div className="lc-result-box">
          <div className="lc-result-header">
            <span className="lc-result-badge">Analysis Complete</span>
            <span className="lc-result-id">{result.review_id || result.document_id || 'N/A'}</span>
          </div>
          {result.result?.overall_assessment ? (
            <div className="lc-assessment">
              <div className="lc-assessment-score">
                Score: <strong>{result.result.overall_assessment.score || 'N/A'}</strong>/100
              </div>
              <div className="lc-assessment-status">
                Status: <strong>{result.result.overall_assessment.status || 'N/A'}</strong>
              </div>
            </div>
          ) : null}
          <details className="lc-details" open>
            <summary>Full Analysis (JSON)</summary>
            <pre className="lc-pre">{JSON.stringify(result, null, 2)}</pre>
          </details>
        </div>
      ) : null}
    </div>
  );
}
