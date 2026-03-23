import React, { useState, useEffect } from "react";
import axiosClient from "../api/axiosClient";

export default function Footer() {
  const year = new Date().getFullYear();
  const [socialLinks, setSocialLinks] = useState([]);

  useEffect(() => {
    const loadLinks = async () => {
      try {
        const response = await axiosClient.get("/api/v1/social-media/settings/social-links", {
          params: { t: Date.now() },
          headers: { "Cache-Control": "no-cache" }
        });
        const linksArray = Array.isArray(response.data?.links)
          ? response.data.links
          : Object.entries(response.data || {}).filter(([, url]) => Boolean(url)).map(([platform, url]) => ({
              platform,
              url,
              enabled: true,
            }));
        setSocialLinks(linksArray);
      } catch (error) {
        console.warn('Failed to fetch social media links:', error);
        // Fallback: empty links (no social media by default)
        setSocialLinks([]);
      }
    };

    loadLinks();

    // Listen for updates
    const handleUpdate = (event) => {
      const activeLinks = event?.detail?.links || {};
      const linksArray = Object.entries(activeLinks).map(([platform, url]) => ({
        platform,
        url,
        enabled: true
      }));
      setSocialLinks(linksArray);
    };

    window.addEventListener('socialLinksUpdated', handleUpdate);
    return () => window.removeEventListener('socialLinksUpdated', handleUpdate);
  }, []);

  const getPlatformIcon = (platform) => {
    const icons = {
      facebook: '📘',
      x: '𝕏',
      twitter: '🐦',
      linkedin: '💼',
      instagram: '📷',
      youtube: '📺',
      tiktok: '🎵',
      whatsapp: '💬',
      telegram: '✈️'
    };
    return icons[platform] || '🔗';
  };

  const getPlatformName = (platform) => {
    const names = {
      facebook: 'Facebook',
      x: 'X',
      twitter: 'Twitter',
      linkedin: 'LinkedIn',
      instagram: 'Instagram',
      youtube: 'YouTube',
      tiktok: 'TikTok',
      whatsapp: 'WhatsApp',
      telegram: 'Telegram'
    };
    return names[platform] || platform;
  };

  return (
    <footer className="w-full glass-footer glass-morph px-6 py-4">
      <div className="footer-content">
        <div className="copyright">
          <p className="text-center text-xs text-slate-300">
            © {year} Gabani Transport Solutions - Secure logistics command center
          </p>
        </div>

        {socialLinks.length > 0 && (
          <div className="social-links">
            <div className="social-links-title">
              <span className="text-xs text-slate-400">Follow Us:</span>
            </div>
            <div className="social-links-icons">
              {socialLinks.map((link) => (
                <a
                  key={link.platform}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="social-link"
                  title={getPlatformName(link.platform)}
                  aria-label={getPlatformName(link.platform)}
                >
                  {getPlatformIcon(link.platform)}
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </footer>
  );
}
