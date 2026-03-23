// Shared finance panel constants
const truthy = (value) => {
    if (value === undefined || value === null) return false;
    const normalized = value.toString().trim().toLowerCase();
    return ["1", "true", "yes", "on"].includes(normalized);
};

const zeroModeEnv = import.meta.env.VITE_FINANCE_ZERO_MODE;
export const FINANCE_ZERO_MODE =
    zeroModeEnv === undefined || zeroModeEnv === null
        ? true
        : truthy(zeroModeEnv);
export const FINANCE_API_BASE = import.meta.env.VITE_FINANCE_API_BASE || "/api/v1/finance";

export const ZERO_DATA = {
    metrics: {
        totalRevenue: 0,
        totalExpenses: 0,
        netProfit: 0,
        taxObligation: 0,
        accountsReceivable: 0,
        accountsPayable: 0,
        cashFlow: 0,
        grossMargin: 0,
    },
    arrays: [],
    booleans: false,
};
