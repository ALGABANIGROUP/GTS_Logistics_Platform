import React, { useEffect, useState, useMemo } from "react";
import RequireAuth from '../../components/RequireAuth.jsx';
import axiosClient from "@/api/axiosClient";

// English-only role mappings (matches backend/security/rbac.py INTERNAL_ROLE_ORDER + PARTNER_ROLE)
const ROLE_DISPLAY = {
  super_admin: "Super Admin",
  admin: "Administrator",
  manager: "Manager",
  user: "User",
  partner: "Partner",
};

const ROLE_COLORS = {
  super_admin: "#DC2626",  // Red - highest privilege
  admin: "#0EA5E9",        // Sky Blue
  manager: "#F59E0B",      // Amber
  user: "#6B7280",         // Gray - default
  partner: "#8B5CF6",      // Purple - special domain
};

// Delete reasons
const DELETE_REASONS = [
  { value: "duplicate", label: "Duplicate Account" },
  { value: "inactive", label: "User Inactivity" },
  { value: "requested", label: "User Request" },
  { value: "violation", label: "Terms Violation" },
  { value: "other", label: "Other Reason" },
];

export default function AdminUsers() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <AdminUsersContent />
    </RequireAuth>
  );
}

function AdminUsersContent() {
  // State management
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [serverStats, setServerStats] = useState(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [filterRole, setFilterRole] = useState("");
  const [filterStatus, setFilterStatus] = useState("");

  // UI state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedIds, setSelectedIds] = useState([]);
  const [bulkBusy, setBulkBusy] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    username: "",
    phone_number: "",
    password: "",
    role: "user",
    is_active: true,
  });

  // Delete confirmation state
  const [deleteReason, setDeleteReason] = useState("");
  const [deleteNotes, setDeleteNotes] = useState("");
  const [notifyUser, setNotifyUser] = useState(false);
  const [archiveData, setArchiveData] = useState(true);

  // Load data
  useEffect(() => {
    loadUsers();
    loadStats();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    setError("");
    try {
      const [res, activityRes] = await Promise.all([
        axiosClient.get("/api/v1/admin/users/management"),
        axiosClient.get("/api/v1/admin/users/activity/recent?limit=100").catch(() => ({ data: [] })),
      ]);
      const userList = res?.data?.users || res?.data?.data?.users || res?.data?.data || res?.data || [];
      const activityList = activityRes?.data || [];
      const lastLoginById = new Map();
      const lastLoginByEmail = new Map();

      if (Array.isArray(activityList)) {
        activityList.forEach((item) => {
          if (item?.user_id != null) lastLoginById.set(String(item.user_id), item.last_login || item.lastLogin || null);
          if (item?.email) lastLoginByEmail.set(String(item.email).toLowerCase(), item.last_login || item.lastLogin || null);
        });
      }

      const normalizedUsers = Array.isArray(userList) ? userList.map((user) => {
        const fallbackLogin =
          user?.last_login ||
          user?.lastLogin ||
          user?.last_login_at ||
          user?.lastLoginAt ||
          lastLoginById.get(String(user.id)) ||
          lastLoginByEmail.get(String(user.email || "").toLowerCase()) ||
          null;

        return {
          ...user,
          last_login: user?.last_login || fallbackLogin,
        };
      }) : [];

      setUsers(normalizedUsers);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to load users");
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const res = await axiosClient.get("/api/v1/admin/users/stats");
      setServerStats(res?.data || null);
    } catch {
      setServerStats(null);
    }
  };

  // Filtered users
  const filteredUsers = useMemo(() => {
    let result = users;

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(user =>
        user.full_name?.toLowerCase().includes(query) ||
        user.email?.toLowerCase().includes(query) ||
        user.username?.toLowerCase().includes(query) ||
        user.phone_number?.toLowerCase().includes(query) ||
        String(user.id).includes(query)
      );
    }

    // Role filter
    if (filterRole) {
      result = result.filter(user => user.role === filterRole);
    }

    // Status filter
    if (filterStatus) {
      const isActive = filterStatus === "active";
      result = result.filter(user => user.is_active === isActive);
    }

    return result;
  }, [users, searchQuery, filterRole, filterStatus]);

  const selectedSet = useMemo(() => new Set(selectedIds.map((id) => String(id))), [selectedIds]);
  const allFilteredSelected = filteredUsers.length > 0 && filteredUsers.every((user) => selectedSet.has(String(user.id)));
  const selectedCount = selectedIds.length;

  // Statistics
  const stats = useMemo(() => {
    return {
      total: users.length,
      active: users.filter(u => u.is_active).length,
      inactive: users.filter(u => !u.is_active).length,
    };
  }, [users]);

  // Handlers
  const normalizeUpdatePayload = (payload) => {
    const cleaned = { ...payload };
    Object.keys(cleaned).forEach((key) => {
      if (cleaned[key] === "" || cleaned[key] === undefined || cleaned[key] === null) {
        delete cleaned[key];
      }
    });
    return cleaned;
  };

  const handleCreate = async () => {
    if (!formData.email || !formData.password) {
      setError("Email and password are required");
      return;
    }

    try {
      await axiosClient.post("/api/v1/admin/users", formData);
      setNotice("User created successfully.");
      setShowCreateModal(false);
      setFormData({
        full_name: "",
        email: "",
        username: "",
        phone_number: "",
        password: "",
        role: "user",
        is_active: true,
      });
      await loadUsers();
      await loadStats();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to create user");
    }
  };

  const handleEdit = async () => {
    if (!selectedUser) return;

    try {
      const payload = normalizeUpdatePayload({
        full_name: formData.full_name,
        email: formData.email,
        username: formData.username,
        phone_number: formData.phone_number,
        role: formData.role,
        is_active: formData.is_active,
        password: formData.password,
      });
      await axiosClient.patch(`/api/v1/admin/users/${selectedUser.id}`, payload);
      setShowEditModal(false);
      setSelectedUser(null);
      setError("");
      setNotice("User updated instantly by System Admin Bot.");
      await loadUsers();
      await loadStats();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to update user");
    }
  };

  const handleDelete = async () => {
    if (!selectedUser || !deleteReason) {
      setError("Please select a reason for deletion");
      return;
    }

    try {
      await axiosClient.delete(`/api/v1/admin/users/${selectedUser.id}`);
      setShowDeleteModal(false);
      setSelectedUser(null);
      setDeleteReason("");
      setDeleteNotes("");
      setError("");
      setNotice("User deactivated instantly by System Admin Bot.");
      await loadUsers();
      await loadStats();
    } catch (err) {
      try {
        await axiosClient.patch(`/api/v1/admin/users/${selectedUser.id}`, { is_active: false });
        setShowDeleteModal(false);
        setSelectedUser(null);
        setDeleteReason("");
        setDeleteNotes("");
        setError("");
        setNotice("User archived instantly by System Admin Bot because full deletion was unavailable.");
        await loadUsers();
        await loadStats();
      } catch (fallbackErr) {
        setError(fallbackErr?.response?.data?.detail || err?.response?.data?.detail || "Failed to delete user");
      }
    }
  };

  const handleToggleStatus = async (user) => {
    try {
      await axiosClient.patch(`/api/v1/admin/users/${user.id}`, {
        is_active: !user.is_active
      });
      setError("");
      setNotice(`User ${user.is_active ? "deactivated" : "activated"} instantly by System Admin Bot.`);
      await loadUsers();
      await loadStats();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to toggle user status");
    }
  };

  const toggleSelectUser = (userId) => {
    const id = String(userId);
    setSelectedIds((prev) => {
      const next = new Set(prev.map((v) => String(v)));
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return Array.from(next);
    });
  };

  const toggleSelectAllFiltered = () => {
    if (allFilteredSelected) {
      setSelectedIds([]);
      return;
    }
    setSelectedIds(filteredUsers.map((user) => String(user.id)));
  };

  const clearSelection = () => setSelectedIds([]);

  const handleBulkDisable = async (confirmed = false) => {
    if (!selectedCount) return;
    if (!confirmed) {
      setConfirmAction({
        kind: "disable",
        title: "Disable selected users?",
        message: `This will disable ${selectedCount} selected user(s).`,
        confirmLabel: "Disable",
      });
      return;
    }

    setBulkBusy(true);
    try {
      const results = await Promise.allSettled(
        selectedIds.map((id) => axiosClient.patch(`/api/v1/admin/users/${id}`, { is_active: false }))
      );
      const failed = results.filter((r) => r.status === "rejected").length;
      if (failed) {
        setError(`${failed} user(s) failed to update.`);
        setNotice("");
      } else {
        setError("");
        setNotice(`${selectedCount} user(s) disabled successfully.`);
      }
      await loadUsers();
      clearSelection();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to update users");
    } finally {
      setBulkBusy(false);
    }
  };

  const handleBulkDelete = async (confirmed = false) => {
    if (!selectedCount) return;
    if (!confirmed) {
      setConfirmAction({
        kind: "delete",
        title: "Delete selected users?",
        message: `This will permanently remove ${selectedCount} selected user(s) where possible and disable any remaining accounts.`,
        confirmLabel: "Delete",
      });
      return;
    }

    setBulkBusy(true);
    try {
      const results = await Promise.allSettled(
        selectedIds.map(async (id) => {
          try {
            await axiosClient.delete(`/api/v1/admin/users/${id}`);
          } catch {
            await axiosClient.patch(`/api/v1/admin/users/${id}`, { is_active: false });
          }
        })
      );
      const failed = results.filter((r) => r.status === "rejected").length;
      if (failed) {
        setError(`${failed} user(s) failed to delete.`);
        setNotice("");
      } else {
        setError("");
        setNotice(`${selectedCount} user(s) processed successfully.`);
      }
      await loadUsers();
      clearSelection();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to delete users");
    } finally {
      setBulkBusy(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "—";
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return "—";
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric"
    });
  };

  const formatRelativeTime = (dateString) => {
    if (!dateString) return "Never";
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return "Never";

    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
  };

  const exportToCSV = () => {
    const csvData = filteredUsers.map(user => ({
      ID: user.id,
      Name: user.full_name || "",
      Email: user.email,
      Role: ROLE_DISPLAY[user.role] || user.role,
      Status: user.is_active ? "Active" : "Inactive",
      Joined: formatDate(user.created_at),
      LastLogin: formatRelativeTime(user.last_login),
    }));

    const headers = Object.keys(csvData[0]);
    const csv = [
      headers.join(","),
      ...csvData.map(row => headers.map(h => row[h]).join(","))
    ].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `users_export_${new Date().toISOString().split("T")[0]}.csv`;
    link.click();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading users...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
            <p className="text-gray-600 mt-1">
              Manage users, roles, and permissions
              {serverStats?.managed_by ? ` • Managed live by ${serverStats.managed_by}` : ""}
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={exportToCSV}
              className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add User
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
            <div className="text-sm text-gray-600">Total Users</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-2xl font-bold text-green-600">{stats.active}</div>
            <div className="text-sm text-gray-600">Active</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-2xl font-bold text-orange-600">{stats.inactive}</div>
            <div className="text-sm text-gray-600">Inactive</div>
          </div>
        </div>
        {serverStats?.last_updated && (
          <div className="mt-3 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-sm text-emerald-700">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            <span>System Admin Bot synced at {new Date(serverStats.last_updated).toLocaleTimeString()}</span>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex justify-between items-center">
          <span>{error}</span>
          <button onClick={() => setError("")} className="text-red-900 hover:text-red-700">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {notice && (
        <div className="mb-4 p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-700 flex justify-between items-center">
          <span>{notice}</span>
          <button onClick={() => setNotice("")} className="text-emerald-900 hover:text-emerald-700">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-4">
        <div className="flex gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by name, email, phone, or ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Roles</option>
            {Object.entries(ROLE_DISPLAY).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          {(searchQuery || filterRole || filterStatus) && (
            <button
              onClick={() => {
                setSearchQuery("");
                setFilterRole("");
                setFilterStatus("");
              }}
              className="px-4 py-2 text-gray-600 hover:text-gray-900"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {selectedCount > 0 && (
          <div className="px-6 py-3 border-b border-gray-200 bg-blue-50 flex items-center justify-between">
            <div className="text-sm text-blue-900">
              {selectedCount} selected
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleBulkDisable}
                disabled={bulkBusy}
                className="px-3 py-1.5 text-sm border border-orange-200 text-orange-700 rounded-md hover:bg-orange-50 disabled:opacity-60"
              >
                Disable Selected
              </button>
              <button
                type="button"
                onClick={handleBulkDelete}
                disabled={bulkBusy}
                className="px-3 py-1.5 text-sm border border-red-200 text-red-700 rounded-md hover:bg-red-50 disabled:opacity-60"
              >
                Delete Selected
              </button>
              <button
                type="button"
                onClick={clearSelection}
                disabled={bulkBusy}
                className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-60"
              >
                Clear
              </button>
            </div>
          </div>
        )}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <input
                    type="checkbox"
                    aria-label="Select all users"
                    checked={allFilteredSelected}
                    onChange={toggleSelectAllFiltered}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Login</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-gray-500">
                    <svg className="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                    <p className="text-lg font-medium">No users found</p>
                    <p className="text-sm">Try adjusting your search or filters</p>
                  </td>
                </tr>
              ) : (
                filteredUsers.map((user) => (
                  <tr key={user.id} className="transition-colors hover:bg-white/5">
                    <td className="px-4 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        aria-label={`Select user ${user.email}`}
                        checked={selectedSet.has(String(user.id))}
                        onChange={() => toggleSelectUser(user.id)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-semibold">
                            {(user.full_name || user.email || "U").charAt(0).toUpperCase()}
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{user.full_name || "—"}</div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                          {user.phone_number && (
                            <div className="text-xs text-gray-400">{user.phone_number}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className="px-2 py-1 text-xs font-semibold rounded-full text-white"
                        style={{ backgroundColor: ROLE_COLORS[user.role] || "#6B7280" }}
                      >
                        {ROLE_DISPLAY[user.role] || user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${user.is_active
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-100 text-gray-800"
                        }`}>
                        {user.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(user.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatRelativeTime(user.last_login)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedUser(user);
                            setFormData({
                              full_name: user.full_name || "",
                              email: user.email,
                              username: user.username || "",
                              phone_number: user.phone_number || "",
                              role: user.role,
                              is_active: user.is_active,
                            });
                            setShowEditModal(true);
                          }}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => handleToggleStatus(user)}
                          className="text-orange-600 hover:text-orange-900"
                        >
                          {user.is_active ? "Deactivate" : "Activate"}
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedUser(user);
                            setShowDeleteModal(true);
                          }}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {confirmAction && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-2">{confirmAction.title}</h2>
            <p className="text-sm text-gray-600 mb-6">{confirmAction.message}</p>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setConfirmAction(null)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={async () => {
                  const action = confirmAction.kind;
                  setConfirmAction(null);
                  if (action === "disable") {
                    await handleBulkDisable(true);
                    return;
                  }
                  await handleBulkDelete(true);
                }}
                className={`px-4 py-2 text-white rounded-lg ${
                  confirmAction.kind === "delete" ? "bg-red-600 hover:bg-red-700" : "bg-orange-600 hover:bg-orange-700"
                }`}
              >
                {confirmAction.confirmLabel}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create/Edit Modal */}
      {(showCreateModal || showEditModal) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-4">
                {showCreateModal ? "Create New User" : "Edit User"}
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={formData.full_name}
                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Username
                  </label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    value={formData.phone_number}
                    onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {showCreateModal && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Password *
                    </label>
                    <input
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Role
                  </label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {Object.entries(ROLE_DISPLAY).map(([key, label]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-900">
                    Active
                  </label>
                </div>
              </div>

              <div className="mt-6 flex gap-3 justify-end">
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setShowEditModal(false);
                    setSelectedUser(null);
                    setFormData({
                      full_name: "",
                      email: "",
                      username: "",
                      phone_number: "",
                      password: "",
                      role: "user",
                      is_active: true,
                    });
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={showCreateModal ? handleCreate : handleEdit}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {showCreateModal ? "Create" : "Save"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <h2 className="ml-4 text-xl font-bold text-gray-900">Delete User</h2>
              </div>

              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <div className="text-sm font-medium text-gray-900">{selectedUser.full_name || selectedUser.email}</div>
                <div className="text-sm text-gray-500">{selectedUser.email}</div>
              </div>

              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-800">
                  <strong>Warning:</strong> This action cannot be undone. The user and all associated data will be deleted.
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Reason for deletion *
                  </label>
                  <select
                    value={deleteReason}
                    onChange={(e) => setDeleteReason(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                    required
                  >
                    <option value="">Select a reason</option>
                    {DELETE_REASONS.map((reason) => (
                      <option key={reason.value} value={reason.value}>
                        {reason.label}
                      </option>
                    ))}
                  </select>
                </div>

                {deleteReason === "other" && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Additional notes
                    </label>
                    <textarea
                      value={deleteNotes}
                      onChange={(e) => setDeleteNotes(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                      rows="3"
                      placeholder="Please provide details..."
                    />
                  </div>
                )}

                <div className="space-y-2">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={notifyUser}
                      onChange={(e) => setNotifyUser(e.target.checked)}
                      className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-900">
                      Send notification email to user
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={archiveData}
                      onChange={(e) => setArchiveData(e.target.checked)}
                      className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-900">
                      Archive data before deletion (can be restored later)
                    </label>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex gap-3 justify-end">
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setSelectedUser(null);
                    setDeleteReason("");
                    setDeleteNotes("");
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  disabled={!deleteReason}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Delete User
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
