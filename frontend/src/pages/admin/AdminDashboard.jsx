import React, { useState, useEffect } from 'react';
import RequireAuth from '../../components/RequireAuth.jsx';
import {
    Container, Paper, Typography, Box, Grid, Card, CardContent, Button, Tabs, Tab, Chip, Menu, MenuItem
} from '@mui/material';
import {
    Dashboard as DashboardIcon,
    SwapHoriz as SwitchIcon,
    Tty as TMSIcon,
    ListAlt as LoadBoardIcon,
    People as UsersIcon,
    Settings as SettingsIcon,
    Analytics as AnalyticsIcon
} from '@mui/icons-material';

const AdminDashboard = () => {
    const [selectedSystem, setSelectedSystem] = useState('tms');
    const [anchorEl, setAnchorEl] = useState(null);
    const [activeTab, setActiveTab] = useState(0);

    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const system = urlParams.get('system') || 'tms';
        setSelectedSystem(system);
    }, []);

    const handleSystemSwitch = (newSystem) => {
        setSelectedSystem(newSystem);
        window.history.pushState({}, '', `/admin/dashboard?system=${newSystem}`);
        setAnchorEl(null);
    };

    const systems = [
        { id: 'tms', name: 'TMS System', icon: <TMSIcon />, color: '#1976d2' },
        { id: 'loadboard', name: 'LoadBoard System', icon: <LoadBoardIcon />, color: '#2e7d32' }
    ];

    const tabs = [
        { label: 'Overview', icon: <DashboardIcon /> },
        { label: 'User Management', icon: <UsersIcon /> },
        { label: 'System Stats', icon: <AnalyticsIcon /> },
        { label: 'Settings', icon: <SettingsIcon /> }
    ];

    const currentSystem = systems.find(s => s.id === selectedSystem);

    return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Paper sx={{ p: 3, mb: 3, backgroundColor: currentSystem.color, color: 'white' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <DashboardIcon sx={{ mr: 2, fontSize: 40 }} />
                            <Box>
                                <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
                                    Admin Dashboard
                                </Typography>
                                <Typography variant="subtitle1">
                                    System Management - {currentSystem.name}
                                </Typography>
                            </Box>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Chip
                                icon={<SwitchIcon />}
                                label="Switch System"
                                onClick={(e) => setAnchorEl(e.currentTarget)}
                                sx={{ backgroundColor: 'rgba(255, 255, 255, 0.2)', color: 'white', '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.3)' } }}
                            />
                            <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
                                {systems.map((system) => (
                                    <MenuItem key={system.id} onClick={() => handleSystemSwitch(system.id)} selected={selectedSystem === system.id}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            {system.icon}
                                            <span>{system.name}</span>
                                            {selectedSystem === system.id && (
                                                <Chip label="Active" size="small" color="primary" />
                                            )}
                                        </Box>
                                    </MenuItem>
                                ))}
                            </Menu>
                            <Button variant="contained" href="/portal" sx={{ backgroundColor: 'white', color: currentSystem.color }}>
                                Back to Portal
                            </Button>
                        </Box>
                    </Box>
                </Paper>
                <Paper sx={{ mb: 3 }}>
                    <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} variant="fullWidth">
                        {tabs.map((tab, index) => (
                            <Tab key={index} icon={tab.icon} label={tab.label} iconPosition="start" />
                        ))}
                    </Tabs>
                </Paper>
                <Grid container spacing={3}>
                    <Grid item xs={12} md={8}>
                        <Paper sx={{ p: 3, height: 400 }}>
                            <Typography variant="h6" gutterBottom>
                                {currentSystem.name} Stats
                            </Typography>
                            {selectedSystem === 'tms' && (
                                <Box>
                                    <Typography>TMS System Stats:</Typography>
                                    <ul>
                                        <li>Active Shipments: 156</li>
                                        <li>Connected Drivers: 23</li>
                                        <li>Total Revenue: $450,000</li>
                                    </ul>
                                </Box>
                            )}
                            {selectedSystem === 'loadboard' && (
                                <Box>
                                    <Typography>LoadBoard Stats:</Typography>
                                    <ul>
                                        <li>Posted Loads: 89</li>
                                        <li>Bids Submitted: 245</li>
                                        <li>Success Rate: 78%</li>
                                    </ul>
                                </Box>
                            )}
                        </Paper>
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <Paper sx={{ p: 3, height: 400 }}>
                            <Typography variant="h6" gutterBottom>
                                Quick Actions
                            </Typography>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                <Button variant="contained" href={`/${selectedSystem}/shipper/dashboard`} startIcon={<TMSIcon />}>
                                    View Shipper Dashboard
                                </Button>
                                <Button variant="contained" href={`/${selectedSystem}/carrier/dashboard`} startIcon={<LoadBoardIcon />}>
                                    View Carrier Dashboard
                                </Button>
                                <Button variant="outlined" href="/portal">
                                    Test Portal Again
                                </Button>
                            </Box>
                        </Paper>
                    </Grid>
                </Grid>
            </Container>
        </RequireAuth>
    );
};

export default AdminDashboard;
