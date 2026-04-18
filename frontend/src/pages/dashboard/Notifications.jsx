// frontend/src/pages/dashboard/Notifications.jsx
import React, { useState, useEffect } from 'react';
import {
  Notifications as NotificationsIcon,
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Business as BusinessIcon,
  Security as SecurityIcon,
  Gavel as LegalIcon,
  LocalShipping as TransportIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useNotification } from '../../contexts/NotificationContext';
import axiosClient from '../../api/axiosClient';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedNotification, setSelectedNotification] = useState(null);
  const { showSuccess, showError } = useNotification();

  // Fetch notifications
  const fetchNotifications = async () => {
    setLoading(true);
    try {
      // Try to fetch from real API
      const response = await axiosClient.get('/api/v1/notifications');
      setNotifications(response.data.notifications || []);
    } catch (error) {
      console.log('Using seed data for notifications');
      // Realistic test data (like the one shown in the image)
      setNotifications(MOCK_NOTIFICATIONS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  // Filter notifications by tab
  const getFilteredNotifications = () => {
    switch (tabValue) {
      case 0: // all
        return notifications;
      case 1: // unread
        return notifications.filter(n => !n.read);
      case 2: // read
        return notifications.filter(n => n.read);
      default:
        return notifications;
    }
  };

  // Select notification icon based on type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'legal':
        return <LegalIcon sx={{ color: '#4caf50' }} />;
      case 'regulatory':
        return <SecurityIcon sx={{ color: '#ff9800' }} />;
      case 'safety':
        return <WarningIcon sx={{ color: '#f44336' }} />;
      case 'transport':
        return <TransportIcon sx={{ color: '#2196f3' }} />;
      default:
        return <InfoIcon sx={{ color: '#757575' }} />;
    }
  };

  // Select background color based on type
  const getNotificationBg = (type) => {
    switch (type) {
      case 'legal':
        return '#e8f5e9';
      case 'regulatory':
        return '#fff3e0';
      case 'safety':
        return '#ffebee';
      case 'transport':
        return '#e3f2fd';
      default:
        return '#f5f5f5';
    }
  };

  // Select source bot name
  const getBotName = (bot) => {
    const bots = {
      'information_coordinator': '📋 Information Coordinator',
      'safety_manager': '🛡️ Safety Manager',
      'mapleload_canada': '🍁 MapleLoad Canada',
      'executive_command': '👔 Executive Command'
    };
    return bots[bot] || bot;
  };

  const handleMarkAsRead = async (id) => {
    try {
      await axiosClient.patch(`/api/v1/notifications/${id}/read`);
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, read: true } : n)
      );
      showSuccess('Notification marked as read');
    } catch (error) {
      console.log('Using seed update');
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, read: true } : n)
      );
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await axiosClient.post('/api/v1/notifications/read-all');
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      showSuccess('All notifications marked as read');
    } catch (error) {
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="glass-page min-h-screen p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Notifications Center
            </h1>
            <p className="text-slate-300 text-sm">
              Legal updates, regulatory changes, and system notifications
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleMarkAllAsRead}
              disabled={unreadCount === 0}
              className="glass-panel border border-white/10 hover:bg-white/10 text-white px-4 py-2 rounded-xl transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <CheckCircleIcon className="h-4 w-4" />
              Mark all as read
            </button>
            <button
              onClick={fetchNotifications}
              className="glass-panel border border-white/10 hover:bg-white/10 text-white px-4 py-2 rounded-xl transition flex items-center gap-2"
            >
              <RefreshIcon className="h-4 w-4" />
              Refresh
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="glass-panel border border-white/10 rounded-xl p-4">
            <p className="text-slate-300 text-sm mb-1">Total</p>
            <p className="text-2xl font-bold text-white">{notifications.length}</p>
          </div>
          <div className="glass-panel border border-white/10 rounded-xl p-4 bg-blue-500/10">
            <p className="text-slate-300 text-sm mb-1">Unread</p>
            <p className="text-2xl font-bold text-blue-400">{unreadCount}</p>
          </div>
          <div className="glass-panel border border-white/10 rounded-xl p-4 bg-green-500/10">
            <p className="text-slate-300 text-sm mb-1">Legal Updates</p>
            <p className="text-2xl font-bold text-green-400">
              {notifications.filter(n => n.type === 'legal').length}
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-white/5 rounded-xl p-1">
          <button
            onClick={() => setTabValue(0)}
            className={`px-4 py-2 rounded-lg transition ${
              tabValue === 0
                ? 'bg-white/20 text-white shadow-lg'
                : 'text-slate-300 hover:text-white hover:bg-white/10'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setTabValue(1)}
            className={`px-4 py-2 rounded-lg transition ${
              tabValue === 1
                ? 'bg-white/20 text-white shadow-lg'
                : 'text-slate-300 hover:text-white hover:bg-white/10'
            }`}
          >
            Unread ({unreadCount})
          </button>
          <button
            onClick={() => setTabValue(2)}
            className={`px-4 py-2 rounded-lg transition ${
              tabValue === 2
                ? 'bg-white/20 text-white shadow-lg'
                : 'text-slate-300 hover:text-white hover:bg-white/10'
            }`}
          >
            Read
          </button>
        </div>

        {/* Notifications List */}
        {loading ? (
          <div className="flex justify-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
          </div>
        ) : getFilteredNotifications().length === 0 ? (
          <div className="glass-panel border border-white/10 rounded-xl p-12 text-center">
            <NotificationsIcon className="h-16 w-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-300 mb-2">No notifications</h3>
            <p className="text-slate-400 text-sm">
              Check back later for updates
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {getFilteredNotifications().map((notification) => (
              <div
                key={notification.id}
                className={`glass-panel border border-white/10 rounded-xl p-4 transition hover:-translate-y-1 ${
                  notification.read ? 'bg-white/5' : 'bg-blue-500/5 border-l-4 border-l-blue-400'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex gap-4 flex-1">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      notification.read ? 'bg-slate-500/20' : 'bg-blue-500/20'
                    }`}>
                      {getNotificationIcon(notification.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap mb-2">
                        <h3 className="text-lg font-semibold text-white">
                          {notification.title}
                        </h3>
                        {!notification.read && (
                          <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full">
                            New
                          </span>
                        )}
                        <span className="px-2 py-1 border border-white/20 text-slate-300 text-xs rounded-full">
                          {notification.type}
                        </span>
                      </div>
                      <p className="text-slate-300 text-sm mb-3">
                        {notification.content}
                      </p>
                      <div className="flex gap-4 items-center flex-wrap text-xs text-slate-400">
                        {notification.bot && (
                          <span>{getBotName(notification.bot)}</span>
                        )}
                        <span>{new Date(notification.created_at).toLocaleString()}</span>
                        {notification.sources && (
                          <span>📚 {notification.sources.length} sources</span>
                        )}
                      </div>
                    </div>
                  </div>
                  {!notification.read && (
                    <button
                      onClick={() => handleMarkAsRead(notification.id)}
                      className="p-2 hover:bg-white/10 rounded-lg transition"
                      title="Mark as read"
                    >
                      <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Realistic test data (like the one in the image)
const MOCK_NOTIFICATIONS = [
  {
    id: 1,
    title: "Daily legal updates - 2026-03-31",
    content: "Daily regulatory scan completed. Timestamp: 2026-03-31 08:00 UTC",
    type: "legal",
    bot: "information_coordinator",
    sources: ["CCMTA", "Transport Canada", "CBSA"],
    read: false,
    created_at: "2026-03-31T12:00:00"
  },
  {
    id: 2,
    title: "Daily legal updates - 2026-03-30",
    content: "Daily regulatory scan completed. Timestamp: 2026-03-30 08:00 UTC",
    type: "legal",
    bot: "mapleload_canada",
    sources: ["CCMTA", "Canadian Transportation Agency", "Transport Canada", "CBSA"],
    read: false,
    created_at: "2026-03-30T12:00:00"
  },
  {
    id: 3,
    title: "Safety Alert - New Regulations",
    content: "New safety regulations for commercial vehicles effective April 2026",
    type: "safety",
    bot: "safety_manager",
    read: false,
    created_at: "2026-03-29T09:19:00"
  }
];

export default Notifications;