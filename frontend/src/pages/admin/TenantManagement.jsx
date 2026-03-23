import React, { useEffect, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";
import { formatTierLabel, normalizeTier, UNIFIED_TIERS } from "../../utils/tierUtils";
import "./TenantManagement.css";

const DOMAIN_SUFFIX = ".company.com";
const TENANTS_ENDPOINT = "/api/v1/admin/tenants";
const TENANT_PLAN_OPTIONS = UNIFIED_TIERS.filter((tier) => tier !== "free");

const normalizeSubdomain = (value) =>
  String(value || "")
    .trim()
    .toLowerCase()
    .replace(/https?:\/\//g, "")
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "")
    .replace(/\.+/g, ".");

const buildDomain = (subdomain) => {
  const s = normalizeSubdomain(subdomain);
  if (!s) return "";
  if (s.endsWith(DOMAIN_SUFFIX)) return s;
  if (s.includes(".")) return s;
  return `${s}${DOMAIN_SUFFIX}`;
};

const normalizeStorage = (value) => {
  const raw = String(value || "").replace("GB", "").trim();
  const num = Number.parseFloat(raw);
  if (Number.isNaN(num) || num < 0) return "0 GB";
  return `${num} GB`;
};

const normalizeTenant = (item) => {
  const domain = item.domain || item.domain_name || "";
  const subdomain = item.subdomain || item.tenant_id || item.id || "";
  const normalizedPlan = normalizeTier(item.plan || "starter", "starter");
  return {
    id: item.id || item.tenantId || item.tenant_id || subdomain || domain || "",
    companyName: item.companyName || item.company_name || item.name || "",
    domain: domain || (subdomain ? buildDomain(subdomain) : ""),
    status: item.status || "active",
    usersCount: Number(item.usersCount ?? item.users_count ?? 0),
    maxUsers: Number(item.maxUsers ?? item.max_users ?? 0),
    createdDate: item.createdDate || item.created_date || "",
    subscriptionEnd: item.subscriptionEnd || item.subscription_end || "",
    plan: normalizedPlan,
    storageUsed: item.storageUsed || item.storage_used || "0 GB",
    totalStorage: item.totalStorage || item.total_storage || "0 GB",
    contactEmail: item.contactEmail || item.contact_email || "",
    contactPhone: item.contactPhone || item.contact_phone || "",
  };
};

const TenantManagement = () => {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [confirmDeleteTenantId, setConfirmDeleteTenantId] = useState(null);

  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [filterPlan, setFilterPlan] = useState("all");

  const [showAddTenant, setShowAddTenant] = useState(false);
  const [showEditTenant, setShowEditTenant] = useState(false);
  const [showTenantDetails, setShowTenantDetails] = useState(false);

  const [selectedTenant, setSelectedTenant] = useState(null);
  const [detailsTab, setDetailsTab] = useState("overview");

  const [newTenant, setNewTenant] = useState({
    companyName: "",
    subdomain: "",
    contactEmail: "",
    contactPhone: "",
    plan: "starter",
    maxUsers: 10,
    totalStorage: 10,
    subscriptionMonths: 12,
  });

  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    newThisMonth: 0,
    expiringSoon: 0,
  });

  useEffect(() => {
    fetchTenants();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    calculateStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tenants]);

  const fetchTenants = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axiosClient.get(TENANTS_ENDPOINT);
      const list =
        res?.data?.data?.tenants || res?.data?.tenants || res?.data?.data || res?.data || [];
      const normalized = Array.isArray(list) ? list.map(normalizeTenant) : [];
      setTenants(normalized.filter((t) => t.id));
    } catch (err) {
      setError(
        err?.normalized?.detail ||
        err?.response?.data?.detail ||
        err?.message ||
        "Failed to load tenants."
      );
      setTenants([]);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = () => {
    const total = tenants.length;
    const active = tenants.filter((t) => t.status === "active").length;

    const today = new Date();
    const thisMonth = today.getMonth();
    const thisYear = today.getFullYear();

    const newThisMonth = tenants.filter((t) => {
      if (!t.createdDate) return false;
      const d = new Date(t.createdDate);
      return d.getMonth() === thisMonth && d.getFullYear() === thisYear;
    }).length;

    const expiringSoon = tenants.filter((t) => {
      if (t.status !== "active" || !t.subscriptionEnd) return false;
      const endDate = new Date(t.subscriptionEnd);
      const diffDays = Math.ceil((endDate - today) / (1000 * 60 * 60 * 24));
      return diffDays <= 30 && diffDays > 0;
    }).length;

    setStats({ total, active, newThisMonth, expiringSoon });
  };

  const filteredTenants = useMemo(() => {
    return tenants.filter((tenant) => {
      const q = searchTerm.trim().toLowerCase();
      const email = String(tenant.contactEmail || "").toLowerCase();
      const domain = String(tenant.domain || "").toLowerCase();
      const name = String(tenant.companyName || "").toLowerCase();

      const matchesSearch = !q || name.includes(q) || domain.includes(q) || email.includes(q);
      const matchesStatus = filterStatus === "all" || tenant.status === filterStatus;
      const matchesPlan = filterPlan === "all" || tenant.plan === filterPlan;

      return matchesSearch && matchesStatus && matchesPlan;
    });
  }, [tenants, searchTerm, filterStatus, filterPlan]);

  const calculateSubscriptionEnd = (months) => {
    const date = new Date();
    date.setMonth(date.getMonth() + Number(months || 0));
    return date.toISOString().split("T")[0];
  };

  const buildPayload = (tenant) => ({
    id: tenant.id,
    companyName: tenant.companyName,
    domain: tenant.domain,
    status: tenant.status,
    usersCount: Number(tenant.usersCount || 0),
    maxUsers: Number(tenant.maxUsers || 0),
    createdDate: tenant.createdDate,
    subscriptionEnd: tenant.subscriptionEnd,
    plan: normalizeTier(tenant.plan, "starter"),
    storageUsed: normalizeStorage(tenant.storageUsed),
    totalStorage: normalizeStorage(tenant.totalStorage),
    contactEmail: tenant.contactEmail,
    contactPhone: tenant.contactPhone,
    subdomain: tenant.subdomain,
  });

  const handleAddTenant = async () => {
    const companyName = newTenant.companyName.trim();
    const contactEmail = newTenant.contactEmail.trim();
    const domain = buildDomain(newTenant.subdomain);

    if (!companyName || !contactEmail || !domain) {
      setFeedback({
        type: "error",
        message: "Please fill required fields: Company Name, Domain, Contact Email.",
      });
      return;
    }

    const payload = {
      id: normalizeSubdomain(newTenant.subdomain) || domain,
      companyName,
      domain,
      status: "active",
      usersCount: 0,
      maxUsers: Number(newTenant.maxUsers || 0),
      createdDate: new Date().toISOString().split("T")[0],
      subscriptionEnd: calculateSubscriptionEnd(newTenant.subscriptionMonths),
      plan: newTenant.plan,
      storageUsed: "0 GB",
      totalStorage: `${Number(newTenant.totalStorage || 0)} GB`,
      contactEmail,
      contactPhone: newTenant.contactPhone.trim(),
      subdomain: normalizeSubdomain(newTenant.subdomain),
    };

    try {
      setLoading(true);
      await axiosClient.post(TENANTS_ENDPOINT, payload);
      await fetchTenants();
      setNewTenant({
        companyName: "",
        subdomain: "",
        contactEmail: "",
        contactPhone: "",
        plan: "starter",
        maxUsers: 10,
        totalStorage: 10,
        subscriptionMonths: 12,
      });
      setShowAddTenant(false);
      setFeedback({ type: "success", message: "Tenant added successfully." });
    } catch (err) {
      setFeedback({
        type: "error",
        message:
          err?.normalized?.detail ||
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to add tenant.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEditTenant = async () => {
    if (!selectedTenant) return;
    const payload = buildPayload(selectedTenant);

    try {
      setLoading(true);
      await axiosClient.put(`${TENANTS_ENDPOINT}/${encodeURIComponent(selectedTenant.id)}`, payload);
      await fetchTenants();
      setShowEditTenant(false);
      setFeedback({ type: "success", message: "Tenant updated successfully." });
    } catch (err) {
      setFeedback({
        type: "error",
        message:
          err?.normalized?.detail ||
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to update tenant.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTenant = async (id) => {
    try {
      setLoading(true);
      await axiosClient.delete(`${TENANTS_ENDPOINT}/${encodeURIComponent(id)}`);
      await fetchTenants();
      if (selectedTenant?.id === id) {
        setSelectedTenant(null);
        setShowTenantDetails(false);
      }
      setFeedback({ type: "success", message: "Tenant deleted successfully." });
    } catch (err) {
      setFeedback({
        type: "error",
        message:
          err?.normalized?.detail ||
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to delete tenant.",
      });
    } finally {
      setConfirmDeleteTenantId(null);
      setLoading(false);
    }
  };

  const toggleTenantStatus = async (tenant) => {
    const nextStatus =
      tenant.status === "active" ? "suspended" : tenant.status === "suspended" ? "inactive" : "active";

    const updated = { ...tenant, status: nextStatus };
    try {
      setLoading(true);
      await axiosClient.put(`${TENANTS_ENDPOINT}/${encodeURIComponent(tenant.id)}`, buildPayload(updated));
      await fetchTenants();
      setFeedback({ type: "success", message: `Tenant status changed to ${nextStatus}.` });
    } catch (err) {
      setFeedback({
        type: "error",
        message:
          err?.normalized?.detail ||
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to update tenant status.",
      });
    } finally {
      setLoading(false);
    }
  };

  const openTenantDetails = (tenant) => {
    setSelectedTenant({ ...tenant });
    setDetailsTab("overview");
    setShowTenantDetails(true);
  };

  const openEditModal = (tenant) => {
    setSelectedTenant({ ...tenant });
    setShowEditTenant(true);
  };

  const exportData = () => {
    const dataStr = JSON.stringify(filteredTenants, null, 2);
    const dataUri = "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);
    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", "tenants-data.json");
    linkElement.click();
  };

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const options = { year: "numeric", month: "short", day: "numeric" };
    return new Date(dateString).toLocaleDateString("en-US", options);
  };

  const daysUntilExpiry = (dateString) => {
    if (!dateString) return null;
    const today = new Date();
    const expiryDate = new Date(dateString);
    return Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));
  };

  const storagePct = (used, total) => {
    const u = Number.parseFloat(used);
    const t = Number.parseFloat(total);
    if (!t || Number.isNaN(u) || Number.isNaN(t)) return 0;
    return Math.max(0, Math.min(100, (u / t) * 100));
  };

  const getPlanClass = (plan) => `tm-plan-${normalizeTier(plan, "starter")}`;

  return (
    <div className="tenant-management">
      <div className="tm-page-header">
        <div>
          <h1>Tenant Management</h1>
          <p className="tm-subtitle">Manage tenant companies and their settings</p>
        </div>
        <button className="tm-btn tm-btn-primary" onClick={() => setShowAddTenant(true)}>
          + Add New Tenant
        </button>
      </div>

      {error ? <div className="tm-error">{error}</div> : null}
      {feedback ? (
        <div className={`tm-feedback tm-feedback-${feedback.type}`}>
          <span>{feedback.message}</span>
          <button type="button" className="tm-feedback-dismiss" onClick={() => setFeedback(null)}>
            Dismiss
          </button>
        </div>
      ) : null}

      <div className="tm-stats-cards">
        <div className="tm-stat-card">
          <div className="tm-stat-icon total">T</div>
          <div className="tm-stat-info">
            <h3>Total Tenants</h3>
            <p className="tm-stat-number">{stats.total}</p>
          </div>
        </div>

        <div className="tm-stat-card">
          <div className="tm-stat-icon active">A</div>
          <div className="tm-stat-info">
            <h3>Active</h3>
            <p className="tm-stat-number">{stats.active}</p>
          </div>
        </div>

        <div className="tm-stat-card">
          <div className="tm-stat-icon new">N</div>
          <div className="tm-stat-info">
            <h3>New This Month</h3>
            <p className="tm-stat-number">{stats.newThisMonth}</p>
          </div>
        </div>

        <div className="tm-stat-card">
          <div className="tm-stat-icon warning">E</div>
          <div className="tm-stat-info">
            <h3>Expiring Soon</h3>
            <p className="tm-stat-number">{stats.expiringSoon}</p>
          </div>
        </div>
      </div>

      <div className="tm-controls">
        <div className="tm-search-box">
          <input
            type="text"
            placeholder="Search by company, domain, or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <span className="tm-search-icon">Search</span>
        </div>

        <div className="tm-filters">
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="suspended">Suspended</option>
          </select>

          <select value={filterPlan} onChange={(e) => setFilterPlan(e.target.value)}>
            <option value="all">All Plans</option>
            {TENANT_PLAN_OPTIONS.map((tier) => (
              <option key={tier} value={tier}>{formatTierLabel(tier)}</option>
            ))}
          </select>

          <button className="tm-btn tm-btn-secondary" onClick={exportData}>
            Export JSON
          </button>
        </div>
      </div>

      <div className="tm-table-wrap">
        {loading ? (
          <div className="tm-loading">
            <div className="tm-spinner" />
            <p>Loading tenants...</p>
          </div>
        ) : filteredTenants.length > 0 ? (
          <table className="tm-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Domain</th>
                <th>Status</th>
                <th>Users</th>
                <th>Plan</th>
                <th>Subscription End</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {filteredTenants.map((tenant) => {
                const daysLeft = daysUntilExpiry(tenant.subscriptionEnd);
                const userPct = tenant.maxUsers
                  ? Math.min(100, (tenant.usersCount / tenant.maxUsers) * 100)
                  : 0;

                return (
                  <tr
                    key={tenant.id}
                    className="tm-row"
                    onClick={() => openTenantDetails(tenant)}
                    role="button"
                    tabIndex={0}
                  >
                    <td>
                      <div className="tm-company">
                        <div className="tm-company-name">{tenant.companyName}</div>
                        <div className="tm-company-email">{tenant.contactEmail || "N/A"}</div>
                      </div>
                    </td>

                    <td>
                      {tenant.domain ? (
                        <a
                          href={`https://${tenant.domain}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="tm-domain-link"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {tenant.domain}
                        </a>
                      ) : (
                        <span className="tm-domain-link">N/A</span>
                      )}
                    </td>

                    <td>
                      <span className={`tm-status tm-status-${tenant.status}`}>{tenant.status}</span>
                    </td>

                    <td>
                      <div className="tm-users-progress">
                        <div className="tm-progress-bar">
                          <div className="tm-progress-fill" style={{ width: `${userPct}%` }} />
                        </div>
                        <span className="tm-users-count">
                          {tenant.usersCount}/{tenant.maxUsers}
                        </span>
                      </div>
                    </td>

                    <td>
                      <span className={`tm-plan ${getPlanClass(tenant.plan)}`}>{formatTierLabel(tenant.plan)}</span>
                    </td>

                    <td>
                      <div className="tm-subscription">
                        <div className="tm-date">{formatDate(tenant.subscriptionEnd)}</div>
                        {tenant.status === "active" && daysLeft && daysLeft <= 30 && daysLeft > 0 && (
                          <div className={`tm-days-left ${daysLeft <= 7 ? "warning" : ""}`}>
                            {daysLeft} days left
                          </div>
                        )}
                      </div>
                    </td>

                    <td>{formatDate(tenant.createdDate)}</td>

                    <td onClick={(e) => e.stopPropagation()}>
                      <div className="tm-actions">
                        <button className="tm-icon-btn edit" onClick={() => openEditModal(tenant)} title="Edit">
                          Edit
                        </button>
                        <button
                          className={`tm-icon-btn toggle ${tenant.status}`}
                          onClick={() => toggleTenantStatus(tenant)}
                          title="Toggle status"
                        >
                          Status
                        </button>
                        <button
                          className="tm-icon-btn delete"
                          onClick={() => setConfirmDeleteTenantId(tenant.id)}
                          title="Delete"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <div className="tm-empty">
            <div className="tm-empty-icon">T</div>
            <h3>No tenants found</h3>
            <p>
              {searchTerm || filterStatus !== "all" || filterPlan !== "all"
                ? "Try adjusting your search or filters."
                : "Start by adding your first tenant."}
            </p>
            <button className="tm-btn tm-btn-primary" onClick={() => setShowAddTenant(true)}>
              + Add New Tenant
            </button>
          </div>
        )}
      </div>

      {showAddTenant && (
        <div className="tm-modal-overlay">
          <div className="tm-modal">
            <h2>Add New Tenant</h2>

            <div className="tm-modal-content">
              <div className="tm-form-grid">
                <div className="tm-form-group">
                  <label>Company Name *</label>
                  <input
                    type="text"
                    value={newTenant.companyName}
                    onChange={(e) => setNewTenant((p) => ({ ...p, companyName: e.target.value }))}
                    placeholder="Enter company name"
                  />
                </div>

                <div className="tm-form-group">
                  <label>Domain *</label>
                  <div className="tm-domain-input">
                    <input
                      type="text"
                      value={newTenant.subdomain}
                      onChange={(e) => setNewTenant((p) => ({ ...p, subdomain: e.target.value }))}
                      placeholder="subdomain"
                    />
                    <span className="tm-domain-suffix">{DOMAIN_SUFFIX}</span>
                  </div>
                  <p className="tm-hint">
                    Will be accessible at: {buildDomain(newTenant.subdomain) || `subdomain${DOMAIN_SUFFIX}`}
                  </p>
                </div>

                <div className="tm-form-group">
                  <label>Contact Email *</label>
                  <input
                    type="email"
                    value={newTenant.contactEmail}
                    onChange={(e) => setNewTenant((p) => ({ ...p, contactEmail: e.target.value }))}
                    placeholder="admin@company.com"
                  />
                </div>

                <div className="tm-form-group">
                  <label>Contact Phone</label>
                  <input
                    type="tel"
                    value={newTenant.contactPhone}
                    onChange={(e) => setNewTenant((p) => ({ ...p, contactPhone: e.target.value }))}
                    placeholder="+1234567890"
                  />
                </div>

                <div className="tm-form-group">
                  <label>Plan Type *</label>
                  <select
                    value={newTenant.plan}
                    onChange={(e) => setNewTenant((p) => ({ ...p, plan: e.target.value }))}
                  >
                    {TENANT_PLAN_OPTIONS.map((tier) => (
                      <option key={tier} value={tier}>{formatTierLabel(tier)}</option>
                    ))}
                  </select>
                </div>

                <div className="tm-form-group">
                  <label>Max Users *</label>
                  <input
                    type="number"
                    value={newTenant.maxUsers}
                    onChange={(e) => setNewTenant((p) => ({ ...p, maxUsers: Number(e.target.value || 0) }))}
                    min="1"
                    max="100000"
                  />
                </div>

                <div className="tm-form-group">
                  <label>Storage (GB) *</label>
                  <input
                    type="number"
                    value={newTenant.totalStorage}
                    onChange={(e) =>
                      setNewTenant((p) => ({ ...p, totalStorage: Number(e.target.value || 0) }))
                    }
                    min="1"
                    max="100000"
                  />
                </div>

                <div className="tm-form-group">
                  <label>Subscription Period *</label>
                  <select
                    value={newTenant.subscriptionMonths}
                    onChange={(e) =>
                      setNewTenant((p) => ({ ...p, subscriptionMonths: Number(e.target.value || 0) }))
                    }
                  >
                    <option value="1">1 Month</option>
                    <option value="3">3 Months</option>
                    <option value="6">6 Months</option>
                    <option value="12">12 Months</option>
                    <option value="24">24 Months</option>
                  </select>
                </div>
              </div>

              <div className="tm-modal-actions">
                <button className="tm-btn tm-btn-secondary" onClick={() => setShowAddTenant(false)}>
                  Cancel
                </button>
                <button className="tm-btn tm-btn-primary" onClick={handleAddTenant}>
                  Create Tenant
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showEditTenant && selectedTenant && (
        <div className="tm-modal-overlay">
          <div className="tm-modal">
            <h2>Edit Tenant</h2>

            <div className="tm-modal-content">
              <div className="tm-form-grid">
                <div className="tm-form-group">
                  <label>Company Name *</label>
                  <input
                    type="text"
                    value={selectedTenant.companyName}
                    onChange={(e) => setSelectedTenant((p) => ({ ...p, companyName: e.target.value }))}
                  />
                </div>

                <div className="tm-form-group">
                  <label>Contact Email *</label>
                  <input
                    type="email"
                    value={selectedTenant.contactEmail}
                    onChange={(e) => setSelectedTenant((p) => ({ ...p, contactEmail: e.target.value }))}
                  />
                </div>

                <div className="tm-form-group">
                  <label>Contact Phone</label>
                  <input
                    type="tel"
                    value={selectedTenant.contactPhone || ""}
                    onChange={(e) => setSelectedTenant((p) => ({ ...p, contactPhone: e.target.value }))}
                  />
                </div>

                <div className="tm-form-group">
                  <label>Status</label>
                  <select
                    value={selectedTenant.status}
                    onChange={(e) => setSelectedTenant((p) => ({ ...p, status: e.target.value }))}
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="suspended">Suspended</option>
                  </select>
                </div>

                <div className="tm-form-group">
                  <label>Plan Type</label>
                  <select
                    value={selectedTenant.plan}
                    onChange={(e) => setSelectedTenant((p) => ({ ...p, plan: e.target.value }))}
                  >
                    {TENANT_PLAN_OPTIONS.map((tier) => (
                      <option key={tier} value={tier}>{formatTierLabel(tier)}</option>
                    ))}
                  </select>
                </div>

                <div className="tm-form-group">
                  <label>Max Users *</label>
                  <input
                    type="number"
                    value={selectedTenant.maxUsers}
                    onChange={(e) => setSelectedTenant((p) => ({ ...p, maxUsers: Number(e.target.value || 0) }))}
                    min="1"
                    max="100000"
                  />
                </div>

                <div className="tm-form-group">
                  <label>Total Storage (GB) *</label>
                  <input
                    type="number"
                    value={String(selectedTenant.totalStorage || "").replace(" GB", "")}
                    onChange={(e) =>
                      setSelectedTenant((p) => ({
                        ...p,
                        totalStorage: `${Number(e.target.value || 0)} GB`,
                      }))
                    }
                    min="1"
                    max="100000"
                  />
                </div>

                <div className="tm-form-group">
                  <label>Subscription End Date</label>
                  <input
                    type="date"
                    value={selectedTenant.subscriptionEnd}
                    onChange={(e) => setSelectedTenant((p) => ({ ...p, subscriptionEnd: e.target.value }))}
                  />
                </div>
              </div>

              <div className="tm-modal-actions">
                <button className="tm-btn tm-btn-secondary" onClick={() => setShowEditTenant(false)}>
                  Cancel
                </button>
                <button className="tm-btn tm-btn-primary" onClick={handleEditTenant}>
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showTenantDetails && selectedTenant && (
        <div className="tm-modal-overlay">
          <div className="tm-modal tm-details-modal">
            <div className="tm-details-header">
              <div>
                <h2 className="tm-details-title">{selectedTenant.companyName}</h2>
                <div className="tm-details-sub">
                  <span className={`tm-status tm-status-${selectedTenant.status}`}>{selectedTenant.status}</span>
                  <span className={`tm-plan ${getPlanClass(selectedTenant.plan)}`}>{formatTierLabel(selectedTenant.plan)}</span>
                </div>
              </div>

              <button className="tm-close" onClick={() => setShowTenantDetails(false)} aria-label="Close">
                X
              </button>
            </div>

            <div className="tm-details-tabs">
              {[
                ["overview", "Overview"],
                ["usage", "Usage"],
                ["users", "Users"],
                ["activity", "Activity"],
                ["billing", "Billing"],
              ].map(([k, label]) => (
                <button
                  key={k}
                  className={`tm-tab ${detailsTab === k ? "active" : ""}`}
                  onClick={() => setDetailsTab(k)}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="tm-modal-content">
              {detailsTab === "overview" && (
                <div className="tm-details-grid">
                  <div className="tm-detail-card">
                    <h3>Basic Information</h3>
                    <div className="tm-kv">
                      <div>
                        <span>Domain</span>
                        {selectedTenant.domain ? (
                          <a href={`https://${selectedTenant.domain}`} target="_blank" rel="noreferrer">
                            {selectedTenant.domain}
                          </a>
                        ) : (
                          <b>N/A</b>
                        )}
                      </div>
                      <div>
                        <span>Contact Email</span>
                        <b>{selectedTenant.contactEmail || "N/A"}</b>
                      </div>
                      <div>
                        <span>Contact Phone</span>
                        <b>{selectedTenant.contactPhone || "N/A"}</b>
                      </div>
                      <div>
                        <span>Created</span>
                        <b>{formatDate(selectedTenant.createdDate)}</b>
                      </div>
                      <div>
                        <span>Subscription End</span>
                        <b>{formatDate(selectedTenant.subscriptionEnd)}</b>
                      </div>
                    </div>
                  </div>

                  <div className="tm-detail-card">
                    <h3>Limits</h3>
                    <div className="tm-kv">
                      <div>
                        <span>Users</span>
                        <b>
                          {selectedTenant.usersCount} / {selectedTenant.maxUsers}
                        </b>
                      </div>
                      <div>
                        <span>Storage</span>
                        <b>
                          {selectedTenant.storageUsed} / {selectedTenant.totalStorage}
                        </b>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {detailsTab === "usage" && (
                <div className="tm-detail-card">
                  <h3>Usage</h3>

                  <div className="tm-usage-block">
                    <label>Users Usage</label>
                    <div className="tm-progress-bar big">
                      <div
                        className="tm-progress-fill"
                        style={{
                          width: `${selectedTenant.maxUsers
                              ? Math.min(100, (selectedTenant.usersCount / selectedTenant.maxUsers) * 100)
                              : 0
                            }%`,
                        }}
                      />
                    </div>
                    <div className="tm-usage-text">
                      {selectedTenant.usersCount}/{selectedTenant.maxUsers} (
                      {selectedTenant.maxUsers
                        ? Math.round((selectedTenant.usersCount / selectedTenant.maxUsers) * 100)
                        : 0}
                      %)
                    </div>
                  </div>

                  <div className="tm-usage-block">
                    <label>Storage Usage</label>
                    <div className="tm-progress-bar big">
                      <div
                        className="tm-progress-fill"
                        style={{ width: `${storagePct(selectedTenant.storageUsed, selectedTenant.totalStorage)}%` }}
                      />
                    </div>
                    <div className="tm-usage-text">
                      {selectedTenant.storageUsed} / {selectedTenant.totalStorage} (
                      {Math.round(storagePct(selectedTenant.storageUsed, selectedTenant.totalStorage))}%)
                    </div>
                  </div>
                </div>
              )}

              {detailsTab === "users" && (
                <div className="tm-detail-card">
                  <h3>Users</h3>
                  <p className="tm-muted">
                    User listing is tenant-scoped and should be loaded from API (e.g. /tenants/:id/users).
                  </p>
                  <div className="tm-placeholder">
                    <div className="tm-placeholder-row" />
                    <div className="tm-placeholder-row" />
                    <div className="tm-placeholder-row" />
                  </div>
                </div>
              )}

              {detailsTab === "activity" && (
                <div className="tm-detail-card">
                  <h3>Activity Logs</h3>
                  <p className="tm-muted">
                    Connect this section to your audit log API to show tenant-scoped events.
                  </p>
                  <div className="tm-placeholder">
                    <div className="tm-placeholder-row" />
                    <div className="tm-placeholder-row" />
                    <div className="tm-placeholder-row" />
                  </div>
                </div>
              )}

              {detailsTab === "billing" && (
                <div className="tm-detail-card">
                  <h3>Billing</h3>
                  <p className="tm-muted">
                    Connect this section to subscription/invoice API to show invoices and payments.
                  </p>
                  <div className="tm-placeholder">
                    <div className="tm-placeholder-row" />
                    <div className="tm-placeholder-row" />
                    <div className="tm-placeholder-row" />
                  </div>
                </div>
              )}

              <div className="tm-details-actions">
                <button
                  className="tm-btn tm-btn-secondary"
                  onClick={() => {
                    setShowTenantDetails(false);
                    openEditModal(selectedTenant);
                  }}
                >
                  Edit Tenant
                </button>

                <button
                  className="tm-btn tm-btn-secondary"
                  onClick={() => {
                    toggleTenantStatus(selectedTenant);
                    setShowTenantDetails(false);
                  }}
                >
                  Toggle Status
                </button>

                <button
                  className="tm-btn tm-btn-danger"
                  onClick={() => {
                    setConfirmDeleteTenantId(selectedTenant.id);
                    setShowTenantDetails(false);
                  }}
                >
                  Delete Tenant
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {confirmDeleteTenantId && (
        <div className="tm-modal-overlay">
          <div className="tm-modal tm-confirm-modal">
            <h2>Delete Tenant</h2>
            <div className="tm-modal-content">
              <p className="tm-muted">This action cannot be undone. The tenant and related access records will be removed.</p>
              <div className="tm-modal-actions">
                <button className="tm-btn tm-btn-secondary" onClick={() => setConfirmDeleteTenantId(null)}>
                  Cancel
                </button>
                <button
                  className="tm-btn tm-btn-danger"
                  onClick={() => handleDeleteTenant(confirmDeleteTenantId)}
                  disabled={loading}
                >
                  Delete Tenant
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TenantManagement;
