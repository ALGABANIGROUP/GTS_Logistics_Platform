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
import { useNotification } from "../../contexts/NotificationContext";
import { useAuth } from "../../contexts/AuthContext.jsx";


const NotificationBell = () => {
    const [anchorEl, setAnchorEl] = useState(null);
    const { notifications } = useNotification();

    // Get recent notifications (last 10)
    const recentNotifications = notifications.slice(-10).reverse();

    const getNotificationIcon = (severity) => {
        switch (severity) {
            case 'success':
                return <CheckCircle color="success" />;
            case 'error':
                return <Error color="error" />;
            case 'warning':
                return <Warning color="warning" />;
            default:
                return <Info color="info" />;
        }
    };

    const formatTime = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        if (diff < 60000) return 'Just now';
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

    return (
        <>
            <Tooltip title="Recent Notifications">
                <IconButton onClick={handleClick} color="inherit">
                    <Badge
                        badgeContent={recentNotifications.length}
                        color="primary"
                    >
                        <NotificationsIcon />
                    </Badge>
                </IconButton>
            </Tooltip>
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleClose}
                PaperProps={{ sx: { width: 350, maxHeight: 400, mt: 1.5 } }}
            >
                <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
                    <Typography variant="h6">Recent Notifications</Typography>
                </Box>
                {recentNotifications.length === 0 ? (
                    <MenuItem disabled>
                        <Typography variant="body2" color="text.secondary">
                            No recent notifications
                        </Typography>
                    </MenuItem>
                ) : (
                    recentNotifications.map((notification) => (
                        <MenuItem key={notification.id} onClick={handleClose}>
                            <ListItemIcon>
                                {getNotificationIcon(notification.severity)}
                            </ListItemIcon>
                            <Box sx={{ flexGrow: 1 }}>
                                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                    {notification.title || 'Notification'}
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                                    {notification.message}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    {formatTime(notification.timestamp)}
                                </Typography>
                            </Box>
                        </MenuItem>
                    ))
                )}
                {recentNotifications.length > 0 && (
                    <Box>
                        <Divider />
                        <Box sx={{ p: 1, textAlign: 'center' }}>
                            <Typography variant="caption" color="text.secondary">
                                Showing last {recentNotifications.length} notifications
                            </Typography>
                        </Box>
                    </Box>
                )}
            </Menu>
        </>
    );
};

export default NotificationBell;
