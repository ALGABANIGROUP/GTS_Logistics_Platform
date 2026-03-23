import React, { useEffect, useState } from "react";
import axiosClient from "../../api/axiosClient";
import "./AdminFooterSettings.css";
import RequireAuth from "../../components/RequireAuth.jsx";

const SETTINGS_ENDPOINT = "/api/v1/admin/platform-settings";

const defaultFooter = {
  emails: {
    support: "",
    sales: "",
    billing: "",
  },
  social_links: {
    linkedin: "",
    x: "",
    facebook: "",
    youtube: "",
    instagram: "",
  },
  branding: {
    platformName: "",
    logoUrl: "",
    faviconUrl: "",
  },
};

export default function AdminFooterSettings() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <AdminFooterSettingsContent />
    </RequireAuth>
  );
}

function AdminFooterSettingsContent() {
  const [footer, setFooter] = useState(defaultFooter);
  const [loading, setLoading] = useState(true);
  const [saveStatus, setSaveStatus] = useState({ state: "idle", message: "" });

  useEffect(() => {
    fetchFooter();
  }, []);

  async function fetchFooter() {
    setLoading(true);
    try {
      const res = await axiosClient.get(SETTINGS_ENDPOINT);
      const data = res.data || {};
      setFooter({
        emails: {
          support: data.email?.support || data.email?.fromEmail || "",
          sales: data.email?.sales || "",
          billing: data.email?.billing || "",
        },
        social_links: {
          linkedin: data.social_links?.linkedin || "",
          x: data.social_links?.x || "",
          facebook: data.social_links?.facebook || "",
          youtube: data.social_links?.youtube || "",
          instagram: data.social_links?.instagram || "",
        },
        branding: {
          platformName: data.branding?.platformName || data.general?.platformName || "",
          logoUrl: data.branding?.logoUrl || data.general?.platformLogo || "",
          faviconUrl: data.branding?.faviconUrl || "",
        },
      });
    } catch {
      setFooter(defaultFooter);
    } finally {
      setLoading(false);
    }
  }

  function handleEmailChange(field, value) {
    setFooter((prev) => ({
      ...prev,
      emails: { ...prev.emails, [field]: value },
    }));
  }

  function handleSocialChange(field, value) {
    setFooter((prev) => ({
      ...prev,
      social_links: { ...prev.social_links, [field]: value },
    }));
  }

  function handleBrandingChange(field, value) {
    setFooter((prev) => ({
      ...prev,
      branding: { ...prev.branding, [field]: value },
    }));
  }

  async function handleSave() {
    setSaveStatus({ state: "saving", message: "" });
    try {
      await axiosClient.put(SETTINGS_ENDPOINT, {
        branding: {
          platformName: footer.branding.platformName,
          logoUrl: footer.branding.logoUrl,
          faviconUrl: footer.branding.faviconUrl,
        },
        general: {
          platformName: footer.branding.platformName,
          platformLogo: footer.branding.logoUrl,
        },
        social_links: footer.social_links,
        email: {
          support: footer.emails.support,
          sales: footer.emails.sales,
          billing: footer.emails.billing,
          fromEmail: footer.emails.support,
        },
      });
      setSaveStatus({ state: "success", message: "Saved successfully." });
    } catch {
      setSaveStatus({ state: "error", message: "Save failed." });
    }
  }

  if (loading) {
    return <div className="admin-footer-settings">Loading...</div>;
  }

  return (
    <div className="admin-footer-settings">
      <h2>Footer Settings</h2>

      <section>
        <h3>Branding</h3>
        <div className="links-list">
          <div className="link-row">
            <input
              value={footer.branding.platformName}
              onChange={(e) => handleBrandingChange("platformName", e.target.value)}
              placeholder="Platform name"
            />
            <input
              value={footer.branding.logoUrl}
              onChange={(e) => handleBrandingChange("logoUrl", e.target.value)}
              placeholder="Logo URL"
            />
          </div>
          <div className="link-row">
            <input
              value={footer.branding.faviconUrl}
              onChange={(e) => handleBrandingChange("faviconUrl", e.target.value)}
              placeholder="Favicon URL"
            />
          </div>
        </div>
      </section>

      <section>
        <h3>Footer Emails</h3>
        <div className="emails-list">
          <label>
            Support
            <input
              value={footer.emails.support}
              onChange={(e) => handleEmailChange("support", e.target.value)}
            />
          </label>
          <label>
            Sales
            <input
              value={footer.emails.sales}
              onChange={(e) => handleEmailChange("sales", e.target.value)}
            />
          </label>
          <label>
            Billing
            <input
              value={footer.emails.billing}
              onChange={(e) => handleEmailChange("billing", e.target.value)}
            />
          </label>
        </div>
      </section>

      <section>
        <h3>Social Links</h3>
        <div className="links-list">
          {Object.entries(footer.social_links).map(([key, value]) => (
            <div className="link-row" key={key}>
              <input
                value={value}
                onChange={(e) => handleSocialChange(key, e.target.value)}
                placeholder={`${key} URL`}
              />
            </div>
          ))}
        </div>
      </section>

      <div className="form-actions">
        <button
          type="button"
          onClick={handleSave}
          className="btn-primary"
          disabled={saveStatus.state === "saving"}
        >
          {saveStatus.state === "saving" ? "Saving..." : "Save"}
        </button>
        <button type="button" onClick={fetchFooter} className="btn-secondary">
          Reload
        </button>
        <span className="save-status">{saveStatus.message}</span>
      </div>
    </div>
  );
}
