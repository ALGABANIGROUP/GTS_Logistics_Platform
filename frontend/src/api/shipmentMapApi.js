import axiosClient from "./axiosClient";

export const getShipmentLiveData = async (shipmentId) => {
  const response = await axiosClient.get(`/api/v1/shipments/${shipmentId}/live`);
  return response?.data?.data || response?.data || null;
};
