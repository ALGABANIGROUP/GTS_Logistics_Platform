import axiosClient from "../api/axiosClient.js";

const API_BASE = "/api/v1/shipments";

const normalizeListResponse = (data) => {
  if (Array.isArray(data)) {
    return { items: data, total: data.length };
  }

  const items =
    data?.items || data?.shipments || data?.data || [];

  return {
    items: Array.isArray(items) ? items : [],
    total: Number.isFinite(data?.total) ? data.total : items?.length || 0,
  };
};

export const listShipments = async (params = {}) => {
  const response = await axiosClient.get(API_BASE + "/", { params });
  return normalizeListResponse(response?.data || {});
};

export const createShipment = async (payload) => {
  const response = await axiosClient.post(API_BASE + "/", payload);
  return response?.data;
};

export const deleteShipment = async (shipmentId) => {
  if (!shipmentId) return null;
  const response = await axiosClient.delete(`${API_BASE}/${shipmentId}`);
  return response?.data;
};

export const getShipmentTimeline = async (shipmentId) => {
  if (!shipmentId) return [];
  const response = await axiosClient.get(`${API_BASE}/${shipmentId}/timeline`);
  return response?.data?.items || [];
};
