import React, { useMemo, useState } from "react";
import {
    Container,
    Paper,
    Typography,
    Box,
    Card,
    CardContent,
    Chip,
    IconButton,
    TextField,
    InputAdornment,
} from "@mui/material";
import {
    ArrowBack,
    Notifications,
    Search,
    CheckCircle,
    Warning,
    Error,
    Info,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useNotification } from "../../contexts/NotificationContext";

const NotificationsPage = () => {
    const navigate = useNavigate();
    const { notifications } = useNotification();

    // Simple state for the simplified notifications page
    const [searchQuery, setSearchQuery] = useState("");

    // Filter notifications based on search
    const filteredNotifications = useMemo(() => {
        if (!searchQuery) return notifications.slice().reverse(); // Show newest first
        return notifications
            .filter(notification =>
                notification.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
                (notification.title && notification.title.toLowerCase().includes(searchQuery.toLowerCase()))
            )
            .reverse();
    }, [notifications, searchQuery]);

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

    return (
        <Container maxWidth="lg" sx={{ mt: 3, mb: 4 }}>
            <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                        <IconButton onClick={() => navigate(-1)}>
                            <ArrowBack />
                        </IconButton>
                        <Box>
                            <Typography variant="h4" sx={{ fontWeight: "bold" }}>
                                <Notifications sx={{ mr: 1, verticalAlign: "middle" }} />
                                Notifications
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Recent notifications and alerts
                            </Typography>
                        </Box>
                    </Box>
                </Box>
            </Paper>

            <Box sx={{ mb: 3 }}>
                <TextField
                    placeholder="Search notifications..."
                    fullWidth
                    size="small"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <Search />
                            </InputAdornment>
                        ),
                    }}
                />
            </Box>

            {filteredNotifications.length === 0 ? (
                <Paper sx={{ p: 4, textAlign: 'center', borderRadius: 2 }}>
                    <Notifications sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                        {searchQuery ? 'No notifications match your search' : 'No notifications yet'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        {searchQuery ? 'Try adjusting your search terms' : 'Notifications will appear here when actions are performed'}
                    </Typography>
                </Paper>
            ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {filteredNotifications.map((notification) => (
                        <Card key={notification.id} sx={{ borderRadius: 2 }}>
                            <CardContent sx={{ pb: '16px !important' }}>
                                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                                    <Box sx={{ mt: 0.5 }}>
                                        {getNotificationIcon(notification.severity)}
                                    </Box>
                                    <Box sx={{ flex: 1 }}>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                                            <Typography variant="h6" sx={{ fontWeight: 500 }}>
                                                {notification.title || 'Notification'}
                                            </Typography>
                                            <Chip
                                                label={notification.severity}
                                                size="small"
                                                color={
                                                    notification.severity === 'success' ? 'success' :
                                                    notification.severity === 'error' ? 'error' :
                                                    notification.severity === 'warning' ? 'warning' : 'info'
                                                }
                                                variant="outlined"
                                            />
                                        </Box>
                                        <Typography variant="body1" sx={{ mb: 1, color: 'text.secondary' }}>
                                            {notification.message}
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            {formatTime(notification.timestamp)}
                                        </Typography>
                                    </Box>
                                </Box>
                            </CardContent>
                        </Card>
                    ))}
                </Box>
            )}
        </Container>
    );
};

export default NotificationsPage;
