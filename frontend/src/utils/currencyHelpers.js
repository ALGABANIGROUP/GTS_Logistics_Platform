import { useCurrencyStore } from "../stores/useCurrencyStore";

/**
 * Format currency amount with the current currency
 * @param {number} amount - The amount to format
 * @param {object} options - Formatting options
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount, options = {}) => {
    const store = useCurrencyStore.getState();
    return store.formatAmount(amount, options);
};

/**
 * Get current currency symbol
 * @returns {string} Currency symbol
 */
export const getCurrencySymbol = () => {
    return useCurrencyStore.getState().currencySymbol;
};

/**
 * Get current currency code
 * @returns {string} Currency code (e.g., "CAD", "USD")
 */
export const getCurrency = () => {
    return useCurrencyStore.getState().currency;
};

/**
 * Convert amount between currencies
 * @param {number} amount - The amount to convert
 * @param {string} fromCurrency - Source currency code
 * @param {string} toCurrency - Target currency code
 * @returns {number} Converted amount
 */
export const convertAmount = (amount, fromCurrency, toCurrency) => {
    const store = useCurrencyStore.getState();
    return store.convertAmount(amount, fromCurrency, toCurrency);
};

/**
 * Convert amount to current currency
 * @param {number} amount - The amount to convert
 * @param {string} fromCurrency - Source currency code
 * @returns {number} Amount in current currency
 */
export const convertToCurrentCurrency = (amount, fromCurrency) => {
    const store = useCurrencyStore.getState();
    return store.convertToCurrentCurrency(amount, fromCurrency);
};

/**
 * Hook for using currency in React components
 */
export const useCurrency = () => {
    const {
        currency,
        currencySymbol,
        currencyName,
        formatAmount,
        setCurrency,
        convertAmount,
        convertToCurrentCurrency,
    } = useCurrencyStore();

    return {
        currency,
        symbol: currencySymbol,
        name: currencyName,
        format: formatAmount,
        setCurrency,
        convert: convertAmount,
        convertToCurrent: convertToCurrentCurrency,
    };
};
