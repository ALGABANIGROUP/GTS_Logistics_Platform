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
        id: Date.now() + Math.random(),
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
      const [statusRes, configRes, dashboardRes, learningRes] = await Promise.all([
        axiosClient.get(`/api/v1/ai/bots/available/${BOT_KEY}/status`),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "config" },
        }),
        axiosClient.post(`/api/v1/ai/bots/available/${BOT_KEY}/run`, {
          context: { action: "dashboard" },
        }),
        axiosClient.get("/api/v1/legal-consultant/stats").catch(() => ({ data: {} })),
      ]);

      setStatus(statusRes.data?.data || statusRes.data?.status || {});
      setConfig(configRes.data?.data || configRes.data?.result || {});
      setDashboard(dashboardRes.data?.data || dashboardRes.data?.result || {});
      setLearningStats(learningRes.data || {});
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
      appendLog(label, { error: error?.response?.data?.detail || error.message }, "critical");
      throw error;
    } finally {
      setBusy(false);
    }
  };

  const searchLaws = async () => {
    const filters = {};
    if (lawRegion !== "all") filters.region = lawRegion;
    const payload = await runAction("Search Laws", {
      action: "search_laws",
      query: lawSearch,
      filters,
    });

    let items = payload.results || [];
    if (!items.length && lawTopic !== "all") {
      const topicPayload = await runAction("Search Laws by Topic", {
        action: "laws_by_topic",
        topic: lawTopic,
      });
      items = topicPayload.laws || [];
    }

    setLawResults(items);
  };

  const loadLaw = async (lawId) => {
    const payload = await runAction("Load Law Details", {
      action: "get_law",
      law_id: lawId,
    });
    setSelectedLaw(payload.law || null);
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
    const payload = await runAction("Check Company Compliance", {
      action: "check_company_compliance",
      country: complianceCountry,
      company_data: {
        name: "GTS Logistics",
        licenses: ["Carrier license", "Driver license"],
        documents: ["Commercial invoice", "Waybill"],
        insurance: ["Vehicle liability insurance"],
      },
    });
    setComplianceResult(payload);
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
    return [];
  }, [lawResults]);

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
                          </p>
                        </div>
                        {law.relevance ? (
                          <span className="rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-xs text-blue-200">
                            {law.relevance}% relevance
                          </span>
                        ) : null}
                      </div>
                      <p className="mt-3 text-sm text-slate-300">{law.summary}</p>
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
                  <option>Saudi Arabia</option>
                  <option>UAE</option>
                  <option>Canada</option>
                  <option>Germany</option>
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
                  <p>Region: <span className="text-white">{selectedLaw.region}</span></p>
                  <p>Transport mode: <span className="text-white">{selectedLaw.transport_mode}</span></p>
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

