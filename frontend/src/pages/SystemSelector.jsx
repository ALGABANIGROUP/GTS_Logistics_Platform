import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import axiosClient from "../api/axiosClient";
import "./SystemSelector.css";

/**
 * System Selector Page - shown after login
 * User selects between GTS Main, TMS, or Admin Panel
 */
export default function SystemSelector() {
    const navigate = useNavigate();
    const { user, isAuthenticated, token } = useAuth();
    const [systems, setSystems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isAdmin, setIsAdmin] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!isAuthenticated) {
            navigate("/login");
            return;
        }

        // Fetch available systems and unified data
        fetchSystemsData();
    }, [isAuthenticated, token]);

    const fetchSystemsData = async () => {
        try {
            // Fetch from unified API
            const response = await axiosClient.get("/api/v1/systems/selector", {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            setSystems(response.data.systems || []);
            setIsAdmin(response.data.user?.is_admin || false);
        } catch (error) {
            console.error("Error fetching systems:", error);
            setError("Failed to fetch data");
            // fallback: default systems
            setSystems([
                {
                    id: "gts_main",
                    title: "GTS Main Platform",
                    description: "Partner and client management",
                    available: true,
                    admin_only: false,
                    icon: "🏢",
                },
                {
                    id: "tms",
                    title: "TMS System",
                    description: "Transport Management System",
                    available: true,
                    admin_only: false,
                    icon: "🚚",
                },
                {
                    id: "admin",
                    title: "Admin Dashboard",
                    description: "Full platform control",
                    available: isAdmin,
                    admin_only: true,
                    icon: "⚙️",
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const selectSystem = async (systemId) => {
        try {
            setLoading(true);

            // Call system switch API
            const response = await axiosClient.post(
                "/api/v1/systems/switch",
                { new_system: systemId },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            // Update token
            if (response.data.token || response.data.access_token) {
                const newToken = response.data.token || response.data.access_token;
                localStorage.setItem("access_token", newToken);
                localStorage.setItem("token", newToken);
            }

            // Navigate to selected system
            switch (systemId) {
                case "tms":
                    navigate("/tms/dashboard");
                    break;
                case "admin":
                    navigate("/admin/unified-dashboard");
                    break;
                case "gts_main":
                default:
                    navigate("/dashboard");
                    break;
            }
        } catch (err) {
            console.error("Error switching system:", err);
            setError("Failed to switch system");
        } finally {
            setLoading(false);
        }
    };

    if (loading && systems.length === 0) {
        return (
            <div className="system-selector-loading">
                <div className="spinner"></div>
                <p>Loading...</p>
            </div>
        );
    }

    return (
        <div className="system-selector-wrapper">
            {/* Header */}
            <header className="selector-header">
                <div className="header-content">
                    <div className="logo-section">
                        <h1>Gabani Transport Solutions (GTS)</h1>
                        <p>Logistics Command & Control Platform</p>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="selector-main">
                <div className="selector-container">
                    <h2 className="selector-title">Select System</h2>
                    <p className="selector-subtitle">Choose the system you want to access</p>

                    {/* Error Message */}
                    {error && (
                        <div className="error-banner">
                            <span>⚠️</span>
                            <p>{error}</p>
                        </div>
                    )}

                    {/* Systems Grid */}
                    <div className="systems-grid">
                        {systems.map((system) => (
                            <div
                                key={system.id}
                                className={`system-card ${system.available ? "available" : "disabled"} ${system.admin_only ? "admin-badge-card" : ""
                                    }`}
                                onClick={() => system.available && selectSystem(system.id)}
                                role="button"
                                tabIndex={system.available ? 0 : -1}
                            >
                                {system.admin_only && (
                                    <div className="admin-badge-small">Admin</div>
                                )}

                                <div className="card-icon">{system.icon}</div>

                                <div className="card-content">
                                    <h3 className="card-title">{system.title}</h3>
                                    <p className="card-description">{system.description}</p>
                                </div>

                                {system.available && <div className="card-arrow">→</div>}

                                {!system.available && (
                                    <div className="card-disabled">Not Available</div>
                                )}
                            </div>
                        ))}
                    </div>

                    {/* Info */}
                    <div className="selector-info">
                        <p>
                            Logged in as: <strong>{user?.email}</strong>
                        </p>
                    </div>
                </div>

                <div className="system-selector-footer">
                    <button
                        className="logout-btn"
                        onClick={() => {
                            localStorage.clear();
                            navigate("/login");
                        }}
                    >
                        Sign Out
                    </button>
                </div>
            </main>
        </div>
    );
}
