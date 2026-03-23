import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const LoadBoardCarrierDashboard = () => (
    <Box sx={{ p: 4 }}>
        <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h4" color="primary" gutterBottom>
                LoadBoard Carrier Dashboard
            </Typography>
            <Typography variant="body1" color="text.secondary">
                Track posted loads, respond to requests, and monitor your fleet performance within the LoadBoard carrier experience.
            </Typography>
        </Paper>
        {/* Carrier-specific widgets and KPIs can be added here */}
    </Box>
);

export default LoadBoardCarrierDashboard;
