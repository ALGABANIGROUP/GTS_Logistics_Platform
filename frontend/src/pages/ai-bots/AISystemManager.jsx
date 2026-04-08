// frontend/src/pages/ai-bots/AISystemManager.jsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  CpuChip as CpuIcon,
  Database as DatabaseIcon,
  Schedule as ScheduleIcon,
  Security as SecurityIcon,
  People as PeopleIcon,
  Flag as FlagIcon,
  Code as CodeIcon
} from '@mui/icons-material';
import { useNotification } from '../../contexts/NotificationContext';
import axiosClient from '../../api/axiosClient';

const AISystemManager = () => {
  const [loading, setLoading] = useState(true);
  const [systemHealth, setSystemHealth] = useState(null);
  const [roleDistribution, setRoleDistribution] = useState([]);
  const [userAccess, setUserAccess] = useState([]);
  const [featureFlags, setFeatureFlags] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [bottlenecks, setBottlenecks] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [sqlQuery, setSqlQuery] = useState('');
  const [sqlResult, setSqlResult] = useState(null);
  const [sqlDialogOpen, setSqlDialogOpen] = useState(false);
  
  const { showSuccess, showError } = useNotification();

  // Fetch all data
  const fetchAllData = useCallback(async () => {
    setLoading(true);
    try {
      console.log('Fetching system health...');
      const healthRes = await axiosClient.get('/api/v1/system-manager/health');
      console.log('Health response:', healthRes.data);
      setSystemHealth(healthRes.data);

      try {
        const rolesRes = await axiosClient.get('/api/v1/system-manager/roles/distribution');
        setRoleDistribution(rolesRes.data.roles || []);
      } catch (e) { console.log('Roles API failed'); }

      try {
        const usersRes = await axiosClient.get('/api/v1/system-manager/users/access');
        setUserAccess(usersRes.data.users || []);
      } catch (e) { console.log('Users API failed'); }

      try {
        const featuresRes = await axiosClient.get('/api/v1/system-manager/features');
        setFeatureFlags(featuresRes.data.features || []);
      } catch (e) { console.log('Features API failed'); }

      try {
        const alertsRes = await axiosClient.get('/api/v1/system-manager/alerts/active');
        setAlerts(alertsRes.data.alerts || []);
      } catch (e) { console.log('Alerts API failed'); }

      try {
        const bottlenecksRes = await axiosClient.get('/api/v1/system-manager/bottlenecks');
        setBottlenecks(bottlenecksRes.data.bottlenecks || []);
      } catch (e) { console.log('Bottlenecks API failed'); }

      try {
        const forecastRes = await axiosClient.get('/api/v1/system-manager/forecast');
        setForecast(forecastRes.data);
      } catch (e) { console.log('Forecast API failed'); }

    } catch (error) {
      console.error('Error fetching system data:', error);
      showError('Failed to fetch system data. Using mock data.');
      
      // Fallback mock data
      setSystemHealth({
        status: "healthy",
        metrics: {
          cpu: { percent: 23.5, cores: 8, status: "normal" },
          memory: { percent: 45.2, used_gb: 7.2, total_gb: 16, status: "normal" },
          disk: { percent: 58.3, free_gb: 245.5, total_gb: 500, status: "normal" },
          database: { status: "healthy", response_time_ms: 45 },
          uptime: { days: 45, human_readable: "45 days, 3 hours" },
          bots: { active: 14, total: 14, names: ["AI Dispatcher", "AI Operations", "AI Security", "AI Legal", "AI Finance", "AI Sales", "AI Customer Service", "AI Documents", "AI Information", "AI Trainer", "AI Partner", "AI Maintenance", "AI System", "AI Safety"] }
        }
      });
      
      setRoleDistribution([
        { role: "super_admin", count: 2, percentage: 5 },
        { role: "admin", count: 5, percentage: 12.5 },
        { role: "manager", count: 8, percentage: 20 },
        { role: "dispatcher", count: 12, percentage: 30 },
        { role: "carrier", count: 8, percentage: 20 },
        { role: "shipper", count: 5, percentage: 12.5 }
      ]);
      
      setUserAccess([
        { id: 1, email: "superadmin@gts.com", full_name: "Super Administrator", role: "super_admin", assigned_bots: ["AI System Manager", "AI Security"], features: ["all"], last_login: new Date().toISOString() },
        { id: 2, email: "admin@gts.com", full_name: "Admin User", role: "admin", assigned_bots: ["AI System Manager"], features: ["user_management"], last_login: new Date().toISOString() }
      ]);
      
      setFeatureFlags([
        { name: "ai_bots_advanced", enabled: true, description: "Advanced AI bot features" },
        { name: "real_time_tracking", enabled: true, description: "Real-time shipment tracking" },
        { name: "analytics_dashboard", enabled: true, description: "Advanced analytics" },
        { name: "api_access", enabled: true, description: "External API access" }
      ]);
      
      setAlerts([
        { id: 1, severity: "warning", message: "Database connection pool at 85% capacity", timestamp: new Date().toISOString() },
        { id: 2, severity: "info", message: "SSL certificate expires in 30 days", timestamp: new Date().toISOString() }
      ]);
      
      setBottlenecks([
        { id: 1, component: "Database", issue: "Slow query on shipments table", impact: "Medium", suggestion: "Add index on created_at" }
      ]);
      
      setForecast({
        recommendation: "System resources are adequate. Monitor memory usage.",
        forecast_days: 10
      });
      
    } finally {
      setLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Analyze SQL
  const handleAnalyzeQuery = async () => {
    if (!sqlQuery.trim()) {
      showError('Please enter a SQL query to analyze');
      return;
    }
    
    try {
      const response = await axiosClient.post('/api/v1/system-manager/sql/analyze', { query: sqlQuery });
      setSqlResult(response.data);
      setSqlDialogOpen(true);
    } catch (error) {
      showError('Failed to analyze query');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  const metrics = systemHealth?.metrics || {};

  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight="bold" sx={{ color: '#1a237e' }}>
            AI System Manager
          </Typography>
          <Typography variant="body2" sx={{ color: '#666', mt: 0.5 }}>
            Platform health, RBAC governance, bot assignment, and operational tuning.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Chip label={`Version 2.0.0`} variant="outlined" />
          <Chip label="Mode: infrastructure" color="primary" />
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={fetchAllData}>
            Refresh
          </Button>
        </Box>
      </Box>

      {/* System Health Cards */}
      <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, color: '#1a237e' }}>
        System Health
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ borderRadius: 2, bgcolor: '#e3f2fd' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <CpuIcon sx={{ fontSize: 40, color: '#1565c0' }} />
                <Typography variant="h3" fontWeight="bold">{metrics.cpu?.percent || 0}%</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">CPU Usage</Typography>
              <LinearProgress variant="determinate" value={metrics.cpu?.percent || 0} sx={{ mt: 1, height: 8, borderRadius: 4 }} />
              <Typography variant="caption" color="text.secondary">{metrics.cpu?.cores || 0} logical cores</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ borderRadius: 2, bgcolor: '#e8f5e9' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <MemoryIcon sx={{ fontSize: 40, color: '#2e7d32' }} />
                <Typography variant="h3" fontWeight="bold">{metrics.memory?.percent || 0}%</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">Memory Usage</Typography>
              <LinearProgress variant="determinate" value={metrics.memory?.percent || 0} sx={{ mt: 1, height: 8, borderRadius: 4 }} />
              <Typography variant="caption" color="text.secondary">{metrics.memory?.used_gb || 0} GB used / {metrics.memory?.total_gb || 16} GB</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ borderRadius: 2, bgcolor: '#fff3e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <StorageIcon sx={{ fontSize: 40, color: '#ef6c00' }} />
                <Typography variant="h3" fontWeight="bold">{metrics.disk?.percent || 0}%</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">Disk Usage</Typography>
              <LinearProgress variant="determinate" value={metrics.disk?.percent || 0} sx={{ mt: 1, height: 8, borderRadius: 4 }} />
              <Typography variant="caption" color="text.secondary">{metrics.disk?.free_gb || 0} GB free</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ borderRadius: 2, bgcolor: '#f3e5f5' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <DatabaseIcon sx={{ fontSize: 40, color: '#6a1b9a' }} />
                <Typography variant="h3" fontWeight="bold">{metrics.database?.response_time_ms || 0}ms</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">Database Response</Typography>
              <Chip size="small" label={metrics.database?.status || "Unknown"} color={metrics.database?.status === 'healthy' ? 'success' : 'warning'} sx={{ mt: 1 }} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Platform Health Section */}
      <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, color: '#1a237e' }}>
        Platform Health
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold">System Status</Typography>
              <Box sx={{ display: 'flex', gap: 3, mt: 2, flexWrap: 'wrap' }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">Uptime</Typography>
                  <Typography variant="body1">{metrics.uptime?.human_readable || 'unknown'}</Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">Managed Bots</Typography>
                  <Typography variant="body1">{metrics.bots?.active || 0}/{metrics.bots?.total || 14}</Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">Overall Status</Typography>
                  <Chip size="small" label={systemHealth?.status || "Unknown"} color={systemHealth?.status === 'healthy' ? 'success' : 'warning'} />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold">Active Bots</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
                {(metrics.bots?.names || []).slice(0, 8).map((bot, idx) => (
                  <Chip key={idx} label={bot} size="small" variant="outlined" />
                ))}
                {(metrics.bots?.names?.length || 0) > 8 && (
                  <Chip label={`+${metrics.bots.names.length - 8} more`} size="small" />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Access Control Summary */}
      <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, color: '#1a237e' }}>
        Access Control Summary
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold">Role Distribution</Typography>
              <Box sx={{ mt: 2 }}>
                {roleDistribution.map((role, idx) => (
                  <Box key={idx} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{role.role}</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '60%' }}>
                      <LinearProgress variant="determinate" value={role.percentage} sx={{ flex: 1, height: 6, borderRadius: 3 }} />
                      <Typography variant="body2" color="text.secondary">{role.count} users</Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                Users with direct bot scopes: {userAccess.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold">Feature Flags</Typography>
              <Box sx={{ mt: 2 }}>
                {featureFlags.map((flag, idx) => (
                  <Box key={idx} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="body2">{flag.name}</Typography>
                    <Chip size="small" label={flag.enabled ? 'Enabled' : 'Disabled'} color={flag.enabled ? 'success' : 'default'} />
                  </Box>
                ))}
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                Feature grants assigned: {featureFlags.filter(f => f.enabled).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* User Access Directory */}
      <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, color: '#1a237e' }}>
        User Access Directory
      </Typography>
      <Button variant="contained" startIcon={<PeopleIcon />} sx={{ mb: 2, bgcolor: '#1a237e' }}>
        Create User
      </Button>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead sx={{ bgcolor: '#f5f5f5' }}>
            <TableRow>
              <TableCell>Identity</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Assigned Bots</TableCell>
              <TableCell>Features</TableCell>
              <TableCell>Last Login</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {userAccess.map((user) => (
              <TableRow key={user.id} hover>
                <TableCell>
                  <Box>
                    <Typography variant="body2" fontWeight="bold">{user.full_name}</Typography>
                    <Typography variant="caption" color="text.secondary">{user.email}</Typography>
                  </Box>
                </TableCell>
                <TableCell><Chip label={user.role} size="small" /></TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {user.assigned_bots?.slice(0, 2).map((bot, idx) => (
                      <Chip key={idx} label={bot} size="small" variant="outlined" />
                    ))}
                    {(user.assigned_bots?.length || 0) > 2 && <Chip label={`+${user.assigned_bots.length - 2}`} size="small" />}
                  </Box>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {user.features?.slice(0, 2).map((feat, idx) => (
                      <Chip key={idx} label={feat} size="small" variant="outlined" />
                    ))}
                  </Box>
                </TableCell>
                <TableCell>{user.last_login ? new Date(user.last_login).toLocaleDateString() : '-'}</TableCell>
                <TableCell>
                  <Tooltip title="Edit">
                    <IconButton size="small"><SecurityIcon fontSize="small" /></IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* System Actions */}
      <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, color: '#1a237e' }}>
        System Actions
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ borderRadius: 2, height: '100%' }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold">Active Alerts</Typography>
              {alerts.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>No active alerts.</Typography>
              ) : (
                alerts.map((alert) => (
                  <Alert key={alert.id} severity={alert.severity} sx={{ mt: 1 }}>
                    {alert.message}
                  </Alert>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ borderRadius: 2, height: '100%' }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold">Bottlenecks</Typography>
              {bottlenecks.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>No bottlenecks flagged.</Typography>
              ) : (
                bottlenecks.map((bn) => (
                  <Box key={bn.id} sx={{ mt: 1, p: 1, bgcolor: '#fff3e0', borderRadius: 1 }}>
                    <Typography variant="body2" fontWeight="bold">{bn.component}</Typography>
                    <Typography variant="caption" color="text.secondary">{bn.issue}</Typography>
                    <Typography variant="caption" display="block" color="success.main">💡 {bn.suggestion}</Typography>
                  </Box>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ borderRadius: 2, height: '100%' }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold">Resource Forecast</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                {forecast?.recommendation || 'No forecast data available.'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* SQL Rewrite Workbench */}
      <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, color: '#1a237e' }}>
        SQL Rewrite Workbench
      </Typography>
      <Card sx={{ borderRadius: 2 }}>
        <CardContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            placeholder="Enter SQL query to analyze..."
            value={sqlQuery}
            onChange={(e) => setSqlQuery(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button variant="contained" startIcon={<CodeIcon />} onClick={handleAnalyzeQuery} sx={{ bgcolor: '#1a237e' }}>
            Analyze Query
          </Button>
        </CardContent>
      </Card>

      {/* SQL Results Dialog */}
      <Dialog open={sqlDialogOpen} onClose={() => setSqlDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>SQL Analysis Results</DialogTitle>
        <DialogContent>
          {sqlResult && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold">Original Query:</Typography>
              <Paper sx={{ p: 2, bgcolor: '#f5f5f5', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                {sqlResult.query}
              </Paper>
              <Typography variant="subtitle1" fontWeight="bold" sx={{ mt: 2 }}>Analysis:</Typography>
              <Typography variant="body2">Complexity: {sqlResult.analysis?.complexity}</Typography>
              <Typography variant="body2">Estimated Cost: {sqlResult.analysis?.estimated_cost}</Typography>
              <Typography variant="subtitle1" fontWeight="bold" sx={{ mt: 2 }}>Suggestions:</Typography>
              <ul>
                {sqlResult.analysis?.suggestions?.map((s, i) => (
                  <li key={i}><Typography variant="body2">{s}</Typography></li>
                ))}
              </ul>
              {sqlResult.analysis?.optimized_version && (
                <>
                  <Typography variant="subtitle1" fontWeight="bold" sx={{ mt: 2 }}>Optimized Version:</Typography>
                  <Paper sx={{ p: 2, bgcolor: '#e8f5e9', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                    {sqlResult.analysis.optimized_version}
                  </Paper>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSqlDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AISystemManager;