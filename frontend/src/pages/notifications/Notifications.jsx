import React, { useMemo, useState } from "react";
import {
    Container,
    Paper,
    Typography,
    Box,
    Grid,
    Card,
    CardContent,
    Chip,
    Button,
    Tabs,
    Tab,
    IconButton,
    Divider,
    Avatar,
    TextField,
    InputAdornment,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
} from "@mui/material";
import {
    ArrowBack,
    Notifications,
    Search,
    Delete,
    CheckCircle,
    Warning,
    Error,
    Info,
    LocalShipping,
    AttachMoney,
    Archive,
    Schedule,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useNotifications } from "../../contexts/NotificationContext";
import { useAuth } from "../../contexts/AuthContext.jsx";

const NotificationsPage = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const {
        getUserNotifications,
        notificationTypes,
        priorities,
        markAsRead,
        markAllAsRead,
        deleteNotification,
        archiveNotification,
        archiveAllRead,
        clearArchived,
        fetchNotifications,
        generatePredefinedNotification,
        scheduleNotification,
        loading,
        error,
    } = useNotifications();

    const userRole = user?.role || "user";
    const userId = user?.id || null;

    const [tabValue, setTabValue] = useState(0);
    const [searchQuery, setSearchQuery] = useState("");
    const [filters, setFilters] = useState({
        type: "",
        priority: "",
        status: "",
        period: "",
    });

    const allNotifications = useMemo(() => {
        return getUserNotifications(userRole, userId);
    }, [getUserNotifications, userRole, userId]);

    const filteredNotifications = useMemo(() => {
        let list = [...allNotifications];

        if (tabValue === 1) list = list.filter((n) => !n.read);
        if (tabValue === 2) list = list.filter((n) => n.requiresAction);
        if (tabValue === 3) list = list.filter((n) => n.archived);

        if (filters.type) list = list.filter((n) => n.type === filters.type);
        if (filters.priority) list = list.filter((n) => n.priority === filters.priority);
        if (filters.status === "unread") list = list.filter((n) => !n.read);
        if (filters.status === "read") list = list.filter((n) => n.read);
        if (filters.status === "archived") list = list.filter((n) => n.archived);

        if (filters.period) {
            const now = new Date();
            const cutoff = new Date(now);
            if (filters.period === "today") cutoff.setHours(0, 0, 0, 0);
            if (filters.period === "week") cutoff.setDate(now.getDate() - 7);
            if (filters.period === "month") cutoff.setDate(now.getDate() - 30);
            list = list.filter((n) => new Date(n.created_at) >= cutoff);
        }

        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            list = list.filter(
                (n) =>
                    n.title.toLowerCase().includes(q) ||
                    n.message.toLowerCase().includes(q) ||
                    JSON.stringify(n.data || {}).toLowerCase().includes(q)
            );
        }

        return list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }, [allNotifications, tabValue, filters, searchQuery]);

    const unreadCount = allNotifications.filter((n) => !n.read).length;
    const actionCount = allNotifications.filter((n) => n.requiresAction).length;
    const archivedCount = allNotifications.filter((n) => n.archived).length;

    const handleScheduleTest = async () => {
        const template = generatePredefinedNotification("SYSTEM_UPDATE", { version: "2.5.0" });
        const scheduleDate = new Date(Date.now() + 5 * 60 * 1000).toISOString();
        await scheduleNotification(template, scheduleDate);
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
                                Notification Center
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Real-time alerts, role targeting, and scheduled messages
                            </Typography>
                        </Box>
                    </Box>
                    <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                        <Button startIcon={<Schedule />} onClick={handleScheduleTest} variant="outlined">
                            Schedule test
                        </Button>
                        <Button startIcon={<CheckCircle />} onClick={markAllAsRead} variant="outlined" disabled={unreadCount === 0}>
                            Mark all as read
                        </Button>
                        <Button startIcon={<Archive />} onClick={archiveAllRead} variant="outlined">
                            Archive read
                        </Button>
                        <Button startIcon={<Delete />} onClick={clearArchived} variant="outlined" color="error">
                            Clear archive
                        </Button>
                    </Box>
                </Box>
            </Paper>

            <Grid container spacing={3}>
                <Grid item xs={12} md={9}>
                    <Paper sx={{ p: 2, height: "100%" }}>
                        <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3, gap: 2, flexWrap: "wrap" }}>
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
                            <Button variant="outlined" onClick={fetchNotifications} disabled={loading}>
                                Refresh
                            </Button>
                        </Box>

                        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", mb: 2 }}>
                            <FormControl size="small" sx={{ minWidth: 140 }}>
                                <InputLabel>Type</InputLabel>
                                <Select
                                    label="Type"
                                    value={filters.type}
                                    onChange={(e) => setFilters((prev) => ({ ...prev, type: e.target.value }))}
                                >
                                    <MenuItem value="">All</MenuItem>
                                    {Object.values(notificationTypes).map((type) => (
                                        <MenuItem key={type.id} value={type.id.toUpperCase()}>
                                            {type.name}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                            <FormControl size="small" sx={{ minWidth: 140 }}>
                                <InputLabel>Priority</InputLabel>
                                <Select
                                    label="Priority"
                                    value={filters.priority}
                                    onChange={(e) => setFilters((prev) => ({ ...prev, priority: e.target.value }))}
                                >
                                    <MenuItem value="">All</MenuItem>
                                    {Object.keys(priorities).map((priority) => (
                                        <MenuItem key={priority} value={priority}>
                                            {priorities[priority].name}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                            <FormControl size="small" sx={{ minWidth: 140 }}>
                                <InputLabel>Status</InputLabel>
                                <Select
                                    label="Status"
                                    value={filters.status}
                                    onChange={(e) => setFilters((prev) => ({ ...prev, status: e.target.value }))}
                                >
                                    <MenuItem value="">All</MenuItem>
                                    <MenuItem value="unread">Unread</MenuItem>
                                    <MenuItem value="read">Read</MenuItem>
                                    <MenuItem value="archived">Archived</MenuItem>
                                </Select>
                            </FormControl>
                            <FormControl size="small" sx={{ minWidth: 140 }}>
                                <InputLabel>Period</InputLabel>
                                <Select
                                    label="Period"
                                    value={filters.period}
                                    onChange={(e) => setFilters((prev) => ({ ...prev, period: e.target.value }))}
                                >
                                    <MenuItem value="">All</MenuItem>
                                    <MenuItem value="today">Today</MenuItem>
                                    <MenuItem value="week">Last 7 days</MenuItem>
                                    <MenuItem value="month">Last 30 days</MenuItem>
                                </Select>
                            </FormControl>
                        </Box>

                        <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
                            <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
                                <Tab label="All" />
                                <Tab label={<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>Unread{unreadCount > 0 && (<Chip label={unreadCount} size="small" color="error" />)}</Box>} />
                                <Tab label={<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>Action required{actionCount > 0 && (<Chip label={actionCount} size="small" color="warning" />)}</Box>} />
                                <Tab label={<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>Archive{archivedCount > 0 && (<Chip label={archivedCount} size="small" color="default" />)}</Box>} />
                            </Tabs>
                        </Box>

                        {error && (
                            <Paper sx={{ p: 2, mb: 2, bgcolor: "#FEE2E2" }}>
                                <Typography color="error">{error}</Typography>
                            </Paper>
                        )}

                        {filteredNotifications.length > 0 ? (
                            <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                                {filteredNotifications.map((notification) => (
                                    <Card
                                        key={notification.id}
                                        variant="outlined"
                                        sx={{
                                            borderLeft: notification.read ? "none" : "4px solid",
                                            borderLeftColor:
                                                notification.priority === "CRITICAL"
                                                    ? "#DC2626"
                                                    : notification.priority === "HIGH"
                                                        ? "#EA580C"
                                                        : notification.priority === "MEDIUM"
                                                            ? "#F59E0B"
                                                            : "#1976d2",
                                            opacity: notification.archived ? 0.7 : 1,
                                        }}
                                    >
                                        <CardContent sx={{ py: 2 }}>
                                            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                                                <Box sx={{ display: "flex", gap: 2, flex: 1 }}>
                                                    <Avatar sx={{ bgcolor: "#E2E8F0", width: 40, height: 40 }}>
                                                        {notification.type === "SHIPMENT" ? (
                                                            <LocalShipping />
                                                        ) : notification.type === "PAYMENT" ? (
                                                            <AttachMoney />
                                                        ) : notification.priority === "CRITICAL" ? (
                                                            <Error />
                                                        ) : notification.priority === "HIGH" ? (
                                                            <Warning />
                                                        ) : notification.priority === "INFO" ? (
                                                            <CheckCircle />
                                                        ) : (
                                                            <Info />
                                                        )}
                                                    </Avatar>
                                                    <Box sx={{ flex: 1 }}>
                                                        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                                                            <Typography variant="subtitle1" sx={{ fontWeight: notification.read ? "normal" : "bold", mb: 0.5 }}>
                                                                {notification.title}
                                                                {notification.requiresAction && (
                                                                    <Chip label="Action" size="small" color="warning" sx={{ ml: 1, fontSize: "0.6rem" }} />
                                                                )}
                                                            </Typography>
                                                            <Typography variant="caption" color="text.secondary">
                                                                {new Date(notification.created_at).toLocaleString()}
                                                            </Typography>
                                                        </Box>
                                                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                                            {notification.message}
                                                        </Typography>
                                                        {notification.actionUrl && (
                                                            <Button
                                                                size="small"
                                                                variant="outlined"
                                                                onClick={() => {
                                                                    if (notification.actionUrl.startsWith("/")) {
                                                                        window.location.href = notification.actionUrl;
                                                                    } else {
                                                                        window.open(notification.actionUrl, "_blank");
                                                                    }
                                                                }}
                                                            >
                                                                {notification.actionLabel || "Open"}
                                                            </Button>
                                                        )}
                                                    </Box>
                                                </Box>
                                                <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
                                                    {!notification.read && (
                                                        <Button size="small" variant="outlined" onClick={() => markAsRead(notification.id)}>
                                                            Mark as read
                                                        </Button>
                                                    )}
                                                    <IconButton size="small" onClick={() => archiveNotification(notification.id)}>
                                                        <Archive fontSize="small" />
                                                    </IconButton>
                                                    <IconButton size="small" color="error" onClick={() => deleteNotification(notification.id)}>
                                                        <Delete fontSize="small" />
                                                    </IconButton>
                                                </Box>
                                            </Box>
                                        </CardContent>
                                    </Card>
                                ))}
                            </Box>
                        ) : (
                            <Box sx={{ textAlign: "center", py: 6 }}>
                                <Notifications sx={{ fontSize: 80, color: "text.disabled", mb: 2 }} />
                                <Typography variant="h6" color="text.secondary" gutterBottom>No notifications</Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {searchQuery ? "No notifications match your search." : "Notifications will appear here when available."}
                                </Typography>
                            </Box>
                        )}
                    </Paper>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
                            Stats
                        </Typography>
                        <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                            <Chip label={`Total: ${allNotifications.length}`} />
                            <Chip label={`Unread: ${unreadCount}`} color="primary" />
                            <Chip label={`Action: ${actionCount}`} color="warning" />
                            <Chip label={`Archived: ${archivedCount}`} />
                        </Box>
                        <Divider sx={{ my: 2 }} />
                        <Typography variant="body2" color="text.secondary">
                            Role scope: {userRole}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            User ID: {userId || "N/A"}
                        </Typography>
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default NotificationsPage;
