import React, { useEffect, useState } from 'react';
import { Container, Paper, Typography, Box, Button, Grid, Chip, CircularProgress, Stack } from '@mui/material';
import { Link, ArrowBack } from '@mui/icons-material';
import { getTrailerTypes, getShipmentTypes } from '../../../services/metaDataApi';
import axiosClient from '../../../api/axiosClient.js';
import { useNavigate } from 'react-router-dom';


const LoadBoardBrokerDashboard = () => {
    const navigate = useNavigate();
    const [trailerTypes, setTrailerTypes] = useState([]);
    const [shipmentTypes, setShipmentTypes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [loads, setLoads] = useState([]);
    const [loadsLoading, setLoadsLoading] = useState(false);

    const getAvailableLoads = async () => {
        const response = await axiosClient.get('/loadboard/loads');
        return response?.data;
    };

    const postLoad = async (payload) => {
        const response = await axiosClient.post('/loadboard/loads', payload);
        return response?.data;
    };

    useEffect(() => {
        const fetchMetaData = async () => {
            try {
                const [trailer, shipment] = await Promise.all([
                    getTrailerTypes(),
                    getShipmentTypes()
                ]);
                setTrailerTypes(trailer);
                setShipmentTypes(shipment);
            } catch (err) {
                setError('Failed to load meta data');
            } finally {
                setLoading(false);
            }
        };
        fetchMetaData();
        fetchLoads();
    }, []);

    const fetchLoads = async () => {
        setLoadsLoading(true);
        try {
            const data = await getAvailableLoads();
            setLoads(Array.isArray(data) ? data : []);
        } catch {
            setLoads([]);
        } finally {
            setLoadsLoading(false);
        }
    };

    const handleNewLoad = async () => {
        const data = {
            shipment_type: shipmentTypes[0] || 'Default',
            trailer_type: trailerTypes[0] || 'Default',
            origin: 'Toronto',
            destination: 'Montreal',
            price: 1000
        };
        try {
            await postLoad(data);
            await fetchLoads();
            alert('New load added successfully!');
        } catch (err) {
            alert('An error occurred while adding the load.');
        }
    };

    const handleExportData = async () => {
        if (!loads.length) {
            alert('No data available to export.');
            return;
        }
        // Export displayed data
        const csvRows = [
            ['LOAD ID', 'ORIGIN', 'DESTINATION', 'EQUIPMENT', 'RATE', 'STATUS'].join(',')
        ];
        loads.forEach(load => {
            csvRows.push([
                load.id,
                load.origin,
                load.destination,
                load.trailer_type,
                load.price,
                load.status
            ].join(','));
        });
        const csvString = csvRows.join('\n');
        const blob = new Blob([csvString], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'loads.csv');
        document.body.appendChild(link);
        link.click();
        link.remove();
        alert('Data exported successfully!');
    };

    const handleImportCSV = async () => {
        alert('Import feature requires file upload UI implementation.');
    };

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Paper sx={{ p: 3, mb: 3, backgroundColor: '#9c27b0', color: 'white' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Link sx={{ mr: 2, fontSize: 40 }} />
                        <Box>
                            <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
                                Broker Control Panel - LoadBoard
                            </Typography>
                            <Typography variant="subtitle1">
                                Managing brokerage between shippers and carriers
                            </Typography>
                        </Box>
                    </Box>
                    <Button startIcon={<ArrowBack />} onClick={() => navigate('/portal')} sx={{ color: 'white', borderColor: 'white' }} variant="outlined">
                        Back to Portal
                    </Button>
                </Box>
                {/* Load Actions */}
                <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
                    <Button variant="contained" color="success" onClick={handleNewLoad}>
                        New Load
                    </Button>
                    <Button variant="contained" color="info" onClick={handleImportCSV}>
                        Import CSV
                    </Button>
                    <Button variant="contained" color="warning" onClick={handleExportData}>
                        Export Data
                    </Button>
                </Stack>
            </Paper>
            <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h5" gutterBottom>
                    Broker Control Panel
                </Typography>
                <Typography color="text.secondary" paragraph>
                    This interface is dedicated to brokers on the LoadBoard platform
                </Typography>
                <Box sx={{ mt: 4 }}>
                    <Typography variant="h6" gutterBottom>
                        Live Load Board
                    </Typography>
                    {loadsLoading ? (
                        <CircularProgress />
                    ) : (
                        <Box sx={{ overflowX: 'auto', mb: 2 }}>
                            <table style={{ width: '100%', color: '#fff', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                                <thead>
                                    <tr>
                                        <th>LOAD ID</th>
                                        <th>ORIGIN</th>
                                        <th>DESTINATION</th>
                                        <th>EQUIPMENT</th>
                                        <th>RATE</th>
                                        <th>STATUS</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {loads.length > 0 ? loads.map((load, idx) => (
                                        <tr key={idx}>
                                            <td>{load.id}</td>
                                            <td>{load.origin}</td>
                                            <td>{load.destination}</td>
                                            <td>{load.trailer_type}</td>
                                            <td>{load.price}</td>
                                            <td>{load.status}</td>
                                        </tr>
                                    )) : (
                                        <tr>
                                            <td colSpan={6} style={{ textAlign: 'center' }}>No loads available currently</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </Box>
                    )}
                </Box>
                <Box sx={{ mt: 4 }}>
                    <Typography variant="body1" gutterBottom>
                        All Shipment Types
                    </Typography>
                    {loading ? (
                        <CircularProgress />
                    ) : error ? (
                        <Typography color="error">{error}</Typography>
                    ) : (
                        <Grid container spacing={2} justifyContent="center" sx={{ mb: 3 }}>
                            {shipmentTypes && shipmentTypes.length > 0 ? shipmentTypes.map((type, idx) => (
                                <Grid item key={idx}>
                                    <Chip label={type} color="primary" variant="outlined" />
                                </Grid>
                            )) : <Typography>No shipment types found.</Typography>}
                        </Grid>
                    )}
                </Box>
                <Box sx={{ mt: 4 }}>
                    <Typography variant="body1" gutterBottom>
                        All Trailer Types
                    </Typography>
                    {loading ? (
                        <CircularProgress />
                    ) : error ? (
                        <Typography color="error">{error}</Typography>
                    ) : (
                        <Grid container spacing={2} justifyContent="center">
                            {trailerTypes && trailerTypes.length > 0 ? trailerTypes.map((type, idx) => (
                                <Grid item key={idx}>
                                    <Chip label={type} color="secondary" variant="outlined" />
                                </Grid>
                            )) : <Typography>No trailer types found.</Typography>}
                        </Grid>
                    )}
                </Box>
            </Paper>
        </Container>
    );
};

export default LoadBoardBrokerDashboard;
