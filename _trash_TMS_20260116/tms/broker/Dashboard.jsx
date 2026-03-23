import React from 'react';
import { Container, Paper, Typography, Box, Button } from '@mui/material';
import { Link, ArrowBack } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const BrokerDashboard = () => {
    const navigate = useNavigate();
    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Paper sx={{ p: 3, mb: 3, backgroundColor: '#9c27b0', color: 'white' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Link sx={{ mr: 2, fontSize: 40 }} />
                        <Box>
                            <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
                                Broker Dashboard - TMS
                            </Typography>
                            <Typography variant="subtitle1">
                                Manage brokerage and track shipments
                            </Typography>
                        </Box>
                    </Box>
                    <Button startIcon={<ArrowBack />} onClick={() => navigate('/portal')} sx={{ color: 'white', borderColor: 'white' }} variant="outlined">
                        Back to Portal
                    </Button>
                </Box>
            </Paper>
            <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h5" gutterBottom>
                    Broker dashboard under development
                </Typography>
                <Typography color="text.secondary" paragraph>
                    This interface is dedicated to brokers in the TMS system
                </Typography>
                <Box sx={{ mt: 4 }}>
                    <Typography variant="body1" gutterBottom>
                        Upcoming Features:
                    </Typography>
                    <ul style={{ textAlign: 'right', direction: 'rtl' }}>
                        <li>Manage all shipments</li>
                        <li>Negotiate between parties</li>
                        <li>Collect commissions</li>
                        <li>Reports and statistics</li>
                    </ul>
                </Box>
            </Paper>
        </Container>
    );
};
export default BrokerDashboard;
