import axiosClient from "../api/axiosClient";

const API_BASE = "/api/v1";
const CUSTOMER_SERVICE_API = `${API_BASE}/customer-service`;

const toArray = (value, fallback = []) => (Array.isArray(value) ? value : fallback);

const normalizeConversation = (item = {}) => ({
    id: item.id,
    userId: item.userId ?? item.user_id,
    customerName: item.customerName ?? item.customer_name ?? "Customer",
    channel: item.channel ?? "webchat",
    status: item.status ?? "active",
    unread: Boolean(item.unread ?? item.unreadCount ?? item.unread_count),
    unreadCount: item.unreadCount ?? item.unread_count ?? 0,
    createdAt: item.createdAt ?? item.created_at,
    lastUpdatedAt: item.lastUpdatedAt ?? item.last_updated_at,
    lastMessage: item.lastMessage ?? item.last_message ?? "",
    lastMessageTime: item.lastMessageTime ?? item.last_updated_at ?? "now",
    messageCount: item.messageCount ?? item.message_count ?? 0,
    sentiment: item.sentiment ?? "neutral",
    language: item.language ?? "en",
    intent: item.intent ?? "unknown",
    needsHuman: Boolean(item.needsHuman ?? item.needs_human),
    linkedTicketId: item.linkedTicketId ?? item.linked_ticket_id ?? null,
});

const normalizeMessage = (item = {}) => ({
    id: item.id ?? `${item.role || item.sender}-${item.timestamp || Date.now()}`,
    sender: item.sender ?? (item.role === "user" ? "customer" : item.role) ?? "bot",
    role: item.role ?? (item.sender === "customer" ? "user" : item.sender) ?? "bot",
    text: item.text ?? item.content ?? "",
    content: item.content ?? item.text ?? "",
    timestamp: item.timestamp ?? new Date().toISOString(),
    read: item.read ?? true,
    intent: item.intent,
    sentiment: item.sentiment,
    language: item.language,
});

const normalizeTicket = (item = {}) => ({
    id: item.id,
    ticketNumber: item.ticketNumber ?? item.ticket_number ?? `TKT-${item.id}`,
    customerEmail: item.customerEmail ?? item.customer_email ?? "",
    customerName: item.customerName ?? item.customer_name ?? "",
    subject: item.subject ?? item.title ?? "",
    description: item.description ?? "",
    status: item.status ?? "open",
    priority: item.priority ?? "medium",
    category: item.category ?? "general",
    assignedTo: item.assignedTo ?? item.assigned_to ?? null,
    comments: toArray(item.comments),
    createdAt: item.createdAt ?? item.created_at,
    updatedAt: item.updatedAt ?? item.updated_at,
});

export const customerServiceAPI = {
    getConversations: async (filters = {}) => {
        try {
            const response = await axiosClient.get(`${CUSTOMER_SERVICE_API}/conversations`, { params: filters });
            return toArray(response.data?.conversations).map(normalizeConversation);
        } catch (error) {
            console.error("Failed to fetch conversations:", error);
            return [];
        }
    },

    getConversationMessages: async (conversationId) => {
        try {
            const response = await axiosClient.get(`${CUSTOMER_SERVICE_API}/conversations/${conversationId}/messages`);
            return toArray(response.data?.messages).map(normalizeMessage);
        } catch (error) {
            console.error("Failed to fetch messages:", error);
            return [];
        }
    },

    startConversation: async (data) => {
        try {
            const response = await axiosClient.post(`${CUSTOMER_SERVICE_API}/conversations`, data);
            return normalizeConversation(response.data?.conversation || {});
        } catch (error) {
            console.error("Failed to start conversation:", error);
            throw error;
        }
    },

    markAsRead: async (conversationId) => {
        try {
            await axiosClient.post(`${CUSTOMER_SERVICE_API}/conversations/${conversationId}/read`);
        } catch (error) {
            console.error("Failed to mark as read:", error);
        }
    },

    markConversationAsRead: async (conversationId) => {
        return customerServiceAPI.markAsRead(conversationId);
    },

    generateAIResponse: async (conversationId, messages) => {
        try {
            const response = await axiosClient.post(`${CUSTOMER_SERVICE_API}/ai/response`, {
                conversation_id: conversationId,
                context: messages,
            });
            return {
                ...response.data,
                suggestion: response.data?.suggestion ?? response.data?.response ?? "",
            };
        } catch (error) {
            console.error("Failed to generate AI response:", error);
            throw error;
        }
    },

    getLiveStats: async () => {
        try {
            const response = await axiosClient.get(`${CUSTOMER_SERVICE_API}/analytics/live-stats`);
            return response.data || {
                activeConversations: 0,
                pendingTickets: 0,
                avgResponseTime: "0m",
                satisfactionRate: "0%",
            };
        } catch (error) {
            console.error("Failed to fetch live stats:", error);
            return {
                activeConversations: 0,
                pendingTickets: 0,
                avgResponseTime: "0m",
                satisfactionRate: "0%",
            };
        }
    },

    getRecentActivity: async (timeRange = "today") => {
        try {
            const response = await axiosClient.get(`${CUSTOMER_SERVICE_API}/analytics/recent-activity`, {
                params: { range: timeRange },
            });
            return toArray(response.data?.activity);
        } catch (error) {
            console.error("Failed to fetch recent activity:", error);
            return [];
        }
    },

    getTopAgents: async () => {
        try {
            const response = await axiosClient.get(`${CUSTOMER_SERVICE_API}/analytics/top-agents`);
            return toArray(response.data?.agents);
        } catch (error) {
            console.error("Failed to fetch top agents:", error);
            return [];
        }
    },

    getConversationMetrics: async (timeRange = "today") => {
        try {
            const response = await axiosClient.get(`${CUSTOMER_SERVICE_API}/analytics/conversation-metrics`, {
                params: { range: timeRange },
            });
            return response.data || {
                total: 0,
                resolved: 0,
                escalated: 0,
                avgDuration: "0m",
            };
        } catch (error) {
            console.error("Failed to fetch conversation metrics:", error);
            return {
                total: 0,
                resolved: 0,
                escalated: 0,
                avgDuration: "0m",
            };
        }
    },

    getTickets: async (filters = {}) => {
        try {
            const response = await axiosClient.get(`${CUSTOMER_SERVICE_API}/tickets`, { params: filters });
            const payload = Array.isArray(response.data) ? response.data : response.data?.tickets;
            return toArray(payload).map(normalizeTicket);
        } catch (error) {
            console.error("Failed to fetch tickets:", error);
            return [];
        }
    },

    createTicket: async (data) => {
        try {
            const response = await axiosClient.post(`${CUSTOMER_SERVICE_API}/tickets`, {
                customer_email: data.customerEmail || data.customer_email || "support@gts.local",
                subject: data.subject,
                description: data.description,
            });
            return normalizeTicket(response.data?.ticket || response.data || {});
        } catch (error) {
            console.error("Failed to create ticket:", error);
            throw error;
        }
    },

    updateTicket: async (ticketId, data) => {
        try {
            const response = await axiosClient.put(`${CUSTOMER_SERVICE_API}/tickets/${ticketId}`, {
                subject: data.subject,
                description: data.description,
                status: data.status,
                priority: data.priority,
                assigned_to: data.assignedTo ?? data.assigned_to,
                comments: data.comments,
            });
            return normalizeTicket(response.data?.ticket || response.data || {});
        } catch (error) {
            console.error("Failed to update ticket:", error);
            throw error;
        }
    },

    closeTicket: async (ticketId, resolution = "") => {
        try {
            const response = await axiosClient.post(`${CUSTOMER_SERVICE_API}/tickets/${ticketId}/close`, {
                resolution,
            });
            return response.data;
        } catch (error) {
            console.error("Failed to close ticket:", error);
            throw error;
        }
    },

    getActiveCalls: async () => {
        try {
            const response = await axiosClient.get(`${CUSTOMER_SERVICE_API}/calls/active`);
            return toArray(response.data?.calls);
        } catch (error) {
            console.error("Failed to fetch active calls:", error);
            return [];
        }
    },

    makeOutboundCall: async (data) => {
        try {
            const response = await axiosClient.post(`${CUSTOMER_SERVICE_API}/calls/outbound`, data);
            return response.data?.call;
        } catch (error) {
            console.error("Failed to make outbound call:", error);
            throw error;
        }
    },

    answerCall: async (callId) => {
        try {
            const response = await axiosClient.post(`${CUSTOMER_SERVICE_API}/calls/${callId}/answer`);
            return response.data;
        } catch (error) {
            console.error("Failed to answer call:", error);
            throw error;
        }
    },

    endCall: async (callId) => {
        try {
            const response = await axiosClient.post(`${CUSTOMER_SERVICE_API}/calls/${callId}/end`);
            return response.data;
        } catch (error) {
            console.error("Failed to end call:", error);
            throw error;
        }
    },

    transferCall: async (callId, targetAgentId) => {
        try {
            const response = await axiosClient.post(`${CUSTOMER_SERVICE_API}/calls/${callId}/transfer`, {
                target_agent: targetAgentId,
            });
            return response.data;
        } catch (error) {
            console.error("Failed to transfer call:", error);
            throw error;
        }
    },

    startRecording: async (callId) => {
        try {
            const response = await axiosClient.post(`${CUSTOMER_SERVICE_API}/calls/${callId}/recording/start`);
            return response.data;
        } catch (error) {
            console.error("Failed to start recording:", error);
            throw error;
        }
    },

    getCampaigns: async (filters = {}) => {
        try {
            const response = await axiosClient.get(`${CUSTOMER_SERVICE_API}/messaging/campaigns`, { params: filters });
            return toArray(response.data?.campaigns);
        } catch (error) {
            console.error("Failed to fetch campaigns:", error);
            return [];
        }
    },

    createCampaign: async (data) => {
        try {
            const response = await axiosClient.post(`${CUSTOMER_SERVICE_API}/messaging/campaigns`, data);
            return response.data?.campaign;
        } catch (error) {
            console.error("Failed to create campaign:", error);
            throw error;
        }
    },

    launchCampaign: async (campaignId) => {
        try {
            const response = await axiosClient.post(`${CUSTOMER_SERVICE_API}/messaging/campaigns/${campaignId}/launch`);
            return response.data;
        } catch (error) {
            console.error("Failed to launch campaign:", error);
            throw error;
        }
    },

    sendTestMessage: async (campaignId, phoneNumber) => {
        try {
            const response = await axiosClient.post(`${CUSTOMER_SERVICE_API}/messaging/campaigns/${campaignId}/test`, {
                phone_number: phoneNumber,
            });
            return response.data;
        } catch (error) {
            console.error("Failed to send test message:", error);
            throw error;
        }
    },

    getMessageQueue: async () => {
        try {
            const response = await axiosClient.get(`${CUSTOMER_SERVICE_API}/messaging/queue`);
            return toArray(response.data?.queue);
        } catch (error) {
            console.error("Failed to fetch message queue:", error);
            return [];
        }
    },
};

export const initWebSocket = async (handlers) => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/customer-service`;

    return new Promise((resolve, reject) => {
        try {
            const ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log("Customer Service WebSocket connected");
                if (handlers.onOpen) handlers.onOpen();

                resolve({
                    send: (data) => {
                        if (ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify(data));
                        }
                    },
                    subscribe: (channel, callback) => {
                        ws.addEventListener("message", (event) => {
                            try {
                                const data = JSON.parse(event.data);
                                if (data.channel === channel) {
                                    callback(data);
                                }
                            } catch (e) {
                                console.error("Failed to parse WS message:", e);
                            }
                        });
                    },
                    addEventListener: (...args) => ws.addEventListener(...args),
                    removeEventListener: (...args) => ws.removeEventListener(...args),
                    close: () => ws.close(),
                });
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (handlers.onMessage) handlers.onMessage(data);
                } catch (e) {
                    console.error("Failed to handle WS message:", e);
                }
            };

            ws.onerror = (error) => {
                console.error("WebSocket error:", error);
                if (handlers.onError) handlers.onError(error);
                reject(error);
            };

            ws.onclose = () => {
                if (handlers.onClose) handlers.onClose();
            };
        } catch (error) {
            reject(error);
        }
    });
};
