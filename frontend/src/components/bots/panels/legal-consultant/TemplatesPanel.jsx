import { useState } from "react";

export default function TemplatesPanel({ service, disabled }) {
  const [documentContent, setDocumentContent] = useState("");
  const [templateType, setTemplateType] = useState("freight_contract");
  const [result, setResult] = useState(null);

  const compare = async () => {
    const res = await service.compareWithTemplate({ documentContent, templateType });
    setResult(res);
  };

  const extract = async () => {
    const res = await service.extractKeyClauses({ documentContent });
    setResult(res);
  };

  return (
    <div className="lc-card">
      <div className="lc-section-title">Templates & Clauses</div>
      <div className="lc-grid">
        <div className="lc-field">
          <label>Template</label>
          <select value={templateType} onChange={(e) => setTemplateType(e.target.value)}>
            <option value="freight_contract">Freight Contract</option>
            <option value="service_agreement">Service Agreement</option>
          </select>
        </div>
      </div>
      <div className="lc-field">
        <label>Document Content</label>
        <textarea rows={8} value={documentContent} onChange={(e) => setDocumentContent(e.target.value)} />
      </div>
      <div className="lc-actions">
        <button onClick={compare} disabled={disabled}>Compare with Template</button>
        <button onClick={extract} disabled={disabled}>Extract Key Clauses</button>
      </div>
      {result ? <pre className="lc-pre">{JSON.stringify(result, null, 2)}</pre> : null}
    </div>
  );
}
