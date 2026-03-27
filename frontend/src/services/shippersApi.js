import axiosClient from "../api/axiosClient";

const API_BASE = "/api/v1/shippers";

const normalizeListResponse = (data) => {
    if (Array.isArray(data)) {
        return { items: data, total: data.length };
    }

    const items =
        data?.items || data?.shippers || data?.data || [];

    return {
        items: Array.isArray(items) ? items : [],
        total: Number.isFinite(data?.total) ? data.total : items?.length || 0,
    };
};

export const listShippers = async (params = {}) => {
    const response = await axiosClient.get(API_BASE + "/", { params });
    return normalizeListResponse(response?.data || {});
};

export const getShipper = async (shipperId) => {
    if (!shipperId) return null;
    const response = await axiosClient.get(`${API_BASE}/${shipperId}`);
    return response?.data;
};

export const createShipper = async (payload) => {
    const response = await axiosClient.post(API_BASE + "/", payload);
    return response?.data;
};

export const updateShipper = async (shipperId, payload) => {
    if (!shipperId) return null;
    const response = await axiosClient.put(`${API_BASE}/${shipperId}`, payload);
    return response?.data;
};

export const deleteShipper = async (shipperId) => {
    if (!shipperId) return null;
    const response = await axiosClient.delete(`${API_BASE}/${shipperId}`);
    return response?.data;
};

export const verifyShipper = async (payload) => {
    const response = await axiosClient.post(`${API_BASE}/verify`, payload);
    return response?.data;
};

export const getShipperStats = async () => {
    const response = await axiosClient.get(`${API_BASE}/stats/summary`);
    return response?.data;
};

export const getRecentShippers = async (limit = 10) => {
    try {
        const response = await axiosClient.get(`${API_BASE}/recent`, {
            params: { limit }
        });
        return normalizeListResponse(response?.data || {});
    } catch {
        const fallback = await listShippers({ page: 1, per_page: limit });
        return {
            items: fallback.items.slice(0, limit),
            total: fallback.total,
        };
    }
};
