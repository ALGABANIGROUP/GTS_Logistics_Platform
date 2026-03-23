import axiosClient from "../api/axiosClient";

const BASE = "/api/v1/email";

const normalizeMailboxesResponse = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.mailboxes)) return payload.mailboxes;
  if (payload && Array.isArray(payload.data)) return payload.data;
  return [];
};

export const listMailboxes = async () => {
  const response = await axiosClient.get(`${BASE}/mailboxes`);
  return normalizeMailboxesResponse(response.data);
};

export const listMyMailboxes = async () => {
  const response = await axiosClient.get(`${BASE}/my/mailboxes`);
  return normalizeMailboxesResponse(response.data);
};

export const setMailboxMode = async (mailboxId, mode) => {
  const response = await axiosClient.post(`${BASE}/mailboxes/${mailboxId}/mode`, { mode });
  return response.data;
};

export const setGlobalMode = async (mode) => {
  const response = await axiosClient.post(`${BASE}/mode`, { mode });
  return response.data;
};

export const listMessages = async (mailboxId, params = {}) => {
  const response = await axiosClient.get(`${BASE}/messages`, {
    params: { mailbox_id: mailboxId, ...params },
  });
  return response.data || [];
};

export const listMyMessages = async (mailboxId, params = {}) => {
  const response = await axiosClient.get(`${BASE}/my/messages`, {
    params: { mailbox_id: mailboxId, ...params },
  });
  return response.data || [];
};

export const getMyMessage = async (messageId) => {
  const response = await axiosClient.get(`${BASE}/my/messages/${messageId}`);
  return response.data;
};

export const getThread = async (threadId) => {
  const response = await axiosClient.get(`${BASE}/threads/${threadId}`);
  return response.data;
};

export const updateThread = async (threadId, payload) => {
  const response = await axiosClient.patch(`${BASE}/threads/${threadId}`, payload);
  return response.data;
};

export const approveMessage = async (messageId, payload = {}) => {
  const response = await axiosClient.post(`${BASE}/messages/${messageId}/approve`, payload);
  return response.data;
};

export const pollMailboxes = async () => {
  const response = await axiosClient.post(`${BASE}/poll`);
  return response.data;
};

export const sendMessage = async (payload) => {
  const response = await axiosClient.post(`${BASE}/send`, payload);
  return response.data;
};

export const createMailbox = async (payload) => {
  const response = await axiosClient.post(`${BASE}/mailboxes`, payload);
  return response.data;
};

export const updateMailbox = async (mailboxId, payload) => {
  const response = await axiosClient.patch(`${BASE}/mailboxes/${mailboxId}`, payload);
  return response.data;
};

export const deleteMailbox = async (mailboxId) => {
  const response = await axiosClient.delete(`${BASE}/mailboxes/${mailboxId}`);
  return response.data;
};

export const requestMailbox = async (payload) => {
  const response = await axiosClient.post(`${BASE}/requests`, payload);
  return response.data;
};

export const listMailboxRequests = async () => {
  const response = await axiosClient.get(`${BASE}/requests`);
  return response.data || [];
};

export const approveMailboxRequest = async (requestId, payload = {}) => {
  const response = await axiosClient.post(`${BASE}/requests/${requestId}/approve`, payload);
  return response.data;
};

export const rejectMailboxRequest = async (requestId, payload = {}) => {
  const response = await axiosClient.post(`${BASE}/requests/${requestId}/reject`, payload);
  return response.data;
};

export const assignBotToMailbox = async (mailboxId, botKey, config = {}) => {
  const response = await axiosClient.patch(`${BASE}/mailboxes/${mailboxId}/assign-bot`, {
    bot_key: botKey,
    config,
  });
  return response.data;
};

export const getAssignedBot = async (mailboxId) => {
  const response = await axiosClient.get(`${BASE}/mailboxes/${mailboxId}/assigned-bot`);
  return response.data;
};

export const getRoutingRules = async (mailboxId) => {
  const response = await axiosClient.get(`${BASE}/mailboxes/${mailboxId}/rules`);
  return response.data;
};

export const createRoutingRule = async (mailboxId, payload) => {
  const response = await axiosClient.post(`${BASE}/mailboxes/${mailboxId}/rules`, payload);
  return response.data;
};

export const getRoutingRule = async (ruleId) => {
  const response = await axiosClient.get(`${BASE}/rules/${ruleId}`);
  return response.data;
};

export const updateRoutingRule = async (ruleId, payload) => {
  const response = await axiosClient.patch(`${BASE}/rules/${ruleId}`, payload);
  return response.data;
};

export const deleteRoutingRule = async (ruleId) => {
  const response = await axiosClient.delete(`${BASE}/rules/${ruleId}`);
  return response.data;
};

export const manuallyRouteMessage = async (messageId) => {
  const response = await axiosClient.post(`${BASE}/messages/${messageId}/route`);
  return response.data;
};
