import axiosClient from "../api/axiosClient";

const BASE = "/api/v1";

export const getDispatchBoard = async (params = {}) => {
  const response = await axiosClient.get(`${BASE}/dispatch/board`, { params });
  return response?.data || {};
};

export const getDispatchInsights = async () => {
  const response = await axiosClient.get(`${BASE}/dispatch/insights`);
  return response?.data || {};
};

export const getRoutePlan = async (shipmentId) => {
  const response = await axiosClient.get(`${BASE}/dispatch/shipments/${shipmentId}/route-plan`);
  return response?.data || null;
};

export const getDriverGuidance = async (shipmentId, driverUserId) => {
  const response = await axiosClient.get(`${BASE}/dispatch/shipments/${shipmentId}/driver-guidance`, {
    params: driverUserId ? { driver_user_id: driverUserId } : undefined,
  });
  return response?.data || null;
};

export const assignShipmentToDriver = async (shipmentId, payload) => {
  const response = await axiosClient.post(`${BASE}/shipments/${shipmentId}/assign`, payload);
  return response?.data;
};

export const getDrivers = async () => {
  const response = await axiosClient.get(`${BASE}/drivers`, { params: { limit: 200, active_only: true } });
  return Array.isArray(response?.data?.drivers) ? response.data.drivers : [];
};
