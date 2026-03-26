import React, { useState, useEffect } from "react";
import { AlertCircle, RefreshCw, Users, Building } from "lucide-react";
import "./TenantManagement.css";

const TenantManagement = () => {
    const [tenants, setTenants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [retryCount, setRetryCount] = useState(0);

    const fetchTenants = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch("/api/v1/tenants");
            if (!response.ok) {
                if (response.status === 503) {
                    throw new Error("Tenant service temporarily unavailable");
                }
                throw new Error(`Failed to fetch tenants: ${response.status}`);
            }

            const data = await response.json();
            setTenants(data.tenants || []);
        } catch (err) {
            console.error("Error fetching tenants:", err);
            setError(err.message);
            setTenants([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTenants();
    }, [retryCount]);

    const handleRetry = () => {
        setRetryCount((prev) => prev + 1);
    };

    if (loading) {
        return (
            <div className="tenant-loading">
                <div className="spinner"></div>
                <p>Loading tenants...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="tenant-error">
                <AlertCircle size={48} />
                <h3>Unable to Load Tenants</h3>
                <p>{error}</p>
                <button onClick={handleRetry}>
                    <RefreshCw size={16} />
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="tenant-management">
            <div className="header">
                <h2>Tenant Management</h2>
                <button className="create-tenant-btn">Create Tenant</button>
            </div>

            {tenants.length === 0 ? (
                <div className="empty-state">
                    <Building size={48} />
                    <p>No tenants found</p>
                    <button>Create your first tenant</button>
                </div>
            ) : (
                <div className="tenants-grid">
                    {tenants.map((tenant) => (
                        <div key={tenant.id} className="tenant-card">
                            <Users className="tenant-icon" />
                            <h3>{tenant.name}</h3>
                            <p>Status: {tenant.status}</p>
                            <p>Created: {new Date(tenant.created_at).toLocaleDateString()}</p>
                            <button>Manage</button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default TenantManagement;
