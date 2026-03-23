import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useCurrencyStore } from "../stores/useCurrencyStore";
import {
  FaArrowRight,
  FaCheckCircle,
  FaClock,
  FaCopy,
  FaCreditCard,
  FaExclamationTriangle,
  FaLock,
  FaRobot,
  FaShieldAlt,
  FaSpinner,
} from "react-icons/fa";
import paymentApi from "../../api/paymentApi";

const relatedBots = [
  { name: "AI Security Manager", role: "Fraud monitoring and gateway protection" },
  { name: "AI Finance Bot", role: "Transaction reporting and revenue visibility" },
  { name: "AI Operations Manager", role: "Operational status and exception handling" },
  { name: "AI General Manager", role: "Executive reporting and oversight" },
  { name: "AI Freight Broker", role: "Shipment payment coordination" },
  { name: "AI Sales Bot", role: "Invoice follow-up and revenue workflows" },
  { name: "AI Legal Consultant", role: "Payment terms and compliance review" },
  { name: "AI System Manager", role: "System health and audit traceability" },
];

function toDisplayString(value, fallback = "Unavailable") {
  if (value == null) return fallback;
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (Array.isArray(value)) {
    return value.map((item) => toDisplayString(item, "")).filter(Boolean).join(", ") || fallback;
  }
  if (typeof value === "object") {
    if ("label" in value && value.label != null) return String(value.label);
    if ("message" in value && value.message != null) return String(value.message);
    if ("detail" in value && value.detail != null) return toDisplayString(value.detail, fallback);
    try {
      return JSON.stringify(value);
    } catch {
      return fallback;
    }
  }
  return fallback;
}

function toErrorMessage(error) {
  const detail = error?.response?.data?.detail;
  if (detail != null) return toDisplayString(detail, "Payment link is invalid or unavailable.");
  const message = error?.message;
  if (message != null) return toDisplayString(message, "Payment link is invalid or unavailable.");
  return "Payment link is invalid or unavailable.";
}

function formatAmount(amount, currency = "USD") {
  try {
    const currentCurrency = currency || useCurrencyStore.getState().currency;
    const locale = useCurrencyStore.getState().currencyLocale;

    return new Intl.NumberFormat(locale, {
      style: "currency",
      currency: currentCurrency,
      minimumFractionDigits: 2,
    }).format(Number(amount || 0));
  } catch {
    return `${currency} ${Number(amount || 0).toFixed(2)}`;
  }
}

function getStatusMeta(status) {
  switch (String(status || "").toLowerCase()) {
    case "completed":
      return {
        label: "Completed",
        icon: <FaCheckCircle className="text-green-600" />,
        badge: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
      };
    case "pending":
    case "processing":
      return {
        label: "Pending",
        icon: <FaClock className="text-amber-600" />,
        badge: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
      };
    default:
      return {
        label: "Attention Required",
        icon: <FaExclamationTriangle className="text-red-600" />,
        badge: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
      };
  }
}

export default function PaymentLinkPage() {
  const { paymentId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [payment, setPayment] = useState(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let active = true;

    const loadPayment = async () => {
      try {
        setLoading(true);
        setError("");
        const response = await paymentApi.get(paymentId);
        if (!active) return;
        setPayment(response);
      } catch (err) {
        if (!active) return;
        setError(toErrorMessage(err));
        setPayment(null);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    if (paymentId) {
      loadPayment();
    } else {
      setLoading(false);
      setError("Missing payment identifier.");
    }

    return () => {
      active = false;
    };
  }, [paymentId]);

  const statusMeta = useMemo(() => getStatusMeta(payment?.status), [payment?.status]);
  const secureLink = typeof window !== "undefined" ? window.location.href : `/pay/${paymentId}`;

  const handleContinue = () => {
    if (!payment?.invoice_id) {
      return;
    }
    navigate(`/payments/${payment.invoice_id}`);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(secureLink);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      setCopied(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4 dark:bg-slate-950">
        <div className="text-center">
          <FaSpinner className="mx-auto mb-4 animate-spin text-4xl text-blue-600" />
          <p className="text-slate-600 dark:text-slate-300">Loading secure payment link...</p>
        </div>
      </div>
    );
  }

  if (!payment) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4 dark:bg-slate-950">
        <div className="w-full max-w-lg rounded-3xl border border-red-200 bg-white p-8 text-center shadow-xl dark:border-red-900/40 dark:bg-slate-900">
          <div className="mb-4 text-5xl text-red-500">!</div>
          <h1 className="mb-2 text-2xl font-bold text-slate-900 dark:text-white">Payment Link Unavailable</h1>
          <p className="mb-6 text-slate-600 dark:text-slate-300">{error || "This payment link could not be loaded."}</p>
          <button
            onClick={() => navigate("/")}
            className="rounded-xl bg-slate-900 px-5 py-3 text-white transition hover:bg-slate-800 dark:bg-blue-600 dark:hover:bg-blue-500"
          >
            Return to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-white to-slate-200 px-4 py-10 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-emerald-100 px-4 py-2 text-sm font-medium text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300">
              <FaShieldAlt />
              Secured by GTS Unified Payment Layer
            </div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Secure Payment Link</h1>
            <p className="mt-2 text-slate-600 dark:text-slate-300">
              Unified payment entry for finance, operations, security, and audit-integrated checkout.
            </p>
          </div>

          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            <FaCopy />
            {copied ? "Link Copied" : "Copy Link"}
          </button>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xl dark:border-slate-800 dark:bg-slate-900">
              <div className="mb-6 flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-6 dark:border-slate-800">
                <div>
                  <div className="text-sm uppercase tracking-wide text-slate-500 dark:text-slate-400">Payment Reference</div>
                  <div className="mt-1 text-xl font-semibold text-slate-900 dark:text-white">
                    {toDisplayString(payment.reference_id, `Payment #${toDisplayString(payment.id, paymentId)}`)}
                  </div>
                </div>
                <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium ${statusMeta.badge}`}>
                  {statusMeta.icon}
                  {statusMeta.label}
                </span>
              </div>

              <div className="mb-6 rounded-2xl bg-slate-50 p-5 dark:bg-slate-950/60">
                <div className="text-sm text-slate-500 dark:text-slate-400">Amount Due</div>
                <div className="mt-2 text-4xl font-bold text-slate-900 dark:text-white">
                  {formatAmount(payment.amount, payment.currency)}
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
                  <div className="text-sm text-slate-500 dark:text-slate-400">Invoice</div>
                  <div className="mt-1 font-medium text-slate-900 dark:text-white">
                    {payment.invoice_id ? `#${toDisplayString(payment.invoice_id)}` : "Not linked"}
                  </div>
                </div>
                <div className="rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
                  <div className="text-sm text-slate-500 dark:text-slate-400">Gateway</div>
                  <div className="mt-1 font-medium text-slate-900 dark:text-white">
                    {toDisplayString(paymentApi.getGatewayName(toDisplayString(payment.payment_gateway, "sudapay")))}
                  </div>
                </div>
                <div className="rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
                  <div className="text-sm text-slate-500 dark:text-slate-400">Created</div>
                  <div className="mt-1 font-medium text-slate-900 dark:text-white">
                    {payment.created_at ? new Date(payment.created_at).toLocaleString() : "Unavailable"}
                  </div>
                </div>
                <div className="rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
                  <div className="text-sm text-slate-500 dark:text-slate-400">Transaction</div>
                  <div className="mt-1 break-all font-medium text-slate-900 dark:text-white">
                    {toDisplayString(payment.gateway_transaction_id, "Will be assigned after checkout")}
                  </div>
                </div>
              </div>

              <div className="mt-8 flex flex-wrap gap-3">
                <button
                  onClick={handleContinue}
                  disabled={!payment.invoice_id}
                  className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <FaLock />
                  Continue to Secure Checkout
                  <FaArrowRight />
                </button>
                <button
                  onClick={() => navigate("/ai-bots/payment")}
                  className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-5 py-3 font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
                >
                  <FaRobot />
                  Open Payment Dashboard
                </button>
              </div>
            </div>

            <div className="mt-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-xl dark:border-slate-800 dark:bg-slate-900">
              <h2 className="mb-4 text-xl font-semibold text-slate-900 dark:text-white">Integrated Bot Oversight</h2>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {relatedBots.map((bot) => (
                  <div key={bot.name} className="rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
                    <div className="font-medium text-slate-900 dark:text-white">{bot.name}</div>
                    <div className="mt-1 text-sm text-slate-600 dark:text-slate-300">{bot.role}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xl dark:border-slate-800 dark:bg-slate-900">
              <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
                <FaShieldAlt className="text-emerald-600" />
                Security Controls
              </h2>
              <ul className="space-y-3 text-sm text-slate-600 dark:text-slate-300">
                <li className="flex items-start gap-2">
                  <FaCheckCircle className="mt-1 text-emerald-600" />
                  TLS-encrypted transport and gateway-tokenized payment flow
                </li>
                <li className="flex items-start gap-2">
                  <FaCheckCircle className="mt-1 text-emerald-600" />
                  SUDAPAY-first routing with existing payment API controls
                </li>
                <li className="flex items-start gap-2">
                  <FaCheckCircle className="mt-1 text-emerald-600" />
                  Audit visibility for finance, security, operations, and system bots
                </li>
                <li className="flex items-start gap-2">
                  <FaCheckCircle className="mt-1 text-emerald-600" />
                  Existing webhook and payment confirmation pipeline preserved
                </li>
              </ul>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xl dark:border-slate-800 dark:bg-slate-900">
              <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
                <FaCreditCard className="text-blue-600" />
                Gateway Strategy
              </h2>
              <div className="space-y-3 text-sm text-slate-600 dark:text-slate-300">
                <div className="rounded-2xl bg-slate-50 p-3 dark:bg-slate-950/60">
                  <div className="font-medium text-slate-900 dark:text-white">Primary</div>
                  <div>SUDAPAY</div>
                </div>
                <div className="rounded-2xl bg-slate-50 p-3 dark:bg-slate-950/60">
                  <div className="font-medium text-slate-900 dark:text-white">Additional labels</div>
                  <div>Stripe and PayPal remain represented in the unified dashboard and API naming.</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
