import React from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';

const StatsCard = ({
    title,
    value,
    icon,
    color = '#1976d2',
    trend = null,
    subtitle = null
}) => {
    const isPositive = trend?.startsWith('+');

    return (
        <Card sx={{
            height: '100%',
            transition: 'transform 0.2s, box-shadow 0.2s',
            '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 6
            }
        }}>
            <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box sx={{ flex: 1 }}>
                        <Typography color="text.secondary" variant="body2" gutterBottom>
                            {title}
                        </Typography>
                        <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mt: 1 }}>
                            {value}
                        </Typography>
                        {subtitle && (
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                                {subtitle}
                            </Typography>
                        )}
                    </Box>
                    <Box sx={{
                        backgroundColor: `${color}15`,
                        borderRadius: '50%',
                        width: 56,
                        height: 56,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0
                    }}>
                        {React.cloneElement(icon, { sx: { fontSize: 28, color } })}
                    </Box>
                </Box>

                {trend && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                        <Chip
                            icon={isPositive ? <TrendingUp /> : <TrendingDown />}
                            label={trend}
                            size="small"
                            sx={{
                                backgroundColor: isPositive ? '#e8f5e9' : '#ffebee',
                                color: isPositive ? '#2e7d32' : '#d32f2f'
                            }}
                        />
                    </Box>
                )}
            </CardContent>
        </Card>
    );
};

export default StatsCard;
