import React, { useState } from 'react';
import {
    Paper,
    Box,
    Typography,
    Grid,
    Card,
    CardContent,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Button,
    ToggleButtonGroup,
    ToggleButton,
    TextField,
    Alert,
    IconButton,
    Tooltip
} from '@mui/material';
import {
    TrendingUp,
    Download,
    FilterAlt,
    Refresh,
    DateRange,
    Analytics,
    BarChart,
    PieChart,
    Timeline,
    TableChart
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

const AdvancedReports = ({ userType = 'shipper' }) => {
    const theme = useTheme();
    const [reportType, setReportType] = useState('monthly');
    const [chartType, setChartType] = useState('line');
    const [dateRange, setDateRange] = useState({
        start: '2024-01-01',
        end: '2024-01-31'
    });
    const [selectedMetrics, setSelectedMetrics] = useState(['revenue', 'shipments']);

    // Sample report data
    const reportData = {
        monthly: [
            { month: 'January', shipments: 45, revenue: 245000, expenses: 180000, profit: 65000 },
            { month: 'February', shipments: 52, revenue: 285000, expenses: 195000, profit: 90000 },
            { month: 'March', shipments: 48, revenue: 265000, expenses: 185000, profit: 80000 },
            { month: 'April', shipments: 61, revenue: 325000, expenses: 210000, profit: 115000 },
        ],
        weekly: [
            { week: 'Week 1', shipments: 12, revenue: 65000, expenses: 45000 },
            { week: 'Week 2', shipments: 15, revenue: 82000, expenses: 55000 },
            { week: 'Week 3', shipments: 11, revenue: 58000, expenses: 42000 },
            { week: 'Week 4', shipments: 14, revenue: 75000, expenses: 50000 },
        ],
        yearly: [
            { year: '2021', shipments: 420, revenue: 2150000, expenses: 1650000 },
            { year: '2022', shipments: 480, revenue: 2450000, expenses: 1850000 },
            { year: '2023', shipments: 520, revenue: 2850000, expenses: 2100000 },
            { year: '2024', shipments: 150, revenue: 850000, expenses: 620000 },
        ]
    };

    const metricsOptions = [
        { value: 'shipments', label: 'Total Shipments', color: theme.palette.primary.main },
        { value: 'revenue', label: 'Revenue', color: theme.palette.success.main },
        { value: 'expenses', label: 'Expenses', color: theme.palette.warning.main },
        { value: 'profit', label: 'Profit', color: theme.palette.info.main },
    ];

    const generateReport = () => {
        // Simulate report generation
        console.log('Generating report with:', { reportType, dateRange, selectedMetrics });
    };

    const exportReport = (format) => {
        // Simulate report export
        alert(`Report exported as ${format}`);
    };

    return (
        <Paper sx={{ p: 3, height: '100%' }}>
            {/* Control bar */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Analytics sx={{ fontSize: 32, color: 'primary.main' }} />
                    <Box>
                        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>Advanced Reports</Typography>
                        <Typography variant="body2" color="text.secondary">Detailed analytics and statistics</Typography>
                    </Box>
                </Box>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Tooltip title="Refresh data">
                        <IconButton><Refresh /></IconButton>
                    </Tooltip>
                    <Button startIcon={<Download />} variant="outlined" onClick={() => exportReport('PDF')}>Export PDF</Button>
                    <Button startIcon={<Download />} variant="contained" onClick={() => exportReport('Excel')}>Export Excel</Button>
                </Box>
            </Box>
            {/* Report filters */}
            <Card variant="outlined" sx={{ mb: 3 }}>
                <CardContent>
                    <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} md={3}>
                            <FormControl fullWidth size="small">
                                <InputLabel>Report Type</InputLabel>
                                <Select value={reportType} onChange={(e) => setReportType(e.target.value)} label="Report Type">
                                    <MenuItem value="monthly">Monthly</MenuItem>
                                    <MenuItem value="weekly">Weekly</MenuItem>
                                    <MenuItem value="yearly">Yearly</MenuItem>
                                    <MenuItem value="custom">Custom</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={12} md={3}>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                                <TextField label="From" type="date" size="small" value={dateRange.start} onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })} InputLabelProps={{ shrink: true }} />
                                <TextField label="To" type="date" size="small" value={dateRange.end} onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })} InputLabelProps={{ shrink: true }} />
                            </Box>
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <FormControl fullWidth size="small">
                                <InputLabel>Metrics</InputLabel>
                                <Select multiple value={selectedMetrics} onChange={(e) => setSelectedMetrics(e.target.value)} label="Metrics">
                                    {metricsOptions.map((option) => (
                                        <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={12} md={2}>
                            <Button fullWidth variant="contained" startIcon={<FilterAlt />} onClick={generateReport}>Apply</Button>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>
            {/* Chart type */}
            <Box sx={{ mb: 3, display: 'flex', justifyContent: 'center' }}>
                <ToggleButtonGroup value={chartType} exclusive onChange={(e, newType) => newType && setChartType(newType)} aria-label="Chart Type">
                    <ToggleButton value="line" aria-label="Line"><Timeline sx={{ mr: 1 }} />Line</ToggleButton>
                    <ToggleButton value="bar" aria-label="Bar"><BarChart sx={{ mr: 1 }} />Bar</ToggleButton>
                    <ToggleButton value="pie" aria-label="Pie"><PieChart sx={{ mr: 1 }} />Pie</ToggleButton>
                    <ToggleButton value="area" aria-label="Area"><TableChart sx={{ mr: 1 }} />Area</ToggleButton>
                </ToggleButtonGroup>
            </Box>
            {/* Data display */}
            <Grid container spacing={3}>
                {/* Quick stats */}
                <Grid item xs={12}>
                    <Grid container spacing={2}>
                        <Grid item xs={6} md={3}>
                            <Card><CardContent sx={{ textAlign: 'center' }}><Typography color="text.secondary" variant="body2">Total Shipments</Typography><Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>520</Typography><Typography variant="caption" color="success.main"><TrendingUp sx={{ fontSize: 14, verticalAlign: 'middle' }} />+12% YoY</Typography></CardContent></Card>
                        </Grid>
                        <Grid item xs={6} md={3}>
                            <Card><CardContent sx={{ textAlign: 'center' }}><Typography color="text.secondary" variant="body2">Total Revenue</Typography><Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>2.85M</Typography><Typography variant="caption" color="success.main"><TrendingUp sx={{ fontSize: 14, verticalAlign: 'middle' }} />+18% YoY</Typography></CardContent></Card>
                        </Grid>
                        <Grid item xs={6} md={3}>
                            <Card><CardContent sx={{ textAlign: 'center' }}><Typography color="text.secondary" variant="body2">Avg Value</Typography><Typography variant="h4" sx={{ fontWeight: 'bold', color: 'warning.main' }}>5,480</Typography><Typography variant="caption" color="success.main"><TrendingUp sx={{ fontSize: 14, verticalAlign: 'middle' }} />+5% Avg</Typography></CardContent></Card>
                        </Grid>
                        <Grid item xs={6} md={3}>
                            <Card><CardContent sx={{ textAlign: 'center' }}><Typography color="text.secondary" variant="body2">Growth Rate</Typography><Typography variant="h4" sx={{ fontWeight: 'bold', color: 'info.main' }}>24%</Typography><Typography variant="caption" color="success.main"><TrendingUp sx={{ fontSize: 14, verticalAlign: 'middle' }} />+4% Q/Q</Typography></CardContent></Card>
                        </Grid>
                    </Grid>
                </Grid>
                {/* Chart panel */}
                <Grid item xs={12} md={8}>
                    <Card sx={{ height: 400 }}>
                        <CardContent>
                            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>{reportType === 'monthly' ? 'Monthly Revenue' : reportType === 'weekly' ? 'Weekly Revenue' : 'Yearly Revenue'}</Typography>
                            <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'rgba(0,0,0,0.02)', borderRadius: 1 }}>
                                <Box sx={{ textAlign: 'center' }}>
                                    <Analytics sx={{ fontSize: 60, color: 'text.disabled', mb: 2 }} />
                                    <Typography color="text.secondary">{chartType === 'line' ? 'Line Chart' : chartType === 'bar' ? 'Bar Chart' : chartType === 'pie' ? 'Pie Chart' : 'Area Chart'}</Typography>
                                    <Typography variant="caption" color="text.secondary">(Will be replaced with real chart library)</Typography>
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
                {/* Analysis */}
                <Grid item xs={12} md={4}>
                    <Card sx={{ height: 400 }}>
                        <CardContent>
                            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>📊 Data Analysis</Typography>
                            <Box sx={{ mt: 2 }}>
                                <Typography variant="body2" gutterBottom><strong>Key Trends:</strong></Typography>
                                <Box component="ul" sx={{ pl: 2 }}>
                                    <li><Typography variant="body2" color="text.secondary">Stable growth in shipment count</Typography></li>
                                    <li><Typography variant="body2" color="text.secondary">Increase in average shipment value</Typography></li>
                                    <li><Typography variant="body2" color="text.secondary">Decrease in operating costs</Typography></li>
                                </Box>
                                <Typography variant="body2" gutterBottom sx={{ mt: 3 }}><strong>Recommendations:</strong></Typography>
                                <Box component="ul" sx={{ pl: 2 }}>
                                    <li><Typography variant="body2" color="text.secondary">Focus on high-profit routes</Typography></li>
                                    <li><Typography variant="body2" color="text.secondary">Optimize fleet usage during peak periods</Typography></li>
                                    <li><Typography variant="body2" color="text.secondary">Expand customer base in growing regions</Typography></li>
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
                {/* Detailed table */}
                <Grid item xs={12}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>📋 Detailed Data</Typography>
                            <Box sx={{ mt: 2, overflowX: 'auto' }}>
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                    <thead>
                                        <tr style={{ backgroundColor: theme.palette.grey[100] }}>
                                            <th style={{ padding: '12px', textAlign: 'right' }}>Period</th>
                                            <th style={{ padding: '12px', textAlign: 'center' }}>Shipments</th>
                                            <th style={{ padding: '12px', textAlign: 'center' }}>Revenue</th>
                                            <th style={{ padding: '12px', textAlign: 'center' }}>Expenses</th>
                                            <th style={{ padding: '12px', textAlign: 'center' }}>Profit</th>
                                            <th style={{ padding: '12px', textAlign: 'center' }}>Growth</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {reportData[reportType].map((row, index) => (
                                            <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                                                <td style={{ padding: '12px', textAlign: 'right', fontWeight: 'bold' }}>{row.month || row.week || row.year}</td>
                                                <td style={{ padding: '12px', textAlign: 'center' }}>{row.shipments}</td>
                                                <td style={{ padding: '12px', textAlign: 'center', color: theme.palette.success.main, fontWeight: 'bold' }}>{row.revenue.toLocaleString()} SAR</td>
                                                <td style={{ padding: '12px', textAlign: 'center', color: theme.palette.warning.main }}>{row.expenses?.toLocaleString()} SAR</td>
                                                <td style={{ padding: '12px', textAlign: 'center', color: theme.palette.info.main, fontWeight: 'bold' }}>{row.profit?.toLocaleString()} SAR</td>
                                                <td style={{ padding: '12px', textAlign: 'center' }}><Chip label={index > 0 ? '+12%' : '- -'} color="success" size="small" sx={{ fontSize: '0.7rem' }} /></td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
            {/* Info alert */}
            <Alert severity="info" sx={{ mt: 3 }}>
                <Typography variant="body2">💡 <strong>Note:</strong> Data is updated as of {new Date().toLocaleDateString()}. You can refresh manually or set auto-update in settings.</Typography>
            </Alert>
        </Paper>
    );
};

export default AdvancedReports;
