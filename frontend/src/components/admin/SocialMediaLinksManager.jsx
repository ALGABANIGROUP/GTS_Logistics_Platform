import React, { useEffect, useState } from "react";
import { useSettingsStore } from "../../stores/useSettingsStore";
import TruckOrbitSpinner from "../loaders/TruckOrbitSpinner";
import "./SocialMediaLinksManager.css";

const SOCIAL_PLATFORMS = [
    { id: "linkedin", name: "LinkedIn", icon: "in", placeholder: "https://linkedin.com/company/yourcompany" },
    { id: "x", name: "X (Twitter)", icon: "X", placeholder: "https://x.com/yourhandle" },
    { id: "facebook", name: "Facebook", icon: "f", placeholder: "https://facebook.com/yourpage" },
    { id: "youtube", name: "YouTube", icon: "▶", placeholder: "https://youtube.com/channel/yourchannel" },
    { id: "instagram", name: "Instagram", icon: "ig", placeholder: "https://instagram.com/yourhandle" },
];

const normalizeLinks = (raw) => {
    if (!raw) return {};
    if (raw.links && typeof raw.links === "object") return raw.links;
    if (typeof raw === "object") return raw;
    return {};
};

const toDisplayMessage = (value, fallback = "An unexpected error occurred.") => {
    if (typeof value === "string" && value.trim()) return value;
    if (Array.isArray(value)) {
        const combined = value
            .map((item) => {
                if (typeof item === "string") return item;
                if (item?.msg) return item.msg;
                if (item?.message) return item.message;
                return null;
            })
            .filter(Boolean)
            .join(", ");
        return combined || fallback;
    }
    if (value && typeof value === "object") {
        if (typeof value.msg === "string" && value.msg.trim()) return value.msg;
        if (typeof value.message === "string" && value.message.trim()) return value.message;
    }
    return fallback;
};

const SocialMediaLinksManager = () => {
    const {
        socialMediaLinks,
        isLoading,
        error,
        success,
        fetchSocialMediaLinks,
        saveSocialMediaLinks,
        clearMessages,
    } = useSettingsStore();

    const [links, setLinks] = useState(() => normalizeLinks(socialMediaLinks));

    useEffect(() => {
        const loadLinks = async () => {
            try {
                const loadedLinks = await fetchSocialMediaLinks();
                setLinks(normalizeLinks(loadedLinks));
            } catch (loadError) {
                console.error("Error loading social links:", loadError);
            }
        };
        loadLinks();
    }, [fetchSocialMediaLinks]);

    useEffect(() => {
        setLinks(normalizeLinks(socialMediaLinks));
    }, [socialMediaLinks]);

    const handleLinkChange = (platform, value) => {
        setLinks((prev) => ({
            ...prev,
            [platform]: value,
        }));
    };

    const updateFooterLinks = (nextLinks = links) => {
        const activeLinks = Object.entries(nextLinks)
            .filter(([_, value]) => value && value.trim() !== "")
            .reduce((acc, [key, value]) => {
                acc[key] = value;
                return acc;
            }, {});

        const event = new CustomEvent("socialLinksUpdated", {
            detail: { links: activeLinks },
        });
        window.dispatchEvent(event);
    };

    const saveLinks = async () => {
        try {
            const savedLinks = await saveSocialMediaLinks(links);
            updateFooterLinks(savedLinks);
        } catch (saveError) {
            console.error("Error saving social links:", saveError);
        }
    };

    const clearAllLinks = async () => {
        const confirmed = window.confirm("Are you sure you want to delete all social media links?");
        if (!confirmed) return;

        const emptyLinks = {};
        setLinks(emptyLinks);
        await saveSocialMediaLinks(emptyLinks);
        updateFooterLinks(emptyLinks);
    };

    if (isLoading) {
        return (
            <div className="social-links-loading">
                <TruckOrbitSpinner />
                <p>Loading social media links...</p>
            </div>
        );
    }

    return (
        <div className="social-media-links-manager">
            <div className="links-header">
                <h3>Social Media Links</h3>
                <p>Configure the social media links that appear in your platform's footer</p>
            </div>

            {error && (
                <div className="error-banner">
                    <span>Warning: {toDisplayMessage(error, "Failed to load social media links.")}</span>
                    <button
                        onClick={() =>
                            fetchSocialMediaLinks().then((loadedLinks) => setLinks(normalizeLinks(loadedLinks)))
                        }
                        className="retry-btn"
                    >
                        Retry
                    </button>
                </div>
            )}

            {success && (
                <div className="success-banner">
                    <span>Success: {success}</span>
                </div>
            )}

            <div className="links-table">
                <div className="table-header">
                    <div className="col-platform">Platform</div>
                    <div className="col-url">URL</div>
                    <div className="col-enabled">Enabled</div>
                    <div className="col-actions">Actions</div>
                </div>

                {SOCIAL_PLATFORMS.map((platform) => {
                    const url = links[platform.id] || "";
                    const isEnabled = !!url.trim();

                    return (
                        <div key={platform.id} className={`table-row ${isEnabled ? "enabled" : "disabled"}`}>
                            <div className="col-platform">
                                <span className="platform-icon">{platform.icon}</span>
                                <span className="platform-name">{platform.name}</span>
                            </div>

                            <div className="col-url">
                                <input
                                    type="url"
                                    value={url}
                                    onChange={(e) => handleLinkChange(platform.id, e.target.value)}
                                    placeholder={platform.placeholder}
                                />
                            </div>

                            <div className="col-enabled">
                                <span className={`status-indicator ${isEnabled ? "active" : "inactive"}`}>
                                    {isEnabled ? "Active" : "Inactive"}
                                </span>
                            </div>

                            <div className="col-actions">
                                {isEnabled && (
                                    <a
                                        href={url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="test-link-btn"
                                        title="Test link"
                                    >
                                        Open
                                    </a>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="links-actions">
                <button className="btn-primary" onClick={saveLinks} disabled={isLoading}>
                    {isLoading ? "Saving..." : "Save Changes"}
                </button>
                <button
                    className="btn-secondary"
                    onClick={() => {
                        setLinks({});
                        clearMessages();
                    }}
                    disabled={isLoading}
                >
                    Reset
                </button>
                <button className="btn-danger" onClick={clearAllLinks} disabled={isLoading}>
                    Clear All
                </button>
            </div>
        </div>
    );
};

export default SocialMediaLinksManager;
