import React, {
    createContext,
    useState,
    useContext,
    useEffect,
    useMemo,
    useCallback,
    useRef,
} from "react";
import { v4 as uuidv4 } from "uuid";
import axiosClient from "../api/axiosClient";
import { getWSClient } from "../utils/wsClient";
import { useAuth } from "./AuthContext.jsx";

const NotificationContext = createContext(null);

const STORAGE_KEY = "gts_notifications_store";
const MAX_STORE = 300;

export const notificationTypes = {
    SYSTEM: {
        id: "system",
        name: "System",
        icon: "settings",
        color: "#3B82F6",
        description: "System updates and maintenance alerts",
    },
    USER: {
        id: "user",
        name: "Users",
        icon: "person",
        color: "#10B981",
        description: "User account events and actions",
    },
    SECURITY: {
        id: "security",
        name: "Security",
        icon: "shield",
        color: "#EF4444",
        description: "Security alerts and warnings",
    },
    SHIPMENT: {
        id: "shipment",
        name: "Shipments",
        icon: "local_shipping",
        color: "#F59E0B",
        description: "Shipment updates and delivery events",
    },
    PAYMENT: {
        id: "payment",
        name: "Payments",
        icon: "payments",
        color: "#8B5CF6",
        description: "Billing and payment notifications",
    },
    REPORT: {
        id: "report",
        name: "Reports",
        icon: "assessment",
        color: "#EC4899",
        description: "Reports and analytics updates",
    },
};

export const priorities = {
    CRITICAL: {
        level: 100,
        name: "Critical",
        color: "#DC2626",
        icon: "error",
    },
    HIGH: {
        level: 80,
        name: "High",
        color: "#EA580C",
        icon: "warning",
    },
    MEDIUM: {
        level: 60,
        name: "Medium",
        color: "#F59E0B",
        icon: "info",
    },
    LOW: {
        level: 40,
        name: "Low",
        color: "#3B82F6",
        icon: "info",
    },
    INFO: {
        level: 20,
        name: "Info",
        color: "#10B981",
        icon: "check_circle",
    },
};

const normalizeNotification = (data) => {
    const now = new Date().toISOString();
    const type = String(data.type || "SYSTEM").toUpperCase();
    const priority = String(data.priority || "MEDIUM").toUpperCase();
    return {
        id: data.id || `notif_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`,
        type,
        priority,
        title: data.title || "Notification",
        message: data.message || "",
        data: data.data || {},
        icon: data.icon,
        color: data.color,
        targetRoles: Array.isArray(data.targetRoles) ? data.targetRoles : [],
        targetUsers: Array.isArray(data.targetUsers) ? data.targetUsers : [],
        requiresAction: Boolean(data.requiresAction),
        actionUrl: data.actionUrl || null,
        actionLabel: data.actionLabel || null,
        expiresAt: data.expiresAt || null,
        created_at: data.created_at || now,
        read: Boolean(data.read),
        archived: Boolean(data.archived),
        read_at: data.read_at || null,
        archived_at: data.archived_at || null,
        scheduled_for: data.scheduled_for || null,
    };
};

export const NotificationProvider = ({ children }) => {
    const { user } = useAuth();
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastChecked, setLastChecked] = useState(null);
    const scheduledTimers = useRef(new Map());
    const wsClient = useMemo(() => getWSClient(), []);

    const updateUnreadCount = useCallback((nextList) => {
        const list = nextList || notifications;
        setUnreadCount(list.filter((n) => !n.read && !n.archived).length);
    }, [notifications]);

    const persist = useCallback((list) => {
        try {
            const payload = list.slice(0, MAX_STORE);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
        } catch {
            // ignore storage errors
        }
    }, []);

    useEffect(() => {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {
                const parsed = JSON.parse(saved).map(normalizeNotification);
                setNotifications(parsed);
            }
        } catch {
            // ignore
        }
    }, []);

    useEffect(() => {
        persist(notifications);
    }, [notifications, persist]);

    const handleWebSocketMessage = useCallback(
        (message) => {
            if (!message) return;
            const type = message.type || message.event;
            switch (type) {
                case "new_notification":
                case "notification":
                    addNotification(message.data || message.notification || message);
                    break;
                case "notifications_list":
                    if (Array.isArray(message.data)) {
                        const next = message.data.map(normalizeNotification);
                        setNotifications(next);
                    }
                    break;
                case "notification_read":
                    if (message.notificationId) {
                        markAsRead(message.notificationId, true, false);
                    }
                    break;
                case "notification_archived":
                    if (message.notificationId) {
                        archiveNotification(message.notificationId, true, false);
                    }
                    break;
                case "unread_count":
                    if (typeof message.count === "number") {
                        setUnreadCount(message.count);
                    }
                    break;
                default:
                    break;
            }
        },
        []
    );

    useEffect(() => {
        if (!user) return undefined;

        const off = wsClient.onMessage((msg) => handleWebSocketMessage(msg));
        wsClient.connect();
        wsClient.subscribe("notifications");
        if (user?.id) {
            wsClient.subscribe(`notifications:${user.id}`);
        }

        return () => {
            off();
        };
    }, [user, wsClient, handleWebSocketMessage]);

    const addNotification = useCallback(
        (notificationData) => {
            const notification = normalizeNotification(notificationData);
            setNotifications((prev) => [notification, ...prev]);

            if (["CRITICAL", "HIGH"].includes(notification.priority)) {
                showDesktopNotification(notification);
            }

            return notification;
        },
        []
    );

    const markAsRead = useCallback(
        (notificationId, read = true, sync = true) => {
            setNotifications((prev) =>
                prev.map((n) =>
                    n.id === notificationId
                        ? {
                            ...n,
                            read,
                            read_at: read ? new Date().toISOString() : null,
                        }
                        : n
                )
            );

            if (sync && wsClient?.ws?.readyState === WebSocket.OPEN) {
                wsClient.send({ type: "mark_read", notificationId, read });
            }
        },
        [wsClient]
    );

    const markAllAsRead = useCallback(() => {
        setNotifications((prev) =>
            prev.map((n) =>
                n.read
                    ? n
                    : { ...n, read: true, read_at: new Date().toISOString() }
            )
        );
        if (wsClient?.ws?.readyState === WebSocket.OPEN) {
            wsClient.send({ type: "mark_all_read" });
        }
    }, [wsClient]);

    const archiveNotification = useCallback(
        (notificationId, archived = true, sync = true) => {
            setNotifications((prev) =>
                prev.map((n) =>
                    n.id === notificationId
                        ? {
                            ...n,
                            archived,
                            archived_at: archived ? new Date().toISOString() : null,
                        }
                        : n
                )
            );
            if (sync && wsClient?.ws?.readyState === WebSocket.OPEN) {
                wsClient.send({ type: "archive", notificationId, archived });
            }
        },
        [wsClient]
    );

    const archiveAllRead = useCallback(() => {
        setNotifications((prev) =>
            prev.map((n) =>
                n.read
                    ? {
                        ...n,
                        archived: true,
                        archived_at: new Date().toISOString(),
                    }
                    : n
            )
        );
    }, []);

    const deleteNotification = useCallback((notificationId) => {
        setNotifications((prev) => prev.filter((n) => n.id !== notificationId));
    }, []);

    const clearArchived = useCallback(() => {
        setNotifications((prev) => prev.filter((n) => !n.archived));
    }, []);

    const getUserNotifications = useCallback(
        (userRole, userId, filters = {}) => {
            return notifications.filter((notification) => {
                const roleKey = String(userRole || "").toLowerCase();
                const userKey = String(userId || "");

                if (notification.expiresAt && new Date(notification.expiresAt) < new Date()) {
                    return false;
                }

                if (notification.targetRoles?.length > 0) {
                    const roles = notification.targetRoles.map((r) => String(r || "").toLowerCase());
                    if (!roles.includes(roleKey) && !roles.includes("*")) {
                        return false;
                    }
                }

                if (notification.targetUsers?.length > 0) {
                    const users = notification.targetUsers.map((u) => String(u || ""));
                    if (!users.includes(userKey) && !users.includes("*")) {
                        return false;
                    }
                }

                if (filters.type && notification.type !== filters.type) return false;
                if (filters.priority && notification.priority !== filters.priority) return false;
                if (filters.unread && notification.read) return false;
                if (filters.archived && !notification.archived) return false;
                if (filters.requiresAction && !notification.requiresAction) return false;

                return true;
            });
        },
        [notifications]
    );

    const getNotificationStats = useCallback(
        (userRole, userId) => {
            const userNotifications = getUserNotifications(userRole, userId);
            return {
                total: userNotifications.length,
                unread: userNotifications.filter((n) => !n.read).length,
                requiresAction: userNotifications.filter((n) => n.requiresAction).length,
                byType: Object.keys(notificationTypes).reduce((acc, type) => {
                    acc[type] = userNotifications.filter((n) => n.type === type).length;
                    return acc;
                }, {}),
                byPriority: Object.keys(priorities).reduce((acc, priority) => {
                    acc[priority] = userNotifications.filter((n) => n.priority === priority).length;
                    return acc;
                }, {}),
            };
        },
        [getUserNotifications]
    );

    const sendNotification = useCallback(async (notificationData) => {
        if (wsClient?.ws?.readyState === WebSocket.OPEN) {
            wsClient.send({ type: "send_notification", data: notificationData });
            return { ok: true };
        }

        const res = await axiosClient.post("/api/v1/notifications", notificationData);
        return res.data;
    }, [wsClient]);

    const scheduleLocalNotification = useCallback((notificationData, scheduleDate) => {
        const scheduleTime = new Date(scheduleDate).getTime();
        const delay = Math.max(0, scheduleTime - Date.now());
        const id = notificationData.id || `sched_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;

        if (scheduledTimers.current.has(id)) {
            clearTimeout(scheduledTimers.current.get(id));
        }

        const timer = setTimeout(() => {
            addNotification({ ...notificationData, id, scheduled_for: scheduleDate });
            scheduledTimers.current.delete(id);
        }, delay);

        scheduledTimers.current.set(id, timer);
    }, [addNotification]);

    const scheduleNotification = useCallback(async (notificationData, scheduleDate) => {
        if (!scheduleDate) return null;
        try {
            const res = await axiosClient.post("/api/v1/notifications/schedule", {
                ...notificationData,
                scheduled_for: scheduleDate,
            });
            return res.data;
        } catch {
            scheduleLocalNotification(notificationData, scheduleDate);
            return { scheduled_for: scheduleDate, local: true };
        }
    }, [scheduleLocalNotification]);

    const generatePredefinedNotification = useCallback((type, data = {}) => {
        const templates = {
            USER_JOINED: {
                type: "USER",
                priority: "INFO",
                title: "New user",
                message: `User ${data.userName || ""} joined the platform`.trim(),
                icon: "person_add",
                color: "#10B981",
                data: { userId: data.userId },
                actionUrl: data.userId ? `/admin/users/${data.userId}` : null,
                actionLabel: "View user",
            },
            SHIPMENT_DELAYED: {
                type: "SHIPMENT",
                priority: "HIGH",
                title: "Shipment delayed",
                message: `Shipment ${data.shipmentId || ""} is delayed`.trim(),
                icon: "schedule",
                color: "#F59E0B",
                data: { shipmentId: data.shipmentId },
                actionUrl: data.shipmentId ? `/shipments/${data.shipmentId}` : null,
                actionLabel: "Track shipment",
            },
            PAYMENT_RECEIVED: {
                type: "PAYMENT",
                priority: "INFO",
                title: "Payment received",
                message: `Payment of ${data.amount || ""} received from ${data.payer || ""}`.trim(),
                icon: "payments",
                color: "#8B5CF6",
                data: { paymentId: data.paymentId },
                actionUrl: data.paymentId ? `/payments/${data.paymentId}` : null,
                actionLabel: "View payment",
            },
            SYSTEM_UPDATE: {
                type: "SYSTEM",
                priority: "MEDIUM",
                title: "System update",
                message: `System updated to version ${data.version || ""}`.trim(),
                icon: "sync",
                color: "#3B82F6",
                data: { version: data.version },
                actionUrl: "/admin/system/updates",
                actionLabel: "View updates",
            },
            SECURITY_ALERT: {
                type: "SECURITY",
                priority: "CRITICAL",
                title: "Security alert",
                message: data.message || "Unusual activity detected",
                icon: "shield",
                color: "#EF4444",
                requiresAction: true,
                actionUrl: "/admin/security/alerts",
                actionLabel: "Review alert",
            },
        };
        return templates[type] || null;
    }, []);

    const fetchNotifications = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await axiosClient.get("/api/v1/notifications", {
                params: { limit: 200 },
            });
            const list = Array.isArray(res.data) ? res.data : res.data?.notifications || [];
            const normalized = list.map(normalizeNotification);
            setNotifications(normalized);
            setLastChecked(new Date().toISOString());
        } catch (err) {
            setError(err?.response?.data?.detail || err?.message || "Failed to load notifications");
        } finally {
            setLoading(false);
        }
    }, []);

    const showDesktopNotification = (notification) => {
        if (typeof window === "undefined" || !("Notification" in window)) return;
        if (Notification.permission === "granted") {
            const desktop = new Notification(notification.title, {
                body: notification.message,
                icon: notification.icon || "/icon.png",
                tag: notification.id,
                requireInteraction: notification.requiresAction,
            });
            desktop.onclick = () => {
                window.focus();
                desktop.close();
                if (notification.actionUrl) {
                    window.open(notification.actionUrl, "_blank");
                }
            };
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then((permission) => {
                if (permission === "granted") {
                    showDesktopNotification(notification);
                }
            });
        }
    };

    return (
        <NotificationContext.Provider
            value={{
                notifications,
                unreadCount,
                loading,
                error,
                lastChecked,
                notificationTypes,
                priorities,
                addNotification,
                markAsRead,
                markAllAsRead,
                archiveNotification,
                archiveAllRead,
                deleteNotification,
                clearArchived,
                getUserNotifications,
                getNotificationStats,
                sendNotification,
                scheduleNotification,
                generatePredefinedNotification,
                fetchNotifications,
            }}
        >
            {children}
        </NotificationContext.Provider>
    );
};

export const useNotifications = () => {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error("useNotifications must be used within NotificationProvider");
    }
    return context;
};
