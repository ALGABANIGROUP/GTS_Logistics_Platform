import React, { useEffect, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";
import "./PlatformSettings.css";
import SocialMediaLinksManager from "../../components/admin/SocialMediaLinksManager";
import CurrencySelector from "../../components/admin/CurrencySelector";
import { usePlatformStore } from "../../stores/usePlatformStore";

const DEFAULTS = {
    general: {
        platformName: "",
        platformLogo: "",
        timeZone: "UTC",
        dateFormat: "YYYY-MM-DD",
        currency: "USD",
    },
    technical: {
        sessionTimeout: 30,
        maxUploadSize: 10,
        cachingEnabled: true,
        maintenanceMode: false,
        apiRateLimit: "100/hour",
        backupFrequency: "daily",
    },
    email: {
        smtpServer: "",
        smtpPort: 587,
        smtpPassword: "",
        fromEmail: "",
        fromName: "",
        useSSL: true,
        useTLS: true,
    },
    security: {
        minPasswordLength: 8,
        requireUppercase: true,
        requireLowercase: true,
        requireNumbers: true,
        requireSpecialChars: true,
        passwordExpiryDays: 90,
        maxFailedAttempts: 5,
        lockoutDuration: 30,
        allowMultiSession: true,
        enable2FA: false,
    },
    database: {
        dbType: "postgres",
        backupRetentionDays: 14,
        cleanupOldDataDays: 90,
        enableDbLogs: true,
        backupWindow: "02:00",
    },
    integrations: {
        apiKeysEnabled: true,
        webhookUrl: "",
        webhookSecret: "",
        ssoEnabled: false,
        ssoProvider: "none",
        mapEnabled: false,
        mapProvider: "google",
        mapApiKey: "",
        mapDefaultZoom: 10,
        mapDefaultLat: 43.653226,
        mapDefaultLng: -79.383184,
    },
    branding: {
        // Social media links are managed separately via dedicated API
    },
};

const TAB_ORDER = [
    "general",
    "technical",
    "email",
    "security",
    "database",
    "integrations",
    "branding",
];

const SETTINGS_ENDPOINT = "/api/v1/admin/platform-settings";

// Currency mapping based on country codes
const CURRENCY_BY_COUNTRY = {
    US: "USD", CA: "CAD", GB: "GBP", EU: "EUR", AU: "AUD", JP: "JPY", CN: "CNY",
    CH: "CHF", SE: "SEK", NO: "NOK", DK: "DKK", PL: "PLN", CZ: "CZK", HU: "HUF",
    RU: "RUB", TR: "TRY", IN: "INR", BR: "BRL", MX: "MXN", AR: "ARS", CL: "CLP",
    CO: "COP", PE: "PEN", UY: "UYU", ZA: "ZAR", EG: "EGP", SA: "SAR", AE: "AED",
    IL: "ILS", KR: "KRW", SG: "SGD", HK: "HKD", TW: "TWD", TH: "THB", MY: "MYR",
    ID: "IDR", PH: "PHP", VN: "VND", NZ: "NZD"
};

const tabLabel = (k) => {
    const map = {
        general: "General",
        technical: "Technical",
        email: "Email",
        security: "Security",
        database: "Database",
        integrations: "Integrations",
        branding: "Branding",
    };
    return map[k] || k;
};

const normalizeSettings = (payload) => {
    const data = payload && typeof payload === "object" ? payload : {};
    return TAB_ORDER.reduce((acc, key) => {
        acc[key] = { ...DEFAULTS[key], ...(data[key] || {}) };
        return acc;
    }, {});
};

const PlatformSettings = () => {
    const { updatePlatformSettings } = usePlatformStore();
    const [settings, setSettings] = useState(() => normalizeSettings(DEFAULTS));
    const [tenantMeta, setTenantMeta] = useState(null);
    const [logoFile, setLogoFile] = useState(null);
    const [backgroundFile, setBackgroundFile] = useState(null);
    const [activeTab, setActiveTab] = useState("general");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [saving, setSaving] = useState(false);
    const [uploadingLogo, setUploadingLogo] = useState(false);
    const [uploadingBackground, setUploadingBackground] = useState(false);
    const [saveStatus, setSaveStatus] = useState(null);
    const [confirmResetSection, setConfirmResetSection] = useState(null);

    const [testEmail, setTestEmail] = useState("");
    const [testEmailStatus, setTestEmailStatus] = useState(null);
    const [testWebhookStatus, setTestWebhookStatus] = useState(null);
    const [detectingLocation, setDetectingLocation] = useState(false);

    const canShowTLS = useMemo(() => true, []);

    useEffect(() => {
        fetchSettings();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchSettings = async () => {
        try {
            setLoading(true);
            setError(null);

            const res = await axiosClient.get(SETTINGS_ENDPOINT);
            const payload = res?.data?.data || res?.data || {};
            setSettings(normalizeSettings(payload));
            setTenantMeta(payload?.tenant || null);
        } catch (e) {
            setError(
                e?.normalized?.detail ||
                e?.response?.data?.detail ||
                e?.message ||
                "Failed to load settings. Please check your network connection."
            );
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (section, field, value) => {
        setSettings((prev) => ({
            ...prev,
            [section]: { ...prev[section], [field]: value },
        }));
    };

    const handleSave = async (section) => {
        try {
            setSaving(true);
            setSaveStatus(null);
            const payload = { [section]: settings[section] };
            const res = await axiosClient.put(SETTINGS_ENDPOINT, payload);
            const updated = res?.data?.data || res?.data || {};
            syncSettingsFromResponse(updated);
            setSaveStatus({ type: "success", message: `${tabLabel(section)} settings saved.` });

            // Update platform store if general settings were saved
            if (section === "general") {
                updatePlatformSettings({
                    platformName: updated.general?.platformName ?? settings.general.platformName,
                    platformLogo: updated.general?.platformLogo ?? settings.general.platformLogo,
                    tenantId: updated?.tenant?.tenantId ?? tenantMeta?.tenantId ?? null,
                });
            }
        } catch (e) {
            setSaveStatus({ type: "error", message: "Failed to save settings. Please try again." });
        } finally {
            setSaving(false);
            setTimeout(() => setSaveStatus(null), 2500);
        }
    };

    const handleResetToDefaults = (section) => {
        setSettings((prev) => ({ ...prev, [section]: { ...DEFAULTS[section] } }));
        setSaveStatus({ type: "success", message: `${tabLabel(section)} settings reset to defaults.` });
    };

    const handleLogoUpload = (file) => {
        if (!file) return;
        setLogoFile(file);
        const url = URL.createObjectURL(file);
        handleInputChange("general", "platformLogo", url);
    };

    const handleBackgroundUpload = (file) => {
        if (!file) return;
        setBackgroundFile(file);
        const url = URL.createObjectURL(file);
        handleInputChange("branding", "backgroundImage", url);
    };

    const syncSettingsFromResponse = (payload) => {
        const normalized = normalizeSettings(payload || {});
        setSettings((prev) => normalizeSettings({ ...prev, ...normalized }));
        if (payload?.tenant) {
            setTenantMeta(payload.tenant);
        }
        updatePlatformSettings({
            platformName: payload?.general?.platformName ?? normalized.general?.platformName,
            platformLogo:
                payload?.general?.platformLogo ??
                payload?.branding?.logoUrl ??
                normalized.general?.platformLogo,
            tenantId: payload?.tenant?.tenantId ?? tenantMeta?.tenantId ?? null,
        });
    };

    const handleUploadLogo = async () => {
        if (!logoFile) return;
        try {
            setUploadingLogo(true);
            const formData = new FormData();
            formData.append("file", logoFile);
            const res = await axiosClient.post(`${SETTINGS_ENDPOINT}/upload-logo`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            syncSettingsFromResponse(res?.data?.settings || {});
            setLogoFile(null);
            setSaveStatus({ type: "success", message: "Logo uploaded successfully." });
        } catch (error) {
            setSaveStatus({
                type: "error",
                message: error?.response?.data?.detail || "Failed to upload logo.",
            });
        } finally {
            setUploadingLogo(false);
        }
    };

    const handleDeleteLogo = async () => {
        try {
            setUploadingLogo(true);
            const res = await axiosClient.delete(`${SETTINGS_ENDPOINT}/logo`);
            syncSettingsFromResponse(res?.data?.settings || {});
            setLogoFile(null);
            setSaveStatus({ type: "success", message: "Logo deleted successfully." });
        } catch (error) {
            setSaveStatus({
                type: "error",
                message: error?.response?.data?.detail || "Failed to delete logo.",
            });
        } finally {
            setUploadingLogo(false);
        }
    };

    const handleUploadBackground = async () => {
        if (!backgroundFile) return;
        try {
            setUploadingBackground(true);
            const formData = new FormData();
            formData.append("file", backgroundFile);
            const res = await axiosClient.post(`${SETTINGS_ENDPOINT}/upload-background`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            syncSettingsFromResponse(res?.data?.settings || {});
            setBackgroundFile(null);
            setSaveStatus({ type: "success", message: "Background uploaded successfully." });
        } catch (error) {
            setSaveStatus({
                type: "error",
                message: error?.response?.data?.detail || "Failed to upload background.",
            });
        } finally {
            setUploadingBackground(false);
        }
    };

    const handleDeleteBackground = async () => {
        try {
            setUploadingBackground(true);
            const res = await axiosClient.delete(`${SETTINGS_ENDPOINT}/background`);
            syncSettingsFromResponse(res?.data?.settings || {});
            setBackgroundFile(null);
            setSaveStatus({ type: "success", message: "Background deleted successfully." });
        } catch (error) {
            setSaveStatus({
                type: "error",
                message: error?.response?.data?.detail || "Failed to delete background.",
            });
        } finally {
            setUploadingBackground(false);
        }
    };

    const handleTestEmail = async () => {
        if (!testEmail) {
            setSaveStatus({ type: "error", message: "Please enter a test email address." });
            return;
        }

        try {
            setTestEmailStatus("sending");

            // Call the backend test email endpoint
            const response = await axiosClient.post(
                `${SETTINGS_ENDPOINT}/test-email`,
                { test_email: testEmail }
            );

            setTestEmailStatus("sent");
            setSaveStatus({ type: "success", message: response.data.message || `Test email sent successfully to ${testEmail}.` });

        } catch (error) {
            setTestEmailStatus("failed");
            const errorMsg = error?.response?.data?.detail ||
                error?.message ||
                "Failed to send test email. Please check your email configuration.";
            setSaveStatus({ type: "error", message: errorMsg });
        } finally {
            setTimeout(() => setTestEmailStatus(null), 2000);
        }
    };

    const handleTestWebhook = async () => {
        try {
            setTestWebhookStatus("sending");
            const response = await axiosClient.post(`${SETTINGS_ENDPOINT}/test-webhook`);
            setTestWebhookStatus("sent");
            setSaveStatus({ type: "success", message: response?.data?.message || "Webhook test delivered successfully." });
        } catch (error) {
            setTestWebhookStatus("failed");
            const errorMsg =
                error?.response?.data?.detail ||
                error?.message ||
                "Failed to send webhook test. Please check the webhook URL.";
            setSaveStatus({ type: "error", message: errorMsg });
        }
    };

    const handleAutoDetectCurrency = async () => {
        try {
            setDetectingLocation(true);
            const response = await fetch('https://ipapi.co/json/');
            const data = await response.json();

            if (data.country_code) {
                const detectedCurrency = CURRENCY_BY_COUNTRY[data.country_code] || "USD";
                handleInputChange("general", "currency", detectedCurrency);
                setSaveStatus({ type: "success", message: `Currency auto-detected: ${detectedCurrency} (${data.country_name || data.country_code})` });
            } else {
                setSaveStatus({ type: "error", message: "Could not detect location. Please select currency manually." });
            }
        } catch (error) {
            console.error("Currency auto-detection failed:", error);
            setSaveStatus({ type: "error", message: "Failed to detect location. Please select currency manually." });
        } finally {
            setDetectingLocation(false);
        }
    };

    const handleAutoDetectTimeZone = async () => {
        try {
            setDetectingLocation(true);
            const response = await fetch('https://ipapi.co/json/');
            const data = await response.json();

            if (data.timezone) {
                // Convert timezone format if needed (ipapi.co gives IANA format like "America/New_York")
                const timezoneValue = data.timezone;
                handleInputChange("general", "timeZone", timezoneValue);
                setSaveStatus({ type: "success", message: `Time zone auto-detected: ${timezoneValue} (${data.country_name || data.country_code})` });
            } else {
                setSaveStatus({ type: "error", message: "Could not detect time zone. Please select manually." });
            }
        } catch (error) {
            console.error("Time zone auto-detection failed:", error);
            setSaveStatus({ type: "error", message: "Failed to detect time zone. Please select manually." });
        } finally {
            setDetectingLocation(false);
        }
    };

    const SectionActions = ({ section }) => (
        <div className="section-actions">
            <button
                className="btn-secondary"
                onClick={() => setConfirmResetSection(section)}
                disabled={saving}
            >
                Reset to Defaults
            </button>
            <button className="btn-primary" onClick={() => handleSave(section)} disabled={saving}>
                {saving ? "Saving..." : `Save ${tabLabel(section)} Settings`}
            </button>
        </div>
    );

    if (loading) {
        return (
            <div className="settings-loading">
                <div className="spinner" />
                <p>Loading platform settings...</p>
            </div>
        );
    }

    return (
        <div className="platform-settings">
            <div className="settings-header">
                <h1>Platform Settings</h1>
                <p className="subtitle">
                    Configure core platform settings and preferences
                    {tenantMeta?.companyName ? ` for ${tenantMeta.companyName}` : ""}
                    {tenantMeta?.tenantType ? ` (${tenantMeta.tenantType})` : ""}
                </p>
            </div>

            {error ? (
                <div className="error-container">
                    <div className="error-icon">!</div>
                    <h3>Network Error</h3>
                    <p>{error}</p>
                    <button className="btn-retry" onClick={fetchSettings}>
                        Retry Connection
                    </button>
                </div>
            ) : (
                <>
                    <div className="settings-tabs">
                        {TAB_ORDER.map((tab) => (
                            <button
                                key={tab}
                                className={`tab-btn ${activeTab === tab ? "active" : ""}`}
                                onClick={() => setActiveTab(tab)}
                            >
                                {tabLabel(tab)}
                            </button>
                        ))}
                    </div>

                    {saveStatus && (
                        <div className={`save-banner ${saveStatus.type}`}>
                            <span>{saveStatus.message}</span>
                        </div>
                    )}

                    <div className="settings-content">
                        {activeTab === "general" && (
                            <div className="settings-section">
                                <h2>General Settings</h2>

                                <div className="settings-grid">
                                    <div className="form-group">
                                        <label>Platform Name</label>
                                        <input
                                            type="text"
                                            value={settings.general.platformName}
                                            onChange={(e) => handleInputChange("general", "platformName", e.target.value)}
                                            placeholder="Enter platform name"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label>Time Zone</label>
                                        <div className="timezone-group">
                                            <select
                                                value={settings.general.timeZone}
                                                onChange={(e) => handleInputChange("general", "timeZone", e.target.value)}
                                            >
                                                <option value="UTC">UTC - Coordinated Universal Time</option>
                                                <option value="America/New_York">EST - Eastern Standard Time</option>
                                                <option value="America/Chicago">CST - Central Standard Time</option>
                                                <option value="America/Denver">MST - Mountain Standard Time</option>
                                                <option value="America/Los_Angeles">PST - Pacific Standard Time</option>
                                                <option value="America/Toronto">EST - Eastern Time (Toronto)</option>
                                                <option value="America/Vancouver">PST - Pacific Time (Vancouver)</option>
                                                <option value="Europe/London">GMT - Greenwich Mean Time</option>
                                                <option value="Europe/Paris">CET - Central European Time</option>
                                                <option value="Europe/Berlin">CET - Central European Time</option>
                                                <option value="Europe/Rome">CET - Central European Time</option>
                                                <option value="Europe/Madrid">CET - Central European Time</option>
                                                <option value="Asia/Dubai">GST - Gulf Standard Time</option>
                                                <option value="Asia/Riyadh">AST - Arabia Standard Time</option>
                                                <option value="Asia/Kolkata">IST - India Standard Time</option>
                                                <option value="Asia/Shanghai">CST - China Standard Time</option>
                                                <option value="Asia/Tokyo">JST - Japan Standard Time</option>
                                                <option value="Asia/Seoul">KST - Korea Standard Time</option>
                                                <option value="Australia/Sydney">AEST - Australian Eastern Time</option>
                                                <option value="Australia/Melbourne">AEST - Australian Eastern Time</option>
                                                <option value="Pacific/Auckland">NZST - New Zealand Time</option>
                                            </select>
                                            <button
                                                className="btn-secondary auto-detect-btn"
                                                onClick={handleAutoDetectTimeZone}
                                                disabled={detectingLocation}
                                                title="Auto-detect time zone based on your location"
                                            >
                                                {detectingLocation ? "Detecting..." : "Auto-Detect"}
                                            </button>
                                        </div>
                                    </div>

                                    <div className="form-group">
                                        <label>Currency</label>
                                        <div className="currency-group">
                                            <select
                                                value={settings.general.currency}
                                                onChange={(e) => handleInputChange("general", "currency", e.target.value)}
                                            >
                                                <option value="USD">USD - US Dollar</option>
                                                <option value="EUR">EUR - Euro</option>
                                                <option value="GBP">GBP - British Pound</option>
                                                <option value="CAD">CAD - Canadian Dollar</option>
                                                <option value="AUD">AUD - Australian Dollar</option>
                                                <option value="JPY">JPY - Japanese Yen</option>
                                                <option value="CNY">CNY - Chinese Yuan</option>
                                                <option value="CHF">CHF - Swiss Franc</option>
                                                <option value="SEK">SEK - Swedish Krona</option>
                                                <option value="NOK">NOK - Norwegian Krone</option>
                                                <option value="DKK">DKK - Danish Krone</option>
                                                <option value="PLN">PLN - Polish Złoty</option>
                                                <option value="CZK">CZK - Czech Koruna</option>
                                                <option value="HUF">HUF - Hungarian Forint</option>
                                                <option value="RUB">RUB - Russian Ruble</option>
                                                <option value="TRY">TRY - Turkish Lira</option>
                                                <option value="INR">INR - Indian Rupee</option>
                                                <option value="BRL">BRL - Brazilian Real</option>
                                                <option value="MXN">MXN - Mexican Peso</option>
                                                <option value="ARS">ARS - Argentine Peso</option>
                                                <option value="CLP">CLP - Chilean Peso</option>
                                                <option value="COP">COP - Colombian Peso</option>
                                                <option value="PEN">PEN - Peruvian Sol</option>
                                                <option value="UYU">UYU - Uruguayan Peso</option>
                                                <option value="ZAR">ZAR - South African Rand</option>
                                                <option value="EGP">EGP - Egyptian Pound</option>
                                                <option value="SAR">SAR - Saudi Riyal</option>
                                                <option value="AED">AED - UAE Dirham</option>
                                                <option value="ILS">ILS - Israeli Shekel</option>
                                                <option value="KRW">KRW - South Korean Won</option>
                                                <option value="SGD">SGD - Singapore Dollar</option>
                                                <option value="HKD">HKD - Hong Kong Dollar</option>
                                                <option value="TWD">TWD - New Taiwan Dollar</option>
                                                <option value="THB">THB - Thai Baht</option>
                                                <option value="MYR">MYR - Malaysian Ringgit</option>
                                                <option value="IDR">IDR - Indonesian Rupiah</option>
                                                <option value="PHP">PHP - Philippine Peso</option>
                                                <option value="VND">VND - Vietnamese Dong</option>
                                                <option value="NZD">NZD - New Zealand Dollar</option>
                                            </select>
                                            <button
                                                className="btn-secondary auto-detect-btn"
                                                onClick={handleAutoDetectCurrency}
                                                disabled={detectingLocation}
                                                title="Auto-detect currency based on your location"
                                            >
                                                {detectingLocation ? "Detecting..." : "Auto-Detect"}
                                            </button>
                                        </div>
                                    </div>

                                    <div className="form-group">
                                        <label>Date Format</label>
                                        <select
                                            value={settings.general.dateFormat}
                                            onChange={(e) => handleInputChange("general", "dateFormat", e.target.value)}
                                        >
                                            <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                                            <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                                            <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                                        </select>
                                    </div>

                                    <div className="form-group full-width">
                                        <label>Platform Logo</label>
                                        <div className="logo-upload">
                                            <div className="logo-row">
                                                <input
                                                    type="file"
                                                    accept=".png,.jpg,.jpeg,.svg,.webp"
                                                    onChange={(e) => handleLogoUpload(e.target.files?.[0])}
                                                />
                                                {settings.general.platformLogo ? (
                                                    <div className="logo-preview">
                                                        <img src={settings.general.platformLogo} alt="Logo Preview" />
                                                    </div>
                                                ) : (
                                                    <div className="logo-placeholder">No logo uploaded</div>
                                                )}
                                            </div>
                                            <div className="section-actions" style={{ marginTop: "0.75rem" }}>
                                                <button
                                                    type="button"
                                                    className="btn-primary"
                                                    onClick={handleUploadLogo}
                                                    disabled={!logoFile || uploadingLogo}
                                                >
                                                    {uploadingLogo ? "Uploading..." : "Upload Logo"}
                                                </button>
                                                <button
                                                    type="button"
                                                    className="btn-secondary"
                                                    onClick={handleDeleteLogo}
                                                    disabled={!settings.general.platformLogo || uploadingLogo}
                                                >
                                                    Delete Logo
                                                </button>
                                            </div>
                                            {logoFile && (
                                                <p className="hint" style={{ marginTop: "0.5rem" }}>
                                                    Selected: {logoFile.name}
                                                </p>
                                            )}
                                            <p className="hint">Recommended: 200x50 PNG or SVG</p>
                                        </div>
                                    </div>
                                </div>

                                <SectionActions section="general" />
                            </div>
                        )}

                        {activeTab === "technical" && (
                            <div className="settings-section">
                                <h2>Technical Settings</h2>

                                <div className="settings-grid">
                                    <div className="form-group">
                                        <label>Session Timeout (minutes)</label>
                                        <input
                                            type="number"
                                            value={settings.technical.sessionTimeout}
                                            onChange={(e) =>
                                                handleInputChange(
                                                    "technical",
                                                    "sessionTimeout",
                                                    Number(e.target.value || 0)
                                                )
                                            }
                                            min="1"
                                            max="1440"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label>Max Upload Size (MB)</label>
                                        <input
                                            type="number"
                                            value={settings.technical.maxUploadSize}
                                            onChange={(e) =>
                                                handleInputChange(
                                                    "technical",
                                                    "maxUploadSize",
                                                    Number(e.target.value || 0)
                                                )
                                            }
                                            min="1"
                                            max="100"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label>API Rate Limit</label>
                                        <select
                                            value={settings.technical.apiRateLimit}
                                            onChange={(e) =>
                                                handleInputChange("technical", "apiRateLimit", e.target.value)
                                            }
                                        >
                                            <option value="50/hour">50 requests/hour</option>
                                            <option value="100/hour">100 requests/hour</option>
                                            <option value="200/hour">200 requests/hour</option>
                                            <option value="500/hour">500 requests/hour</option>
                                        </select>
                                    </div>

                                    <div className="form-group">
                                        <label>Backup Frequency</label>
                                        <select
                                            value={settings.technical.backupFrequency}
                                            onChange={(e) =>
                                                handleInputChange("technical", "backupFrequency", e.target.value)
                                            }
                                        >
                                            <option value="hourly">Hourly</option>
                                            <option value="daily">Daily</option>
                                            <option value="weekly">Weekly</option>
                                            <option value="monthly">Monthly</option>
                                        </select>
                                    </div>

                                    <div className="form-group checkbox-group">
                                        <label className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={settings.technical.cachingEnabled}
                                                onChange={(e) =>
                                                    handleInputChange("technical", "cachingEnabled", e.target.checked)
                                                }
                                            />
                                            Enable Caching
                                        </label>
                                    </div>

                                    <div className="form-group checkbox-group">
                                        <label className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={settings.technical.maintenanceMode}
                                                onChange={(e) =>
                                                    handleInputChange("technical", "maintenanceMode", e.target.checked)
                                                }
                                            />
                                            Maintenance Mode
                                        </label>
                                        {settings.technical.maintenanceMode && (
                                            <p className="warning-text">
                                                The platform will be inaccessible except for admins.
                                            </p>
                                        )}
                                    </div>
                                </div>

                                <SectionActions section="technical" />
                            </div>
                        )}

                        {activeTab === "email" && (
                            <div className="settings-section">
                                <h2>Email Settings</h2>

                                <div className="settings-grid">
                                    <div className="form-group">
                                        <label>SMTP Server</label>
                                        <input
                                            type="text"
                                            value={settings.email.smtpServer}
                                            onChange={(e) => handleInputChange("email", "smtpServer", e.target.value)}
                                            placeholder="smtp.example.com"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label>SMTP Port</label>
                                        <input
                                            type="number"
                                            value={settings.email.smtpPort}
                                            onChange={(e) =>
                                                handleInputChange("email", "smtpPort", Number(e.target.value || 0))
                                            }
                                            placeholder="587"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label>SMTP Password</label>
                                        <input
                                            type="password"
                                            value={settings.email.smtpPassword || ""}
                                            onChange={(e) => handleInputChange("email", "smtpPassword", e.target.value)}
                                            placeholder="Enter SMTP password"
                                        />
                                        <p className="hint">Password will be encrypted and stored securely</p>
                                    </div>

                                    <div className="form-group">
                                        <label>From Email</label>
                                        <input
                                            type="email"
                                            value={settings.email.fromEmail}
                                            onChange={(e) => handleInputChange("email", "fromEmail", e.target.value)}
                                            placeholder="noreply@company.com"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label>From Name</label>
                                        <input
                                            type="text"
                                            value={settings.email.fromName}
                                            onChange={(e) => handleInputChange("email", "fromName", e.target.value)}
                                            placeholder="Platform Notifications"
                                        />
                                    </div>

                                    <div className="form-group checkbox-group">
                                        <label className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={settings.email.useSSL}
                                                onChange={(e) => handleInputChange("email", "useSSL", e.target.checked)}
                                            />
                                            Use SSL
                                        </label>
                                    </div>

                                    {canShowTLS && (
                                        <div className="form-group checkbox-group">
                                            <label className="checkbox-label">
                                                <input
                                                    type="checkbox"
                                                    checked={settings.email.useTLS}
                                                    onChange={(e) => handleInputChange("email", "useTLS", e.target.checked)}
                                                />
                                                Use TLS
                                            </label>
                                        </div>
                                    )}
                                </div>

                                <div className="test-email-section">
                                    <h3>Test Email Configuration</h3>
                                    <div className="test-email-form">
                                        <input
                                            type="email"
                                            value={testEmail}
                                            onChange={(e) => setTestEmail(e.target.value)}
                                            placeholder="Enter test email address"
                                        />
                                        <button
                                            className={`btn-test ${testEmailStatus === "sending" ? "sending" : ""}`}
                                            onClick={handleTestEmail}
                                            disabled={testEmailStatus === "sending"}
                                        >
                                            {testEmailStatus === "sending" ? "Sending..." : "Send Test Email"}
                                        </button>
                                    </div>
                                </div>

                                <SectionActions section="email" />
                            </div>
                        )}

                        {activeTab === "security" && (
                            <div className="settings-section">
                                <h2>Security Settings</h2>

                                <div className="settings-grid">
                                    <div className="form-group">
                                        <label>Minimum Password Length</label>
                                        <input
                                            type="number"
                                            value={settings.security.minPasswordLength}
                                            onChange={(e) =>
                                                handleInputChange(
                                                    "security",
                                                    "minPasswordLength",
                                                    Number(e.target.value || 0)
                                                )
                                            }
                                            min="6"
                                            max="32"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label>Password Expiry (days)</label>
                                        <input
                                            type="number"
                                            value={settings.security.passwordExpiryDays}
                                            onChange={(e) =>
                                                handleInputChange(
                                                    "security",
                                                    "passwordExpiryDays",
                                                    Number(e.target.value || 0)
                                                )
                                            }
                                            min="0"
                                            max="365"
                                        />
                                        {settings.security.passwordExpiryDays === 0 && (
                                            <p className="hint">0 means passwords never expire</p>
                                        )}
                                    </div>

                                    <div className="form-group">
                                        <label>Max Failed Login Attempts</label>
                                        <input
                                            type="number"
                                            value={settings.security.maxFailedAttempts}
                                            onChange={(e) =>
                                                handleInputChange(
                                                    "security",
                                                    "maxFailedAttempts",
                                                    Number(e.target.value || 0)
                                                )
                                            }
                                            min="1"
                                            max="10"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label>Lockout Duration (minutes)</label>
                                        <input
                                            type="number"
                                            value={settings.security.lockoutDuration}
                                            onChange={(e) =>
                                                handleInputChange(
                                                    "security",
                                                    "lockoutDuration",
                                                    Number(e.target.value || 0)
                                                )
                                            }
                                            min="1"
                                            max="1440"
                                        />
                                    </div>

                                    <div className="form-group checkbox-group">
                                        <label className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={settings.security.allowMultiSession}
                                                onChange={(e) =>
                                                    handleInputChange("security", "allowMultiSession", e.target.checked)
                                                }
                                            />
                                            Allow Multiple Sessions
                                        </label>
                                    </div>

                                    <div className="form-group checkbox-group">
                                        <label className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={settings.security.enable2FA}
                                                onChange={(e) => handleInputChange("security", "enable2FA", e.target.checked)}
                                            />
                                            Enable Two-Factor Authentication (2FA)
                                        </label>
                                    </div>

                                    <div className="form-group full-width">
                                        <label>Password Complexity Requirements</label>
                                        <div className="checkbox-list">
                                            <label className="checkbox-label">
                                                <input
                                                    type="checkbox"
                                                    checked={settings.security.requireUppercase}
                                                    onChange={(e) =>
                                                        handleInputChange("security", "requireUppercase", e.target.checked)
                                                    }
                                                />
                                                Require uppercase letters (A-Z)
                                            </label>
                                            <label className="checkbox-label">
                                                <input
                                                    type="checkbox"
                                                    checked={settings.security.requireLowercase}
                                                    onChange={(e) =>
                                                        handleInputChange("security", "requireLowercase", e.target.checked)
                                                    }
                                                />
                                                Require lowercase letters (a-z)
                                            </label>
                                            <label className="checkbox-label">
                                                <input
                                                    type="checkbox"
                                                    checked={settings.security.requireNumbers}
                                                    onChange={(e) =>
                                                        handleInputChange("security", "requireNumbers", e.target.checked)
                                                    }
                                                />
                                                Require numbers (0-9)
                                            </label>
                                            <label className="checkbox-label">
                                                <input
                                                    type="checkbox"
                                                    checked={settings.security.requireSpecialChars}
                                                    onChange={(e) =>
                                                        handleInputChange("security", "requireSpecialChars", e.target.checked)
                                                    }
                                                />
                                                Require special characters (!@#$%^&*)
                                            </label>
                                        </div>
                                    </div>
                                </div>

                                <SectionActions section="security" />
                            </div>
                        )}

                        {activeTab === "database" && (
                            <div className="settings-section">
                                <h2>Database Settings</h2>

                                <div className="settings-grid">
                                    <div className="form-group">
                                        <label>Database Type</label>
                                        <select
                                            value={settings.database.dbType}
                                            onChange={(e) => handleInputChange("database", "dbType", e.target.value)}
                                        >
                                            <option value="postgres">PostgreSQL</option>
                                            <option value="mysql">MySQL</option>
                                            <option value="mssql">SQL Server</option>
                                            <option value="mongodb">MongoDB</option>
                                        </select>
                                    </div>

                                    <div className="form-group">
                                        <label>Backup Retention (days)</label>
                                        <input
                                            type="number"
                                            value={settings.database.backupRetentionDays}
                                            onChange={(e) =>
                                                handleInputChange(
                                                    "database",
                                                    "backupRetentionDays",
                                                    Number(e.target.value || 0)
                                                )
                                            }
                                            min="1"
                                            max="365"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label>Cleanup Old Data (days)</label>
                                        <input
                                            type="number"
                                            value={settings.database.cleanupOldDataDays}
                                            onChange={(e) =>
                                                handleInputChange(
                                                    "database",
                                                    "cleanupOldDataDays",
                                                    Number(e.target.value || 0)
                                                )
                                            }
                                            min="0"
                                            max="3650"
                                        />
                                        {settings.database.cleanupOldDataDays === 0 && (
                                            <p className="hint">0 means no automatic cleanup</p>
                                        )}
                                    </div>

                                    <div className="form-group">
                                        <label>Backup Window (HH:mm)</label>
                                        <input
                                            type="time"
                                            value={settings.database.backupWindow}
                                            onChange={(e) =>
                                                handleInputChange("database", "backupWindow", e.target.value)
                                            }
                                        />
                                    </div>

                                    <div className="form-group checkbox-group">
                                        <label className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={settings.database.enableDbLogs}
                                                onChange={(e) =>
                                                    handleInputChange("database", "enableDbLogs", e.target.checked)
                                                }
                                            />
                                            Enable Database Logs
                                        </label>
                                    </div>
                                </div>

                                <SectionActions section="database" />
                            </div>
                        )}

                        {activeTab === "integrations" && (
                            <div className="settings-section">
                                <h2>Integration Settings</h2>

                                <div className="settings-grid">
                                    <div className="form-group checkbox-group">
                                        <label className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={settings.integrations.apiKeysEnabled}
                                                onChange={(e) =>
                                                    handleInputChange("integrations", "apiKeysEnabled", e.target.checked)
                                                }
                                            />
                                            Enable API Keys
                                        </label>
                                    </div>

                                    <div className="form-group full-width">
                                        <label>Webhook URL</label>
                                        <input
                                            type="text"
                                            value={settings.integrations.webhookUrl}
                                            onChange={(e) => handleInputChange("integrations", "webhookUrl", e.target.value)}
                                            placeholder="https://example.com/webhook"
                                        />
                                    </div>

                                    <div className="form-group full-width">
                                        <label>Webhook Secret</label>
                                        <input
                                            type="password"
                                            value={settings.integrations.webhookSecret}
                                            onChange={(e) =>
                                                handleInputChange("integrations", "webhookSecret", e.target.value)
                                            }
                                            placeholder="Enter webhook secret"
                                        />
                                        <button
                                            type="button"
                                            className="btn-secondary"
                                            style={{ marginTop: "0.5rem", width: "fit-content" }}
                                            onClick={handleTestWebhook}
                                            disabled={testWebhookStatus === "sending"}
                                        >
                                            {testWebhookStatus === "sending" ? "Testing..." : "Test Webhook"}
                                        </button>
                                    </div>

                                    <div className="form-group checkbox-group">
                                        <label className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={settings.integrations.ssoEnabled}
                                                onChange={(e) =>
                                                    handleInputChange("integrations", "ssoEnabled", e.target.checked)
                                                }
                                            />
                                            Enable SSO
                                        </label>
                                    </div>

                                    <div className="form-group">
                                        <label>SSO Provider</label>
                                        <select
                                            value={settings.integrations.ssoProvider}
                                            onChange={(e) =>
                                                handleInputChange("integrations", "ssoProvider", e.target.value)
                                            }
                                            disabled={!settings.integrations.ssoEnabled}
                                        >
                                            <option value="none">None</option>
                                            <option value="okta">Okta</option>
                                            <option value="azuread">Azure AD</option>
                                            <option value="google">Google</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="subsection" style={{ marginTop: '2rem' }}>
                                    <h3 style={{ color: '#3b82f6', marginBottom: '1rem' }}>Map Provider Configuration</h3>

                                    <div className="settings-grid">
                                        <div className="form-group checkbox-group">
                                            <label className="checkbox-label">
                                                <input
                                                    type="checkbox"
                                                    checked={settings.integrations.mapEnabled}
                                                    onChange={(e) =>
                                                        handleInputChange("integrations", "mapEnabled", e.target.checked)
                                                    }
                                                />
                                                Enable Map Integration
                                            </label>
                                        </div>

                                        <div className="form-group">
                                            <label>Map Provider</label>
                                            <select
                                                value={settings.integrations.mapProvider}
                                                onChange={(e) =>
                                                    handleInputChange("integrations", "mapProvider", e.target.value)
                                                }
                                                disabled={!settings.integrations.mapEnabled}
                                            >
                                                <option value="google">Google Maps</option>
                                                <option value="mapbox">Mapbox</option>
                                                <option value="openstreetmap">OpenStreetMap</option>
                                                <option value="leaflet">Leaflet</option>
                                            </select>
                                        </div>

                                        <div className="form-group full-width">
                                            <label>API Key / Token</label>
                                            <input
                                                type="password"
                                                value={settings.integrations.mapApiKey}
                                                onChange={(e) =>
                                                    handleInputChange("integrations", "mapApiKey", e.target.value)
                                                }
                                                placeholder="Enter API key or access token"
                                                disabled={!settings.integrations.mapEnabled}
                                            />
                                            <p className="hint" style={{ marginTop: '0.5rem' }}>
                                                {settings.integrations.mapProvider === 'google' && 'Get your API key from Google Cloud Console'}
                                                {settings.integrations.mapProvider === 'mapbox' && 'Get your access token from Mapbox Dashboard'}
                                                {settings.integrations.mapProvider === 'openstreetmap' && 'OpenStreetMap is free and does not require an API key'}
                                                {settings.integrations.mapProvider === 'leaflet' && 'Leaflet is free and does not require an API key'}
                                            </p>
                                        </div>

                                        <div className="form-group">
                                            <label>Default Zoom Level</label>
                                            <input
                                                type="number"
                                                value={settings.integrations.mapDefaultZoom}
                                                onChange={(e) =>
                                                    handleInputChange(
                                                        "integrations",
                                                        "mapDefaultZoom",
                                                        Number(e.target.value || 10)
                                                    )
                                                }
                                                min="1"
                                                max="20"
                                                disabled={!settings.integrations.mapEnabled}
                                            />
                                            <p className="hint">1 = World view, 20 = Street level</p>
                                        </div>

                                        <div className="form-group">
                                            <label>Default Center Latitude</label>
                                            <input
                                                type="number"
                                                step="0.000001"
                                                value={settings.integrations.mapDefaultLat}
                                                onChange={(e) =>
                                                    handleInputChange(
                                                        "integrations",
                                                        "mapDefaultLat",
                                                        Number(e.target.value || 0)
                                                    )
                                                }
                                                placeholder="43.653226"
                                                disabled={!settings.integrations.mapEnabled}
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label>Default Center Longitude</label>
                                            <input
                                                type="number"
                                                step="0.000001"
                                                value={settings.integrations.mapDefaultLng}
                                                onChange={(e) =>
                                                    handleInputChange(
                                                        "integrations",
                                                        "mapDefaultLng",
                                                        Number(e.target.value || 0)
                                                    )
                                                }
                                                placeholder="-79.383184"
                                                disabled={!settings.integrations.mapEnabled}
                                            />
                                        </div>
                                    </div>
                                </div>

                                <SectionActions section="integrations" />
                            </div>
                        )}

                        {activeTab === "branding" && (
                            <div className="settings-section">
                                <h2>Branding Settings</h2>
                                <p className="section-description">
                                    Manage your platform's branding elements including social media links and visual identity.
                                </p>

                                <CurrencySelector />

                                <div className="subsection" style={{ marginBottom: "1.5rem" }}>
                                    <h3 style={{ color: "#3b82f6", marginBottom: "1rem" }}>Background Image</h3>
                                    <div className="logo-upload">
                                        <div className="logo-row">
                                            <input
                                                type="file"
                                                accept=".png,.jpg,.jpeg,.webp"
                                                onChange={(e) => handleBackgroundUpload(e.target.files?.[0])}
                                            />
                                            {settings.branding?.backgroundImage ? (
                                                <div className="logo-preview">
                                                    <img
                                                        src={settings.branding.backgroundImage}
                                                        alt="Background Preview"
                                                        style={{ objectFit: "cover", width: "100%", height: "100%" }}
                                                    />
                                                </div>
                                            ) : (
                                                <div className="logo-placeholder">No background uploaded</div>
                                            )}
                                        </div>
                                        <div className="section-actions" style={{ marginTop: "0.75rem" }}>
                                            <button
                                                type="button"
                                                className="btn-primary"
                                                onClick={handleUploadBackground}
                                                disabled={!backgroundFile || uploadingBackground}
                                            >
                                                {uploadingBackground ? "Uploading..." : "Upload Background"}
                                            </button>
                                            <button
                                                type="button"
                                                className="btn-secondary"
                                                onClick={handleDeleteBackground}
                                                disabled={!settings.branding?.backgroundImage || uploadingBackground}
                                            >
                                                Delete Background
                                            </button>
                                        </div>
                                        {backgroundFile && (
                                            <p className="hint" style={{ marginTop: "0.5rem" }}>
                                                Selected: {backgroundFile.name}
                                            </p>
                                        )}
                                        <p className="hint">Recommended: 1920x1080 PNG, JPG, or WEBP</p>
                                    </div>
                                </div>

                                <SocialMediaLinksManager />
                            </div>
                        )}
                    </div>
                </>
            )}

            {confirmResetSection && (
                <div className="settings-confirm-overlay">
                    <div className="settings-confirm-modal">
                        <h3>Reset Settings</h3>
                        <p>Reset {tabLabel(confirmResetSection)} settings to their default values?</p>
                        <div className="settings-confirm-actions">
                            <button className="btn-secondary" onClick={() => setConfirmResetSection(null)}>
                                Cancel
                            </button>
                            <button
                                className="btn-primary"
                                onClick={() => {
                                    handleResetToDefaults(confirmResetSection);
                                    setConfirmResetSection(null);
                                }}
                            >
                                Reset
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PlatformSettings;
