import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axiosClient from "../../api/axiosClient";
import "./SocialMediaFooter.css";
import {
    FaFacebookF,
    FaGlobe,
    FaInstagram,
    FaLinkedinIn,
    FaXTwitter,
    FaYoutube,
} from "react-icons/fa6";

const platformIcons = {
    linkedin: FaLinkedinIn,
    twitter: FaXTwitter,
    x: FaXTwitter,
    facebook: FaFacebookF,
    youtube: FaYoutube,
    instagram: FaInstagram,
};

const platformColors = {
    linkedin: "#0a66c2",
    twitter: "#1d9bf0",
    x: "#1d9bf0",
    facebook: "#1877f2",
    youtube: "#ff0000",
    instagram: "#e1306c",
};

const getPlatformMeta = (platform) => {
    const key = String(platform || "").toLowerCase();
    return {
        Icon: platformIcons[key] || FaGlobe,
        color: platformColors[key] || "#e2e8f0",
    };
};

const normalizeLinks = (raw) => {
    if (!raw) return [];

    if (Array.isArray(raw)) {
        return raw
            .map((item) => ({
                platform: item.platform || item.id || "",
                url: item.url || "",
                displayName: item.displayName || item.name || item.platform || item.id || "",
            }))
            .filter((item) => item.platform && item.url);
    }

    if (typeof raw === "object") {
        return Object.entries(raw)
            .filter(([, url]) => Boolean(url))
            .map(([platform, url]) => ({
                platform,
                url,
                displayName: platform,
            }));
    }

    return [];
};

const SocialMediaFooter = () => {
    const [socialLinks, setSocialLinks] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchSocialLinks();

        // Listen for social links updates from admin panel
        const handleSocialLinksUpdate = (event) => {
            const nextLinks = normalizeLinks(event?.detail?.links);
            if (nextLinks.length > 0) {
                setSocialLinks(nextLinks);
                setLoading(false);
                return;
            }
            fetchSocialLinks();
        };

        window.addEventListener("socialLinksUpdated", handleSocialLinksUpdate);

        return () => {
            window.removeEventListener("socialLinksUpdated", handleSocialLinksUpdate);
        };
    }, []);

    const fetchSocialLinks = async () => {
        try {
            const response = await axiosClient.get("/api/v1/social-media/settings/social-links", {
                params: { t: Date.now() },
                headers: { "Cache-Control": "no-cache" },
            });
            const normalized = normalizeLinks(response.data?.links || response.data);
            setSocialLinks(normalized);
        } catch (error) {
            console.error("Error fetching social links:", error);
            setSocialLinks([]);
        } finally {
            setLoading(false);
        }
    };

    const linksToRender = socialLinks;

    return (
        <footer
            style={{
                width: "100%",
                background: "rgba(15, 23, 42, 0.57)",
                borderTop: "1px solid rgba(255,255,255,0.1)",
                padding: "1.5rem",
                textAlign: "center",
                color: "#94a3b8",
                fontSize: "0.875rem",
                backdropFilter: "blur(14px)",
                WebkitBackdropFilter: "blur(14px)",
            }}
        >
            <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "1rem" }}>
                    <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                        <p style={{ margin: "0", fontSize: "0.875rem" }}>
                            Copyright 2026 Gabani Transport Solutions - Secure logistics command center
                        </p>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.75rem", color: "#64748b" }}>
                            <span>🌍</span>
                            <span>We contribute 1% to carbon removal via Stripe Climate</span>
                        </div>
                    </div>
                    <Link
                        to="/terms-and-conditions"
                        style={{
                            color: "#94a3b8",
                            textDecoration: "none",
                            fontSize: "0.875rem",
                            transition: "color 0.3s"
                        }}
                        onMouseEnter={(e) => (e.currentTarget.style.color = "#cbd5e1")}
                        onMouseLeave={(e) => (e.currentTarget.style.color = "#94a3b8")}
                    >
                        Terms & Conditions
                    </Link>
                </div>
                <div
                    style={{
                        display: "flex",
                        justifyContent: "center",
                        gap: "2rem",
                        marginTop: "1rem",
                        flexWrap: "wrap",
                        opacity: loading ? 0.6 : 1,
                    }}
                >
                    {linksToRender.map((link) => {
                        const { Icon, color } = getPlatformMeta(link.platform);
                        return (
                            <a
                                key={link.platform}
                                href={link.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                aria-label={link.displayName || link.platform}
                                style={{
                                    color: "#cbd5e1",
                                    textDecoration: "none",
                                    fontSize: "2rem",
                                    transition: "opacity 0.3s",
                                    display: "inline-flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                }}
                                onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.7")}
                                onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
                            >
                                <Icon className="social-media-icon" style={{ color }} aria-hidden="true" />
                            </a>
                        );
                    })}
                </div>
            </div>
        </footer>
    );
};

export default SocialMediaFooter;
