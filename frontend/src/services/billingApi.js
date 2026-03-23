import axiosClient from "../api/axiosClient";

export const getPolicyContext = async () => {
  const response = await axiosClient.get("/api/v1/policy/context");
  return response?.data || {};
};

export const getPlans = async (country) => {
  const response = await axiosClient.get("/api/v1/billing/plans", {
    params: country ? { country } : undefined,
  });
  return response?.data || {};
};

export const getAdminPricingCatalog = async (country) => {
  const response = await axiosClient.get("/api/v1/admin/billing/catalog", {
    params: country ? { country } : undefined,
  });
  return response?.data || {};
};

export const updateAdminPricingCatalog = async (payload) => {
  const response = await axiosClient.put("/api/v1/admin/billing/catalog", payload);
  return response?.data || {};
};
