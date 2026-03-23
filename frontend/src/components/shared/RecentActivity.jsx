import React from 'react';
import {
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Avatar,
    Chip,
    Typography,
    Box
} from '@mui/material';
import {
    CheckCircle,
    Pending,
    Error,
    LocalShipping,
    AttachMoney,
    Person,
    Schedule
} from '@mui/icons-material';

const RecentActivity = ({ activities = [], title = "Recent Activity" }) => {
    const getActivityIcon = (type) => {
        switch (type) {
            case 'shipment_created': return <LocalShipping />;
            case 'payment_received': return <AttachMoney />;
            case 'user_registered': return <Person />;
            case 'status_changed': return <Schedule />;
            default: return <CheckCircle />;
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed': return 'success';
            case 'pending': return 'warning';
            case 'failed': return 'error';
            default: return 'info';
        }
    };

    const formatTime = (timestamp) => {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <Box sx={{ width: '100%' }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                {title}
            </Typography>
            <List sx={{ width: '100%' }}>
                {activities.length > 0 ? (
                    activities.map((activity, index) => (
                        <ListItem
                            key={index}
                            sx={{
                                borderBottom: index < activities.length - 1 ? '1px solid #f0f0f0' : 'none',
                                py: 1.5
                            }}
                        >
                            <ListItemIcon sx={{ minWidth: 40 }}>
                                <Avatar sx={{
                                    bgcolor: `${getStatusColor(activity.status)}.light`,
                                    width: 32,
                                    height: 32
                                }}>
                                    {getActivityIcon(activity.type)}
                                </Avatar>
                            </ListItemIcon>
                            <ListItemText
                                primary={
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                            {activity.message}
                                        </Typography>
                                        <Chip
                                            label={formatTime(activity.timestamp)}
                                            size="small"
                                            variant="outlined"
                                            sx={{ fontSize: '10px' }}
                                        />
                                    </Box>
                                }
                                secondary={
                                    activity.details && (
                                        <Typography variant="caption" color="text.secondary">
                                            {activity.details}
                                        </Typography>
                                    )
                                }
                            />
                        </ListItem>
                    ))
                ) : (
                    <ListItem>
                        <ListItemText
                            primary={
                                <Typography color="text.secondary" align="center">
                                    No recent activity
                                </Typography>
                            }
                        />
                    </ListItem>
                )}
            </List>
        </Box>
    );
};

export default RecentActivity;
