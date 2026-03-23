import axiosClient from "./axiosClient";

const BASE = "/api/v1/email/ai/stats";

export const getEmailBotStats = async () => {
  const response = await axiosClient.get(`${BASE}/bots`);
  return response.data;
};

export const getEmailSentimentTrends = async () => {
  const response = await axiosClient.get(`${BASE}/trends`);
  return response.data;
};

export const getEmailDecisionStats = async () => {
  const response = await axiosClient.get(`${BASE}/decisions`);
  return response.data;
};
