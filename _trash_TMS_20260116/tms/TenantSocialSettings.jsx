import React, { useEffect, useState } from "react";
import axiosClient from "../../api/axiosClient";
import "./TenantSocialSettings.css";

const PLATFORMS = [
    { key: "facebook", label: "Facebook" },
    { key: "instagram", label: "Instagram" },
    { key: "x", label: "Twitter/X" },
    { key: "linkedin", label: "LinkedIn" },
];

export default function TenantSocialSettings() {
    const [connections, setConnections] = useState([]);
    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState({ state: "idle", message: "" });

    useEffect(() => {
        fetchConnections();
    }, []);

    async function fetchConnections() {
        setLoading(true);
        try {
            const res = await axiosClient.get("/api/tms/tenant/social-connections");
            setConnections(res.data || []);
        } catch (e) {
            setConnections([]);
        } finally {
            setLoading(false);
        }
    }

    async function handleAction(platform, action, connId) {
        setStatus({ state: "saving", message: "" });
        try {
            let url = `/api/tms/tenant/social-connections/${platform}`;
            if (action === "manual") url += "/manual";
            else if (action === "connect") url += "/connect";
            else if (action === "verify" && connId) url = `/api/tms/tenant/social-connections/${connId}/verify`;
            else if (action === "refresh" && connId) url = `/api/tms/tenant/social-connections/${connId}/refresh`;
            else if (action === "disconnect" && connId) url = `/api/tms/tenant/social-connections/${connId}`;
            let method = action === "disconnect" ? "delete" : "post";
            await axiosClient({ url, method });
            setStatus({ state: "success", message: "Action successful." });
            fetchConnections();
        } catch (e) {
            setStatus({ state: "error", message: "Action failed." });
        }
    }

    if (loading) return <div className="tenant-social-settings">Loading...</div>;

    return (
        <div className="tenant-social-settings">
            <h2>Social Connections</h2>
            <div className="security-note">Tokens are encrypted and stored securely.</div>
            <div className="health-row">
                Connected: {connections.filter(c => c.status === "connected").length} / {PLATFORMS.length}
                {connections.some(c => c.status === "expired" || c.status === "invalid") && (
                    <span className="error">Some connections need attention!</span>
                )}
            </div>
            <div className="platforms-cards">
                {PLATFORMS.map(({ key, label }) => {
                    const conn = connections.find(c => c.platform === key);
                    return (
                        <div className="platform-card" key={key}>
                            <div className={`status-badge status-${conn?.status || "not_connected"}`}>{conn?.status || "not_connected"}</div>
                            <div className="platform-label">{label}</div>
                            <div className="account-name">{conn?.accountName || "Not Connected"}</div>
                            <div className="actions">
                                {!conn && (
                                    <>
                                        <button className="btn-primary" onClick={() => handleAction(key, "connect")}>Connect (OAuth)</button>
                                        <button className="btn-secondary" onClick={() => handleAction(key, "manual")}>Manual Setup</button>
                                    </>
                                )}
                                {conn && (
                                    <>
                                        <button className="btn-secondary" onClick={() => handleAction(key, "verify", conn.id)}>Verify</button>
                                        {conn.status === "expired" && (
                                            <button className="btn-primary" onClick={() => handleAction(key, "refresh", conn.id)}>Refresh</button>
                                        )}
                                        <button className="btn-danger" onClick={() => handleAction(key, "disconnect", conn.id)}>Disconnect</button>
                                    </>
                                )}
                            </div>
                            {conn && (
                                <div className="meta">
                                    <div>Expires: {conn.expiresAt ? new Date(conn.expiresAt).toLocaleString() : "-"}</div>
                                    <div>Last Verified: {conn.lastVerifiedAt ? new Date(conn.lastVerifiedAt).toLocaleString() : "-"}</div>
                                    <div>Scopes: {conn.scopes?.join(", ")}</div>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
            <div className="form-actions">
                <span className="save-status">
                    {status.state === 'success' && status.message}
                    {status.state === 'error' && status.message}
                </span>
            </div>
        </div>
    );
}
