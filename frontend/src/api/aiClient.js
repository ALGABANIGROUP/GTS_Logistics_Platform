// frontend/src/api/aiClient.js (or .ts)

import axiosClient from "./axiosClient";

// GET /ai/{name}/status
export const getBotStatus = async (name) => {
    const res = await axiosClient.get(`/api/v1/ai/bots/available/${name}/status`);
    return res.data;
};

// GET /ai/{name}/config
export const getBotConfig = async (name) => {
    const res = await axiosClient.get(`/api/v1/ai/bots/available/${name}/config`);
    return res.data;
};

// POST /ai/{name}/run
export const runBot = async (name, payload = {}) => {
    const res = await axiosClient.post(`/api/v1/ai/bots/available/${name}/run`, payload || {});
    return res.data;
};

// Finance helper (used earlier)
export const runFinanceSummary = async () => {
    const data = await runBot("finance_bot", {});
    if (data.summary) return data.summary;
    if (data.data?.summary) return data.data.summary;
    return data;
};

// NEW: GET /system/bots/status  -> used by AI Bots hub page
export const getAllBotsStatus = async () => {
    const res = await axiosClient.get("/api/v1/system/bots/status");
    return res.data;
};
