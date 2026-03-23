import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FaArrowRight,
  FaChartLine,
  FaCheckCircle,
  FaCreditCard,
  FaExchangeAlt,
  FaFileInvoice,
  FaHistory,
  FaMoneyBillWave,
  FaRobot,
  FaShieldAlt,
  FaSpinner,
  FaSync,
  FaTimesCircle,
  FaWallet,
} from "react-icons/fa";
import paymentApi from "../../api/paymentApi";
import financeApi from "../../services/financeApi";

const tabs = [
  { id: "overview", label: "Overview", icon: FaChartLine },
  { id: "payments", label: "Payments", icon: FaCreditCard },
  { id: "invoices", label: "Invoices", icon: FaFileInvoice },
  { id: "bots", label: "Bot Integration", icon: FaRobot },
  { id: "security", label: "Security", icon: FaShieldAlt },
];

const botLinks = [
  {
    title: "AI Finance Bot",
    description: "Financial analysis, revenue tracking, and expense management.",
    icon: "💰",
    path: "/ai-bots/finance",
    color: "bg-purple-600 hover:bg-purple-700",
  },
  {
    title: "AI Freight Broker",
    description: "Shipment settlements and brokerage payment coordination.",
    icon: "🚛",
    path: "/ai-bots/freight_broker",
    color: "bg-blue-600 hover:bg-blue-700",
  },
  {
    title: "AI Sales Bot",
    description: "Invoice generation and revenue follow-up workflows.",
    icon: "💼",
    path: "/ai-bots/sales",
    color: "bg-green-600 hover:bg-green-700",
  },
  {
    title: "AI Marketing Manager",
    description: "Campaign spend visibility and marketing budget signals.",
    icon: "📢",
    path: "/admin/ai/marketing-bot",
    color: "bg-orange-600 hover:bg-orange-700",
  },
  {
    title: "AI General Manager",
    description: "Executive finance overview and business reporting.",
    icon: "👔",
    path: "/ai-bots/general-manager",
    color: "bg-slate-600 hover:bg-slate-700",
  },
  {
    title: "AI Legal Consultant",
    description: "Payment terms, agreements, and compliance review.",
    icon: "⚖️",
    path: "/ai-bots/legal",
    color: "bg-indigo-600 hover:bg-indigo-700",
  },
];

function formatCurrency(amount, currency = "USD") {
  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      minimumFractionDigits: 2,
    }).format(Number(amount || 0));
  } catch {
    return `${currency} ${Number(amount || 0).toFixed(2)}`;
  }
}

function normalizeStatus(status) {
  return String(status || "").toLowerCase();
}

export default function PaymentBotDashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [error, setError] = useState("");
  const [paymentStats, setPaymentStats] = useState(null);
  const [financeStats, setFinanceStats] = useState(null);
  const [invoices, setInvoices] = useState([]);

  const loadDashboardData = async ({ silent = false } = {}) => {
    if (silent) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      setError("");
      const [paymentSummary, financeSummary, invoiceResponse] = await Promise.all([
        paymentApi.getStats({ limit: 50, offset: 0 }),
        financeApi.getDashboardStats(),
        financeApi.getInvoices(),
      ]);

      setPaymentStats(paymentSummary);
      setFinanceStats(financeSummary);
      setInvoices(invoiceResponse.items || []);
    } catch (err) {
      console.error("Failed to load payment bot dashboard:", err);
      setError(err?.response?.data?.detail || err?.message || "Failed to load payment dashboard.");
      setPaymentStats(null);
      setFinanceStats(null);
      setInvoices([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const pendingInvoices = useMemo(
    () => invoices.filter((invoice) => ["pending", "sent", "overdue"].includes(normalizeStatus(invoice.status))),
    [invoices]
  );

  const paymentCurrency = useMemo(() => {
    const recent = paymentStats?.recent_payments || [];
    return recent[0]?.currency || "USD";
  }, [paymentStats]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100 dark:bg-gray-900">
        <div className="text-center">
          <FaSpinner className="mx-auto mb-4 animate-spin text-4xl text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">Loading payment dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 px-4 py-8 dark:bg-gray-900">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="mb-2 flex items-center gap-3">
              <FaMoneyBillWave className="text-4xl text-green-600" />
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Payment Gateway Dashboard</h1>
            </div>
            <p className="text-gray-600 dark:text-gray-400">
              Secure payment processing powered by <strong className="text-blue-600">SUDAPAY</strong> and integrated with{" "}
              <strong className="text-purple-600">AI Finance Bot</strong>.
            </p>
          </div>

          <button
            onClick={() => loadDashboardData({ silent: true })}
            className="inline-flex items-center gap-2 rounded-lg bg-slate-800 px-4 py-2 text-white transition hover:bg-slate-700"
          >
            <FaSync className={refreshing ? "animate-spin" : ""} />
            Refresh
          </button>
        </div>

        {error ? (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700 dark:border-red-900/40 dark:bg-red-900/20 dark:text-red-300">
            {error}
          </div>
        ) : null}

        <div className="mb-6 border-b border-gray-200 dark:border-gray-700">
          <nav className="flex flex-wrap gap-4">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 rounded-t-lg px-4 py-2 transition ${
                    activeTab === tab.id
                      ? "bg-blue-600 text-white"
                      : "text-gray-600 hover:bg-gray-200 dark:text-gray-400 dark:hover:bg-gray-800"
                  }`}
                >
                  <Icon className="text-sm" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {activeTab === "overview" && (
          <>
            <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800">
                <div className="mb-2 flex items-center justify-between">
                  <FaMoneyBillWave className="text-2xl text-green-500" />
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatCurrency(paymentStats?.total_amount || 0, paymentCurrency)}
                  </span>
                </div>
                <p className="text-gray-600 dark:text-gray-400">Total Processed</p>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-500">
                  {paymentStats?.total_payments || 0} transactions
                </p>
              </div>

              <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800">
                <div className="mb-2 flex items-center justify-between">
                  <FaChartLine className="text-2xl text-blue-500" />
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">
                    {paymentStats?.success_rate || 0}%
                  </span>
                </div>
                <p className="text-gray-600 dark:text-gray-400">Success Rate</p>
                <p className="mt-1 text-sm text-green-600">Live payment completion ratio</p>
              </div>

              <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800">
                <div className="mb-2 flex items-center justify-between">
                  <FaFileInvoice className="text-2xl text-orange-500" />
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">{pendingInvoices.length}</span>
                </div>
                <p className="text-gray-600 dark:text-gray-400">Pending Invoices</p>
                <button onClick={() => setActiveTab("invoices")} className="mt-1 text-sm text-blue-600 hover:text-blue-700">
                  View invoice queue →
                </button>
              </div>

              <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800">
                <div className="mb-2 flex items-center justify-between">
                  <FaShieldAlt className="text-2xl text-purple-500" />
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">PCI-DSS</span>
                </div>
                <p className="text-gray-600 dark:text-gray-400">Security Status</p>
                <p className="mt-1 text-sm text-green-600">Encrypted and gateway-tokenized</p>
              </div>
            </div>

            <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
              <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800">
                <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
                  <FaWallet className="mr-2 inline text-blue-500" />
                  Payment Methods
                </h3>
                <div className="space-y-3">
                  {(paymentStats?.payment_methods || []).map((method, idx) => (
                    <div
                      key={`${method.name}-${idx}`}
                      className="flex items-center justify-between rounded-lg bg-gray-50 p-3 dark:bg-gray-700"
                    >
                      <div className="flex items-center gap-3">
                        <FaCreditCard className="text-gray-500" />
                        <span className="text-gray-700 dark:text-gray-300">{method.name}</span>
                      </div>
                      <span className="text-sm text-gray-500 dark:text-gray-400">{method.usage_count} uses</span>
                    </div>
                  ))}
                  {!(paymentStats?.payment_methods || []).length && (
                    <p className="py-4 text-center text-gray-500 dark:text-gray-400">No payment method activity found.</p>
                  )}
                </div>
              </div>

              <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800">
                <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
                  <FaRobot className="mr-2 inline text-purple-500" />
                  AI Finance Bot Integration
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total Revenue</span>
                    <span className="font-semibold text-green-600">
                      {formatCurrency(financeStats?.total_revenue || 0, "USD")}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Pending Payments</span>
                    <span className="font-semibold text-orange-600">
                      {formatCurrency(financeStats?.pending_payments || 0, "USD")}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Last Sync</span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {financeStats?.last_sync ? new Date(financeStats.last_sync).toLocaleString() : "Just now"}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => navigate("/ai-bots/finance")}
                  className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-purple-600 py-2 text-white transition hover:bg-purple-700"
                >
                  <FaRobot />
                  Open Finance Bot
                </button>
              </div>
            </div>

            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800">
              <div className="mb-4 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  <FaHistory className="mr-2 inline text-blue-500" />
                  Recent Transactions
                </h3>
                <button onClick={() => navigate("/payments/history")} className="text-sm text-blue-600 hover:text-blue-700">
                  View All
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <th className="py-3 text-left text-gray-600 dark:text-gray-400">Date</th>
                      <th className="py-3 text-left text-gray-600 dark:text-gray-400">Amount</th>
                      <th className="py-3 text-left text-gray-600 dark:text-gray-400">Status</th>
                      <th className="py-3 text-left text-gray-600 dark:text-gray-400">Method</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(paymentStats?.recent_payments || []).map((payment) => {
                      const status = normalizeStatus(payment.status);
                      return (
                        <tr key={payment.id} className="border-b border-gray-100 dark:border-gray-700">
                          <td className="py-3 text-gray-700 dark:text-gray-300">
                            {payment.date ? new Date(payment.date).toLocaleDateString() : "N/A"}
                          </td>
                          <td className="py-3 font-medium text-gray-900 dark:text-white">
                            {formatCurrency(payment.amount, payment.currency || paymentCurrency)}
                          </td>
                          <td className="py-3">
                            <span
                              className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs ${
                                status === "completed"
                                  ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300"
                                  : status === "pending" || status === "processing"
                                    ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300"
                                    : "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300"
                              }`}
                            >
                              {status === "completed" && <FaCheckCircle className="text-xs" />}
                              {(status === "pending" || status === "processing") && (
                                <FaSpinner className="animate-spin text-xs" />
                              )}
                              {status !== "completed" && status !== "pending" && status !== "processing" && (
                                <FaTimesCircle className="text-xs" />
                              )}
                              {status || "unknown"}
                            </span>
                          </td>
                          <td className="py-3 text-gray-500 dark:text-gray-400">{payment.method}</td>
                        </tr>
                      );
                    })}
                    {!(paymentStats?.recent_payments || []).length && (
                      <tr>
                        <td colSpan="4" className="py-8 text-center text-gray-500 dark:text-gray-400">
                          No recent transactions
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {activeTab === "payments" && (
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800">
            <h2 className="mb-4 text-xl font-bold text-gray-900 dark:text-white">Payment Execution</h2>
            <p className="mb-6 text-gray-600 dark:text-gray-400">
              Payments are initiated from invoice-specific routes. Open a pending invoice below to continue to the secure
              payment screen.
            </p>
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              {pendingInvoices.slice(0, 6).map((invoice) => (
                <div
                  key={invoice.id}
                  className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900/40"
                >
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-semibold text-gray-900 dark:text-white">{invoice.number || `Invoice #${invoice.id}`}</span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">{invoice.status}</span>
                  </div>
                  <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
                    Amount: {formatCurrency(invoice.amount_usd || 0, "USD")}
                  </div>
                  <button
                    onClick={() => navigate(`/payments/${invoice.id}`)}
                    className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
                  >
                    <FaCreditCard />
                    Open Payment
                  </button>
                </div>
              ))}
            </div>
            {!pendingInvoices.length && (
              <div className="rounded-lg bg-gray-50 p-6 text-gray-500 dark:bg-gray-900/40 dark:text-gray-400">
                No pending invoices are ready for payment.
              </div>
            )}
          </div>
        )}

        {activeTab === "invoices" && (
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Invoice Queue</h2>
              <button
                onClick={() => navigate("/ai-bots/shippers/invoices")}
                className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
              >
                Open invoice workspace
                <FaArrowRight />
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="py-3 text-left text-gray-600 dark:text-gray-400">Invoice</th>
                    <th className="py-3 text-left text-gray-600 dark:text-gray-400">Date</th>
                    <th className="py-3 text-left text-gray-600 dark:text-gray-400">Amount</th>
                    <th className="py-3 text-left text-gray-600 dark:text-gray-400">Status</th>
                    <th className="py-3 text-left text-gray-600 dark:text-gray-400">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {invoices.slice(0, 12).map((invoice) => (
                    <tr key={invoice.id} className="border-b border-gray-100 dark:border-gray-700">
                      <td className="py-3 font-medium text-gray-900 dark:text-white">{invoice.number || `Invoice #${invoice.id}`}</td>
                      <td className="py-3 text-gray-600 dark:text-gray-400">{invoice.date || "N/A"}</td>
                      <td className="py-3 text-gray-900 dark:text-white">{formatCurrency(invoice.amount_usd || 0, "USD")}</td>
                      <td className="py-3 text-gray-600 capitalize dark:text-gray-400">{invoice.status}</td>
                      <td className="py-3">
                        {["pending", "sent", "overdue"].includes(normalizeStatus(invoice.status)) ? (
                          <button
                            onClick={() => navigate(`/payments/${invoice.id}`)}
                            className="inline-flex items-center gap-2 rounded-lg bg-orange-600 px-3 py-2 text-white transition hover:bg-orange-700"
                          >
                            <FaExchangeAlt />
                            Pay Now
                          </button>
                        ) : (
                          <span className="text-sm text-gray-500 dark:text-gray-400">No action needed</span>
                        )}
                      </td>
                    </tr>
                  ))}
                  {!invoices.length && (
                    <tr>
                      <td colSpan="5" className="py-8 text-center text-gray-500 dark:text-gray-400">
                        No invoices available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === "bots" && (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {botLinks.map((bot) => (
              <div
                key={bot.title}
                className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg transition hover:shadow-xl dark:border-gray-700 dark:bg-gray-800"
              >
                <div className="mb-4 text-4xl">{bot.icon}</div>
                <h3 className="mb-2 text-lg font-bold text-gray-900 dark:text-white">{bot.title}</h3>
                <p className="mb-4 text-sm text-gray-600 dark:text-gray-400">{bot.description}</p>
                <button
                  onClick={() => navigate(bot.path)}
                  className={`flex w-full items-center justify-center gap-2 rounded-lg py-2 text-white transition ${bot.color}`}
                >
                  Open
                  <FaArrowRight />
                </button>
              </div>
            ))}
          </div>
        )}

        {activeTab === "security" && (
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800">
            <h2 className="mb-4 text-xl font-bold text-gray-900 dark:text-white">Security Status</h2>
            <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-900/20">
                <FaCheckCircle className="mb-2 text-xl text-green-600" />
                <p className="font-semibold text-green-800 dark:text-green-300">PCI-oriented controls in place</p>
                <p className="text-sm text-green-700 dark:text-green-400">Gateway handling is tokenized and isolated.</p>
              </div>
              <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20">
                <FaShieldAlt className="mb-2 text-xl text-blue-600" />
                <p className="font-semibold text-blue-800 dark:text-blue-300">TLS-protected transport</p>
                <p className="text-sm text-blue-700 dark:text-blue-400">Payment traffic uses encrypted transport end to end.</p>
              </div>
            </div>

            <button
              onClick={() => navigate("/ai-bots/security_manager")}
              className="inline-flex items-center gap-2 rounded-lg bg-slate-700 px-4 py-2 text-white transition hover:bg-slate-600"
            >
              <FaShieldAlt />
              Open Security Manager
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
