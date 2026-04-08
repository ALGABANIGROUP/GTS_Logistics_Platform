// frontend/src/pages/admin/Partners.jsx
import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  Select,
  MenuItem,
  CircularProgress,
  Tooltip,
  Avatar,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Rating,
  Tab,
  Tabs,
  InputLabel
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Business as BusinessIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Refresh as RefreshIcon,
  LocalShipping as TruckIcon,
  Inventory as ShipperIcon,
  Handshake as BrokerIcon,
  Factory as SupplierIcon,
  People as CustomerIcon,
} from '@mui/icons-material';
import { useNotification } from '../../contexts/NotificationContext';
import axiosClient from '../../api/axiosClient';

const glassPanelSx = {
  background: 'var(--glass-bg, rgba(15, 23, 42, 0.35))',
  border: '1px solid var(--glass-border, rgba(255, 255, 255, 0.12))',
  backdropFilter: 'var(--glass-blur, blur(18px))',
  WebkitBackdropFilter: 'var(--glass-blur, blur(18px))',
  boxShadow: 'var(--glass-shadow, 0 10px 30px rgba(0, 0, 0, 0.35))',
};

const glassFieldSx = {
  '& .MuiOutlinedInput-root': {
    background: 'rgba(15, 23, 42, 0.32)',
    color: '#f8fafc',
    borderRadius: 3,
    backdropFilter: 'blur(14px)',
    WebkitBackdropFilter: 'blur(14px)',
    '& fieldset': {
      borderColor: 'rgba(255,255,255,0.12)',
    },
    '&:hover fieldset': {
      borderColor: 'rgba(255,255,255,0.22)',
    },
    '&.Mui-focused fieldset': {
      borderColor: 'rgba(96, 165, 250, 0.7)',
      boxShadow: '0 0 0 3px rgba(59, 130, 246, 0.15)',
    },
    '& input::placeholder': {
      color: 'rgba(226, 232, 240, 0.55)',
      opacity: 1,
    },
    '& textarea::placeholder': {
      color: 'rgba(226, 232, 240, 0.55)',
      opacity: 1,
    },
  },
  '& .MuiInputLabel-root': {
    color: 'rgba(226, 232, 240, 0.75)',
  },
  '& .MuiInputLabel-root.Mui-focused': {
    color: '#bfdbfe',
  },
  '& .MuiSvgIcon-root': {
    color: 'rgba(191, 219, 254, 0.8)',
  },
};

const ghostButtonSx = {
  borderRadius: 999,
  textTransform: 'none',
  px: 2.5,
  borderColor: 'rgba(255,255,255,0.16)',
  color: '#e2e8f0',
  background: 'rgba(15, 23, 42, 0.28)',
  backdropFilter: 'blur(14px)',
  WebkitBackdropFilter: 'blur(14px)',
  '&:hover': {
    borderColor: 'rgba(255,255,255,0.24)',
    background: 'rgba(30, 41, 59, 0.42)',
  },
};

const Partners = () => {
  const [partners, setPartners] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [partnerType, setPartnerType] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalPartners, setTotalPartners] = useState(0);
  const [stats, setStats] = useState({ total: 0, active: 0, inactive: 0, by_type: {} });
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingPartner, setEditingPartner] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [partnerToDelete, setPartnerToDelete] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  const [formData, setFormData] = useState({
    name: '',
    type: 'carrier',
    email: '',
    phone: '',
    address: '',
    contact_person: '',
    mc_number: '',
    dot_number: '',
    tax_id: '',
    website: '',
    notes: '',
    status: 'active',
    rating: 3,
    tags: []
  });

  const [tagInput, setTagInput] = useState('');

  const { showSuccess, showError, showInfo } = useNotification();

  const applyTabFilter = useCallback((value) => {
    setTabValue(value);
    setPage(0);
    switch (value) {
      case 1:
        setPartnerType('carrier');
        break;
      case 2:
        setPartnerType('shipper');
        break;
      case 3:
        setPartnerType('broker');
        break;
      case 4:
        setPartnerType('supplier');
        break;
      default:
        setPartnerType('all');
        break;
    }
  }, []);

  // جلب الشركاء
  const fetchPartners = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axiosClient.get('/api/v1/partners/', {
        params: {
          page: page + 1,
          limit: rowsPerPage,
          search: searchTerm || undefined,
          partner_type: partnerType !== 'all' ? partnerType : undefined,
          status: statusFilter !== 'all' ? statusFilter : undefined
        }
      });
      setPartners(response.data.partners || []);
      setTotalPartners(response.data.total || 0);
    } catch (error) {
      showError(error.response?.data?.detail || 'Failed to fetch partners');
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, searchTerm, partnerType, statusFilter, showError]);

  // جلب الإحصائيات
  const fetchStats = useCallback(async () => {
    try {
      const response = await axiosClient.get('/api/v1/partners/stats/summary');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  }, []);

  useEffect(() => {
    fetchPartners();
    fetchStats();
  }, [fetchPartners, fetchStats]);

  useEffect(() => {
    const nextTab = {
      all: 0,
      carrier: 1,
      shipper: 2,
      broker: 3,
      supplier: 4,
    }[partnerType] ?? 0;

    if (tabValue !== nextTab) {
      setTabValue(nextTab);
    }
  }, [partnerType, tabValue]);

  // فتح حوار إنشاء/تعديل
  const handleOpenDialog = (partner = null) => {
    if (partner) {
      setEditingPartner(partner);
      setFormData({
        name: partner.name,
        type: partner.type,
        email: partner.email || '',
        phone: partner.phone || '',
        address: partner.address || '',
        contact_person: partner.contact_person || '',
        mc_number: partner.mc_number || '',
        dot_number: partner.dot_number || '',
        tax_id: partner.tax_id || '',
        website: partner.website || '',
        notes: partner.notes || '',
        status: partner.status,
        rating: partner.rating || 3,
        tags: partner.tags || []
      });
    } else {
      setEditingPartner(null);
      setFormData({
        name: '',
        type: 'carrier',
        email: '',
        phone: '',
        address: '',
        contact_person: '',
        mc_number: '',
        dot_number: '',
        tax_id: '',
        website: '',
        notes: '',
        status: 'active',
        rating: 3,
        tags: []
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingPartner(null);
  };

  // إضافة علامة (Tag)
  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({ ...formData, tags: [...formData.tags, tagInput.trim()] });
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove) => {
    setFormData({ ...formData, tags: formData.tags.filter(tag => tag !== tagToRemove) });
  };

  // حفظ شريك
  const handleSavePartner = async () => {
    if (!formData.name) {
      showError('Partner name is required');
      return;
    }

    try {
      showInfo(editingPartner ? 'Updating partner...' : 'Creating partner...');

      if (editingPartner) {
        await axiosClient.patch(`/api/v1/partners/${editingPartner.id}`, formData);
        showSuccess('Partner updated successfully');
      } else {
        await axiosClient.post('/api/v1/partners/', formData);
        showSuccess('Partner created successfully');
      }

      handleCloseDialog();
      fetchPartners();
      fetchStats();
    } catch (error) {
      showError(error.response?.data?.detail || 'Failed to save partner');
    }
  };

  // حذف شريك
  const handleDeleteClick = (partner) => {
    setPartnerToDelete(partner);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!partnerToDelete) return;

    try {
      showInfo('Deactivating partner...');
      await axiosClient.delete(`/api/v1/partners/${partnerToDelete.id}`);
      showSuccess('Partner deactivated successfully');
      setDeleteDialogOpen(false);
      setPartnerToDelete(null);
      fetchPartners();
      fetchStats();
    } catch (error) {
      showError(error.response?.data?.detail || 'Failed to delete partner');
    }
  };

  // الحصول على أيقونة نوع الشريك
  const getPartnerIcon = (type) => {
    switch (type) {
      case 'carrier': return <TruckIcon sx={{ color: '#2196f3' }} />;
      case 'shipper': return <ShipperIcon sx={{ color: '#4caf50' }} />;
      case 'broker': return <BrokerIcon sx={{ color: '#ff9800' }} />;
      case 'supplier': return <SupplierIcon sx={{ color: '#9c27b0' }} />;
      case 'customer': return <CustomerIcon sx={{ color: '#00bcd4' }} />;
      default: return <BusinessIcon />;
    }
  };

  const getPartnerTypeLabel = (type) => {
    const types = {
      carrier: '🚚 Carrier',
      shipper: '📦 Shipper',
      broker: '🤝 Broker',
      supplier: '🏭 Supplier',
      customer: '👥 Customer'
    };
    return types[type] || type;
  };

  const getStatusColor = (status) => {
    return status === 'active' ? '#bbf7d0' : status === 'inactive' ? '#fecaca' : '#fed7aa';
  };

  return (
    <Box className="glass-page" sx={{ p: { xs: 2, md: 3 }, color: '#e2e8f0' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4, gap: 2, flexWrap: 'wrap' }}>
        <Box>
          <Typography variant="h4" fontWeight="bold" sx={{ color: '#f8fafc', letterSpacing: '-0.03em' }}>
            Partner Management
          </Typography>
          <Typography variant="body2" sx={{ color: 'rgba(226, 232, 240, 0.75)', mt: 0.75 }}>
            Manage carriers, shippers, brokers, suppliers, and customers
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{
            background: 'linear-gradient(135deg, rgba(59,130,246,0.78), rgba(37,99,235,0.88))',
            boxShadow: '0 18px 35px rgba(37, 99, 235, 0.28)',
            '&:hover': {
              background: 'linear-gradient(135deg, rgba(96,165,250,0.9), rgba(37,99,235,0.92))',
            },
            borderRadius: 999,
            textTransform: 'none',
            px: 3.25,
            py: 1.1,
          }}
        >
          Add Partner
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card className="glass-card" sx={{ ...glassPanelSx, borderRadius: 4 }}>
            <CardContent>
              <Typography variant="body2" sx={{ color: 'rgba(226, 232, 240, 0.72)' }}>Total Partners</Typography>
              <Typography variant="h3" fontWeight="bold" sx={{ color: '#93c5fd', mt: 1 }}>
                {stats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card className="glass-card" sx={{ ...glassPanelSx, borderRadius: 4 }}>
            <CardContent>
              <Typography variant="body2" sx={{ color: 'rgba(226, 232, 240, 0.72)' }}>Active</Typography>
              <Typography variant="h3" fontWeight="bold" sx={{ color: '#86efac', mt: 1 }}>
                {stats.active}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card className="glass-card" sx={{ ...glassPanelSx, borderRadius: 4 }}>
            <CardContent>
              <Typography variant="body2" sx={{ color: 'rgba(226, 232, 240, 0.72)' }}>Inactive</Typography>
              <Typography variant="h3" fontWeight="bold" sx={{ color: '#fca5a5', mt: 1 }}>
                {stats.inactive}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card className="glass-card" sx={{ ...glassPanelSx, borderRadius: 4 }}>
            <CardContent>
              <Typography variant="body2" sx={{ color: 'rgba(226, 232, 240, 0.72)' }}>Partner Types</Typography>
              <Typography variant="h6" fontWeight="bold" sx={{ color: '#fdba74', mt: 1 }}>
                {Object.keys(stats.by_type || {}).length} Types
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Tabs
        value={tabValue}
        onChange={(e, v) => applyTabFilter(v)}
        sx={{
          mb: 3,
          minHeight: 'auto',
          '& .MuiTabs-flexContainer': {
            gap: 1,
            flexWrap: 'wrap',
          },
          '& .MuiTabs-indicator': {
            display: 'none',
          },
        }}
      >
        {['All Partners', 'Carriers', 'Shippers', 'Brokers', 'Suppliers'].map((label, index) => (
          <Tab
            key={label}
            label={label}
            disableRipple
            sx={{
              ...ghostButtonSx,
              minHeight: 'auto',
              py: 1,
              color: tabValue === index ? '#f8fafc' : 'rgba(226, 232, 240, 0.76)',
              borderColor: tabValue === index ? 'rgba(96,165,250,0.4)' : ghostButtonSx.borderColor,
              background: tabValue === index ? 'rgba(59, 130, 246, 0.2)' : ghostButtonSx.background,
            }}
          />
        ))}
      </Tabs>

      {/* Search and Filters */}
      <Paper className="glass-panel" sx={{ ...glassPanelSx, p: 2, mb: 3, borderRadius: 4, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
        <TextField
          placeholder="Search by name, email, MC number..."
          value={searchTerm}
          onChange={(e) => {
            setPage(0);
            setSearchTerm(e.target.value);
          }}
          size="small"
          sx={{ ...glassFieldSx, flex: 1, minWidth: 200 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: 'rgba(191, 219, 254, 0.8)' }} />
              </InputAdornment>
            )
          }}
        />
        <FormControl size="small" sx={{ ...glassFieldSx, minWidth: 150 }}>
          <InputLabel>Type</InputLabel>
          <Select
            value={partnerType}
            onChange={(e) => {
              setPage(0);
              setPartnerType(e.target.value);
            }}
            label="Type"
          >
            <MenuItem value="all">All Types</MenuItem>
            <MenuItem value="carrier">🚚 Carrier</MenuItem>
            <MenuItem value="shipper">📦 Shipper</MenuItem>
            <MenuItem value="broker">🤝 Broker</MenuItem>
            <MenuItem value="supplier">🏭 Supplier</MenuItem>
            <MenuItem value="customer">👥 Customer</MenuItem>
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ ...glassFieldSx, minWidth: 120 }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={statusFilter}
            onChange={(e) => {
              setPage(0);
              setStatusFilter(e.target.value);
            }}
            label="Status"
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="inactive">Inactive</MenuItem>
          </Select>
        </FormControl>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={fetchPartners} size="small" sx={ghostButtonSx}>
          Refresh
        </Button>
      </Paper>

      {/* Partners Table */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress sx={{ color: '#93c5fd' }} />
        </Box>
      ) : partners.length === 0 ? (
        <Paper className="glass-panel" sx={{ ...glassPanelSx, p: 6, textAlign: 'center', borderRadius: 4 }}>
          <BusinessIcon sx={{ fontSize: 64, color: 'rgba(191, 219, 254, 0.7)', mb: 2 }} />
          <Typography variant="h6" sx={{ color: '#f8fafc' }}>No partners found</Typography>
          <Typography variant="body2" sx={{ color: 'rgba(226, 232, 240, 0.7)', mt: 1 }}>
            Click &quot;Add Partner&quot; to create your first partner
          </Typography>
        </Paper>
      ) : (
        <>
          <TableContainer component={Paper} className="glass-table" sx={{ ...glassPanelSx, borderRadius: 4, overflow: 'hidden' }}>
            <Table>
              <TableHead sx={{ bgcolor: 'rgba(255,255,255,0.04)' }}>
                <TableRow>
                  <TableCell sx={{ color: '#cbd5e1', borderBottomColor: 'rgba(255,255,255,0.08)' }}>Partner</TableCell>
                  <TableCell sx={{ color: '#cbd5e1', borderBottomColor: 'rgba(255,255,255,0.08)' }}>Type</TableCell>
                  <TableCell sx={{ color: '#cbd5e1', borderBottomColor: 'rgba(255,255,255,0.08)' }}>Contact</TableCell>
                  <TableCell sx={{ color: '#cbd5e1', borderBottomColor: 'rgba(255,255,255,0.08)' }}>MC/DOT</TableCell>
                  <TableCell sx={{ color: '#cbd5e1', borderBottomColor: 'rgba(255,255,255,0.08)' }}>Status</TableCell>
                  <TableCell sx={{ color: '#cbd5e1', borderBottomColor: 'rgba(255,255,255,0.08)' }}>Rating</TableCell>
                  <TableCell align="center" sx={{ color: '#cbd5e1', borderBottomColor: 'rgba(255,255,255,0.08)' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {partners.map((partner) => (
                  <TableRow
                    key={partner.id}
                    hover
                    sx={{
                      '& .MuiTableCell-root': {
                        borderBottomColor: 'rgba(255,255,255,0.06)',
                        color: '#e2e8f0',
                      },
                      '&:hover': {
                        backgroundColor: 'rgba(255,255,255,0.04)',
                      },
                    }}
                  >
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Avatar sx={{
                          width: 40,
                          height: 40,
                          background: 'linear-gradient(135deg, rgba(59,130,246,0.82), rgba(99,102,241,0.75))',
                          boxShadow: '0 12px 24px rgba(37, 99, 235, 0.24)',
                        }}>
                          {getPartnerIcon(partner.type)}
                        </Avatar>
                        <Box>
                          <Typography variant="body1" fontWeight="medium" sx={{ color: '#f8fafc' }}>
                            {partner.name}
                          </Typography>
                          {partner.website && (
                            <Typography variant="caption" sx={{ color: 'rgba(226, 232, 240, 0.6)' }}>
                              {partner.website}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        icon={getPartnerIcon(partner.type)}
                        label={getPartnerTypeLabel(partner.type)}
                        sx={{
                          bgcolor: 'rgba(255,255,255,0.06)',
                          color: '#e2e8f0',
                          border: '1px solid rgba(255,255,255,0.08)',
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      {partner.email && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <EmailIcon sx={{ fontSize: 14, color: 'rgba(191, 219, 254, 0.8)' }} />
                          <Typography variant="body2" sx={{ color: 'rgba(226, 232, 240, 0.82)' }}>{partner.email}</Typography>
                        </Box>
                      )}
                      {partner.phone && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                          <PhoneIcon sx={{ fontSize: 14, color: 'rgba(191, 219, 254, 0.8)' }} />
                          <Typography variant="body2" sx={{ color: 'rgba(226, 232, 240, 0.82)' }}>{partner.phone}</Typography>
                        </Box>
                      )}
                    </TableCell>
                    <TableCell>
                      {partner.mc_number && <Typography variant="body2" sx={{ color: '#e2e8f0' }}>MC: {partner.mc_number}</Typography>}
                      {partner.dot_number && <Typography variant="body2" fontSize="0.7rem" sx={{ color: 'rgba(226, 232, 240, 0.7)' }}>DOT: {partner.dot_number}</Typography>}
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={partner.status}
                        sx={{
                          bgcolor: partner.status === 'active'
                            ? 'rgba(34, 197, 94, 0.18)'
                            : partner.status === 'inactive'
                              ? 'rgba(239, 68, 68, 0.18)'
                              : 'rgba(249, 115, 22, 0.18)',
                          color: getStatusColor(partner.status),
                          fontWeight: 600,
                          border: '1px solid rgba(255,255,255,0.08)',
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Rating value={partner.rating || 0} size="small" readOnly sx={{ '& .MuiRating-iconFilled': { color: '#fbbf24' } }} />
                    </TableCell>
                    <TableCell align="center">
                      <Tooltip title="Edit">
                        <IconButton size="small" onClick={() => handleOpenDialog(partner)} sx={{
                          color: 'rgba(226, 232, 240, 0.78)',
                          background: 'rgba(255,255,255,0.04)',
                          mr: 0.5,
                          '&:hover': { background: 'rgba(255,255,255,0.1)' },
                        }}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton size="small" onClick={() => handleDeleteClick(partner)} sx={{
                          color: 'rgba(252, 165, 165, 0.92)',
                          background: 'rgba(127, 29, 29, 0.14)',
                          '&:hover': { background: 'rgba(127, 29, 29, 0.24)' },
                        }}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <Box className="glass-panel" sx={{ ...glassPanelSx, mt: 2, borderRadius: 4, overflow: 'hidden' }}>
            <TablePagination
              component="div"
              count={totalPartners}
              page={page}
              onPageChange={(e, newPage) => setPage(newPage)}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
              rowsPerPageOptions={[5, 10, 25, 50]}
              sx={{
                color: '#e2e8f0',
                '& .MuiTablePagination-selectIcon, & .MuiTablePagination-actions button': {
                  color: '#e2e8f0',
                },
              }}
            />
          </Box>
        </>
      )}

      {/* Create/Edit Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
        PaperProps={{
          className: 'glass-modal',
          sx: {
            ...glassPanelSx,
            background: 'rgba(11, 18, 32, 0.72)',
            borderRadius: 5,
            overflow: 'hidden',
            color: '#e2e8f0',
          },
        }}
      >
        <DialogTitle sx={{ background: 'linear-gradient(180deg, rgba(37,99,235,0.24), rgba(15,23,42,0.18))', color: '#f8fafc', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          {editingPartner ? 'Edit Partner' : 'Add New Partner'}
        </DialogTitle>
        <DialogContent sx={{ mt: 2, color: '#e2e8f0' }}>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Company Name *"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                sx={glassFieldSx}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <FormControl fullWidth sx={glassFieldSx}>
                <InputLabel>Partner Type *</InputLabel>
                <Select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  label="Partner Type *"
                  MenuProps={{
                    PaperProps: {
                      sx: {
                        ...glassPanelSx,
                        background: 'rgba(15, 23, 42, 0.92)',
                        color: '#e2e8f0',
                        mt: 1,
                      },
                    },
                  }}
                >
                  <MenuItem value="carrier">🚚 Carrier</MenuItem>
                  <MenuItem value="shipper">📦 Shipper</MenuItem>
                  <MenuItem value="broker">🤝 Broker</MenuItem>
                  <MenuItem value="supplier">🏭 Supplier</MenuItem>
                  <MenuItem value="customer">👥 Customer</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                sx={glassFieldSx}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                sx={glassFieldSx}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Contact Person"
                value={formData.contact_person}
                onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                sx={glassFieldSx}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Website"
                value={formData.website}
                onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                sx={glassFieldSx}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="MC Number"
                value={formData.mc_number}
                onChange={(e) => setFormData({ ...formData, mc_number: e.target.value })}
                sx={glassFieldSx}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="DOT Number"
                value={formData.dot_number}
                onChange={(e) => setFormData({ ...formData, dot_number: e.target.value })}
                sx={glassFieldSx}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Address"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                multiline
                rows={2}
                sx={glassFieldSx}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Notes"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                multiline
                rows={3}
                sx={glassFieldSx}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <FormControl fullWidth sx={glassFieldSx}>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  label="Status"
                  MenuProps={{
                    PaperProps: {
                      sx: {
                        ...glassPanelSx,
                        background: 'rgba(15, 23, 42, 0.92)',
                        color: '#e2e8f0',
                        mt: 1,
                      },
                    },
                  }}
                >
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography variant="body2" sx={{ mb: 1, color: 'rgba(226, 232, 240, 0.75)' }}>Rating</Typography>
              <Rating
                value={formData.rating}
                onChange={(e, newValue) => setFormData({ ...formData, rating: newValue || 0 })}
                sx={{ '& .MuiRating-iconFilled': { color: '#fbbf24' }, '& .MuiRating-iconEmpty': { color: 'rgba(255,255,255,0.18)' } }}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <Typography variant="body2" sx={{ mb: 1, color: 'rgba(226, 232, 240, 0.75)' }}>Tags</Typography>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
                {formData.tags.map((tag) => (
                  <Chip
                    key={tag}
                    label={tag}
                    size="small"
                    onDelete={() => handleRemoveTag(tag)}
                    sx={{
                      bgcolor: 'rgba(59, 130, 246, 0.16)',
                      color: '#bfdbfe',
                      border: '1px solid rgba(255,255,255,0.08)',
                    }}
                  />
                ))}
                <TextField
                  size="small"
                  placeholder="Add tag..."
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddTag();
                    }
                  }}
                  sx={{ ...glassFieldSx, width: 140 }}
                />
                <Button size="small" onClick={handleAddTag} variant="outlined" sx={ghostButtonSx}>Add</Button>
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2, gap: 1, borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <Button onClick={handleCloseDialog} variant="outlined" sx={ghostButtonSx}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSavePartner}
            disabled={!formData.name}
            sx={{
              borderRadius: 999,
              textTransform: 'none',
              px: 2.75,
              background: 'linear-gradient(135deg, rgba(59,130,246,0.78), rgba(37,99,235,0.88))',
              '&:hover': {
                background: 'linear-gradient(135deg, rgba(96,165,250,0.88), rgba(37,99,235,0.92))',
              },
            }}
          >
            {editingPartner ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        PaperProps={{
          className: 'glass-modal',
          sx: {
            ...glassPanelSx,
            background: 'rgba(11, 18, 32, 0.74)',
            borderRadius: 5,
            overflow: 'hidden',
            color: '#e2e8f0',
          },
        }}
      >
        <DialogTitle sx={{ background: 'linear-gradient(180deg, rgba(220,38,38,0.26), rgba(127,29,29,0.18))', color: '#f8fafc', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography sx={{ mt: 2, color: '#e2e8f0' }}>
            Are you sure you want to deactivate &quot;{partnerToDelete?.name}&quot;?
            <br /><br />
            <span style={{ color: '#fca5a5' }}>
              This will set the partner status to inactive. You can reactivate later.
            </span>
          </Typography>
        </DialogContent>
        <DialogActions sx={{ borderTop: '1px solid rgba(255,255,255,0.08)', p: 2 }}>
          <Button onClick={() => setDeleteDialogOpen(false)} variant="outlined" sx={ghostButtonSx}>Cancel</Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            sx={{
              borderRadius: 999,
              textTransform: 'none',
              px: 2.75,
              background: 'linear-gradient(135deg, rgba(239,68,68,0.85), rgba(185,28,28,0.9))',
              '&:hover': {
                background: 'linear-gradient(135deg, rgba(248,113,113,0.88), rgba(185,28,28,0.94))',
              },
            }}
          >
            Deactivate
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Partners;
