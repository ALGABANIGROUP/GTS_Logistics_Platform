import { useEffect, useMemo, useRef, useState } from "react";
import GlobalTransportLaws from "../components/GlobalTransportLaws";
import { DOCUMENT_LOGO_SRC } from "../utils/documentBranding";


const LAW_LIBRARY = [
  {
    id: 1,
    country: "SA",
    countryName: "Saudi Arabia",
    title: "Road Transport Regulations",
    type: "Road",
    typeKey: "road",
    region: "middle_east",
    year: 2023,
    tags: ["road", "logistics", "safety"],
    highlighted: true,
  },
  {
    id: 2,
    country: "AE",
    countryName: "United Arab Emirates",
    title: "Commercial Maritime Transport Code",
    type: "Sea",
    typeKey: "sea",
    region: "middle_east",
    year: 2022,
    tags: ["ports", "containers"],
  },
  {
    id: 3,
    country: "EG",
    countryName: "Egypt",
    title: "Traffic and Logistics Act",
    type: "Road",
    typeKey: "road",
    region: "africa",
    year: 2021,
    tags: ["road", "safety", "permits"],
  },
  {
    id: 4,
    country: "USA",
    countryName: "United States",
    title: "Federal Motor Carrier Safety Regulations",
    type: "Road",
    typeKey: "road",
    region: "america",
    year: 2023,
    tags: ["compliance", "fmcsa", "safety"],
  },
  {
    id: 5,
    country: "DE",
    countryName: "Germany",
    title: "Air Cargo Act",
    type: "Air",
    typeKey: "air",
    region: "europe",
    year: 2022,
    tags: ["aviation", "cargo", "customs"],
  },
  {
    id: 6,
    country: "CN",
    countryName: "China",
    title: "Multimodal Transport Rules",
    type: "Multimodal",
    typeKey: "multi",
    region: "asia",
    year: 2023,
    tags: ["rail", "road", "sea"],
  },
  {
    id: 7,
    country: "IN",
    countryName: "India",
    title: "Rail Freight Regulations",
    type: "Rail",
    typeKey: "rail",
    region: "asia",
    year: 2022,
    tags: ["rail", "freight", "tariffs"],
  },
  {
    id: 8,
    country: "GB",
    countryName: "United Kingdom",
    title: "International Transport Act",
    type: "Multimodal",
    typeKey: "multi",
    region: "europe",
    year: 2023,
    tags: ["international", "road", "sea"],
  },
  {
    id: 9,
    country: "FR",
    countryName: "France",
    title: "Highway Freight Regulation",
    type: "Road",
    typeKey: "road",
    region: "europe",
    year: 2022,
    tags: ["road", "toll", "logistics"],
  },
  {
    id: 10,
    country: "JP",
    countryName: "Japan",
    title: "Maritime Transport Law",
    type: "Sea",
    typeKey: "sea",
    region: "asia",
    year: 2023,
    tags: ["shipping", "ports", "export"],
  },
  {
    id: 11,
    country: "AU",
    countryName: "Australia",
    title: "Air Freight Cargo Standards",
    type: "Air",
    typeKey: "air",
    region: "asia",
    year: 2022,
    tags: ["air", "freight", "security"],
  },
  {
    id: 12,
    country: "BR",
    countryName: "Brazil",
    title: "Domestic Transport Framework",
    type: "Road",
    typeKey: "road",
    region: "america",
    year: 2023,
    tags: ["domestic", "road", "permits"],
  },
];

const LEGAL_FIELDS = [
  { id: 1, name: "Tax", icon: "TAX", count: 2450 },
  { id: 2, name: "Transport", icon: "TRN", count: 3200 },
  { id: 3, name: "Corporate", icon: "CORP", count: 1870 },
  { id: 4, name: "Intellectual Property", icon: "IP", count: 1250 },
  { id: 5, name: "Contracts", icon: "CTR", count: 4300 },
  { id: 6, name: "Compliance", icon: "CMP", count: 2900 },
];

const LEGAL_ACTIONS = [
  { id: 1, label: "Contract review", type: "contract_review", premium: false },
  { id: 2, label: "Compliance check", type: "compliance_check", premium: false },
  { id: 3, label: "Risk assessment", type: "risk_assessment", premium: false },
  { id: 4, label: "Clause analysis", type: "clause_analysis", premium: false },
  { id: 5, label: "Document comparison", type: "document_comparison", premium: true },
  { id: 6, label: "Template generation", type: "template_generation", premium: true },
  { id: 7, label: "Tax analysis", type: "tax_analysis", premium: true },
  { id: 8, label: "Law review", type: "law_review", premium: true },
];

const QUICK_QUERIES = [
  "Review confidentiality clauses in the transport contract",
  "Identify tax exposure and obligations",
  "Compare Saudi and UAE transport law",
  "Verify GDPR compliance for document processing",
  "Surface legal risks in the agreement",
];

const LOG_FILTERS = [
  { value: "all", label: "All" },
  { value: "analysis", label: "Analysis" },
  { value: "compliance", label: "Compliance" },
  { value: "tax", label: "Tax" },
  { value: "contract", label: "Contract" },
  { value: "transport", label: "Transport" },
  { value: "review", label: "Review" },
  { value: "warning", label: "Warning" },
  { value: "info", label: "Info" },
];

const OM_REQUEST_TYPES = [
  { value: "legal_review", label: "Legal review" },
  { value: "contract_drafting", label: "Contract drafting" },
  { value: "compliance_audit", label: "Compliance audit" },
  { value: "dispute_resolution", label: "Dispute resolution" },
  { value: "international_law", label: "International law" },
];

const REGION_LABELS = {
  middle_east: "Middle East",
  europe: "Europe",
  asia: "Asia",
  america: "Americas",
  africa: "Africa",
};

const buildNotification = (message, type = "info") => ({ message, type });

export default function LegalConsultantDashboard() {
  const fileInputRef = useRef(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [botMessage, setBotMessage] = useState("");
  const [advancedContext, setAdvancedContext] = useState("");
  const [showJsonEditor, setShowJsonEditor] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedAction, setSelectedAction] = useState(LEGAL_ACTIONS[0]);
  const [selectedField, setSelectedField] = useState(LEGAL_FIELDS[0]);
  const [activeLogFilters, setActiveLogFilters] = useState(["all"]);
  const [showOmChat, setShowOmChat] = useState(false);
  const [lawSearchQuery, setLawSearchQuery] = useState("");
  const [selectedRegion, setSelectedRegion] = useState("all");
  const [selectedLawType, setSelectedLawType] = useState("all");
  const [lawsPage, setLawsPage] = useState(1);
  const [notification, setNotification] = useState(null);
  const [omChatInput, setOmChatInput] = useState("");
  const [omMessage, setOmMessage] = useState("");
  const [selectedOmRequestType, setSelectedOmRequestType] = useState("legal_review");
  const [analyzedDocuments, setAnalyzedDocuments] = useState(1247);
  const [stats, setStats] = useState({ tax: 85, transport: 92, corporate: 78, ip: 65 });
  const [logs, setLogs] = useState([
    {
      id: 1,
      timestamp: "09:45:23",
      type: "analysis",
      message: "Completed international transport contract review",
      document: "international_transport_contract.pdf",
      jurisdiction: "Saudi Arabia",
      legalField: "Transport",
      details: { pages: 22, riskLevel: "medium", taxImplications: true },
    },
    {
      id: 2,
      timestamp: "09:30:15",
      type: "compliance",
      message: "GDPR compliance check completed",
      document: "privacy_policy.docx",
      jurisdiction: "Europe",
      legalField: "Corporate",
      details: { compliant: 92, issues: 2, gdprArticles: ["15", "17"] },
    },
    {
      id: 3,
      timestamp: "09:15:00",
      type: "tax",
      message: "Reviewed quarterly tax report",
      document: "q1_tax_report.pdf",
      jurisdiction: "United Arab Emirates",
      legalField: "Tax",
      details: { taxableAmount: 1250000, deductions: 320000, netTax: 186000 },
    },
  ]);
  const [omRequests, setOmRequests] = useState([
    {
      id: "OM-2024-001",
      type: "Legal review",
      message: "Review a cross-border shipping contract",
      status: "Complete",
      date: "2024-01-15",
    },
    {
      id: "OM-2024-002",
      type: "Contract drafting",
      message: "Draft a logistics partnership agreement",
      status: "In review",
      date: "2024-01-16",
    },
  ]);
  const [omChatMessages, setOmChatMessages] = useState([
    {
      id: 1,
      sender: "user",
      content: "I need a legal review for a German transport contract.",
      time: "10:30",
    },
    {
      id: 2,
      sender: "om",
      content: "Request received. Assigning to EU transport specialist.",
      time: "10:32",
    },
  ]);

  const lastUpdated = useMemo(() => new Date().toLocaleString("en-US"), []);

  const filteredLawBase = useMemo(() => {
    let filtered = LAW_LIBRARY;
    if (lawSearchQuery) {
      const query = lawSearchQuery.toLowerCase();
      filtered = filtered.filter(
        (law) =>
          law.countryName.toLowerCase().includes(query) ||
          law.title.toLowerCase().includes(query) ||
          law.tags.some((tag) => tag.toLowerCase().includes(query))
      );
    }
    if (selectedRegion !== "all") {
      filtered = filtered.filter((law) => law.region === selectedRegion);
    }
    if (selectedLawType !== "all") {
      filtered = filtered.filter((law) => law.typeKey === selectedLawType);
    }
    return filtered;
  }, [lawSearchQuery, selectedRegion, selectedLawType]);

  useEffect(() => {
    setLawsPage(1);
  }, [lawSearchQuery, selectedRegion, selectedLawType]);

  const lawsPerPage = 6;
  const totalLawsPages = Math.max(1, Math.ceil(filteredLawBase.length / lawsPerPage));
  const filteredLaws = filteredLawBase.slice(
    (lawsPage - 1) * lawsPerPage,
    lawsPage * lawsPerPage
  );

  const filteredLogs = useMemo(() => {
    if (activeLogFilters.includes("all")) return logs;
    return logs.filter((log) => activeLogFilters.includes(log.type));
  }, [activeLogFilters, logs]);

  const recentOmRequests = omRequests.slice(0, 3);

  const notify = (message, type = "info") => {
    setNotification(buildNotification(message, type));
    setTimeout(() => setNotification(null), 4000);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  const riskClass = (score) => {
    if (score < 30) return "bg-emerald-400";
    if (score < 70) return "bg-amber-400";
    return "bg-rose-500";
  };

  const severityLabel = (severity) => {
    const labels = {
      critical: "Critical",
      high: "High",
      medium: "Medium",
      low: "Low",
      info: "Info",
    };
    return labels[severity] || severity;
  };

  const statusLabel = (status) => {
    const labels = {
      compliant: "Compliant",
      non_compliant: "Non-compliant",
      requires_review: "Needs review",
      partial: "Partial",
    };
    return labels[status] || status;
  };

  const logTypeLabel = (type) => {
    const labels = {
      analysis: "Analysis",
      compliance: "Compliance",
      tax: "Tax",
      contract: "Contract",
      transport: "Transport",
      review: "Review",
      warning: "Warning",
      info: "Info",
    };
    return labels[type] || type;
  };

  const notificationClass = (type) => {
    if (type === "success") return "border-emerald-400/40 bg-emerald-500/15 text-emerald-100";
    if (type === "warning") return "border-amber-400/40 bg-amber-500/15 text-amber-100";
    if (type === "error") return "border-rose-400/40 bg-rose-500/15 text-rose-100";
    return "border-sky-400/40 bg-sky-500/15 text-sky-100";
  };

  const openFilePicker = () => fileInputRef.current?.click();

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    const next = [];
    const allowedExtensions = ["pdf", "doc", "docx", "txt", "rtf", "xlsx", "xls"];
    files.slice(0, 10).forEach((file) => {
      const ext = String(file.name || "")
        .split(".")
        .pop()
        .toLowerCase();
      if (!allowedExtensions.includes(ext)) {
        notify(`Unsupported file type: ${file.name}`, "warning");
        return;
      }
      if (file.size > 20 * 1024 * 1024) {
        notify(`File too large: ${file.name}`, "warning");
        return;
      }
      if (!selectedFiles.find((f) => f.name === file.name)) {
        next.push(file);
      }
    });
    setSelectedFiles((prev) => [...prev, ...next]);
    event.target.value = "";
  };

  const handleFileDrop = (event) => {
    event.preventDefault();
    const files = Array.from(event.dataTransfer.files);
    handleFileSelect({ target: { files } });
  };

  const removeFile = (fileToRemove) => {
    setSelectedFiles((prev) => prev.filter((file) => file !== fileToRemove));
  };

  const clearFiles = () => {
    setSelectedFiles([]);
    setAnalysisResults(null);
  };

  const analyzeDocuments = async () => {
    if (!selectedFiles.length) {
      notify("Select files before analysis.", "warning");
      return;
    }
    setIsRunning(true);
    notify("Running legal analysis...", "info");
    try {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      const results = {
        analysisField: selectedField?.name || "General",
        analyzedAt: new Date().toLocaleString("en-US"),
        totalClauses: 28,
        riskScore: 65,
        taxRisk: 45,
        contractRisk: 70,
        complianceRisk: 60,
        findings: [
          {
            id: 1,
            title: "Ambiguous liability clause",
            severity: "high",
            category: "Transport",
            description: "Liability allocation is unclear for multi-leg shipments.",
            legalReference: "International Transport Convention Section 12",
            suggestion: "Add clear handoff responsibilities per carrier leg.",
            alternativeClause:
              "Each carrier is responsible for loss or damage occurring during its custody period.",
          },
          {
            id: 2,
            title: "Tax exposure not defined",
            severity: "medium",
            category: "Tax",
            description: "Contract omits responsibility for transit taxes and duties.",
            legalReference: "VAT Regulation Article 8",
            suggestion: "Specify tax obligations for each transit jurisdiction.",
            alternativeClause:
              "The shipper assumes all transit taxes and duties unless otherwise agreed in writing.",
          },
          {
            id: 3,
            title: "Confidentiality scope is outdated",
            severity: "low",
            category: "Corporate",
            description: "Digital data handling is not covered in confidentiality terms.",
            legalReference: "Data protection guidance 2022",
            suggestion: "Extend confidentiality to cloud storage and electronic records.",
          },
        ],
        compliance: {
          regulations: [
            { name: "Saudi Road Transport Law", status: "compliant" },
            { name: "International Transport Convention", status: "partial" },
            { name: "GDPR", status: "requires_review" },
            { name: "Unified Customs Code", status: "non_compliant" },
          ],
        },
      };
      setAnalysisResults(results);
      setAnalyzedDocuments((prev) => prev + selectedFiles.length);
      setLogs((prev) => [
        {
          id: Date.now(),
          timestamp: new Date().toLocaleTimeString("en-US"),
          type: "analysis",
          message: `Analyzed ${selectedFiles.length} document(s)`,
          document: selectedFiles.map((f) => f.name).join(", "),
          jurisdiction: "Multi-region",
          legalField: selectedField?.name || "General",
          details: {
            riskScore: results.riskScore,
            findingsCount: results.findings.length,
            complianceScore: "72%",
          },
        },
        ...prev,
      ]);
      notify("Analysis complete.", "success");
    } catch (error) {
      notify("Analysis failed.", "error");
    } finally {
      setIsRunning(false);
    }
  };

  const analyzeBulkDocuments = async () => {
    notify("Starting bulk analysis...", "info");
    await analyzeDocuments();
  };

  const selectLegalField = (field) => {
    setSelectedField(field);
    notify(`Selected field: ${field.name}`, "info");
  };

  const selectAction = (action) => {
    setSelectedAction(action);
    setBotMessage(`Action: ${action.label}`);
    notify(`Selected action: ${action.label}`, "info");
  };

  const runLegalConsultant = async () => {
    if (!botMessage.trim() && !advancedContext.trim()) {
      notify("Add a request message or context.", "warning");
      return;
    }
    setIsRunning(true);
    notify("Processing request...", "info");
    try {
      const context = advancedContext.trim() ? JSON.parse(advancedContext) : {};
      await new Promise((resolve) => setTimeout(resolve, 1500));
      setLogs((prev) => [
        {
          id: Date.now(),
          timestamp: new Date().toLocaleTimeString("en-US"),
          type: selectedAction?.type || "analysis",
          message: botMessage.trim() || "General request",
          document: context.document || null,
          jurisdiction: context.jurisdiction || "Unspecified",
          legalField: selectedField?.name || "General",
          details: {
            context,
            model: "LegalAI-Pro",
            confidence: "92%",
          },
        },
        ...prev,
      ]);
      notify("Request completed.", "success");
    } catch (error) {
      notify("Request failed.", "error");
    } finally {
      setIsRunning(false);
    }
  };

  const refreshLegalStatus = () => {
    setAnalyzedDocuments((prev) => prev + Math.floor(Math.random() * 4));
    setStats((prev) => ({
      tax: Math.min(100, prev.tax + 1),
      transport: Math.min(100, prev.transport + 1),
      corporate: Math.min(100, prev.corporate + 1),
      ip: Math.min(100, (prev.ip || 0) + 1),
    }));
    notify("Status updated.", "success");
  };

  const toggleJsonEditor = () => setShowJsonEditor((prev) => !prev);

  const validateJson = () => {
    try {
      JSON.parse(advancedContext);
      notify("JSON is valid.", "success");
    } catch (error) {
      notify(`Invalid JSON: ${error.message}`, "error");
    }
  };

  const loadPreset = (preset) => {
    const presets = {
      tax_review: {
        jurisdiction: "saudi_arabia",
        legal_fields: ["tax", "compliance"],
        review_depth: "detailed",
        tax_types: ["vat", "income", "customs"],
        output_format: "tax_report",
      },
      transport_contract: {
        jurisdiction: "multi",
        legal_fields: ["transport", "contract", "international"],
        transport_modes: ["road", "sea", "air"],
        incoterms: ["CIF", "FOB", "EXW"],
        review_depth: "comprehensive",
      },
      corporate_compliance: {
        jurisdiction: "uae",
        legal_fields: ["corporate", "compliance", "governance"],
        regulations: ["companies_law", "aml", "data_protection"],
        review_depth: "audit",
      },
      international_trade: {
        jurisdiction: "international",
        legal_fields: ["trade", "customs", "export_control"],
        agreements: ["WTO", "GCC", "bilateral"],
        review_depth: "expert",
      },
    };
    setAdvancedContext(JSON.stringify(presets[preset], null, 2));
    notify(`Loaded preset: ${preset}`, "info");
  };

  const toggleLogFilter = (filter) => {
    if (filter === "all") {
      setActiveLogFilters(["all"]);
      return;
    }
    setActiveLogFilters((prev) => {
      const next = prev.filter((f) => f !== "all");
      if (next.includes(filter)) {
        const trimmed = next.filter((f) => f !== filter);
        return trimmed.length ? trimmed : ["all"];
      }
      return [...next, filter];
    });
  };

  const viewLawDetails = (law) => notify(`Viewing details for ${law.title}`, "info");
  const compareWithLocalLaw = (law) => notify(`Comparing ${law.countryName} law with local rules`, "info");
  const downloadLaw = (law) => notify(`Preparing download: ${law.title}`, "info");

  const prevLawsPage = () => setLawsPage((prev) => Math.max(1, prev - 1));
  const nextLawsPage = () => setLawsPage((prev) => Math.min(totalLawsPages, prev + 1));

  const sendOmChatMessage = () => {
    if (!omChatInput.trim()) return;
    setOmChatMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        sender: "user",
        content: omChatInput,
        time: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
    setOmChatInput("");
    setTimeout(() => {
      setOmChatMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: "om",
          content: "Request received. We will reply within one business day.",
          time: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    }, 800);
  };

  const sendToOperationManager = () => {
    if (!omMessage.trim() && !analysisResults) {
      notify("Add a message or analysis before sending.", "warning");
      return;
    }
    const selectedType = OM_REQUEST_TYPES.find(
      (item) => item.value === selectedOmRequestType
    );
    setOmRequests((prev) => [
      {
        id: `OM-${Date.now()}`,
        type: selectedType?.label || selectedOmRequestType,
        typeValue: selectedOmRequestType,
        message: omMessage || "Legal analysis attached",
        status: "Received",
        date: new Date().toLocaleDateString("en-US"),
      },
      ...prev,
    ]);
    setOmMessage("");
    notify("Sent to operations manager.", "success");
  };

  const exportAnalysis = () => {
    if (!analysisResults) return;
    const payload = {
      ...analysisResults,
      exportDate: new Date().toISOString(),
      exportedBy: "AI Legal Consultant",
      version: "2.0.0",
    };
    const dataStr = JSON.stringify(payload, null, 2);
    const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
    const fileName = `legal-analysis-${new Date().toISOString().slice(0, 10)}.json`;
    const link = document.createElement("a");
    link.setAttribute("href", dataUri);
    link.setAttribute("download", fileName);
    link.click();
    notify("Analysis exported.", "success");
  };

  const exportLegalLogs = () => {
    const payload = { logs, exportDate: new Date().toISOString() };
    const dataStr = JSON.stringify(payload, null, 2);
    const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
    const fileName = `legal-logs-${new Date().toISOString().slice(0, 10)}.json`;
    const link = document.createElement("a");
    link.setAttribute("href", dataUri);
    link.setAttribute("download", fileName);
    link.click();
    notify("Exported logs.", "success");
  };

  const printContractReport = () => {
    const contractItems = logs.filter((item) => {
      const haystack = `${item.type || ""} ${item.message || ""} ${item.legalField || ""}`.toLowerCase();
      return haystack.includes("contract");
    });

    const printWindow = window.open("", "_blank", "width=900,height=700");
    if (!printWindow) return;

    const rows = (contractItems.length ? contractItems : logs)
      .map(
        (item) => `
        <tr>
          <td>${item.timestamp || "-"}</td>
          <td>${item.message || "-"}</td>
          <td>${item.document || "-"}</td>
          <td>${item.jurisdiction || "-"}</td>
        </tr>
      `
      )
      .join("");

    const html = `
      <html>
        <head>
          <title>Contract Report</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 24px; color: #111; }
            .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ddd; padding-bottom: 12px; margin-bottom: 16px; }
            .logo { width: 180px; height: auto; object-fit: contain; }
            .meta { text-align: right; font-size: 13px; color: #444; }
            h1 { margin: 0; font-size: 21px; }
            p { margin: 6px 0 14px; color: #444; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; font-size: 13px; text-align: left; vertical-align: top; }
            th { background: #f4f4f4; }
          </style>
        </head>
        <body>
          <div class="header">
            <img class="logo" src="${DOCUMENT_LOGO_SRC}" alt="GTS Mono Logo" />
            <div class="meta">
              <div>AI Legal Consultant</div>
              <div>${new Date().toLocaleString()}</div>
            </div>
          </div>

          <h1>Contracts Report</h1>
          <p>Prepared for contracts, invoices, and printing workflows.</p>

          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Activity</th>
                <th>Document</th>
                <th>Jurisdiction</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </body>
      </html>
    `;

    printWindow.document.open();
    printWindow.document.write(html);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => printWindow.print(), 250);
  };

  const clearLogs = () => {
    setLogs([]);
    notify("Logs cleared.", "info");
  };

  return (
    <div className="glass-page p-6 max-w-7xl mx-auto space-y-6">
      <header className="glass-card p-6 rounded-2xl flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div>
          <div className="text-sm text-white/70">AILegalConsultant</div>
          <h1 className="text-2xl font-semibold text-white">AI Legal Consultant</h1>
          <p className="text-white/70 text-sm">
            Specialized in tax, corporate, transport, intellectual property, contracts, and compliance.
          </p>
          <div className="flex flex-wrap gap-2 mt-3 text-xs">
            <span className="rounded-full bg-amber-500/20 text-amber-100 px-2 py-1 font-semibold">TAX</span>
            <span className="rounded-full bg-emerald-500/20 text-emerald-100 px-2 py-1 font-semibold">CORP</span>
            <span className="rounded-full bg-sky-500/20 text-sky-100 px-2 py-1 font-semibold">TRANSPORT</span>
            <span className="rounded-full bg-violet-500/20 text-violet-100 px-2 py-1 font-semibold">IP</span>
            <span className="rounded-full bg-rose-500/20 text-rose-100 px-2 py-1 font-semibold">CONTRACTS</span>
            <span className="rounded-full bg-indigo-500/20 text-indigo-100 px-2 py-1 font-semibold">COMPLIANCE</span>
          </div>
        </div>
        <div className="flex flex-col items-start lg:items-end gap-2 text-sm text-white/70">
          <span className="rounded-full border border-emerald-400/40 bg-emerald-500/15 px-3 py-1 text-xs font-semibold text-emerald-100">
            Advanced intelligence mode
          </span>
          <span>Last updated: {lastUpdated}</span>
          <button type="button" className="glass-card px-4 py-2 text-white hover:bg-white/10" onClick={() => setShowOmChat(true)}>
            Operations Manager
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section className="space-y-6">
          <div className="glass-card p-6 rounded-2xl space-y-4">
            <div className="text-white font-semibold">Document Review</div>
            <div
              className="rounded-xl border border-dashed border-white/20 p-4 text-center text-white/70"
              onDragOver={(event) => event.preventDefault()}
              onDrop={handleFileDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.rtf,.xlsx,.xls"
                style={{ display: "none" }}
                onChange={handleFileSelect}
              />
              <div className="text-white text-sm font-semibold">Drop documents here</div>
              <button type="button" className="text-sky-200 underline mt-2" onClick={openFilePicker}>
                Browse files
              </button>
              <div className="text-xs text-white/50 mt-2">
                Contracts, policies, tax documents. Up to 10 files, 20MB each.
              </div>
            </div>
            {!!selectedFiles.length && (
              <ul className="space-y-2 text-sm text-white/80">
                {selectedFiles.map((file) => (
                  <li key={file.name} className="flex items-center justify-between gap-3">
                    <span className="truncate">{file.name}</span>
                    <span className="text-xs text-white/60">{formatFileSize(file.size)}</span>
                    <button type="button" className="text-xs text-rose-200" onClick={() => removeFile(file)}>
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <div className="flex flex-wrap gap-2">
              <button type="button" className="glass-card px-4 py-2 text-white hover:bg-white/10" disabled={!selectedFiles.length} onClick={analyzeDocuments}>
                Analyze
              </button>
              <button type="button" className="glass-card px-4 py-2 text-white hover:bg-white/10" onClick={clearFiles}>
                Clear
              </button>
              <button type="button" className="glass-card px-4 py-2 text-white hover:bg-white/10" disabled={!selectedFiles.length} onClick={analyzeBulkDocuments}>
                Bulk analyze
              </button>
            </div>
          </div>

          <div className="glass-card p-6 rounded-2xl space-y-4">
            <GlobalTransportLaws />
          </div>


          <div className="glass-card p-6 rounded-2xl space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="text-white font-semibold">Analysis Results</div>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  className="glass-card px-3 py-2 text-white"
                  onClick={exportAnalysis}
                  disabled={!analysisResults}
                >
                  Export report
                </button>
                <button
                  type="button"
                  className="glass-card px-3 py-2 text-white"
                  onClick={sendToOperationManager}
                  disabled={!analysisResults}
                >
                  Send to operations
                </button>
              </div>
            </div>
            {analysisResults ? (
              <div className="space-y-4 text-sm text-white/80">
                <div className="grid gap-2 sm:grid-cols-3">
                  <div>
                    <div className="text-xs text-white/60">Analysis field</div>
                    <div className="font-semibold text-white">{analysisResults.analysisField}</div>
                  </div>
                  <div>
                    <div className="text-xs text-white/60">Analyzed at</div>
                    <div className="font-semibold text-white">{analysisResults.analyzedAt}</div>
                  </div>
                  <div>
                    <div className="text-xs text-white/60">Total clauses</div>
                    <div className="font-semibold text-white">{analysisResults.totalClauses}</div>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-white/60">Risk score</div>
                  <div className="text-2xl font-semibold text-white">{analysisResults.riskScore}%</div>
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden mt-2">
                    <div
                      className={`h-full ${riskClass(analysisResults.riskScore)}`}
                      style={{ width: `${analysisResults.riskScore}%` }}
                    />
                  </div>
                </div>
                <div className="grid gap-2 sm:grid-cols-3 text-xs text-white/70">
                  <span>Tax: {analysisResults.taxRisk}%</span>
                  <span>Contract: {analysisResults.contractRisk}%</span>
                  <span>Compliance: {analysisResults.complianceRisk}%</span>
                </div>
                <div>
                  <div className="text-white font-semibold">Detailed findings</div>
                  <div className="space-y-2">
                    {analysisResults.findings.map((finding) => (
                      <div key={finding.id} className="rounded-lg border border-white/10 p-3">
                        <div className="flex flex-wrap gap-2 text-white font-semibold">
                          <span>{finding.title}</span>
                          <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs">
                            {severityLabel(finding.severity)}
                          </span>
                          <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs">
                            {finding.category}
                          </span>
                        </div>
                        <div className="text-white/70 mt-2">{finding.description}</div>
                        {finding.legalReference ? (
                          <div className="text-xs text-white/50 mt-2">
                            Reference: {finding.legalReference}
                          </div>
                        ) : null}
                        {finding.suggestion ? (
                          <div className="text-xs text-white/50">
                            Recommendation: {finding.suggestion}
                          </div>
                        ) : null}
                        {finding.alternativeClause ? (
                          <div className="text-xs text-white/50">
                            Alternative clause: {finding.alternativeClause}
                          </div>
                        ) : null}
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="text-white font-semibold">Compliance matrix</div>
                  <div className="space-y-2 mt-2">
                    {(analysisResults.compliance?.regulations || []).map((item) => (
                      <div key={item.name} className="flex items-center justify-between text-xs text-white/70">
                        <span>{item.name}</span>
                        <span>{statusLabel(item.status)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-sm text-white/60">No analysis yet. Upload a document to begin.</div>
            )}
          </div>
        </section>

        <section className="space-y-6">
          <div className="glass-card p-6 rounded-2xl space-y-4">
            <div className="text-white font-semibold">Control Center</div>
            <div className="grid gap-2 sm:grid-cols-2">
              {LEGAL_FIELDS.map((field) => (
                <button
                  key={field.id}
                  type="button"
                  className={`rounded-xl border px-3 py-2 text-left text-sm ${selectedField?.id === field.id ? "border-sky-400/60 bg-sky-500/10" : "border-white/10 bg-white/5"}`}
                  onClick={() => selectLegalField(field)}
                >
                  <div className="text-white font-semibold">{field.name}</div>
                  <div className="text-xs text-white/60">{field.count} items</div>
                </button>
              ))}
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              {LEGAL_ACTIONS.map((action) => (
                <button
                  key={action.id}
                  type="button"
                  className={`rounded-xl border px-3 py-2 text-left text-sm ${selectedAction?.id === action.id ? "border-emerald-400/60 bg-emerald-500/10" : "border-white/10 bg-white/5"}`}
                  onClick={() => selectAction(action)}
                >
                  <div className="text-white font-semibold">{action.label}</div>
                  {action.premium && <div className="text-xs text-amber-200">PRO</div>}
                </button>
              ))}
            </div>
            <textarea
              className="w-full rounded-lg bg-white/10 border border-white/10 px-3 py-2 text-sm text-white"
              rows={3}
              placeholder="Describe the legal task."
              value={botMessage}
              onChange={(event) => setBotMessage(event.target.value)}
            />
            <div className="flex flex-wrap gap-2 text-xs text-white/60">
              {QUICK_QUERIES.map((query) => (
                <button
                  key={query}
                  type="button"
                  className="rounded-full border border-white/10 px-3 py-1 text-white/70 hover:text-white"
                  onClick={() => setBotMessage(query)}
                >
                  {query}
                </button>
              ))}
            </div>
            <div className="rounded-xl border border-white/10 p-4 space-y-3">
              <div className="text-white font-semibold">Operations manager</div>
              <select
                className="w-full rounded-lg bg-white/10 border border-white/10 px-3 py-2 text-sm text-white"
                value={selectedOmRequestType}
                onChange={(event) => setSelectedOmRequestType(event.target.value)}
              >
                {OM_REQUEST_TYPES.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
              <textarea
                className="w-full rounded-lg bg-white/10 border border-white/10 px-3 py-2 text-sm text-white"
                rows={2}
                placeholder="Message to operations manager"
                value={omMessage}
                onChange={(event) => setOmMessage(event.target.value)}
              />
              <div className="flex gap-2">
                <button type="button" className="glass-card px-3 py-2 text-white" onClick={sendToOperationManager}>
                  Send
                </button>
                <button type="button" className="glass-card px-3 py-2 text-white" onClick={() => notify("Loading request history...", "info")}>
                  View requests
                </button>
              </div>
              {recentOmRequests.length ? (
                <div className="space-y-2 text-xs text-white/70">
                  {recentOmRequests.map((request) => (
                    <div key={request.id} className="rounded-lg border border-white/10 p-2">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold">{request.type}</span>
                        <span className="rounded-full bg-white/10 px-2 py-0.5">{request.status}</span>
                      </div>
                      <div className="text-white/60">{request.message}</div>
                      <div className="flex items-center justify-between text-white/40">
                        <span>{request.date}</span>
                        <span>{request.id}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
            <div className="rounded-xl border border-white/10 p-4 space-y-2">
              <div className="flex items-center justify-between text-white font-semibold">
                <span>Advanced context (JSON)</span>
                <div className="flex gap-2 text-xs">
                  <button type="button" onClick={toggleJsonEditor}>{showJsonEditor ? "Hide" : "Show"}</button>
                  <button type="button" onClick={validateJson}>Validate</button>
                </div>
              </div>
              {showJsonEditor ? (
                <textarea
                  className="w-full rounded-lg bg-white/10 border border-white/10 px-3 py-2 text-sm text-white"
                  rows={4}
                  value={advancedContext}
                  onChange={(event) => setAdvancedContext(event.target.value)}
                />
              ) : null}
              <div className="flex flex-wrap gap-2 text-xs text-white/60">
                <button type="button" onClick={() => loadPreset("tax_review")}>Tax review</button>
                <button type="button" onClick={() => loadPreset("transport_contract")}>Transport contract</button>
                <button type="button" onClick={() => loadPreset("corporate_compliance")}>Corporate compliance</button>
                <button type="button" onClick={() => loadPreset("international_trade")}>International trade</button>
              </div>
            </div>
            <div className="flex gap-2">
              <button type="button" className="glass-card px-4 py-2 text-white" disabled={isRunning} onClick={runLegalConsultant}>
                {isRunning ? "Working..." : "Run legal consultant"}
              </button>
              <button type="button" className="glass-card px-4 py-2 text-white" onClick={refreshLegalStatus}>
                Refresh status
              </button>
            </div>
          </div>

          <div className="glass-card p-6 rounded-2xl space-y-4">
            <div className="text-white font-semibold">Activity Logs</div>
            <div className="flex flex-wrap gap-2 text-xs text-white/60">
              {LOG_FILTERS.map((filter) => (
                <button
                  key={filter.value}
                  type="button"
                  className={`rounded-full px-3 py-1 border ${activeLogFilters.includes(filter.value) ? "border-sky-300/50 text-sky-100" : "border-white/10"}`}
                  onClick={() => toggleLogFilter(filter.value)}
                >
                  {filter.label}
                </button>
              ))}
            </div>
            <div className="space-y-2 text-sm text-white/70">
              {filteredLogs.length ? (
                filteredLogs.map((log) => (
                  <div key={log.id} className="rounded-lg border border-white/10 p-3">
                    <div className="flex items-center justify-between text-white">
                      <span>{log.message}</span>
                      <span className="text-xs text-white/50">{log.timestamp}</span>
                    </div>
                    <div className="flex flex-wrap gap-2 text-xs text-white/50 mt-1">
                      <span className="rounded-full bg-white/10 px-2 py-0.5">
                        {logTypeLabel(log.type)}
                      </span>
                      {log.jurisdiction ? (
                        <span className="rounded-full bg-white/10 px-2 py-0.5">{log.jurisdiction}</span>
                      ) : null}
                      {log.legalField ? (
                        <span className="rounded-full bg-white/10 px-2 py-0.5">{log.legalField}</span>
                      ) : null}
                    </div>
                    {log.document ? <div className="text-xs text-white/50">{log.document}</div> : null}
                    {log.details ? (
                      <pre className="mt-2 rounded-lg bg-white/5 p-2 text-xs text-white/60 overflow-x-auto">
                        {JSON.stringify(log.details, null, 2)}
                      </pre>
                    ) : null}
                  </div>
                ))
              ) : (
                <div className="text-white/50">No activity yet.</div>
              )}
            </div>
            <div className="flex gap-2">
              <button type="button" className="glass-card px-3 py-2 text-white" onClick={exportLegalLogs}>
                Export logs
              </button>
              <button type="button" className="glass-card px-3 py-2 text-white" onClick={printContractReport}>
                Print contract report
              </button>
              <button type="button" className="glass-card px-3 py-2 text-white" onClick={clearLogs}>
                Clear
              </button>
            </div>
          </div>

          <div className="glass-card p-6 rounded-2xl space-y-3">
            <div className="text-white font-semibold">System Overview</div>
            <div className="grid gap-2 text-sm text-white/70 sm:grid-cols-2">
              <div>
                <div className="text-xs text-white/50">Status</div>
                <div className="text-white">Integrated</div>
              </div>
              <div>
                <div className="text-xs text-white/50">Version</div>
                <div className="text-white">2.0.0</div>
              </div>
              <div>
                <div className="text-xs text-white/50">Countries</div>
                <div className="text-white">120</div>
              </div>
              <div>
                <div className="text-xs text-white/50">Laws stored</div>
                <div className="text-white">15,000+</div>
              </div>
              <div>
                <div className="text-xs text-white/50">Documents reviewed</div>
                <div className="text-white">{analyzedDocuments}</div>
              </div>
              <div>
                <div className="text-xs text-white/50">Average analysis time</div>
                <div className="text-white">3.8 seconds</div>
              </div>
              <div>
                <div className="text-xs text-white/50">Accuracy</div>
                <div className="text-white">94.7%</div>
              </div>
              <div>
                <div className="text-xs text-white/50">Contact</div>
                <div className="text-white">operations@gabanilogistics.com</div>
              </div>
            </div>
            <div className="space-y-2 text-xs text-white/60">
              <div>
                <span>Tax</span>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-amber-400" style={{ width: `${stats.tax}%` }} />
                </div>
              </div>
              <div>
                <span>Transport</span>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-sky-400" style={{ width: `${stats.transport}%` }} />
                </div>
              </div>
              <div>
                <span>Corporate</span>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-400" style={{ width: `${stats.corporate}%` }} />
                </div>
              </div>
              <div>
                <span>Intellectual Property</span>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-violet-400" style={{ width: `${stats.ip}%` }} />
                </div>
              </div>
            </div>
            <div className="text-xs text-white/50">All requests are routed through operations management.</div>
          </div>
        </section>
      </div>

      {showOmChat ? (
        <div className="fixed inset-0 bg-slate-900/70 flex items-center justify-center z-50">
          <div className="glass-card p-6 rounded-2xl w-full max-w-lg space-y-4">
            <div className="flex items-center justify-between text-white">
              <span className="font-semibold">Operations manager chat</span>
              <button type="button" className="text-white/60" onClick={() => setShowOmChat(false)}>
                Close
              </button>
            </div>
            <div className="space-y-3 text-sm text-white/70 max-h-64 overflow-y-auto">
              {omChatMessages.map((msg) => (
                <div key={msg.id} className="rounded-lg border border-white/10 p-3">
                  <div className="text-xs text-white/50">{msg.sender === "user" ? "You" : "Operations manager"}</div>
                  <div>{msg.content}</div>
                  <div className="text-xs text-white/40">{msg.time}</div>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <textarea
                className="flex-1 rounded-lg bg-white/10 border border-white/10 px-3 py-2 text-sm text-white"
                rows={2}
                value={omChatInput}
                onChange={(event) => setOmChatInput(event.target.value)}
                placeholder="Write a message"
              />
              <button type="button" className="glass-card px-4 py-2 text-white" onClick={sendOmChatMessage}>
                Send
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {notification ? (
        <div
          className={`fixed bottom-6 right-6 glass-card px-4 py-3 rounded-xl text-sm border ${notificationClass(notification.type)}`}
        >
          {notification.message}
        </div>
      ) : null}
    </div>
  );
}
