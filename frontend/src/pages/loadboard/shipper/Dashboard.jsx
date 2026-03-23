import React from 'react';
import { Container, Paper, Typography, Box, Button } from '@mui/material';
import { LocalShipping, ArrowBack } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const LoadBoardShipperDashboard = () => {
    const navigate = useNavigate();
    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Paper sx={{ p: 3, mb: 3, backgroundColor: '#1976d2', color: 'white' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <LocalShipping sx={{ mr: 2, fontSize: 40 }} />
                        <Box>
                            <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
                                Shipper Dashboard - LoadBoard
                            </Typography>
                            <Typography variant="subtitle1">
                                Post shipments and search for carriers
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
                    Shipper Dashboard Under Development
                </Typography>
                <Typography color="text.secondary" paragraph>
                    This interface is dedicated to shippers on the LoadBoard platform.
                </Typography>
                <Box sx={{ mt: 4 }}>
                    <Typography variant="body1" gutterBottom>
                        Upcoming Features:
                    </Typography>
                    <ul style={{ textAlign: 'left', direction: 'ltr' }}>
                        <li>Post new shipments</li>
                        <li>Track offers</li>
                        <li>Rate carriers</li>
                        <li>Reports and statistics</li>
                    </ul>
                </Box>
            </Paper>
        </Container>
    );
};
export default LoadBoardShipperDashboard;
