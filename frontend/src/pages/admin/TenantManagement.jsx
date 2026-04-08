import { useCallback, useEffect, useMemo, useState } from "react";
import PropTypes from "prop-types";
import {
  Alert,
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  Grid,
  IconButton,
  InputAdornment,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Switch,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import {
  Add as AddIcon,
  Business as BusinessIcon,
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Email as EmailIcon,
  Language as LanguageIcon,
  Phone as PhoneIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Cancel as CancelIcon,
} from "@mui/icons-material";
import { useNotification } from "../../contexts/NotificationContext";
import axiosClient from "../../api/axiosClient";

const DEFAULT_FORM = {
  name: "",
  domain: "",
  email: "",
  phone: "",
  address: "",
  subscription_tier: "basic",
  is_active: true,
};

const getTierColor = (tier) => {
  switch (tier) {
    case "enterprise":
      return { bg: "rgba(34, 197, 94, 0.18)", color: "#bbf7d0", label: "Enterprise" };
    case "professional":
      return { bg: "rgba(59, 130, 246, 0.18)", color: "#bfdbfe", label: "Professional" };
    case "basic":
      return { bg: "rgba(249, 115, 22, 0.18)", color: "#fed7aa", label: "Basic" };
    default:
      return { bg: "rgba(148, 163, 184, 0.18)", color: "#e2e8f0", label: tier || "Unknown" };
  }
};

const glassPanelSx = {
  background: "var(--glass-bg, rgba(15, 23, 42, 0.35))",
  border: "1px solid var(--glass-border, rgba(255, 255, 255, 0.12))",
  backdropFilter: "var(--glass-blur, blur(18px))",
  WebkitBackdropFilter: "var(--glass-blur, blur(18px))",
  boxShadow: "var(--glass-shadow, 0 10px 30px rgba(0, 0, 0, 0.35))",
};

const glassFieldSx = {
  "& .MuiOutlinedInput-root": {
    background: "rgba(15, 23, 42, 0.32)",
    color: "#f8fafc",
    borderRadius: 3,
    backdropFilter: "blur(14px)",
    WebkitBackdropFilter: "blur(14px)",
    "& fieldset": {
      borderColor: "rgba(255,255,255,0.12)",
    },
    "&:hover fieldset": {
      borderColor: "rgba(255,255,255,0.22)",
    },
    "&.Mui-focused fieldset": {
      borderColor: "rgba(96, 165, 250, 0.7)",
      boxShadow: "0 0 0 3px rgba(59, 130, 246, 0.15)",
    },
    "& input::placeholder": {
      color: "rgba(226, 232, 240, 0.55)",
      opacity: 1,
    },
    "& textarea::placeholder": {
      color: "rgba(226, 232, 240, 0.55)",
      opacity: 1,
    },
    "& .MuiSvgIcon-root": {
      color: "rgba(191, 219, 254, 0.8)",
    },
  },
  "& .MuiInputLabel-root": {
    color: "rgba(226, 232, 240, 0.75)",
  },
  "& .MuiInputLabel-root.Mui-focused": {
    color: "#bfdbfe",
  },
  "& .MuiFormHelperText-root": {
    color: "rgba(226, 232, 240, 0.65)",
  },
};

const ghostButtonSx = {
  borderRadius: 999,
  textTransform: "none",
  px: 2.5,
  borderColor: "rgba(255,255,255,0.16)",
  color: "#e2e8f0",
  background: "rgba(15, 23, 42, 0.28)",
  backdropFilter: "blur(14px)",
  WebkitBackdropFilter: "blur(14px)",
  "&:hover": {
    borderColor: "rgba(255,255,255,0.24)",
    background: "rgba(30, 41, 59, 0.42)",
  },
};

function StatusChip({ isActive }) {
  return (
    <Chip
      size="small"
      icon={isActive ? <CheckCircleIcon sx={{ fontSize: 16 }} /> : <CancelIcon sx={{ fontSize: 16 }} />}
      label={isActive ? "Active" : "Inactive"}
      sx={{
        bgcolor: isActive ? "rgba(34, 197, 94, 0.18)" : "rgba(239, 68, 68, 0.18)",
        color: isActive ? "#bbf7d0" : "#fecaca",
        fontWeight: 600,
        border: "1px solid rgba(255,255,255,0.08)",
        "& .MuiChip-icon": { color: "inherit" },
      }}
    />
  );
}

StatusChip.propTypes = {
  isActive: PropTypes.bool.isRequired,
};

const TenantManagement = () => {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage] = useState(10);
  const [totalTenants, setTotalTenants] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTenant, setEditingTenant] = useState(null);
  const [formData, setFormData] = useState(DEFAULT_FORM);
  const [pageError, setPageError] = useState("");

  const { showSuccess, showError } = useNotification();

  const fetchTenants = useCallback(async () => {
    setLoading(true);
    setPageError("");
    try {
      const response = await axiosClient.get("/api/v1/tenants/", {
        params: {
          page: page + 1,
          limit: rowsPerPage,
          search: searchTerm || undefined,
        },
      });
      const data = response?.data || {};
      setTenants(Array.isArray(data.tenants) ? data.tenants : []);
      setTotalTenants(Number(data.total || 0));
    } catch (error) {
      const message =
        error?.response?.data?.detail || error?.message || "Failed to fetch tenants";
      setPageError(String(message));
      showError(message, "Loading Error");
      setTenants([]);
      setTotalTenants(0);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, searchTerm, showError]);

  useEffect(() => {
    fetchTenants();
  }, [fetchTenants]);

  const handleOpenDialog = (tenant = null) => {
    if (tenant) {
      setEditingTenant(tenant);
      setFormData({
        name: tenant.name || "",
        domain: tenant.domain || "",
        email: tenant.email || "",
        phone: tenant.phone || "",
        address: tenant.address || "",
        subscription_tier: tenant.subscription_tier || "basic",
        is_active: Boolean(tenant.is_active),
      });
    } else {
      setEditingTenant(null);
      setFormData(DEFAULT_FORM);
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingTenant(null);
    setFormData(DEFAULT_FORM);
  };

  const handleSaveTenant = async () => {
    if (!formData.name.trim()) {
      showError("Company name is required", "Validation Error");
      return;
    }

    setSaving(true);
    try {
      if (editingTenant) {
        await axiosClient.patch(`/api/v1/tenants/${editingTenant.id}`, formData);
        showSuccess("Tenant updated successfully", "Update Complete");
      } else {
        await axiosClient.post("/api/v1/tenants/", formData);
        showSuccess("Tenant created successfully", "Creation Complete");
      }
      handleCloseDialog();
      await fetchTenants();
    } catch (error) {
      showError(error?.response?.data?.detail || "Failed to save tenant", "Save Failed");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteTenant = async (tenantId, tenantName) => {
    if (!window.confirm(`Are you sure you want to delete "${tenantName}"?`)) {
      return;
    }

    try {
      await axiosClient.delete(`/api/v1/tenants/${tenantId}`);
      showSuccess("Tenant deleted successfully", "Deletion Complete");
      await fetchTenants();
    } catch (error) {
      showError(error?.response?.data?.detail || "Failed to delete tenant", "Deletion Failed");
    }
  };

  const stats = useMemo(
    () => ({
      total: totalTenants,
      active: tenants.filter((tenant) => tenant.is_active).length,
      inactive: tenants.filter((tenant) => !tenant.is_active).length,
      enterprise: tenants.filter((tenant) => tenant.subscription_tier === "enterprise").length,
    }),
    [tenants, totalTenants]
  );

  return (
    <Box className="glass-page" sx={{ p: { xs: 2, md: 3 }, color: "#e2e8f0" }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4, gap: 2, flexWrap: "wrap" }}>
        <Box>
          <Typography variant="h4" fontWeight="bold" sx={{ color: "#f8fafc", letterSpacing: "-0.03em" }}>
            Tenant Management
          </Typography>
          <Typography variant="body2" sx={{ color: "rgba(226, 232, 240, 0.75)", mt: 0.75 }}>
            Manage organizations and their subscription plans
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{
            background: "linear-gradient(135deg, rgba(59,130,246,0.78), rgba(37,99,235,0.88))",
            boxShadow: "0 18px 35px rgba(37, 99, 235, 0.28)",
            "&:hover": {
              background: "linear-gradient(135deg, rgba(96,165,250,0.9), rgba(37,99,235,0.92))",
            },
            borderRadius: 999,
            textTransform: "none",
            px: 3.25,
            py: 1.1,
          }}
        >
          Create Tenant
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[
          { label: "Total Tenants", value: stats.total, color: "#1a237e" },
          { label: "Active", value: stats.active, color: "#2e7d32" },
          { label: "Inactive", value: stats.inactive, color: "#c62828" },
          { label: "Enterprise", value: stats.enterprise, color: "#1565c0" },
        ].map((item) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={item.label}>
            <Card
              className="glass-card"
              sx={{
                ...glassPanelSx,
                borderRadius: 4,
                position: "relative",
                overflow: "hidden",
                "&::before": {
                  content: '""',
                  position: "absolute",
                  inset: 0,
                  background: "linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.01) 55%)",
                  pointerEvents: "none",
                },
              }}
            >
              <CardContent>
                <Typography variant="body2" sx={{ color: "rgba(226, 232, 240, 0.72)" }}>
                  {item.label}
                </Typography>
                <Typography variant="h3" fontWeight="bold" sx={{ color: item.color, mt: 1 }}>
                  {item.value}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Paper
        className="glass-panel"
        sx={{
          ...glassPanelSx,
          p: 2,
          mb: 3,
          borderRadius: 4,
          display: "flex",
          gap: 2,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <TextField
          placeholder="Search by name or domain..."
          value={searchTerm}
          onChange={(event) => {
            setPage(0);
            setSearchTerm(event.target.value);
          }}
          size="small"
          sx={{ ...glassFieldSx, flex: 1, minWidth: 280 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: "rgba(191, 219, 254, 0.8)" }} />
              </InputAdornment>
            ),
          }}
        />
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={fetchTenants} size="small" sx={ghostButtonSx}>
          Refresh
        </Button>
      </Paper>

      {pageError ? (
        <Alert
          severity="error"
          className="glass-panel"
          sx={{
            ...glassPanelSx,
            mb: 3,
            borderRadius: 3,
            color: "#fee2e2",
            background: "rgba(127, 29, 29, 0.28)",
            "& .MuiAlert-icon": { color: "#fca5a5" },
          }}
        >
          {pageError}
        </Alert>
      ) : null}

      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
          <CircularProgress sx={{ color: "#93c5fd" }} />
        </Box>
      ) : tenants.length === 0 ? (
        <Paper
          className="glass-panel"
          sx={{
            ...glassPanelSx,
            p: 6,
            textAlign: "center",
            borderRadius: 4,
          }}
        >
          <BusinessIcon sx={{ fontSize: 64, color: "rgba(191, 219, 254, 0.7)", mb: 2 }} />
          <Typography variant="h6" sx={{ color: "#f8fafc" }}>
            No tenants found
          </Typography>
          <Typography variant="body2" sx={{ color: "rgba(226, 232, 240, 0.7)", mt: 1 }}>
            Click &quot;Create Tenant&quot; to add your first organization
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {tenants.map((tenant) => {
            const tierInfo = getTierColor(tenant.subscription_tier);
            return (
              <Grid size={{ xs: 12, md: 6, lg: 4 }} key={tenant.id}>
                <Card
                  className="glass-card"
                  sx={{
                    ...glassPanelSx,
                    borderRadius: 3,
                    transition: "transform 0.2s, box-shadow 0.2s, border-color 0.2s",
                    background: "linear-gradient(180deg, rgba(15,23,42,0.16), rgba(15,23,42,0.34))",
                    "&:hover": {
                      transform: "translateY(-4px)",
                      boxShadow: "0 18px 36px rgba(0,0,0,0.26)",
                      borderColor: "rgba(255,255,255,0.2)",
                    },
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 2 }}>
                      <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                        <Avatar
                          sx={{
                            width: 48,
                            height: 48,
                            background: "linear-gradient(135deg, rgba(59,130,246,0.82), rgba(99,102,241,0.75))",
                            boxShadow: "0 12px 24px rgba(37, 99, 235, 0.24)",
                          }}
                        >
                          <BusinessIcon />
                        </Avatar>
                        <Box>
                          <Typography variant="h6" fontWeight="bold" sx={{ color: "#f8fafc" }}>
                            {tenant.name}
                          </Typography>
                          <Chip
                            size="small"
                            label={tierInfo.label}
                            sx={{
                              bgcolor: tierInfo.bg,
                              color: tierInfo.color,
                              mt: 0.5,
                              fontSize: "0.7rem",
                              fontWeight: 700,
                              border: "1px solid rgba(255,255,255,0.08)",
                            }}
                          />
                        </Box>
                      </Box>
                      <Box>
                        <Tooltip title="Edit">
                          <IconButton
                            size="small"
                            onClick={() => handleOpenDialog(tenant)}
                            sx={{
                              color: "rgba(226, 232, 240, 0.78)",
                              background: "rgba(255,255,255,0.04)",
                              mr: 0.5,
                              "&:hover": { background: "rgba(255,255,255,0.1)" },
                            }}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteTenant(tenant.id, tenant.name)}
                            sx={{
                              color: "rgba(252, 165, 165, 0.92)",
                              background: "rgba(127, 29, 29, 0.14)",
                              "&:hover": { background: "rgba(127, 29, 29, 0.24)" },
                            }}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>

                    <Box sx={{ mt: 2 }}>
                      {tenant.domain ? (
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
                          <LanguageIcon sx={{ fontSize: 16, color: "rgba(191, 219, 254, 0.8)" }} />
                          <Typography variant="body2" sx={{ color: "rgba(226, 232, 240, 0.82)" }}>
                            {tenant.domain}
                          </Typography>
                        </Box>
                      ) : null}
                      {tenant.email ? (
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
                          <EmailIcon sx={{ fontSize: 16, color: "rgba(191, 219, 254, 0.8)" }} />
                          <Typography variant="body2" sx={{ color: "rgba(226, 232, 240, 0.82)" }}>
                            {tenant.email}
                          </Typography>
                        </Box>
                      ) : null}
                      {tenant.phone ? (
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
                          <PhoneIcon sx={{ fontSize: 16, color: "rgba(191, 219, 254, 0.8)" }} />
                          <Typography variant="body2" sx={{ color: "rgba(226, 232, 240, 0.82)" }}>
                            {tenant.phone}
                          </Typography>
                        </Box>
                      ) : null}
                    </Box>

                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        mt: 2,
                        pt: 2,
                        borderTop: "1px solid rgba(255,255,255,0.08)",
                        gap: 1,
                        flexWrap: "wrap",
                      }}
                    >
                      <StatusChip isActive={tenant.is_active} />
                      <Typography variant="caption" sx={{ color: "rgba(226, 232, 240, 0.6)" }}>
                        Created: {tenant.created_at ? new Date(tenant.created_at).toLocaleDateString() : "N/A"}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {totalTenants > rowsPerPage ? (
        <Box
          className="glass-panel"
          sx={{
            ...glassPanelSx,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 1.5,
            mt: 4,
            borderRadius: 4,
            px: 2.5,
            py: 1.5,
          }}
        >
          <Typography variant="body2" sx={{ color: "rgba(226, 232, 240, 0.76)" }}>
            Showing {Math.min((page * rowsPerPage) + 1, totalTenants)}-
            {Math.min((page + 1) * rowsPerPage, totalTenants)} of {totalTenants}
          </Typography>
          <Box sx={{ ml: 2, display: "flex", gap: 1 }}>
            <Button
              variant="outlined"
              size="small"
              disabled={page === 0}
              onClick={() => setPage((value) => Math.max(value - 1, 0))}
              sx={ghostButtonSx}
            >
              Previous
            </Button>
            <Button
              variant="outlined"
              size="small"
              disabled={(page + 1) * rowsPerPage >= totalTenants}
              onClick={() => setPage((value) => value + 1)}
              sx={ghostButtonSx}
            >
              Next
            </Button>
          </Box>
        </Box>
      ) : null}

      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          className: "glass-modal",
          sx: {
            ...glassPanelSx,
            background: "rgba(11, 18, 32, 0.72)",
            borderRadius: 5,
            overflow: "hidden",
            color: "#e2e8f0",
          },
        }}
      >
        <DialogTitle
          sx={{
            background: "linear-gradient(180deg, rgba(37,99,235,0.24), rgba(15,23,42,0.18))",
            color: "#f8fafc",
            borderBottom: "1px solid rgba(255,255,255,0.08)",
          }}
        >
          {editingTenant ? "Edit Tenant" : "Create New Tenant"}
        </DialogTitle>
        <DialogContent sx={{ mt: 2, color: "#e2e8f0" }}>
          <TextField
            fullWidth
            label="Company Name"
            value={formData.name}
            onChange={(event) => setFormData((prev) => ({ ...prev, name: event.target.value }))}
            margin="normal"
            required
            sx={glassFieldSx}
          />
          <TextField
            fullWidth
            label="Domain"
            value={formData.domain}
            onChange={(event) => setFormData((prev) => ({ ...prev, domain: event.target.value }))}
            margin="normal"
            placeholder="example.com"
            sx={glassFieldSx}
          />
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={formData.email}
            onChange={(event) => setFormData((prev) => ({ ...prev, email: event.target.value }))}
            margin="normal"
            sx={glassFieldSx}
          />
          <TextField
            fullWidth
            label="Phone"
            value={formData.phone}
            onChange={(event) => setFormData((prev) => ({ ...prev, phone: event.target.value }))}
            margin="normal"
            sx={glassFieldSx}
          />
          <TextField
            fullWidth
            label="Address"
            value={formData.address}
            onChange={(event) => setFormData((prev) => ({ ...prev, address: event.target.value }))}
            margin="normal"
            multiline
            rows={2}
            sx={glassFieldSx}
          />
          <FormControl fullWidth margin="normal" sx={glassFieldSx}>
            <InputLabel>Subscription Tier</InputLabel>
            <Select
              value={formData.subscription_tier}
              onChange={(event) => setFormData((prev) => ({ ...prev, subscription_tier: event.target.value }))}
              label="Subscription Tier"
              MenuProps={{
                PaperProps: {
                  sx: {
                    ...glassPanelSx,
                    background: "rgba(15, 23, 42, 0.92)",
                    color: "#e2e8f0",
                    mt: 1,
                  },
                },
              }}
            >
              <MenuItem value="basic">Basic</MenuItem>
              <MenuItem value="professional">Professional</MenuItem>
              <MenuItem value="enterprise">Enterprise</MenuItem>
            </Select>
          </FormControl>
          <FormControlLabel
            control={
              <Switch
                checked={formData.is_active}
                onChange={(event) => setFormData((prev) => ({ ...prev, is_active: event.target.checked }))}
                sx={{
                  "& .MuiSwitch-switchBase.Mui-checked": {
                    color: "#60a5fa",
                  },
                  "& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track": {
                    backgroundColor: "rgba(59, 130, 246, 0.55)",
                  },
                  "& .MuiSwitch-track": {
                    backgroundColor: "rgba(255,255,255,0.18)",
                  },
                }}
              />
            }
            label="Active"
            sx={{ mt: 1, color: "rgba(226, 232, 240, 0.82)" }}
          />
        </DialogContent>
        <DialogActions sx={{ p: 2, gap: 1, borderTop: "1px solid rgba(255,255,255,0.08)" }}>
          <Button onClick={handleCloseDialog} variant="outlined" sx={ghostButtonSx}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSaveTenant}
            disabled={!formData.name.trim() || saving}
            sx={{
              borderRadius: 999,
              textTransform: "none",
              px: 2.75,
              background: "linear-gradient(135deg, rgba(59,130,246,0.78), rgba(37,99,235,0.88))",
              "&:hover": {
                background: "linear-gradient(135deg, rgba(96,165,250,0.88), rgba(37,99,235,0.92))",
              },
            }}
          >
            {saving ? "Saving..." : editingTenant ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TenantManagement;
