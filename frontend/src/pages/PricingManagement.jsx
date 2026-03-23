import React, { useEffect, useMemo, useState } from "react";

import { useAuth } from "../contexts/AuthContext";
import {
  getAdminPricingCatalog,
  getPolicyContext,
  updateAdminPricingCatalog,
} from "../services/billingApi";
import { isAdminRole } from "../utils/userRole";
import "./PricingManagement.css";

const REGION_OPTIONS = ["GLOBAL", "US", "CA"];

const PLAN_AUDIENCE_HINTS = {
  FREE: "Solo drivers and very small fleets",
  STARTER: "Small transport companies",
  GROWTH: "Mid-size transport companies",
  PROFESSIONAL: "Large transport companies",
  ENTERPRISE: "Large enterprises and brokerages",
};

const createItem = () => ({
  code: "",
  name: "",
  price_amount: 0,
  currency: "USD",
  unit: "month",
});

const createPlan = () => ({
  code: "",
  name: "",
  description: "",
  currency: "USD",
  price_amount: 0,
  limits: {
    vehicles: 0,
    users: 0,
  },
  highlights: [],
  suitable_for: [],
  is_demo: false,
  is_free: false,
  addons: [],
});

const normalizePlan = (plan) => ({
  code: plan?.code || "",
  name: plan?.name || "",
  description: plan?.description || "",
  currency: plan?.currency || "USD",
  price_amount: Number(plan?.price_amount || 0),
  limits: {
    vehicles: plan?.limits?.vehicles ?? 0,
    users: plan?.limits?.users ?? 0,
  },
  highlights: Array.isArray(plan?.highlights) ? plan.highlights : Array.isArray(plan?.features) ? plan.features : [],
  suitable_for: Array.isArray(plan?.suitable_for) ? plan.suitable_for : [],
  is_demo: Boolean(plan?.is_demo),
  is_free: Boolean(plan?.is_free),
  addons: Array.isArray(plan?.addons) ? plan.addons : [],
});

const normalizeList = (items = [], fallbackCurrency = "USD") =>
  items.map((item) => ({
    code: item?.code || "",
    name: item?.name || "",
    price_amount: Number(item?.price_amount || 0),
    currency: item?.currency || fallbackCurrency,
    unit: item?.unit || "month",
  }));

const parseLines = (value) =>
  String(value || "")
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);

const formatLines = (items) => (Array.isArray(items) ? items.join("\n") : "");

const PricingManagement = () => {
  const { user, role } = useAuth();
  const adminAccess = isAdminRole(role);

  const [country, setCountry] = useState("GLOBAL");
  const [plans, setPlans] = useState([]);
  const [addons, setAddons] = useState([]);
  const [vehiclePricing, setVehiclePricing] = useState([]);
  const [userPricing, setUserPricing] = useState([]);
  const [botPricing, setBotPricing] = useState([]);
  const [botBundle, setBotBundle] = useState(null);
  const [automationServices, setAutomationServices] = useState([]);
  const [analyticsServices, setAnalyticsServices] = useState([]);
  const [integrationServices, setIntegrationServices] = useState([]);
  const [transactionFees, setTransactionFees] = useState({
    platform_fee_percent: 0,
    supported_gateways: [],
    notes: [],
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadCatalog = async (regionOverride) => {
    setLoading(true);
    setError("");
    setMessage("");
    try {
      let context = null;
      try {
        context = await getPolicyContext();
      } catch {
        context = null;
      }

      const region = regionOverride || context?.country || context?.region || "GLOBAL";
      const response = await getAdminPricingCatalog(region);
      const currency = response?.plans?.[0]?.currency || (region === "CA" ? "CAD" : "USD");

      setCountry(response?.country || region);
      setPlans((response?.plans || []).map(normalizePlan));
      setAddons(normalizeList(response?.addons || [], currency));
      setVehiclePricing(normalizeList(response?.vehicle_pricing || [], currency));
      setUserPricing(normalizeList(response?.user_pricing || [], currency));
      setBotPricing(normalizeList(response?.bot_pricing || [], currency));
      setBotBundle(
        response?.bot_bundle
          ? {
              ...createItem(),
              ...response.bot_bundle,
              price_amount: Number(response?.bot_bundle?.price_amount || 0),
              currency: response?.bot_bundle?.currency || currency,
            }
          : null
      );
      setAutomationServices(normalizeList(response?.extra_services?.automation || [], currency));
      setAnalyticsServices(normalizeList(response?.extra_services?.analytics || [], currency));
      setIntegrationServices(normalizeList(response?.extra_services?.integrations || [], currency));
      setTransactionFees({
        platform_fee_percent: Number(response?.transaction_fees?.platform_fee_percent || 0),
        supported_gateways: response?.transaction_fees?.supported_gateways || [],
        notes: response?.transaction_fees?.notes || [],
      });
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to load pricing catalog.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!adminAccess) return;
    loadCatalog();
  }, [adminAccess]);

  const stats = useMemo(
    () => ({
      plans: plans.length,
      addons: vehiclePricing.length + userPricing.length + addons.length,
      bots: botPricing.length + (botBundle ? 1 : 0),
      services: automationServices.length + analyticsServices.length + integrationServices.length,
    }),
    [addons.length, analyticsServices.length, automationServices.length, botBundle, botPricing.length, integrationServices.length, plans.length, userPricing.length, vehiclePricing.length]
  );

  const updatePlan = (index, patch) => {
    setPlans((current) => current.map((item, itemIndex) => (itemIndex === index ? { ...item, ...patch } : item)));
  };

  const updatePlanLimits = (index, field, value) => {
    setPlans((current) =>
      current.map((item, itemIndex) =>
        itemIndex === index
          ? { ...item, limits: { ...(item.limits || {}), [field]: value === "" ? 0 : Number(value) } }
          : item
      )
    );
  };

  const updateListItem = (setter, index, field, value) => {
    setter((current) =>
      current.map((item, itemIndex) =>
        itemIndex === index
          ? {
              ...item,
              [field]: field === "price_amount" ? Number(value || 0) : value,
            }
          : item
      )
    );
  };

  const addListItem = (setter, currency) => {
    setter((current) => [...current, { ...createItem(), currency }]);
  };

  const removeListItem = (setter, index) => {
    setter((current) => current.filter((_, itemIndex) => itemIndex !== index));
  };

  const addPlan = () => {
    setPlans((current) => [...current, { ...createPlan(), currency: plans[0]?.currency || "USD" }]);
  };

  const removePlan = (index) => {
    setPlans((current) => current.filter((_, itemIndex) => itemIndex !== index));
  };

  const saveCatalog = async () => {
    setSaving(true);
    setError("");
    setMessage("");

    try {
      const payload = {
        country,
        plans: plans.map((plan) => ({
          ...plan,
          code: String(plan.code || "").toUpperCase(),
          highlights: plan.highlights,
          suitable_for: plan.suitable_for,
        })),
        addons,
        vehicle_pricing: vehiclePricing,
        user_pricing: userPricing,
        bot_pricing: botPricing,
        bot_bundle: botBundle,
        extra_services: {
          automation: automationServices,
          analytics: analyticsServices,
          integrations: integrationServices,
        },
        transaction_fees: transactionFees,
      };

      await updateAdminPricingCatalog(payload);
      setMessage("Pricing catalog saved successfully.");
      await loadCatalog(country);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to save pricing catalog.");
    } finally {
      setSaving(false);
    }
  };

  const renderListEditor = (title, description, items, setter) => (
    <div className="plan-details">
      <div className="details-header">
        <div>
          <h2>{title}</h2>
          {description ? <p className="pm-section-copy">{description}</p> : null}
        </div>
        <button type="button" className="edit-btn" onClick={() => addListItem(setter, plans[0]?.currency || "USD")}>
          Add Item
        </button>
      </div>
      <div className="pm-list-grid">
        {items.map((item, index) => (
          <div key={`${item.code || "item"}-${index}`} className="pm-list-card">
            <div className="pm-list-fields">
              <input className="pm-input" value={item.code} onChange={(e) => updateListItem(setter, index, "code", e.target.value.toUpperCase())} placeholder="Code" />
              <input className="pm-input" value={item.name} onChange={(e) => updateListItem(setter, index, "name", e.target.value)} placeholder="Name" />
              <input className="pm-input" type="number" value={item.price_amount} onChange={(e) => updateListItem(setter, index, "price_amount", e.target.value)} placeholder="Price" />
              <input className="pm-input" value={item.currency} onChange={(e) => updateListItem(setter, index, "currency", e.target.value.toUpperCase())} placeholder="Currency" />
              <input className="pm-input" value={item.unit} onChange={(e) => updateListItem(setter, index, "unit", e.target.value)} placeholder="Unit" />
            </div>
            <button type="button" className="pm-inline-remove" onClick={() => removeListItem(setter, index)}>
              Remove
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  if (!adminAccess) {
    return (
      <div className="pricing-management unauthorized">
        <div className="error-box">
          <h1>Access Denied</h1>
          <p>This page is only available for super admin and admin users.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="pricing-management">
        <div className="pm-header-content">
          <h1>Super Admin Subscription Settings</h1>
          <p>Loading pricing catalog...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pricing-management">
      <header className="pm-header">
        <div className="pm-header-content">
          <h1>Super Admin Subscription Settings</h1>
          <p>Edit public plans, prices, included features, limits, add-ons, bots, and transaction settings.</p>
        </div>
        <div className="pm-toolbar">
          <select className="pm-input" value={country} onChange={(e) => loadCatalog(e.target.value)}>
            {REGION_OPTIONS.map((region) => (
              <option key={region} value={region}>
                {region}
              </option>
            ))}
          </select>
          <button type="button" className="pm-secondary-btn" onClick={() => loadCatalog(country)} disabled={saving}>
            Reload
          </button>
          <button type="button" className="pm-secondary-btn" onClick={addPlan} disabled={saving}>
            Add Plan
          </button>
          <button type="button" className="edit-btn" onClick={saveCatalog} disabled={saving}>
            {saving ? "Saving..." : "Save Catalog"}
          </button>
        </div>
      </header>

      {error ? <div className="error-box"><p>{error}</p></div> : null}
      {message ? <div className="error-box" style={{ borderColor: "#22c55e", color: "#dcfce7" }}><p>{message}</p></div> : null}

      <div className="stats-section">
        <div className="stat-card"><div className="stat-value">{stats.plans}</div><div className="stat-label">Plans</div></div>
        <div className="stat-card"><div className="stat-value">{stats.addons}</div><div className="stat-label">Add-on Rows</div></div>
        <div className="stat-card"><div className="stat-value">{stats.bots}</div><div className="stat-label">Bot Offers</div></div>
        <div className="stat-card"><div className="stat-value">{stats.services}</div><div className="stat-label">Extra Services</div></div>
        <div className="stat-card"><div className="stat-value">{user?.email}</div><div className="stat-label">Editor</div></div>
      </div>

      <div className="pm-structure-grid">
        <div className="pm-structure-card">
          <span className="pm-structure-kicker">Core pricing</span>
          <h3>Subscription Plans</h3>
          <p>Define the public plan ladder, monthly pricing, hard limits, and the target audience for each tier.</p>
        </div>
        <div className="pm-structure-card">
          <span className="pm-structure-kicker">Capacity expansion</span>
          <h3>Add-ons and usage</h3>
          <p>Control extra seats, extra vehicles, and optional add-ons without changing the base package.</p>
        </div>
        <div className="pm-structure-card">
          <span className="pm-structure-kicker">AI revenue</span>
          <h3>Bots and bundles</h3>
          <p>Price each AI bot separately and maintain a discounted full bundle for upsell.</p>
        </div>
        <div className="pm-structure-card">
          <span className="pm-structure-kicker">Billing policy</span>
          <h3>Services and fees</h3>
          <p>Keep service upsells, payment gateways, and platform fee rules in one commercial control panel.</p>
        </div>
      </div>

      <section className="pm-block">
        <div className="pm-block-header">
          <div>
            <span className="pm-block-kicker">Public catalog</span>
            <h2>Core Plans</h2>
            <p className="pm-section-copy">These are the main subscription tiers shown to users when they compare packages.</p>
          </div>
        </div>
      <div className="plans-grid">
        {plans.map((plan, index) => (
          <div key={plan.code || index} className="plan-card selected">
            <div className="plan-header">
              <div className="pm-plan-heading">
                <div className="pm-plan-badges">
                  <span className="pm-badge">{plan.code || "NEW"}</span>
                  {plan.is_free ? <span className="pm-badge pm-badge-success">Free</span> : null}
                </div>
                <button type="button" className="pm-danger-btn" onClick={() => removePlan(index)}>
                  Delete Plan
                </button>
              </div>
            </div>

            <div className="pm-two-col">
              <input className="pm-input" value={plan.code} onChange={(e) => updatePlan(index, { code: e.target.value.toUpperCase() })} placeholder="Code" />
              <input className="pm-input" value={plan.name} onChange={(e) => updatePlan(index, { name: e.target.value })} placeholder="Plan name" />
            </div>

            <div className="pm-price-row">
              <input className="pm-input" type="number" value={plan.price_amount} onChange={(e) => updatePlan(index, { price_amount: Number(e.target.value || 0) })} placeholder="Monthly price" />
              <input className="pm-input" value={plan.currency} onChange={(e) => updatePlan(index, { currency: e.target.value.toUpperCase() })} placeholder="Currency" />
              <label className="pm-checkbox">
                <input type="checkbox" checked={plan.is_free} onChange={(e) => updatePlan(index, { is_free: e.target.checked })} />
                <span>Free plan</span>
              </label>
            </div>

            <textarea className="pm-input pm-textarea" value={plan.description} onChange={(e) => updatePlan(index, { description: e.target.value })} placeholder="Description" />

            <div className="pm-two-col">
              <input className="pm-input" type="number" value={plan?.limits?.vehicles ?? 0} onChange={(e) => updatePlanLimits(index, "vehicles", e.target.value)} placeholder="Vehicles" />
              <input className="pm-input" type="number" value={plan?.limits?.users ?? 0} onChange={(e) => updatePlanLimits(index, "users", e.target.value)} placeholder="Users" />
            </div>

            <textarea
              className="pm-input pm-textarea"
              value={formatLines(plan.highlights)}
              onChange={(e) => updatePlan(index, { highlights: parseLines(e.target.value) })}
              placeholder="Features, one per line"
            />

            <textarea
              className="pm-input pm-textarea"
              value={formatLines(plan.suitable_for)}
              onChange={(e) => updatePlan(index, { suitable_for: parseLines(e.target.value) })}
              placeholder="Best for, one per line"
            />

            <div className="pm-plan-footnote">
              {plan.suitable_for?.length
                ? `Audience: ${plan.suitable_for.join(" • ")}`
                : `Audience hint: ${PLAN_AUDIENCE_HINTS[plan.code] || "Define the target audience for this plan."}`}
            </div>
          </div>
        ))}
      </div>
      </section>

      <section className="pm-block">
        <div className="pm-block-header">
          <div>
            <span className="pm-block-kicker">Plan expansion</span>
            <h2>Add-ons and Limits</h2>
            <p className="pm-section-copy">Use these editors for modular extras and usage-based pricing attached to a base plan.</p>
          </div>
        </div>
        {renderListEditor("Catalog Add-ons", "General optional extras that can be attached to any package.", addons, setAddons)}
        {renderListEditor("Vehicle Pricing", "Tiered monthly pricing for additional vehicles beyond each plan limit.", vehiclePricing, setVehiclePricing)}
        {renderListEditor("User Pricing", "Monthly seat pricing for standard and administrative users.", userPricing, setUserPricing)}
      </section>

      <section className="pm-block">
        <div className="pm-block-header">
          <div>
            <span className="pm-block-kicker">AI revenue</span>
            <h2>Bots and Bundles</h2>
            <p className="pm-section-copy">Configure standalone AI bot offers and the discounted full suite bundle.</p>
          </div>
        </div>
        {renderListEditor("AI Bot Pricing", "Sell each AI bot separately with a dedicated code and monthly price.", botPricing, setBotPricing)}

      <div className="plan-details">
        <div className="details-header">
          <div>
            <h2>Bot Bundle</h2>
            <p className="pm-section-copy">Offer a packaged price for the complete AI bot suite.</p>
          </div>
          {!botBundle ? (
            <button type="button" className="edit-btn" onClick={() => setBotBundle(createItem())}>
              Add Bundle
            </button>
          ) : null}
        </div>
        {botBundle ? (
          <div className="pm-list-grid">
            <div className="pm-list-card pm-list-card-wide">
              <div className="pm-list-fields">
                <input className="pm-input" value={botBundle.code} onChange={(e) => setBotBundle((current) => ({ ...current, code: e.target.value.toUpperCase() }))} placeholder="Code" />
                <input className="pm-input" value={botBundle.name} onChange={(e) => setBotBundle((current) => ({ ...current, name: e.target.value }))} placeholder="Bundle name" />
                <input className="pm-input" type="number" value={botBundle.price_amount} onChange={(e) => setBotBundle((current) => ({ ...current, price_amount: Number(e.target.value || 0) }))} placeholder="Price" />
                <input className="pm-input" value={botBundle.currency} onChange={(e) => setBotBundle((current) => ({ ...current, currency: e.target.value.toUpperCase() }))} placeholder="Currency" />
                <input className="pm-input" value={botBundle.unit} onChange={(e) => setBotBundle((current) => ({ ...current, unit: e.target.value }))} placeholder="Unit" />
              </div>
              <button type="button" className="pm-inline-remove" onClick={() => setBotBundle(null)}>
                Remove
              </button>
            </div>
          </div>
        ) : null}
      </div>
      </section>

      <section className="pm-block">
        <div className="pm-block-header">
          <div>
            <span className="pm-block-kicker">Upsells</span>
            <h2>Additional Services</h2>
            <p className="pm-section-copy">Group operational, analytics, and integration services as premium upsells.</p>
          </div>
        </div>
        {renderListEditor("Automation Services", "Operational automations such as invoicing and recurring workflows.", automationServices, setAutomationServices)}
        {renderListEditor("Analytics Services", "Premium analytical services such as route and fuel intelligence.", analyticsServices, setAnalyticsServices)}
        {renderListEditor("Integration Services", "API and external system integrations offered as paid services.", integrationServices, setIntegrationServices)}
      </section>

      <section className="pm-block">
        <div className="pm-block-header">
          <div>
            <span className="pm-block-kicker">Billing policy</span>
            <h2>Transaction Fees</h2>
            <p className="pm-section-copy">Define platform fee rules, payment gateway support, and customer-facing billing notes.</p>
          </div>
        </div>
      <div className="plan-details">
        <div className="details-header">
          <div>
            <h2>Transaction Fees</h2>
            <p className="pm-section-copy">This section controls billing logic rather than the package structure itself.</p>
          </div>
        </div>
        <div className="pm-form-shell">
          <div className="pm-form-panel">
            <div className="pm-form-grid">
              <div>
                <label className="pm-field-label">Platform Fee Percent</label>
                <input
                  className="pm-input"
                  type="number"
                  step="0.1"
                  value={transactionFees.platform_fee_percent}
                  onChange={(e) =>
                    setTransactionFees((current) => ({
                      ...current,
                      platform_fee_percent: Number(e.target.value || 0),
                    }))
                  }
                />
              </div>
              <div>
                <label className="pm-field-label">Supported Gateways</label>
                <textarea
                  className="pm-input pm-textarea"
                  value={formatLines(transactionFees.supported_gateways)}
                  onChange={(e) =>
                    setTransactionFees((current) => ({
                      ...current,
                      supported_gateways: parseLines(e.target.value),
                    }))
                  }
                />
              </div>
            </div>
            <div>
              <label className="pm-field-label">Notes</label>
              <textarea
                className="pm-input pm-textarea pm-textarea-lg"
                value={formatLines(transactionFees.notes)}
                onChange={(e) =>
                  setTransactionFees((current) => ({
                    ...current,
                    notes: parseLines(e.target.value),
                  }))
                }
              />
            </div>
          </div>
        </div>
      </div>
      </section>

      <div className="pm-bottom-bar">
        <div>
          <strong>Unsaved changes</strong>
          <p>Review pricing, add-ons, bots, and gateway fees, then save the catalog.</p>
        </div>
        <div className="pm-bottom-actions">
          <button type="button" className="pm-secondary-btn" onClick={() => loadCatalog(country)} disabled={saving}>
            Discard Changes
          </button>
          <button type="button" className="edit-btn" onClick={saveCatalog} disabled={saving}>
            {saving ? "Saving..." : "Save Catalog"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PricingManagement;
