import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getPlans, getPolicyContext } from "../services/billingApi";
import { useCurrencyStore } from "../stores/useCurrencyStore";

const sectionTitles = {
  automation: "Automation",
  analytics: "Analytics",
  integrations: "Integrations",
};

const Pricing = () => {
  const [plans, setPlans] = useState([]);
  const [addons, setAddons] = useState([]);
  const [vehiclePricing, setVehiclePricing] = useState([]);
  const [userPricing, setUserPricing] = useState([]);
  const [botPricing, setBotPricing] = useState([]);
  const [botBundle, setBotBundle] = useState(null);
  const [extraServices, setExtraServices] = useState({});
  const [transactionFees, setTransactionFees] = useState({});
  const [country, setCountry] = useState("GLOBAL");
  const { currency, setCountry: setStoreCountry, setCurrency } = useCurrencyStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    let active = true;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const context = await getPolicyContext();
        const region = context?.country || context?.region || "GLOBAL";
        const currencyCode = context?.currency || "USD";
        if (!active) return;

        setCountry(region);
        if (currencyCode) {
          setCurrency(currencyCode);
        } else if (region && region.length === 2) {
          setStoreCountry(region.toUpperCase());
        }

        const plansResponse = await getPlans(region);
        if (!active) return;

        setPlans(plansResponse?.plans || []);
        setAddons(plansResponse?.addons || []);
        setVehiclePricing(plansResponse?.vehicle_pricing || []);
        setUserPricing(plansResponse?.user_pricing || []);
        setBotPricing(plansResponse?.bot_pricing || []);
        setBotBundle(plansResponse?.bot_bundle || null);
        setExtraServices(plansResponse?.extra_services || {});
        setTransactionFees(plansResponse?.transaction_fees || {});
      } catch (err) {
        if (!active) return;
        setError(
          err?.response?.data?.detail?.message ||
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to load pricing."
        );
      } finally {
        if (active) setLoading(false);
      }
    };

    load();
    return () => {
      active = false;
    };
  }, [setCurrency, setStoreCountry]);

  const serviceGroups = useMemo(
    () => Object.entries(extraServices || {}).filter(([, items]) => Array.isArray(items) && items.length > 0),
    [extraServices]
  );

  const handleUpgrade = () => {
    navigate("/account");
  };

  const formatLimit = (value) => {
    if (value === -1) return "Unlimited";
    if (value === null || value === undefined) return null;
    return value;
  };

  const formatPrice = (item) => {
    const suffix = item?.unit ? ` / ${item.unit}` : "";
    return `${item.price_amount} ${item.currency}${suffix}`;
  };

  const renderPricingTable = (title, firstColumn, items) => {
    if (!items?.length) return null;
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <h3 className="text-base font-semibold text-slate-800">{title}</h3>
        <div className="mt-3 overflow-x-auto">
          <table className="min-w-full text-sm text-slate-600">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500">
                <th className="py-2 pr-4 font-semibold">{firstColumn}</th>
                <th className="py-2 font-semibold">Price</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.code} className="border-b border-slate-100 last:border-0">
                  <td className="py-2 pr-4">{item.name}</td>
                  <td className="py-2">{formatPrice(item)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <p className="text-gray-500">Loading pricing...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <p className="text-sm text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">GTS Logistics Platform Pricing</h1>
        <p className="text-sm text-slate-500">
          Subscription packages and add-ons for {country} ({currency}).
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {plans.map((plan) => {
          const isFree = Boolean(plan?.is_free) || plan?.code === "FREE";
          return (
            <div
              key={plan.code}
              className={`rounded-xl border p-4 shadow-sm ${
                isFree ? "border-emerald-200 bg-emerald-50" : "border-slate-200 bg-white"
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-slate-800">{plan.name}</h2>
                  <p className="text-xs text-slate-500">{plan.description}</p>
                </div>
                {isFree ? (
                  <span className="rounded-full bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-700">
                    Free
                  </span>
                ) : null}
              </div>

              <div className="mt-4 text-2xl font-bold text-slate-800">
                {isFree ? "0" : plan.price_amount} {plan.currency}
                <span className="text-sm font-normal text-slate-400"> / month</span>
              </div>

              {plan.suitable_for?.length ? (
                <div className="mt-2 text-xs text-slate-500">
                  <p className="font-semibold text-slate-600">Best for</p>
                  <ul className="mt-1 space-y-1">
                    {plan.suitable_for.map((item) => (
                      <li key={item}>- {item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              <div className="mt-2 text-xs text-slate-500">
                {formatLimit(plan.limits?.vehicles) !== null ? (
                  <p>Vehicles: {formatLimit(plan.limits?.vehicles)}</p>
                ) : null}
                {formatLimit(plan.limits?.users) !== null ? (
                  <p>Users: {formatLimit(plan.limits?.users)}</p>
                ) : null}
              </div>

              <ul className="mt-4 space-y-1 text-sm text-slate-600">
                {(plan.highlights || plan.features || []).map((feature) => (
                  <li key={feature}>- {feature}</li>
                ))}
              </ul>

              <button
                onClick={handleUpgrade}
                className={`mt-4 w-full rounded-lg px-3 py-2 text-sm font-semibold ${
                  isFree
                    ? "bg-emerald-200 text-emerald-900 hover:bg-emerald-300"
                    : "bg-slate-900 text-white hover:bg-slate-800"
                }`}
              >
                {isFree ? "Upgrade" : "Select Plan"}
              </button>
            </div>
          );
        })}
      </div>

      {renderPricingTable("Additional Vehicle Pricing", "Number of Vehicles", vehiclePricing)}
      {renderPricingTable("Additional User Pricing", "Type", userPricing)}

      {addons.length > 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <h3 className="text-base font-semibold text-slate-800">Catalog Add-ons</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {addons.map((addon) => (
              <span
                key={addon.code}
                className="rounded-full border border-slate-200 px-3 py-1 text-xs font-medium text-slate-700"
              >
                {addon.name}
                {addon.price_amount !== undefined ? ` - ${formatPrice(addon)}` : ""}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {botPricing.length > 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <h3 className="text-base font-semibold text-slate-800">AI Bots Pricing</h3>
          <div className="mt-3 overflow-x-auto">
            <table className="min-w-full text-sm text-slate-600">
              <thead>
                <tr className="border-b border-slate-200 text-left text-slate-500">
                  <th className="py-2 pr-4 font-semibold">Bot</th>
                  <th className="py-2 font-semibold">Monthly Price</th>
                </tr>
              </thead>
              <tbody>
                {botPricing.map((bot) => (
                  <tr key={bot.code} className="border-b border-slate-100 last:border-0">
                    <td className="py-2 pr-4">{bot.name}</td>
                    <td className="py-2">{formatPrice(bot)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {botBundle ? (
            <p className="mt-3 text-sm font-semibold text-slate-700">
              {botBundle.name}: {formatPrice(botBundle)}
            </p>
          ) : null}
        </div>
      ) : null}

      {serviceGroups.length > 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <h3 className="text-base font-semibold text-slate-800">Additional Services</h3>
          <div className="mt-4 grid gap-4 lg:grid-cols-3">
            {serviceGroups.map(([group, items]) => (
              <div key={group}>
                <h4 className="text-sm font-semibold text-slate-700">
                  {sectionTitles[group] || group.replace(/_/g, " ")}
                </h4>
                <div className="mt-2 overflow-x-auto">
                  <table className="min-w-full text-sm text-slate-600">
                    <tbody>
                      {items.map((item) => (
                        <tr key={item.code} className="border-b border-slate-100 last:border-0">
                          <td className="py-2 pr-4">{item.name}</td>
                          <td className="py-2">{formatPrice(item)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {transactionFees?.platform_fee_percent ? (
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <h3 className="text-base font-semibold text-slate-800">Transaction Fees</h3>
          <p className="mt-2 text-sm text-slate-600">
            Platform Fee: {transactionFees.platform_fee_percent}% per transaction.
          </p>
          {transactionFees.supported_gateways?.length ? (
            <p className="mt-2 text-sm text-slate-600">
              Payment gateways: {transactionFees.supported_gateways.join(", ")}.
            </p>
          ) : null}
          {transactionFees.notes?.map((note) => (
            <p key={note} className="mt-1 text-sm text-slate-500">
              {note}
            </p>
          ))}
        </div>
      ) : null}
    </div>
  );
};

export default Pricing;
