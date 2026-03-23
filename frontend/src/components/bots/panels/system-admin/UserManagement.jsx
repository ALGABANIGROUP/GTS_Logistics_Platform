// src/components/bots/panels/system-admin/UserManagement.jsx
import React, { useState, useEffect } from 'react';
import { adminService } from '../../../../services/adminService';
import './UserManagement.css';

const UserManagement = ({ onNewNotification, refreshKey }) => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0, total_pages: 0 });
    const [filters, setFilters] = useState({ role: '', active_only: true, search: '' });
    const [selectedUser, setSelectedUser] = useState(null);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [statistics, setStatistics] = useState(null);

    const [newUser, setNewUser] = useState({
        email: '',
        full_name: '',
        company: '',
        country: '',
        role: 'USER',
        password: '',
        is_active: true,
        user_type: 'Freight Broker',
        phone_number: ''
    });

    useEffect(() => {
        loadUsers();
        loadStatistics();
    }, [pagination.page, filters, refreshKey]);

    const loadUsers = async () => {
        setLoading(true);
        try {
            // Get users from Database (new data source)
            const data = await adminService.getUsersFromDatabase(pagination.page, pagination.limit, filters);

            // Fallback to original if database source fails
            if (data.error) {
                console.warn('Database source unavailable, using original');
                const fallback = await adminService.listUsers(pagination.page, pagination.limit, filters);
                setUsers(fallback.users || []);
                setPagination(prev => ({
                    ...prev,
                    total: fallback.total || 0,
                    total_pages: fallback.total_pages || 0
                }));
            } else {
                setUsers(data.users || []);
                setPagination(prev => ({
                    ...prev,
                    total: data.total || 0,
                    total_pages: data.total_pages || 0
                }));
            }
        } catch (error) {
            console.error('Failed to load users:', error);
            onNewNotification('Failed to load users', '');
        } finally {
            setLoading(false);
        }
    };

    const loadStatistics = async () => {
        try {
            // Get statistics from Database (new data source)
            const stats = await adminService.getUserStatisticsFromDatabase();

            // Fallback to original if database source fails
            if (stats.error) {
                console.warn('Database statistics unavailable, using original');
                const fallback = await adminService.getUsersStatistics();
                setStatistics(fallback);
            } else {
                setStatistics(stats);
            }
        } catch (error) {
            console.error('Failed to load statistics:', error);
        }
    };

    const handleCreateUser = async (e) => {
        e.preventDefault();
        try {
            await adminService.createUser(newUser);
            onNewNotification('User created successfully', '');
            setShowCreateForm(false);
            setNewUser({
                email: '',
                full_name: '',
                company: '',
                country: '',
                role: 'USER',
                password: '',
                is_active: true,
                user_type: 'Freight Broker',
                phone_number: ''
            });
            loadUsers();
            loadStatistics();
        } catch (error) {
            console.error('Failed to create user:', error);
            onNewNotification('Failed to create user', '');
        }
    };

    const handleDisableUser = async (userId) => {
        if (!confirm('Are you sure you want to disable this user?')) return;

        try {
            await adminService.disableUser(userId);
            onNewNotification('User disabled', '');
            loadUsers();
            loadStatistics();
        } catch (error) {
            console.error('Failed to disable user:', error);
            onNewNotification('Failed to disable user', '');
        }
    };

    const handleEnableUser = async (userId) => {
        try {
            await adminService.enableUser(userId);
            onNewNotification('User enabled', '');
            loadUsers();
            loadStatistics();
        } catch (error) {
            console.error('Failed to enable user:', error);
            onNewNotification('Failed to enable user', '');
        }
    };

    const handleViewDetails = async (userId) => {
        try {
            const userDetails = await adminService.getUserDetails(userId);
            setSelectedUser(userDetails);
        } catch (error) {
            console.error('Failed to load user details:', error);
            onNewNotification('Failed to load user details', '');
        }
    };

    const getRoleBadgeColor = (role) => {
        const colors = {
            'SUPER_ADMIN': '#ef4444',
            'ADMIN': '#f97316',
            'MANAGER': '#eab308',
            'USER': '#3b82f6',
            'GUEST': '#64748b'
        };
        return colors[role] || '#64748b';
    };

    return (
        <div className="user-management">
            {/* Statistics Dashboard */}
            {statistics && (
                <div className="user-stats-grid">
                    <div className="stat-card-user">
                        <span className="stat-icon-user"></span>
                        <div className="stat-content-user">
                            <span className="stat-value-user">{statistics.summary.total_users}</span>
                            <span className="stat-label-user">Total Users</span>
                        </div>
                    </div>
                    <div className="stat-card-user">
                        <span className="stat-icon-user"></span>
                        <div className="stat-content-user">
                            <span className="stat-value-user">{statistics.summary.active_users}</span>
                            <span className="stat-label-user">Active Users</span>
                        </div>
                    </div>
                    <div className="stat-card-user">
                        <span className="stat-icon-user"></span>
                        <div className="stat-content-user">
                            <span className="stat-value-user">{statistics.summary.inactive_users}</span>
                            <span className="stat-label-user">Inactive Users</span>
                        </div>
                    </div>
                    <div className="stat-card-user">
                        <span className="stat-icon-user"></span>
                        <div className="stat-content-user">
                            <span className="stat-value-user">{statistics.summary.new_users_last_7_days}</span>
                            <span className="stat-label-user">New (7 days)</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Filters and Actions */}
            <div className="user-controls">
                <div className="user-filters">
                    <input
                        type="text"
                        placeholder=" Search by email or name..."
                        value={filters.search}
                        onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                        className="filter-input"
                    />
                    <select
                        value={filters.role}
                        onChange={(e) => setFilters({ ...filters, role: e.target.value })}
                        className="filter-select"
                    >
                        <option value="">All Roles</option>
                        <option value="SUPER_ADMIN">Super Admin</option>
                        <option value="ADMIN">Admin</option>
                        <option value="MANAGER">Manager</option>
                        <option value="USER">User</option>
                        <option value="GUEST">Guest</option>
                    </select>
                    <label className="filter-checkbox">
                        <input
                            type="checkbox"
                            checked={filters.active_only}
                            onChange={(e) => setFilters({ ...filters, active_only: e.target.checked })}
                        />
                        <span>Active Only</span>
                    </label>
                </div>
                <button
                    className="btn-create-user"
                    onClick={() => setShowCreateForm(true)}
                >
                    Create User
                </button>
            </div>

            {/* Users Table */}
            <div className="users-table-container">
                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading users...</p>
                    </div>
                ) : users.length === 0 ? (
                    <div className="empty-state">
                        <span className="empty-icon"></span>
                        <h3>No Users Found</h3>
                        <p>No users match your current filters</p>
                    </div>
                ) : (
                    <table className="users-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Email</th>
                                <th>Name</th>
                                <th>Company</th>
                                <th>Role</th>
                                <th>Status</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.id}>
                                    <td>{user.id}</td>
                                    <td className="user-email">{user.email}</td>
                                    <td>{user.full_name || '-'}</td>
                                    <td>{user.company || '-'}</td>
                                    <td>
                                        <span
                                            className="role-badge"
                                            style={{ background: getRoleBadgeColor(user.role) }}
                                        >
                                            {user.role}
                                        </span>
                                    </td>
                                    <td>
                                        <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                                            {user.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td>{user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}</td>
                                    <td className="actions-cell">
                                        <button
                                            className="btn-action btn-view"
                                            onClick={() => handleViewDetails(user.id)}
                                            title="View Details"
                                        >

                                        </button>
                                        {user.is_active ? (
                                            <button
                                                className="btn-action btn-disable"
                                                onClick={() => handleDisableUser(user.id)}
                                                title="Disable User"
                                            >

                                            </button>
                                        ) : (
                                            <button
                                                className="btn-action btn-enable"
                                                onClick={() => handleEnableUser(user.id)}
                                                title="Enable User"
                                            >

                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Pagination */}
            {pagination.total_pages > 1 && (
                <div className="pagination">
                    <button
                        disabled={pagination.page === 1}
                        onClick={() => setPagination({ ...pagination, page: pagination.page - 1 })}
                        className="btn-page"
                    >
                        Previous
                    </button>
                    <span className="page-info">
                        Page {pagination.page} of {pagination.total_pages}
                    </span>
                    <button
                        disabled={pagination.page >= pagination.total_pages}
                        onClick={() => setPagination({ ...pagination, page: pagination.page + 1 })}
                        className="btn-page"
                    >
                        Next
                    </button>
                </div>
            )}

            {/* Create User Modal */}
            {showCreateForm && (
                <div className="modal-overlay" onClick={() => setShowCreateForm(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3> Create New User</h3>
                            <button className="btn-close-modal" onClick={() => setShowCreateForm(false)}></button>
                        </div>
                        <form onSubmit={handleCreateUser} className="create-user-form">
                            <div className="form-row">
                                <div className="form-group">
                                    <label>Email *</label>
                                    <input
                                        type="email"
                                        required
                                        value={newUser.email}
                                        onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                                        className="form-input"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Full Name</label>
                                    <input
                                        type="text"
                                        value={newUser.full_name}
                                        onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                                        className="form-input"
                                    />
                                </div>
                            </div>
                            <div className="form-row">
                                <div className="form-group">
                                    <label>Company</label>
                                    <input
                                        type="text"
                                        value={newUser.company}
                                        onChange={(e) => setNewUser({ ...newUser, company: e.target.value })}
                                        className="form-input"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Country</label>
                                    <input
                                        type="text"
                                        value={newUser.country}
                                        onChange={(e) => setNewUser({ ...newUser, country: e.target.value })}
                                        className="form-input"
                                    />
                                </div>
                            </div>
                            <div className="form-row">
                                <div className="form-group">
                                    <label>Role</label>
                                    <select
                                        value={newUser.role}
                                        onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                                        className="form-select"
                                    >
                                        <option value="USER">User</option>
                                        <option value="MANAGER">Manager</option>
                                        <option value="ADMIN">Admin</option>
                                        <option value="SUPER_ADMIN">Super Admin</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>User Type</label>
                                    <select
                                        value={newUser.user_type}
                                        onChange={(e) => setNewUser({ ...newUser, user_type: e.target.value })}
                                        className="form-select"
                                    >
                                        <option value="Freight Broker">Freight Broker</option>
                                        <option value="Carrier">Carrier</option>
                                        <option value="Shipper">Shipper</option>
                                    </select>
                                </div>
                            </div>
                            <div className="form-row">
                                <div className="form-group">
                                    <label>Phone Number</label>
                                    <input
                                        type="tel"
                                        value={newUser.phone_number}
                                        onChange={(e) => setNewUser({ ...newUser, phone_number: e.target.value })}
                                        className="form-input"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Password</label>
                                    <input
                                        type="password"
                                        value={newUser.password}
                                        onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                                        className="form-input"
                                    />
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        checked={newUser.is_active}
                                        onChange={(e) => setNewUser({ ...newUser, is_active: e.target.checked })}
                                    />
                                    <span>Active</span>
                                </label>
                            </div>
                            <div className="form-actions">
                                <button type="button" className="btn-cancel" onClick={() => setShowCreateForm(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn-submit">
                                    Create User
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* User Details Modal */}
            {selectedUser && (
                <div className="modal-overlay" onClick={() => setSelectedUser(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3> User Details</h3>
                            <button className="btn-close-modal" onClick={() => setSelectedUser(null)}></button>
                        </div>
                        <div className="user-details">
                            <div className="detail-row">
                                <span className="detail-label">ID:</span>
                                <span className="detail-value">{selectedUser.user?.id}</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Email:</span>
                                <span className="detail-value">{selectedUser.user?.email}</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Full Name:</span>
                                <span className="detail-value">{selectedUser.user?.full_name || '-'}</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Company:</span>
                                <span className="detail-value">{selectedUser.user?.company || '-'}</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Country:</span>
                                <span className="detail-value">{selectedUser.user?.country || '-'}</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Role:</span>
                                <span
                                    className="role-badge"
                                    style={{ background: getRoleBadgeColor(selectedUser.user?.role) }}
                                >
                                    {selectedUser.user?.role}
                                </span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Status:</span>
                                <span className={`status-badge ${selectedUser.user?.is_active ? 'active' : 'inactive'}`}>
                                    {selectedUser.user?.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Created:</span>
                                <span className="detail-value">
                                    {selectedUser.user?.created_at ? new Date(selectedUser.user.created_at).toLocaleString() : '-'}
                                </span>
                            </div>
                            {selectedUser.statistics && (
                                <>
                                    <h4>Statistics</h4>
                                    <div className="detail-row">
                                        <span className="detail-label">Shipments:</span>
                                        <span className="detail-value">{selectedUser.statistics.shipments_count}</span>
                                    </div>
                                    <div className="detail-row">
                                        <span className="detail-label">Account Age:</span>
                                        <span className="detail-value">{selectedUser.statistics.account_age_days} days</span>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserManagement;
