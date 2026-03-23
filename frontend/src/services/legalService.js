import axiosClient from "../api/axiosClient";

// Legal Consultant API client (frontend)
// Note: All labels/strings are English-only per codebase rules.

const safeGet = async (path, params = {}) => {
  try {
    const res = await axiosClient.get(path, { params });
    return res?.data || null;
  } catch (e) {
    return { error: true, detail: e?.response?.data || e?.message || "Request failed" };
  }
};

const safePostForm = async (path, formData) => {
  try {
    const res = await axiosClient.post(path, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res?.data || null;
  } catch (e) {
    return { error: true, detail: e?.response?.data || e?.message || "Request failed" };
  }
};

export const legalService = {
  // Review endpoints
  reviewDocument: async ({ title, content, documentType, jurisdiction = "uae" }) => {
    const fd = new FormData();
    fd.append("title", title || "Untitled");
    fd.append("content", content || "");
    fd.append("document_type", documentType || "contract");
    fd.append("jurisdiction", jurisdiction);
    return safePostForm("/legal/review/document", fd);
  },
  uploadAndReview: async ({ file, documentType, jurisdiction = "uae" }) => {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("document_type", documentType || "contract");
    fd.append("jurisdiction", jurisdiction);
    return safePostForm("/legal/review/upload", fd);
  },
  reviewHistory: async ({ limit = 50, offset = 0 } = {}) =>
    safeGet("/legal/review/history", { limit, offset }),
  compareWithTemplate: async ({ documentContent, templateType }) => {
    const fd = new FormData();
    fd.append("document_content", documentContent || "");
    fd.append("template_type", templateType || "freight_contract");
    return safePostForm("/legal/review/compare", fd);
  },
  extractKeyClauses: async ({ documentContent }) => {
    const fd = new FormData();
    fd.append("document_content", documentContent || "");
    return safePostForm("/legal/review/clauses", fd);
  },

  // Compliance endpoints
  checkCompliance: async ({ activity, jurisdiction = "uae" }) =>
    safeGet("/legal/compliance/check", { activity, jurisdiction }),
  complianceStatus: async ({ jurisdiction = "uae" } = {}) =>
    safeGet("/legal/compliance/status", { jurisdiction }),
  monitorChanges: async ({ keywords = ["freight","logistics","shipping"], jurisdiction } = {}) =>
    safeGet("/legal/compliance/monitor", { keywords, jurisdiction }),
  complianceAlerts: async ({ severity, jurisdiction } = {}) =>
    safeGet("/legal/compliance/alerts", { severity, jurisdiction }),
  regulations: async ({ jurisdiction = "uae", category } = {}) =>
    safeGet("/legal/compliance/regulations", { jurisdiction, category }),

  // Bot status (optional helper)
  botStatus: async () => safeGet("/legal/status"),
};

export default legalService;
