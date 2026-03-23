import { useState } from "react";
import legalService from "../../../../services/legalService";
import ReviewPanel from "./ReviewPanel";
import CompliancePanel from "./CompliancePanel";
import RiskPanel from "./RiskPanel";
import TemplatesPanel from "./TemplatesPanel";
import AdvisoryPanel from "./AdvisoryPanel";
import "./LegalConsultant.css";

export default function LegalConsultant() {
  const [tab, setTab] = useState("review");
  const svc = legalService; // Always use real API service

  const tabs = [
    { id: "review", label: "Review" },
    { id: "compliance", label: "Compliance" },
    { id: "risk", label: "Risk" },
    { id: "templates", label: "Templates" },
    { id: "advisory", label: "Advisory" },
  ];

  return (
    <div className="lc-wrap">

      <header className="lc-header">
        <div className="lc-title">
          <div className="lc-icon"></div>
          <div>
            <div className="lc-h1">AI Legal Consultant</div>
            <div className="lc-sub">Documents  Compliance  Risk  Advisory</div>
          </div>
        </div>
        <nav className="lc-tabs">
          {tabs.map((t) => (
            <button
              key={t.id}
              className={tab === t.id ? "active" : ""}
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="lc-body">
        {tab === "review" && <ReviewPanel service={svc} disabled={false} />}
        {tab === "compliance" && (
          <CompliancePanel service={svc} disabled={false} />
        )}
        {tab === "risk" && <RiskPanel service={svc} disabled={false} />}
        {tab === "templates" && (
          <TemplatesPanel service={svc} disabled={false} />
        )}
        {tab === "advisory" && (
          <AdvisoryPanel service={svc} disabled={false} />
        )}
      </main>
    </div>
  );
}
