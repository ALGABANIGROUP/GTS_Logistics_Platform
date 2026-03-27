import axiosClient from "../api/axiosClient";

const API_BASE = "/api/v1/carriers";

const normalizeListResponse = (data) => {
    if (Array.isArray(data)) {
        return { items: data, total: data.length };
    }

    const items =
        data?.items || data?.carriers || data?.data || [];

    return {
        items: Array.isArray(items) ? items : [],
        total: Number.isFinite(data?.total) ? data.total : items?.length || 0,
    };
};

export const listCarriers = async (params = {}) => {
    const response = await axiosClient.get(API_BASE + "/", { params });
    return normalizeListResponse(response?.data || {});
};

export const getCarrier = async (carrierId) => {
    if (!carrierId) return null;
    const response = await axiosClient.get(`${API_BASE}/${carrierId}`);
    return response?.data;
};

export const createCarrier = async (payload) => {
    const response = await axiosClient.post(API_BASE + "/", payload);
    return response?.data;
};

export const updateCarrier = async (carrierId, payload) => {
    if (!carrierId) return null;
    const response = await axiosClient.put(`${API_BASE}/${carrierId}`, payload);
    return response?.data;
};

export const deleteCarrier = async (carrierId) => {
    if (!carrierId) return null;
    const response = await axiosClient.delete(`${API_BASE}/${carrierId}`);
    return response?.data;
};

export const verifyCarrier = async (payload) => {
    const response = await axiosClient.post(`${API_BASE}/verify`, payload);
    return response?.data;
};

export const getCarrierStats = async () => {
    const response = await axiosClient.get(`${API_BASE}/stats/summary`);
    return response?.data;
};

export const getRecentCarriers = async (limit = 10) => {
    try {
        const response = await axiosClient.get(`${API_BASE}/recent`, {
            params: { limit }
        });
        return normalizeListResponse(response?.data || {});
    } catch {
        const fallback = await listCarriers({ page: 1, per_page: limit });
        return {
            items: fallback.items.slice(0, limit),
            total: fallback.total,
        };
    }
};
