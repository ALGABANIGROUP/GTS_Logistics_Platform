import axiosClient from "../api/axiosClient";

const LEGACY_INVOICES_API = "/api/v1/invoices";
const UNIFIED_FINANCE_API = "/api/v1/finance";

const normalizeInvoices = (data) => {
    const items = Array.isArray(data) ? data : data?.items || [];
    return items.map((invoice) => ({
        ...invoice,
        amount_usd: invoice?.amount_usd ?? invoice?.net_amount ?? invoice?.amount ?? 0,
    }));
};

const normalizeCollection = (data) => (Array.isArray(data) ? data : data?.items || []);

export const getInvoices = async () => {
    try {
        const response = await axiosClient.get(`${UNIFIED_FINANCE_API}/invoices`);
        const items = normalizeInvoices(response?.data);
        return {
            items,
            total: Number(response?.data?.total ?? items.length),
        };
    } catch {
        const response = await axiosClient.get(LEGACY_INVOICES_API);
        const items = normalizeInvoices(response?.data);
        return {
            items,
            total: items.length,
        };
    }
};

export const getExpenses = async () => {
    const response = await axiosClient.get(`${UNIFIED_FINANCE_API}/expenses`);
    const items = normalizeCollection(response?.data);
    return {
        items,
        total: Number(response?.data?.total ?? items.length),
    };
};

export const getPayments = async () => {
    const response = await axiosClient.get(`${UNIFIED_FINANCE_API}/payments`);
    const items = normalizeCollection(response?.data);
    return {
        items,
        total: Number(response?.data?.total ?? items.length),
    };
};

export const createInvoice = async (payload) => {
    const response = await axiosClient.post(`${UNIFIED_FINANCE_API}/invoices`, payload);
    return response?.data;
};

export const createExpense = async (payload) => {
    const response = await axiosClient.post(`${UNIFIED_FINANCE_API}/expenses`, payload);
    return response?.data;
};

export const createPayment = async (payload) => {
    const response = await axiosClient.post(`${UNIFIED_FINANCE_API}/payments`, payload);
    return response?.data;
};

export const bootstrapDemoData = async () => {
    const response = await axiosClient.post(`${UNIFIED_FINANCE_API}/bootstrap-demo`);
    return response?.data;
};

export const payInvoice = async (invoiceId, amount, gateway = "sudapay", extra = {}) => {
    return createPayment({
        payment_type: "invoice",
        invoice_id: invoiceId,
        amount,
        gateway,
        ...extra,
    });
};

export const payExpense = async (expenseId, amount, supplierName, gateway = "sudapay", extra = {}) => {
    return createPayment({
        payment_type: "expense",
        expense_id: expenseId,
        amount,
        gateway,
        supplier_name: supplierName,
        ...extra,
    });
};

export const getPendingInvoices = async (limit = 5) => {
    const response = await getInvoices();
    const items = response.items
        .filter((invoice) => ["pending", "sent", "overdue"].includes(String(invoice?.status || "").toLowerCase()))
        .slice(0, limit);

    return {
        items,
        total: items.length,
    };
};

export const updateInvoiceStatus = async (invoiceId, status) => {
    if (!invoiceId) return null;
    const response = await axiosClient.patch(`${LEGACY_INVOICES_API}/${invoiceId}`, { status });
    return response?.data;
};

export const markInvoicePaid = async (invoiceId) => updateInvoiceStatus(invoiceId, "paid");
export const markInvoiceOverdue = async (invoiceId) => updateInvoiceStatus(invoiceId, "overdue");

export const getDashboardStats = async () => {
    try {
        const response = await axiosClient.get(`${UNIFIED_FINANCE_API}/dashboard`);
        const metrics = response?.data?.metrics || {};
        const recentInvoices = normalizeInvoices(response?.data?.recent?.invoices);
        const recentExpenses = normalizeCollection(response?.data?.recent?.expenses);
        const totalRevenue = Number(metrics.total_revenue || 0);
        const totalExpenses = Number(metrics.total_expenses || 0);
        const netProfit = Number(metrics.net_profit || totalRevenue - totalExpenses || 0);

        return {
            total_invoices: Number(metrics.invoice_count || recentInvoices.length || 0),
            total_revenue: totalRevenue,
            total_expenses: totalExpenses,
            net_profit: netProfit,
            net_margin: totalRevenue > 0 ? Number(((netProfit / totalRevenue) * 100).toFixed(2)) : 0,
            pending_payments: Number(metrics.accounts_receivable || 0),
            paid_invoices: Number(metrics.payment_count || 0),
            pending_invoices: recentInvoices.filter((invoice) =>
                ["pending", "sent", "overdue", "draft"].includes(String(invoice?.status || "").toLowerCase())
            ).length,
            recent_invoices: recentInvoices,
            recent_expenses: recentExpenses,
            last_sync: new Date().toISOString(),
        };
    } catch {
        const response = await getInvoices();
        const items = response.items || [];
        const expenseResponse = await getExpenses().catch(() => ({ items: [] }));
        const expenses = expenseResponse.items || [];

        const pendingInvoices = items.filter((invoice) =>
            ["pending", "sent", "overdue"].includes(String(invoice?.status || "").toLowerCase())
        );
        const totalRevenue = items.reduce((sum, invoice) => sum + Number(invoice?.amount_usd || 0), 0);
        const totalExpenses = expenses.reduce((sum, expense) => sum + Number(expense?.amount || 0), 0);
        const netProfit = totalRevenue - totalExpenses;

        return {
            total_invoices: items.length,
            total_revenue: totalRevenue,
            total_expenses: totalExpenses,
            net_profit: netProfit,
            net_margin: totalRevenue > 0 ? Number(((netProfit / totalRevenue) * 100).toFixed(2)) : 0,
            pending_payments: pendingInvoices.reduce((sum, invoice) => sum + Number(invoice?.amount_usd || 0), 0),
            paid_invoices: items.filter((invoice) => String(invoice?.status || "").toLowerCase() === "paid").length,
            pending_invoices: pendingInvoices.length,
            recent_invoices: items.slice(0, 10),
            recent_expenses: expenses.slice(0, 10),
            last_sync: new Date().toISOString(),
        };
    }
};

export const getTrialBalance = async (asOfDate) => {
    const response = await axiosClient.get(`${UNIFIED_FINANCE_API}/ledger/trial-balance`, {
        params: { as_of_date: asOfDate },
    });
    return response?.data;
};

export const getIncomeStatement = async (startDate, endDate) => {
    const response = await axiosClient.get(`${UNIFIED_FINANCE_API}/ledger/income-statement`, {
        params: { start_date: startDate, end_date: endDate },
    });
    return response?.data;
};

export const getBalanceSheet = async (asOfDate) => {
    const response = await axiosClient.get(`${UNIFIED_FINANCE_API}/ledger/balance-sheet`, {
        params: { as_of_date: asOfDate },
    });
    return response?.data;
};

const financeApi = {
    getInvoices,
    getExpenses,
    getPayments,
    createInvoice,
    createExpense,
    createPayment,
    bootstrapDemoData,
    payInvoice,
    payExpense,
    getPendingInvoices,
    getDashboardStats,
    getTrialBalance,
    getIncomeStatement,
    getBalanceSheet,
    updateInvoiceStatus,
    markInvoicePaid,
    markInvoiceOverdue,
};

export default financeApi;
