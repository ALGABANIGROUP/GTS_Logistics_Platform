import { useEffect, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";

const BOT_KEY = "legal_bot";
const glassCard =
  "rounded-2xl border border-white/10 bg-white/5 shadow-lg shadow-black/30 backdrop-blur-xl";

const toneMap = {
  low: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  medium: "border-amber-500/20 bg-amber-500/10 text-amber-200",
  high: "border-orange-500/20 bg-orange-500/10 text-orange-200",
  critical: "border-rose-500/20 bg-rose-500/10 text-rose-200",
  excellent: "border-emerald-500/20 bg-emerald-500/10 text-emerald-200",
  good: "border-blue-500/20 bg-blue-500/10 text-blue-200",
  attention_needed: "border-amber-500/20 bg-amber-500/10 text-amber-200",
};

const LEGAL_CAPABILITIES_FALLBACK = {
  capabilities: [
    "canadian_regulatory_updates",
    "multi_country_compliance",
    "search_laws",
    "get_law",
    "analyze_contract",
    "check_company_compliance",
    "calculate_liability",
    "required_documents",
  ],
};

const normalizeLegalEntry = (item) => ({
  ...item,
  id: item?.id,
  name: item?.name || item?.title || item?.headline || "Legal update",
  summary: item?.summary || item?.description || "No summary available.",
  applicable_in: item?.applicable_in || item?.region || "Canada",
  category: item?.category || "regulation",
});

const COMPLIANCE_COUNTRY_OPTIONS = [
  { label: "Saudi Arabia", code: "sa" },
  { label: "UAE", code: "uae" },
  { label: "Canada", code: "ca" },
  { label: "United States", code: "us" },
  { label: "Mexico", code: "mx" },
];

const buildLocalFallback = (context) => {
  const action = context?.action;

  if (action === "analyze_contract") {
    const text = String(context?.contract_text || "");
    const issues = [];
    if (!/liability/i.test(text)) issues.push("Missing core clause: liability");
    if (!/force majeure/i.test(text)) issues.push("Missing core clause: force majeure");
    if (!/termination/i.test(text)) issues.push("Missing core clause: termination");
    const risks = /unlimited liability/i.test(text)
      ? [{ risk: "Unlimited liability exposure", severity: "high" }]
      : [];

    return {
      clauses_summary: {
        governing_law: /governing law[: ]+([^\n]+)/i.exec(text)?.[1]?.trim() || "Not specified",
        dispute_resolution: /arbitration/i.test(text) ? "arbitration" : "not specified",
        duration: { period: /(\d+\s+(?:month|months|year|years))/i.exec(text)?.[1] || "Not specified" },
        price: Number(/(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(USD|CAD|SAR|EUR|AED)/i.exec(text)?.[1]?.replace(/,/g, "") || 0),
      },
      compliance: {
        is_compliant: issues.length === 0,
        issues,
      },
      risks,
      suggestions:
        issues.length || risks.length
          ? [...issues, ...risks.map((risk) => `Revise immediately: ${risk.risk}`)]
          : ["Contract structure looks acceptable for a first-pass review."],
      risk_level: risks.length ? "high" : issues.length ? "medium" : "low",
    };
  }

  if (action === "check_company_compliance") {
    const country = context?.country || "Canada";
    const companyData = context?.company_data || {};
    const profile = {
      licenses: ["Safety fitness certificate", "Operating authority"],
      documents: ["Bill of lading", "Customs invoice"],
      insurance: ["Liability insurance", "Cargo insurance"],
    };
    const missing = [];
    Object.entries(profile).forEach(([group, items]) => {
      const provided = companyData[group] || [];
      items.forEach((item) => {
        if (!provided.includes(item)) missing.push(item);
      });
    });
    const total = Object.values(profile).flat().length;
    const compliancePercentage = total ? Math.round(((total - missing.length) / total) * 100) : 0;
    return {
      country,
      compliance_percentage: compliancePercentage,
      status: compliancePercentage >= 90 ? "excellent" : compliancePercentage >= 70 ? "good" : "attention_needed",
      missing_requirements: missing,
      official_sources: [],
      compliance_sections: [],
    };
  }

  if (action === "calculate_liability") {
    const limits = {
      cmr_convention_1956: 8.33,
      montreal_convention_1999: 19,
      hamburg_rules_1978: 2.5,
      hague_rules_1924: 2,
    };
    const law = context?.law || "cmr_convention_1956";
    const weight = Number(context?.weight || 0);
    const value = Number(context?.value || 0);
    const compensation = Math.min(weight * (limits[law] || 8.33), value);
    return {
      law_applied: law,
      compensation,
      max_compensation: compensation,
      unit: "SDR",
      notes: "Calculated from a local fallback while the legal runtime is unavailable.",
    };
  }

  if (action === "required_documents") {
    const destination = context?.destination || "Canada";
    const goodsType = context?.goods_type || "general";
    const documents = [
      { name: "Commercial invoice", required: true },
      { name: "Bill of lading", required: true },
    ];
    if (destination === "Canada") {
      documents.push({ name: "Customs invoice", required: true });
    }
    if (goodsType === "electronics") {
      documents.push({ name: "Conformity certificate", required: "depends_on_destination" });
    }
    return {
      origin: context?.origin,
      destination,
      goods_type: goodsType,
      documents,
    };
  }

  return null;
};

const formatRelative = (value) => {
  if (!value) return "Unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
};

export default function AILegalConsultant() {
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState({});
  const [config, setConfig] = useState({});
  const [dashboard, setDashboard] = useState({});
  const [canadianUpdates, setCanadianUpdates] = useState([]);
  const [learningStats, setLearningStats] = useState({});
  const [lawSearch, setLawSearch] = useState("");
  const [lawRegion, setLawRegion] = useState("all");
  const [lawTopic, setLawTopic] = useState("all");
  const [lawResults, setLawResults] = useState([]);
  const [selectedLaw, setSelectedLaw] = useState(null);
  const [contractText, setContractText] = useState(
    "First party: GTS Logistics\nSecond party: Carrier Alpha\nSubject: Cross-border carriage service\nTerm: 12 months\nFreight charge: 15000 USD\nThe carrier accepts unlimited liability.\nArbitration shall be seated in London."
  );
  const [contractReview, setContractReview] = useState(null);
  const [complianceCountry, setComplianceCountry] = useState("Saudi Arabia");
  const [complianceResult, setComplianceResult] = useState(null);
  const [liabilityLaw, setLiabilityLaw] = useState("cmr_convention_1956");
  const [liabilityWeight, setLiabilityWeight] = useState(1000);
  const [liabilityValue, setLiabilityValue] = useState(15000);
  const [liabilityResult, setLiabilityResult] = useState(null);
  const [docOrigin, setDocOrigin] = useState("Canada");
  const [docDestination, setDocDestination] = useState("Saudi Arabia");
  const [goodsType, setGoodsType] = useState("electronics");
  const [documentsResult, setDocumentsResult] = useState(null);
  const [actionLog, setActionLog] = useState([]);

  const appendLog = (label, payload, state = "good") => {
    setActionLog((prev) => [
      {
        id: Date.now() + performance.now(),
        label,
        payload,
        state,
        timestamp: new Date().toISOString(),
      },
      ...prev.slice(0, 7),
    ]);
  };

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [statusRes, canadaDashboardRes, updatesRes, learningRes] = await Promise.allSettled([
        axiosClient.get(`/api/v1/ai/bots/available/${BOT_KEY}/status`),
        axiosClient.get("/api/v1/legal/dashboard"),
        axiosClient.get("/api/v1/legal/updates", { params: { region: "Canada", limit: 12 } }),
        axiosClient.get("/api/v1/legal-consultant/stats"),
      ]);

      setStatus(
        statusRes.status === "fulfilled"
          ? statusRes.value.data?.data || statusRes.value.data?.status || {}
          : {}
      );
      setConfig(LEGAL_CAPABILITIES_FALLBACK);
      setDashboard(
        canadaDashboardRes.status === "fulfilled"
          ? canadaDashboardRes.value.data || {}
          : {}
      );
      setCanadianUpdates(
        updatesRes.status === "fulfilled"
          ? (updatesRes.value.data?.updates || []).map(normalizeLegalEntry)
          : []
      );
      setLearningStats(
        learningRes.status === "fulfilled"
          ? learningRes.value.data || {}
          : {}
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const runAction = async (label, context) => {
    setBusy(true);
    try {
      const res = await axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, { context });
      const payload = res.data?.data || res.data?.result || res.data;
      appendLog(label, payload, "good");
      return payload;
    } catch (error) {
      const fallback = buildLocalFallback(context);
      if (fallback) {
        appendLog(label, fallback, "attention_needed");
        return fallback;
      }
      appendLog(label, { error: error?.response?.data?.detail || error.message }, "critical");
      throw error;
    } finally {
      setBusy(false);
    }
  };

  const searchLaws = async () => {
    setBusy(true);
    try {
      const response = await axiosClient.post("/api/v1/legal/search", {
        query: lawSearch,
        category: lawTopic !== "all" ? lawTopic : null,
        region: lawRegion !== "all" ? lawRegion : null,
        limit: 30,
      });
      const items = (response.data?.results || []).map(normalizeLegalEntry);
      setLawResults(items);
      appendLog("Search Laws", { results: items.length }, "good");
    } catch (error) {
      appendLog("Search Laws", { error: error?.response?.data?.detail || error.message }, "critical");
    } finally {
      setBusy(false);
    }
  };

  const loadLaw = async (lawId) => {
    setBusy(true);
    try {
      const response = await axiosClient.get(`/api/v1/legal/regulation/${lawId}`);
      setSelectedLaw(normalizeLegalEntry(response.data || {}));
      appendLog("Load Law Details", { id: lawId }, "good");
    } catch (error) {
      appendLog("Load Law Details", { error: error?.response?.data?.detail || error.message }, "critical");
    } finally {
      setBusy(false);
    }
  };

  const analyzeContract = async () => {
    const payload = await runAction("Analyze Contract", {
      action: "analyze_contract",
      contract_text: contractText,
      metadata: {
        source: "legal_dashboard",
        contract_type: "carriage",
      },
    });
    setContractReview(payload);
    await fetchAll();
  };

  const runComplianceCheck = async () => {
    const localPayload = await runAction("Check Company Compliance", {
      action: "check_company_compliance",
      country: complianceCountry,
      company_data: {
        name: "GTS Logistics",
        licenses: ["Carrier license", "Driver license"],
        documents: ["Commercial invoice", "Waybill"],
        insurance: ["Vehicle liability insurance"],
      },
    });
    const selectedCountry =
      COMPLIANCE_COUNTRY_OPTIONS.find((item) => item.label === complianceCountry)?.code || "sa";

    try {
      const response = await axiosClient.get(`/api/v1/compliance/overview/${selectedCountry}`);
      const overview = response.data || {};
      const mergedPayload = {
        ...localPayload,
        country: overview.country || localPayload.country,
        official_sources: overview.sources || [],
        compliance_sections: overview.sections || [],
        live_feeds: overview.live_feeds || {},
        generated_at: overview.generated_at,
      };
      setComplianceResult(mergedPayload);
      appendLog("Compliance References", { country: mergedPayload.country, sources: mergedPayload.official_sources.length }, "good");
    } catch (error) {
      appendLog("Compliance References", { error: error?.response?.data?.detail || error.message }, "attention_needed");
      setComplianceResult(localPayload);
    }
  };

  const calculateLiability = async () => {
    const payload = await runAction("Calculate Liability", {
      action: "calculate_liability",
      law: liabilityLaw,
      weight: Number(liabilityWeight),
      value: Number(liabilityValue),
      damage_type: "damage",
    });
    setLiabilityResult(payload);
  };

  const loadRequiredDocuments = async () => {
    const payload = await runAction("Required Documents", {
      action: "required_documents",
      origin: docOrigin,
      destination: docDestination,
      goods_type: goodsType,
    });
    setDocumentsResult(payload);
  };

  const recentSearches = dashboard?.recent_searches || [];
  const stats = dashboard?.stats || {};
  const coverage = dashboard?.coverage || {};
  const commonQueries = dashboard?.common_queries || [];

  const displayedLaws = useMemo(() => {
    if (lawResults.length) return lawResults;
    return canadianUpdates;
  }, [lawResults, canadianUpdates]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="text-center">
          <div className="mx-auto mb-4 h-16 w-16 animate-spin rounded-full border-b-2 border-amber-400" />
          <p className="text-slate-300">Loading Legal Consultant dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-500 to-red-800 text-lg font-bold text-white shadow-lg shadow-red-950/40">
              LAW
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">AI Legal Consultant</h1>
              <p className="text-sm text-slate-300">
                Transport law research, contract analysis, compliance checks, liability guidance, and shipping documents.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className={`${glassCard} px-4 py-2`}>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Version</p>
              <p className="text-sm font-semibold text-white">{status.version || "2.0.0"}</p>
            </div>
            <div className={`${glassCard} px-4 py-2`}>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Mode</p>
              <p className="text-sm font-semibold text-white capitalize">{status.mode || "governance"}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl space-y-6 px-4 py-6">
        <div className="grid gap-4 md:grid-cols-5">
          {[
            { label: "Law Library", value: stats.total_laws || status.law_count || 0, tone: "from-amber-500 to-orange-700" },
            { label: "Regions Covered", value: stats.regions_covered || status.regions_covered || 0, tone: "from-blue-500 to-cyan-700" },
            { label: "Topics Covered", value: stats.topics_covered || status.topics_covered || 0, tone: "from-violet-500 to-fuchsia-700" },
            { label: "Contracts Reviewed", value: stats.contracts_reviewed || 0, tone: "from-emerald-500 to-green-700" },
            { label: "Learning Sessions", value: learningStats.total_sessions ?? "-", tone: "from-slate-500 to-slate-700" },
          ].map((item) => (
            <div key={item.label} className={`rounded-2xl bg-gradient-to-br ${item.tone} p-5 text-white shadow-lg`}>
              <p className="text-3xl font-bold">{item.value}</p>
              <p className="mt-1 text-sm text-white/80">{item.label}</p>
            </div>
          ))}
        </div>

        <div className={`${glassCard} p-6`}>
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-bold text-white">Legal Library Search</h2>
              <p className="text-sm text-slate-400">Search transport conventions, regional law, insurance clauses, and customs frameworks.</p>
            </div>
            <button
              onClick={fetchAll}
              disabled={busy}
              className="rounded-xl border border-white/10 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/5 disabled:opacity-50"
            >
              Refresh
            </button>
          </div>

          <div className="grid gap-3 md:grid-cols-[1fr_220px_220px_120px]">
            <input
              value={lawSearch}
              onChange={(e) => setLawSearch(e.target.value)}
              placeholder="Search CMR, Montreal, liability, customs, insurance..."
              className="rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
            />
            <select
              value={lawRegion}
              onChange={(e) => setLawRegion(e.target.value)}
              className="rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
            >
              <option value="all">All regions</option>
              <option value="International">International</option>
              <option value="Saudi Arabia">Saudi Arabia</option>
              <option value="Canada">Canada</option>
              <option value="Europe">Europe</option>
              <option value="UAE">UAE</option>
            </select>
            <select
              value={lawTopic}
              onChange={(e) => setLawTopic(e.target.value)}
              className="rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
            >
              <option value="all">All topics</option>
              <option value="liability">Liability</option>
              <option value="documents">Documents</option>
              <option value="compliance">Compliance</option>
              <option value="insurance">Insurance</option>
              <option value="customs">Customs</option>
            </select>
            <button
              onClick={searchLaws}
              disabled={busy}
              className="rounded-xl bg-amber-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-amber-500 disabled:opacity-50"
            >
              Search
            </button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <div className={`${glassCard} p-6`}>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">Law Results</h2>
                <span className="text-sm text-slate-400">{displayedLaws.length} loaded</span>
              </div>
              <div className="space-y-3">
                {displayedLaws.length ? (
                  displayedLaws.map((law) => (
                    <button
                      key={law.id}
                      onClick={() => loadLaw(law.id)}
                      className="w-full rounded-xl border border-white/10 bg-slate-900/50 p-4 text-left transition hover:bg-slate-900/80"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <p className="font-semibold text-white">{law.name}</p>
                          <p className="mt-1 text-xs text-slate-400">
                              {law.category || law.region || law.topic} · {law.applicable_in || "Legal library"}
                              {law.source ? ` · ${law.source}` : ""}
                            </p>
                          </div>
                        {law.relevance ? (
                          <span className="rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-xs text-blue-200">
                            {law.relevance}% relevance
                          </span>
                        ) : null}
                        </div>
                        <p className="mt-3 text-sm text-slate-300">{law.summary}</p>
                        {law.url ? (
                          <a
                            href={law.url}
                            target="_blank"
                            rel="noreferrer"
                            className="mt-3 inline-flex text-xs text-amber-300 underline-offset-2 hover:underline"
                            onClick={(event) => event.stopPropagation()}
                          >
                            Official source
                          </a>
                        ) : null}
                      </button>
                    ))
                ) : (
                  <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6 text-center text-sm text-slate-400">
                    Run a search to load legal materials.
                  </div>
                )}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">Contract Analysis</h2>
                <button
                  onClick={analyzeContract}
                  disabled={busy}
                  className="rounded-xl bg-red-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-600 disabled:opacity-50"
                >
                  Analyze Contract
                </button>
              </div>
              <textarea
                value={contractText}
                onChange={(e) => setContractText(e.target.value)}
                className="min-h-[180px] w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
              />
              {contractReview ? (
                <div className="mt-4 space-y-4">
                  <div className="flex flex-wrap items-center gap-3">
                    <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[contractReview.risk_level] || toneMap.medium}`}>
                      {contractReview.risk_level} risk
                    </span>
                    <span className={`rounded-full border px-3 py-1 text-xs ${contractReview.compliance?.is_compliant ? toneMap.excellent : toneMap.attention_needed}`}>
                      {contractReview.compliance?.is_compliant ? "compliant" : "attention needed"}
                    </span>
                  </div>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <p className="text-sm font-semibold text-white">Clause summary</p>
                      <div className="mt-3 space-y-2 text-sm text-slate-300">
                        <p>Governing law: <span className="text-white">{contractReview.clauses_summary?.governing_law || "Not specified"}</span></p>
                        <p>Dispute resolution: <span className="text-white">{contractReview.clauses_summary?.dispute_resolution || "Not specified"}</span></p>
                        <p>Duration: <span className="text-white">{contractReview.clauses_summary?.duration?.period || "Not specified"}</span></p>
                        <p>Price: <span className="text-white">{contractReview.clauses_summary?.price || 0}</span></p>
                      </div>
                    </div>
                    <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <p className="text-sm font-semibold text-white">Compliance issues</p>
                      <div className="mt-3 space-y-2 text-sm text-slate-300">
                        {(contractReview.compliance?.issues || []).length ? (
                          contractReview.compliance.issues.map((issue) => <p key={issue}>{issue}</p>)
                        ) : (
                          <p>No missing core clauses detected.</p>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {(contractReview.risks || []).map((risk, index) => (
                      <div key={`${risk.risk}-${index}`} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                        <div className="flex items-center justify-between gap-3">
                          <p className="font-semibold text-white">{risk.risk}</p>
                          <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[risk.severity] || toneMap.medium}`}>
                            {risk.severity}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                    <p className="text-sm font-semibold text-white">Suggestions</p>
                    <div className="mt-3 space-y-2 text-sm text-slate-300">
                      {(contractReview.suggestions || []).map((item) => <p key={item}>{item}</p>)}
                    </div>
                  </div>
                </div>
              ) : null}
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              <div className={`${glassCard} p-6`}>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-lg font-bold text-white">Compliance Check</h2>
                  <button
                    onClick={runComplianceCheck}
                    disabled={busy}
                    className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-500 disabled:opacity-50"
                  >
                    Run Check
                  </button>
                </div>
                <select
                  value={complianceCountry}
                  onChange={(e) => setComplianceCountry(e.target.value)}
                  className="mb-4 w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                >
                  {COMPLIANCE_COUNTRY_OPTIONS.map((country) => (
                    <option key={country.code}>{country.label}</option>
                  ))}
                </select>
                {complianceResult ? (
                  <div className="space-y-3">
                    <span className={`rounded-full border px-3 py-1 text-xs ${toneMap[complianceResult.status] || toneMap.good}`}>
                      {complianceResult.status} · {complianceResult.compliance_percentage}%
                    </span>
                    <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <p className="text-sm font-semibold text-white">Missing requirements</p>
                      <div className="mt-3 space-y-2 text-sm text-slate-300">
                        {(complianceResult.missing_requirements || []).length ? (
                          complianceResult.missing_requirements.map((item) => <p key={item}>{item}</p>)
                        ) : (
                          <p>No missing requirements.</p>
                        )}
                      </div>
                    </div>
                    {(complianceResult.official_sources || []).length ? (
                      <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                        <p className="text-sm font-semibold text-white">Official sources</p>
                        <div className="mt-3 space-y-2 text-sm text-slate-300">
                          {complianceResult.official_sources.map((source) => (
                            <div key={source.url}>
                              <a
                                href={source.url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-amber-300 underline-offset-2 hover:underline"
                              >
                                {source.name}
                              </a>
                              {source.notes ? <p className="mt-1 text-xs text-slate-400">{source.notes}</p> : null}
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null}
                    {(complianceResult.compliance_sections || []).length ? (
                      <div className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                        <p className="text-sm font-semibold text-white">Country references</p>
                        <div className="mt-3 space-y-3 text-sm text-slate-300">
                          {complianceResult.compliance_sections.map((section) => (
                            <div key={section.id} className="rounded-lg border border-white/10 bg-slate-950/40 p-3">
                              <p className="font-medium text-white">{section.title}</p>
                              {section.summary ? <p className="mt-1">{section.summary}</p> : null}
                              {section.endpoint ? <p className="mt-1 text-xs text-slate-400">{section.endpoint}</p> : null}
                              {(section.items || []).length ? (
                                <p className="mt-2 text-xs text-slate-400">{section.items.length} live items loaded.</p>
                              ) : null}
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null}
                  </div>
                ) : null}
              </div>

              <div className={`${glassCard} p-6`}>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-lg font-bold text-white">Liability Calculator</h2>
                  <button
                    onClick={calculateLiability}
                    disabled={busy}
                    className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-500 disabled:opacity-50"
                  >
                    Calculate
                  </button>
                </div>
                <div className="grid gap-3">
                  <select
                    value={liabilityLaw}
                    onChange={(e) => setLiabilityLaw(e.target.value)}
                    className="rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                  >
                    <option value="cmr_convention_1956">CMR Convention 1956</option>
                    <option value="hamburg_rules_1978">Hamburg Rules 1978</option>
                    <option value="montreal_convention_1999">Montreal Convention 1999</option>
                    <option value="hague_rules_1924">Hague Rules 1924</option>
                  </select>
                  <input
                    type="number"
                    value={liabilityWeight}
                    onChange={(e) => setLiabilityWeight(e.target.value)}
                    placeholder="Weight in kg"
                    className="rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                  />
                  <input
                    type="number"
                    value={liabilityValue}
                    onChange={(e) => setLiabilityValue(e.target.value)}
                    placeholder="Cargo value"
                    className="rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                  />
                </div>
                {liabilityResult ? (
                  <div className="mt-4 rounded-xl border border-white/10 bg-slate-900/50 p-4 text-sm text-slate-300">
                    <p>Law applied: <span className="font-semibold text-white">{liabilityResult.law_applied}</span></p>
                    <p className="mt-2">Compensation: <span className="font-semibold text-white">{liabilityResult.compensation} {liabilityResult.unit}</span></p>
                    <p className="mt-2">Max compensation: <span className="font-semibold text-white">{liabilityResult.max_compensation} {liabilityResult.unit}</span></p>
                    <p className="mt-2">{liabilityResult.notes}</p>
                  </div>
                ) : null}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Selected Law</h2>
                {selectedLaw ? (
                  <div className="mt-4 space-y-3 text-sm text-slate-300">
                    <p className="text-base font-semibold text-white">{selectedLaw.name}</p>
                    <p>{selectedLaw.summary}</p>
                    {selectedLaw.source ? <p>Source: <span className="text-white">{selectedLaw.source}</span></p> : null}
                    {selectedLaw.published_at ? <p>Updated: <span className="text-white">{formatRelative(selectedLaw.published_at)}</span></p> : null}
                    <p>Region: <span className="text-white">{selectedLaw.region}</span></p>
                    <p>Transport mode: <span className="text-white">{selectedLaw.transport_mode}</span></p>
                    {selectedLaw.url ? (
                      <a
                        href={selectedLaw.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex text-xs text-amber-300 underline-offset-2 hover:underline"
                      >
                        Open official source
                      </a>
                    ) : null}
                    <div className="space-y-2">
                    {(selectedLaw.key_points || []).map((point) => (
                      <div key={point} className="rounded-xl border border-white/10 bg-slate-900/50 p-3">
                        {point}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="mt-4 rounded-xl border border-white/10 bg-slate-900/50 p-6 text-center text-sm text-slate-400">
                  Select a law from search results to inspect its legal summary.
                </div>
              )}
            </div>

            <div className={`${glassCard} p-6`}>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">Required Documents</h2>
                <button
                  onClick={loadRequiredDocuments}
                  disabled={busy}
                  className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-500 disabled:opacity-50"
                >
                  Load
                </button>
              </div>
              <div className="space-y-3">
                <input
                  value={docOrigin}
                  onChange={(e) => setDocOrigin(e.target.value)}
                  placeholder="Origin country"
                  className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                />
                <input
                  value={docDestination}
                  onChange={(e) => setDocDestination(e.target.value)}
                  placeholder="Destination country"
                  className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                />
                <input
                  value={goodsType}
                  onChange={(e) => setGoodsType(e.target.value)}
                  placeholder="Goods type"
                  className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                />
              </div>
              {documentsResult ? (
                <div className="mt-4 space-y-2">
                  {(documentsResult.documents || []).map((doc) => (
                    <div key={doc.name} className="rounded-xl border border-white/10 bg-slate-900/50 p-4 text-sm text-slate-300">
                      <p className="font-semibold text-white">{doc.name}</p>
                      <p className="mt-1">Required: {String(doc.required)}</p>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Coverage</h2>
              <div className="mt-4 space-y-3">
                {Object.entries(coverage).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-900/50 px-4 py-3">
                    <span className="text-sm capitalize text-slate-300">{key}</span>
                    <span className="text-sm font-semibold text-white">{value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Common Queries</h2>
              <div className="mt-4 space-y-2">
                {commonQueries.map((item) => (
                  <div key={item} className="rounded-xl border border-white/10 bg-slate-900/50 p-3 text-sm text-slate-300">
                    {item}
                  </div>
                ))}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Recent Searches</h2>
              <div className="mt-4 space-y-3">
                {recentSearches.length ? (
                  recentSearches.map((item, index) => (
                    <div key={`${item.query}-${index}`} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <p className="text-sm font-semibold text-white">{item.query || "Untitled search"}</p>
                      <p className="mt-1 text-xs text-slate-400">{formatRelative(item.timestamp)}</p>
                    </div>
                  ))
                ) : (
                  <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6 text-center text-sm text-slate-400">
                    No recent searches yet.
                  </div>
                )}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Action Log</h2>
              <div className="mt-4 space-y-3">
                {actionLog.length ? (
                  actionLog.map((item) => (
                    <div key={item.id} className="rounded-xl border border-white/10 bg-slate-900/50 p-4">
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-semibold text-white">{item.label}</p>
                        <span className={`rounded-full border px-2 py-1 text-[11px] ${toneMap[item.state] || toneMap.good}`}>
                          {item.state}
                        </span>
                      </div>
                      <p className="mt-2 text-xs text-slate-400">{formatRelative(item.timestamp)}</p>
                    </div>
                  ))
                ) : (
                  <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6 text-center text-sm text-slate-400">
                    No actions recorded yet.
                  </div>
                )}
              </div>
            </div>

            <div className={`${glassCard} p-6`}>
              <h2 className="text-lg font-bold text-white">Capabilities</h2>
              <div className="mt-4 flex flex-wrap gap-2">
                {(config.capabilities || []).map((capability) => (
                  <span key={capability} className="rounded-full border border-white/10 bg-slate-900/50 px-3 py-1 text-xs text-slate-300">
                    {capability}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
