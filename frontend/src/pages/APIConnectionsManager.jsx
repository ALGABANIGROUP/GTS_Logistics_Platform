import React, { useState, useEffect } from "react";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import axiosClient from "../api/axiosClient";

const APIConnectionsManager = () => {
    const [connections, setConnections] = useState([]);
    const [categories, setCategories] = useState([]);
    const [connectionTypes, setConnectionTypes] = useState([]);
    const [stats, setStats] = useState(null);
    const [showAddModal, setShowAddModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [selectedConnection, setSelectedConnection] = useState(null);
    const [loading, setLoading] = useState(true);
    const [testingConnection, setTestingConnection] = useState(null);

    const [formData, setFormData] = useState({
        platform_name: "",
        platform_category: "other",
        description: "",
        api_url: "",
        connection_type: "api_key",
        api_key: "",
        api_secret: "",
        access_token: "",
        refresh_token: "",
        client_id: "",
        client_secret: "",
        oauth_callback_url: "",
        is_active: true
    });

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);

            // Load connections
            const connectionsRes = await axiosClient.get("/api/v1/admin/api-connections/");
            setConnections(connectionsRes.data.connections || []);

            // Load categories
            const categoriesRes = await axiosClient.get("/api/v1/admin/api-connections/categories/list");
            setCategories(categoriesRes.data.categories || []);

            // Load connection types
            const typesRes = await axiosClient.get("/api/v1/admin/api-connections/connection-types/list");
            setConnectionTypes(typesRes.data.connection_types || []);

            // Load stats
            const statsRes = await axiosClient.get("/api/v1/admin/api-connections/stats");
            setStats(statsRes.data.stats || {});

            setLoading(false);
        } catch (error) {
            console.error("Failed to load data:", error);
            toast.error("Failed to load API connections");
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === "checkbox" ? checked : value
        }));
    };

    const handleAddConnection = async (e) => {
        e.preventDefault();
        try {
            await axiosClient.post("/api/v1/admin/api-connections/", formData);
            toast.success("API connection added successfully!");
            setShowAddModal(false);
            resetForm();
            loadData();
        } catch (error) {
            console.error("Failed to add connection:", error);
            toast.error(error.response?.data?.detail || "Failed to add API connection");
        }
    };

    const handleEditConnection = async (e) => {
        e.preventDefault();
        try {
            await axiosClient.put(`/api/v1/admin/api-connections/${selectedConnection.id}`, formData);
            toast.success("API connection updated successfully!");
            setShowEditModal(false);
            setSelectedConnection(null);
            resetForm();
            loadData();
        } catch (error) {
            console.error("Failed to update connection:", error);
            toast.error(error.response?.data?.detail || "Failed to update API connection");
        }
    };

    const handleDeleteConnection = async (connection) => {
        if (!window.confirm(`Are you sure you want to delete '${connection.platform_name}'?`)) {
            return;
        }

        try {
            await axiosClient.delete(`/api/v1/admin/api-connections/${connection.id}`);
            toast.success("API connection deleted successfully!");
            loadData();
        } catch (error) {
            console.error("Failed to delete connection:", error);
            toast.error(error.response?.data?.detail || "Failed to delete API connection");
        }
    };

    const handleTestConnection = async (connection) => {
        setTestingConnection(connection.id);
        try {
            const response = await axiosClient.post(`/api/v1/admin/api-connections/${connection.id}/test`);

            if (response.data.status === "success") {
                toast.success(`✅ Connection test successful! (${response.data.test_result.http_status})`);
            } else {
                toast.warning(`⚠️ Connection test failed: ${response.data.test_result.message}`);
            }

            loadData(); // Refresh to show updated test status
        } catch (error) {
            console.error("Failed to test connection:", error);
            toast.error("Failed to test connection");
        } finally {
            setTestingConnection(null);
        }
    };

    const openEditModal = (connection) => {
        setSelectedConnection(connection);
        setFormData({
            platform_name: connection.platform_name,
            platform_category: connection.platform_category,
            description: connection.description || "",
            api_url: connection.api_url,
            connection_type: connection.connection_type,
            api_key: "",  // Don't pre-fill secrets
            api_secret: "",
            access_token: "",
            refresh_token: "",
            client_id: connection.client_id || "",
            client_secret: "",
            oauth_callback_url: connection.oauth_callback_url || "",
            is_active: connection.is_active
        });
        setShowEditModal(true);
    };

    const resetForm = () => {
        setFormData({
            platform_name: "",
            platform_category: "other",
            description: "",
            api_url: "",
            connection_type: "api_key",
            api_key: "",
            api_secret: "",
            access_token: "",
            refresh_token: "",
            client_id: "",
            client_secret: "",
            oauth_callback_url: "",
            is_active: true
        });
    };

    const getStatusBadge = (connection) => {
        if (!connection.is_active) {
            return <span className="px-2 py-1 text-xs rounded bg-gray-200 text-gray-700">Inactive</span>;
        }
        if (connection.is_verified) {
            return <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-700">✓ Verified</span>;
        }
        if (connection.last_test_status === "failed") {
            return <span className="px-2 py-1 text-xs rounded bg-red-100 text-red-700">✗ Failed</span>;
        }
        return <span className="px-2 py-1 text-xs rounded bg-yellow-100 text-yellow-700">⏳ Pending</span>;
    };

    const getCategoryIcon = (category) => {
        const icons = {
            social_media: "📱",
            payment: "💳",
            erp: "📊",
            crm: "👥",
            logistics: "🚚",
            analytics: "📈",
            communication: "💬",
            storage: "💾",
            other: "🔌"
        };
        return icons[category] || "🔌";
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading API connections...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto p-6">
            <ToastContainer position="top-right" />

            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    🔌 API Connections Manager
                </h1>
                <p className="text-gray-600">
                    Manage external platform integrations (Social Media, Payment, ERP, etc.)
                </p>
            </div>

            {/* Stats Cards */}
            {stats && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
                        <div className="text-sm text-gray-600 mb-1">Total Connections</div>
                        <div className="text-3xl font-bold text-gray-900">{stats.total_connections}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
                        <div className="text-sm text-gray-600 mb-1">Active</div>
                        <div className="text-3xl font-bold text-green-600">{stats.active_connections}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
                        <div className="text-sm text-gray-600 mb-1">Verified</div>
                        <div className="text-3xl font-bold text-purple-600">{stats.verified_connections}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6 border-l-4 border-orange-500">
                        <div className="text-sm text-gray-600 mb-1">Success Rate</div>
                        <div className="text-3xl font-bold text-orange-600">{stats.overall_success_rate}%</div>
                    </div>
                </div>
            )}

            {/* Actions */}
            <div className="mb-6 flex justify-between items-center">
                <button
                    onClick={() => setShowAddModal(true)}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition"
                >
                    + Add New API Connection
                </button>
                <button
                    onClick={loadData}
                    className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium transition"
                >
                    🔄 Refresh
                </button>
            </div>

            {/* Connections List */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Platform
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Category
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Connection Type
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Status
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Last Tested
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {connections.length === 0 ? (
                            <tr>
                                <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                                    No API connections configured yet. Click "Add New API Connection" to get started.
                                </td>
                            </tr>
                        ) : (
                            connections.map((connection) => (
                                <tr key={connection.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <span className="text-2xl mr-3">{getCategoryIcon(connection.platform_category)}</span>
                                            <div>
                                                <div className="text-sm font-medium text-gray-900">{connection.platform_name}</div>
                                                <div className="text-xs text-gray-500 truncate max-w-xs">{connection.api_url}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-700">
                                            {connection.platform_category?.replace("_", " ")}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                                        {connection.connection_type?.replace("_", " ").toUpperCase()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        {getStatusBadge(connection)}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {connection.last_tested_at ? new Date(connection.last_tested_at).toLocaleString() : "Never"}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                                        <button
                                            onClick={() => handleTestConnection(connection)}
                                            disabled={testingConnection === connection.id}
                                            className="text-blue-600 hover:text-blue-900 disabled:opacity-50"
                                        >
                                            {testingConnection === connection.id ? "Testing..." : "Test"}
                                        </button>
                                        <button
                                            onClick={() => openEditModal(connection)}
                                            className="text-indigo-600 hover:text-indigo-900"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => handleDeleteConnection(connection)}
                                            className="text-red-600 hover:text-red-900"
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Add/Edit Modal */}
            {(showAddModal || showEditModal) && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="p-6">
                            <h2 className="text-2xl font-bold mb-6">
                                {showEditModal ? "Edit API Connection" : "Add New API Connection"}
                            </h2>

                            <form onSubmit={showEditModal ? handleEditConnection : handleAddConnection}>
                                <div className="space-y-4">
                                    {/* Platform Name */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Platform Name *
                                        </label>
                                        <input
                                            type="text"
                                            name="platform_name"
                                            value={formData.platform_name}
                                            onChange={handleInputChange}
                                            required
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                            placeholder="e.g., Facebook, Stripe, SAP"
                                        />
                                    </div>

                                    {/* Category & Connection Type */}
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                Category *
                                            </label>
                                            <select
                                                name="platform_category"
                                                value={formData.platform_category}
                                                onChange={handleInputChange}
                                                required
                                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                            >
                                                {categories.map(cat => (
                                                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                Connection Type *
                                            </label>
                                            <select
                                                name="connection_type"
                                                value={formData.connection_type}
                                                onChange={handleInputChange}
                                                required
                                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                            >
                                                {connectionTypes.map(type => (
                                                    <option key={type.value} value={type.value}>{type.label}</option>
                                                ))}
                                            </select>
                                        </div>
                                    </div>

                                    {/* Description */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Description
                                        </label>
                                        <textarea
                                            name="description"
                                            value={formData.description}
                                            onChange={handleInputChange}
                                            rows="2"
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                            placeholder="Brief description of this integration"
                                        />
                                    </div>

                                    {/* API URL */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            API URL *
                                        </label>
                                        <input
                                            type="url"
                                            name="api_url"
                                            value={formData.api_url}
                                            onChange={handleInputChange}
                                            required
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                            placeholder="https://api.example.com/v1"
                                        />
                                    </div>

                                    {/* Credentials */}
                                    <div className="border-t pt-4">
                                        <h3 className="text-lg font-medium mb-4">Authentication Credentials</h3>

                                        {(formData.connection_type === "api_key" || formData.connection_type === "basic_auth") && (
                                            <>
                                                <div className="mb-4">
                                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                                        API Key
                                                    </label>
                                                    <input
                                                        type="password"
                                                        name="api_key"
                                                        value={formData.api_key}
                                                        onChange={handleInputChange}
                                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                                        placeholder={showEditModal ? "Leave empty to keep current" : "Enter API key"}
                                                    />
                                                </div>
                                                {formData.connection_type === "basic_auth" && (
                                                    <div>
                                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                                            API Secret
                                                        </label>
                                                        <input
                                                            type="password"
                                                            name="api_secret"
                                                            value={formData.api_secret}
                                                            onChange={handleInputChange}
                                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                                            placeholder={showEditModal ? "Leave empty to keep current" : "Enter API secret"}
                                                        />
                                                    </div>
                                                )}
                                            </>
                                        )}

                                        {formData.connection_type === "bearer_token" && (
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                                    Access Token
                                                </label>
                                                <input
                                                    type="password"
                                                    name="access_token"
                                                    value={formData.access_token}
                                                    onChange={handleInputChange}
                                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                                    placeholder={showEditModal ? "Leave empty to keep current" : "Enter access token"}
                                                />
                                            </div>
                                        )}

                                        {formData.connection_type === "oauth2" && (
                                            <>
                                                <div className="mb-4">
                                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                                        Client ID
                                                    </label>
                                                    <input
                                                        type="text"
                                                        name="client_id"
                                                        value={formData.client_id}
                                                        onChange={handleInputChange}
                                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                                        placeholder="OAuth Client ID"
                                                    />
                                                </div>
                                                <div className="mb-4">
                                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                                        Client Secret
                                                    </label>
                                                    <input
                                                        type="password"
                                                        name="client_secret"
                                                        value={formData.client_secret}
                                                        onChange={handleInputChange}
                                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                                        placeholder={showEditModal ? "Leave empty to keep current" : "OAuth Client Secret"}
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                                        Callback URL
                                                    </label>
                                                    <input
                                                        type="url"
                                                        name="oauth_callback_url"
                                                        value={formData.oauth_callback_url}
                                                        onChange={handleInputChange}
                                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                                        placeholder="https://your-app.com/oauth/callback"
                                                    />
                                                </div>
                                            </>
                                        )}
                                    </div>

                                    {/* Active Status */}
                                    <div className="flex items-center">
                                        <input
                                            type="checkbox"
                                            name="is_active"
                                            checked={formData.is_active}
                                            onChange={handleInputChange}
                                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                        />
                                        <label className="ml-2 block text-sm text-gray-900">
                                            Active (connection can be used)
                                        </label>
                                    </div>
                                </div>

                                {/* Form Actions */}
                                <div className="mt-6 flex justify-end space-x-3">
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setShowAddModal(false);
                                            setShowEditModal(false);
                                            setSelectedConnection(null);
                                            resetForm();
                                        }}
                                        className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                    >
                                        {showEditModal ? "Update Connection" : "Add Connection"}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default APIConnectionsManager;
