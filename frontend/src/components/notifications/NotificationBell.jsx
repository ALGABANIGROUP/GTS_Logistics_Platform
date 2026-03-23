import React, { useMemo, useState } from "react";
import {
    Badge,
    IconButton,
    Menu,
    MenuItem,
    Typography,
    Box,
    Chip,
    Button,
    Divider,
    Avatar,
    ListItemIcon,
    Tooltip
} from '@mui/material';
import {
    Notifications as NotificationsIcon,
    CheckCircle,
    Warning,
    Info,
    Error,
    LocalShipping,
    AttachMoney,
    ClearAll,
    MarkChatRead,
    Launch,
    Archive
} from '@mui/icons-material';
import { useNotifications } from "../../contexts/NotificationContext";
import { useAuth } from "../../contexts/AuthContext.jsx";


const NotificationBell = () => {
    const [anchorEl, setAnchorEl] = useState(null);
    const { user } = useAuth();
    const {
        getUserNotifications,
        markAsRead,
        markAllAsRead,
        deleteNotification,
        archiveNotification,
        priorities,
    } = useNotifications();

    const userRole = user?.role || "user";
    const userId = user?.id || null;

    const notifications = useMemo(() => {
        return getUserNotifications(userRole, userId)
            .filter((n) => !n.archived)
            .slice(0, 15);
    }, [getUserNotifications, userRole, userId]);

    const userUnreadCount = useMemo(() => {
        return notifications.filter((n) => !n.read).length;
    }, [notifications]);

    const hasCritical = useMemo(() => {
        return notifications.some((n) => !n.read && ["CRITICAL", "HIGH"].includes(n.priority));
    }, [notifications]);

    const getNotificationIcon = (type) => {
        switch (type) {
            case "PAYMENT":
                return <AttachMoney color="secondary" />;
            case "SHIPMENT":
                return <LocalShipping color="primary" />;
            case "SECURITY":
                return <Error color="error" />;
            case "SYSTEM":
                return <Info color="info" />;
            case "REPORT":
                return <CheckCircle color="success" />;
            default:
                return <Warning color="warning" />;
        }
    };

    const formatTime = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        if (diff < 60000) return 'Now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} min ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
        return date.toLocaleDateString();
    };

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleNotificationClick = (notification) => {
        if (!notification.read) {
            markAsRead(notification.id);
        }
        if (notification.actionUrl) {
            if (notification.actionUrl.startsWith("/")) {
                window.location.href = notification.actionUrl;
            } else {
                window.open(notification.actionUrl, "_blank");
            }
        }
        handleClose();
    };

    return (
        <>
            <Tooltip title="Notifications">
                <IconButton onClick={handleClick} color="inherit">
                    <Badge
                        badgeContent={userUnreadCount}
                        color="error"
                        variant={userUnreadCount > 0 ? "standard" : "dot"}
                    >
                        <Box sx={{ position: "relative" }}>
                            <NotificationsIcon />
                            {hasCritical && (
                                <Box
                                    sx={{
                                        position: "absolute",
                                        right: -2,
                                        bottom: -2,
                                        width: 8,
                                        height: 8,
                                        bgcolor: priorities.CRITICAL.color,
                                        borderRadius: "50%",
                                        border: "1px solid #fff",
                                    }}
                                />
                            )}
                        </Box>
                    </Badge>
                </IconButton>
            </Tooltip>
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleClose}
                PaperProps={{ sx: { width: 380, maxHeight: 500, mt: 1.5 } }}
            >
                <Box sx={{ p: 2, pb: 1 }}>
                    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                            Notifications
                            {userUnreadCount > 0 && (
                                <Chip label={`${userUnreadCount} unread`} size="small" color="primary" sx={{ ml: 1, fontSize: '0.7rem' }} />
                            )}
                        </Typography>
                        <Box>
                            {userUnreadCount > 0 && (
                                <Button size="small" startIcon={<MarkChatRead />} onClick={markAllAsRead} sx={{ mr: 1 }}>
                                    Mark all as read
                                </Button>
                            )}
                        </Box>
                    </Box>
                </Box>
                <Divider />
                <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                    <>
                        {notifications.length > 0 ? (
                            notifications.map((notification) => (
                                <div key={notification.id}>
                                    <MenuItem
                                        onClick={() => handleNotificationClick(notification)}
                                        sx={{
                                            py: 2,
                                            px: 2.5,
                                            borderLeft: notification.read ? 'none' : '4px solid',
                                            borderLeftColor: notification.priority === 'CRITICAL'
                                                ? '#DC2626'
                                                : notification.priority === 'HIGH'
                                                    ? '#EA580C'
                                                    : notification.priority === 'MEDIUM'
                                                        ? '#F59E0B'
                                                        : '#1976d2',
                                            backgroundColor: notification.read ? 'transparent' : 'rgba(25, 118, 210, 0.04)'
                                        }}
                                    >
                                        <ListItemIcon sx={{ minWidth: 40 }}>
                                            <Avatar sx={{ bgcolor: notification.color || "#E2E8F0", width: 32, height: 32 }}>
                                                {getNotificationIcon(notification.type)}
                                            </Avatar>
                                        </ListItemIcon>
                                        <Box sx={{ flex: 1, ml: 2 }}>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                                <Typography variant="subtitle2" sx={{ fontWeight: notification.read ? 'normal' : 'bold', color: notification.read ? 'text.secondary' : 'text.primary' }}>
                                                    {notification.title}
                                                </Typography>
                                                <Typography variant="caption" color="text.secondary">
                                                    {formatTime(notification.created_at)}
                                                </Typography>
                                            </Box>
                                            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                                {notification.message}
                                            </Typography>
                                            {notification.actionUrl && (
                                                <Button
                                                    size="small"
                                                    variant="outlined"
                                                    sx={{ mt: 1 }}
                                                    endIcon={<Launch fontSize="small" />}
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleNotificationClick(notification);
                                                    }}
                                                >
                                                    {notification.actionLabel || "Open"}
                                                </Button>
                                            )}
                                        </Box>
                                        <IconButton size="small" onClick={(e) => { e.stopPropagation(); deleteNotification(notification.id); }} sx={{ ml: 1 }}>
                                            <ClearAll fontSize="small" />
                                        </IconButton>
                                        <IconButton size="small" onClick={(e) => { e.stopPropagation(); archiveNotification(notification.id); }} sx={{ ml: 1 }}>
                                            <Archive fontSize="small" />
                                        </IconButton>
                                    </MenuItem>
                                    <Divider />
                                </div>
                            ))
                        ) : (
                            <Box sx={{ textAlign: 'center', py: 4 }}>
                                <NotificationsIcon sx={{ fontSize: 60, color: 'text.disabled', mb: 2 }} />
                                <Typography color="text.secondary">No notifications yet</Typography>
                            </Box>
                        )}
                    </>
                </Box>
                {notifications.length > 0 && (
                    <>
                        <Divider />
                        <Box sx={{ p: 1.5, textAlign: 'center' }}>
                            <Button fullWidth variant="text" size="small" onClick={() => { window.location.href = '/notifications'; }}>
                                View all notifications
                            </Button>
                        </Box>
                    </>
                )}
            </Menu>
        </>
    );
};

export default NotificationBell;
