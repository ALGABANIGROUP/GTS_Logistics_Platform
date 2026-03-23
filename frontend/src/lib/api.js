import axiosClient from "../api/axiosClient";
import {
  clearAuthCache,
  readAuthToken,
  writeAuthToken,
} from "../utils/authStorage";

const unwrap = (response) => response?.data ?? response;

const request = async (config) => {
  const response = await axiosClient.request(config);
  return response;
};

const requestJson = async (config) => unwrap(await request(config));

const normalizeAnalysis = (payload) => {
  const report =
    payload?.result?.report ||
    payload?.report ||
    payload?.data?.report ||
    payload?.data ||
    {};
  const finance = report?.finance || {};
  const revenue =
    finance.revenue_total ??
    finance.total_revenue ??
    finance.total_income ??
    0;
  const expenses =
    finance.expenses_total ??
    finance.total_expenses ??
    finance.total_cost ??
    0;
  const profit =
    report?.kpis?.profit ??
    (typeof revenue === "number" && typeof expenses === "number"
      ? revenue - expenses
      : 0);

  return {
    total_income: revenue,
    total_expense: expenses,
    profit,
    month: report?.period_label || report?.period?.start || "",
    report,
  };
};

export const API_BASE =
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_BASE_URL) ||
  "";

export function getValidAuthToken() {
  return readAuthToken() || null;
}

export async function ensureAuthToken() {
  const token = readAuthToken();
  if (!token) {
    throw new Error("Authentication required");
  }
  return token;
}

export async function apiFetch(path, opts = {}) {
  const method = opts.method || "GET";
  const responseType = opts.responseType || "json";
  const data = opts.body;
  return request({
    url: path,
    method,
    data,
    headers: opts.headers,
    responseType,
  });
}

export async function fetchJson(path, opts = {}) {
  return requestJson({
    url: path,
    method: opts.method || "GET",
    data: opts.body,
    headers: opts.headers,
  });
}

export function getAuthHeaders() {
  const token = readAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function authFetch(path, opts = {}) {
  return apiFetch(path, opts);
}

export async function authFetchJson(path, opts = {}) {
  return fetchJson(path, opts);
}

export async function getDevToken() {
  throw new Error("Dev token flow has been removed. Use the normal login flow.");
}

export function storeAuthToken(token) {
  if (token) {
    writeAuthToken(token);
  }
}

export function clearAuthToken() {
  clearAuthCache();
}

export function isAuthenticated() {
  return Boolean(readAuthToken());
}

export async function getWeeklyReport() {
  return authFetchJson("/reports/weekly");
}

export async function getWeeklyReportMd() {
  return authFetchJson("/reports/weekly/md");
}

export async function getWeeklyReportFileResponse() {
  return authFetch("/reports/weekly/file", {
    method: "GET",
    responseType: "blob",
  });
}

export async function getAiGeneralAnalysis(payload = {}) {
  const res = await runAIBot("general_manager", {
    message: "analysis",
    context: payload || {},
    meta: { source: "ui" },
  });
  return normalizeAnalysis(res);
}

export async function runAIBot(botName, payload = {}) {
  if (!botName) throw new Error("botName is required");
  return authFetchJson(`/api/v1/ai/bots/available/${encodeURIComponent(botName)}/run`, {
    method: "POST",
    body: payload,
  });
}
