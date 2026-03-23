import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const LoadBoardShipperDashboard = () => {
    return (
        <Box sx={{ p: 4 }}>
            <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h4" color="primary" gutterBottom>
                    LoadBoard Shipper Dashboard
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    Welcome! Here you can post loads, track offers, and manage your shipments on the LoadBoard platform.
                </Typography>
            </Paper>
            {/* Add more shipper-specific widgets and panels here */}
        </Box>
    );
};

export default LoadBoardShipperDashboard;
