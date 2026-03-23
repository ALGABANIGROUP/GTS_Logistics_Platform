import React, { useEffect, useState } from "react";
import axiosClient from "../../api/axiosClient";
import RequireAuth from "../../components/RequireAuth.jsx";

const PORTAL_NOTIFICATIONS_ENDPOINT = "/api/v1/admin/portal/notifications";

export default function AdminNotifications() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <AdminNotificationsContent />
    </RequireAuth>
  );
}

function AdminNotificationsContent() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [unreadCount, setUnreadCount] = useState(0);
  const [filter, setFilter] = useState("all");

  const fetchNotifications = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axiosClient.get(PORTAL_NOTIFICATIONS_ENDPOINT, {
        params: {
          limit: 100,
          unread_only: filter === "unread",
        },
        validateStatus: (status) => status < 500,
      });

      if (res.status === 404) {
        setNotifications([]);
        setUnreadCount(0);
      } else if (res.status === 200) {
        setNotifications(res.data?.notifications || []);
        setUnreadCount(res.data?.unread_count || 0);
      }
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to load notifications");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [filter]);

  const formatDate = (dateStr) => {
    if (!dateStr) return "Unknown";
    const date = new Date(dateStr);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case "new_request":
        return "New";
      case "approved":
      case "request_approved":
        return "Approved";
      case "denied":
      case "rejected":
      case "request_rejected":
        return "Rejected";
      case "verified":
        return "Verified";
      default:
        return "Update";
    }
  };

  const filteredNotifications = notifications.filter((notification) => {
    if (filter === "unread") return !notification.read;
    if (filter === "read") return notification.read;
    return true;
  });

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-100">Portal Notifications</h1>
            <p className="mt-1 text-gray-400">Manage portal access request notifications</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center rounded-full border border-gray-700 bg-gray-800 px-3 py-1 text-sm font-medium text-blue-400">
              {unreadCount} Unread
            </span>
            <button
              onClick={fetchNotifications}
              className="rounded-lg bg-blue-600 px-3 py-2 text-sm text-white transition-colors hover:bg-blue-700"
            >
              Refresh
            </button>
          </div>
        </div>

        <div className="flex gap-2">
          {["all", "unread", "read"].map((value) => (
            <button
              key={value}
              onClick={() => setFilter(value)}
              className={`rounded-lg px-4 py-2 font-medium capitalize transition-colors ${
                filter === value
                  ? "bg-blue-600 text-white"
                  : "border border-gray-700 bg-gray-800 text-gray-300 hover:bg-gray-700"
              }`}
            >
              {value}
            </button>
          ))}
        </div>
      </div>

      {error ? (
        <div className="mb-4 rounded-lg border border-red-700 bg-red-900 p-4 text-red-200">{error}</div>
      ) : null}

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-blue-600"></div>
        </div>
      ) : null}

      {!loading && filteredNotifications.length === 0 ? (
        <div className="py-12 text-center">
          <div className="mb-2 text-4xl">Inbox</div>
          <p className="text-gray-400">No {filter !== "all" ? filter : ""} notifications</p>
        </div>
      ) : null}

      {!loading && filteredNotifications.length > 0 ? (
        <div className="space-y-3">
          {filteredNotifications.map((notification) => (
            <div
              key={notification.id}
              className="rounded-lg border border-gray-700 bg-gray-900 p-4 transition-colors hover:border-gray-600"
            >
              <div className="flex items-start gap-4">
                <div className="min-w-[88px] text-xs font-semibold uppercase tracking-wide text-slate-300">
                  {getNotificationIcon(notification.notification_type)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-gray-100">{notification.title}</h3>
                    <span className="text-xs text-gray-400">{formatDate(notification.created_at)}</span>
                  </div>
                  <p className="mt-1 text-sm text-gray-300">{notification.message}</p>
                  {notification.request_id ? (
                    <p className="mt-2 text-xs text-gray-500">Request ID: {notification.request_id}</p>
                  ) : null}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
