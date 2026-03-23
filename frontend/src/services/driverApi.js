import axiosClient from "../api/axiosClient";

const BASE = "/api/v1";

export const getDriverShipments = async () => {
  const response = await axiosClient.get(`${BASE}/driver/shipments`);
  return response?.data || [];
};

export const postDriverCheckpoint = async (shipmentId, payload) => {
  const response = await axiosClient.post(
    `${BASE}/driver/shipments/${shipmentId}/checkpoint`,
    payload
  );
  return response?.data;
};

export const postDriverLocation = async (payload) => {
  const response = await axiosClient.post(`${BASE}/driver/location`, payload);
  return response?.data;
};
