import { create } from "zustand";
import { persist } from "zustand/middleware";

// Currency configuration
const CURRENCIES = {
    CAD: { symbol: "$", name: "Canadian Dollar", locale: "en-CA" },
    USD: { symbol: "$", name: "US Dollar", locale: "en-US" },
    EUR: { symbol: "€", name: "Euro", locale: "en-EU" },
    GBP: { symbol: "£", name: "British Pound", locale: "en-GB" },
    SAR: { symbol: "SAR", name: "Saudi Riyal", locale: "ar-SA" },
    AED: { symbol: "AED", name: "UAE Dirham", locale: "ar-AE" },
    JPY: { symbol: "¥", name: "Japanese Yen", locale: "ja-JP" },
    CNY: { symbol: "¥", name: "Chinese Yuan", locale: "zh-CN" },
};

// Country to currency mapping
const COUNTRY_CURRENCY_MAP = {
    CA: "CAD",
    US: "USD",
    GB: "GBP",
    SA: "SAR",
    AE: "AED",
    JP: "JPY",
    CN: "CNY",
    // EU countries
    DE: "EUR",
    FR: "EUR",
    IT: "EUR",
    ES: "EUR",
    NL: "EUR",
};

// Detect user's location and set currency from user data
const detectCurrencyFromUserLocation = (userCountry) => {
    if (userCountry && COUNTRY_CURRENCY_MAP[userCountry]) {
        return COUNTRY_CURRENCY_MAP[userCountry];
    }
    // Fallback to default
    return "CAD";
};

// Detect user's location and set currency from browser
const detectCurrencyFromBrowserLocale = async () => {
    try {
        // Try to detect from browser locale first
        const locale = navigator.language || navigator.userLanguage;
        const countryCode = locale.split("-")[1];

        if (countryCode && COUNTRY_CURRENCY_MAP[countryCode]) {
            return COUNTRY_CURRENCY_MAP[countryCode];
        }

        // Fallback: Try IP-based geolocation (optional - requires external service)
        // For now, just return default
        return "CAD";
    } catch (error) {
        console.warn("Failed to detect currency from location:", error);
        return "CAD";
    }
};

export const useCurrencyStore = create(
    persist(
        (set, get) => ({
            // State
            currency: "CAD",
            country: "CA",
            exchangeRates: {},
            lastUpdated: null,

            // Computed values
            get currencySymbol() {
                return CURRENCIES[get().currency]?.symbol || "$";
            },

            get currencyName() {
                return CURRENCIES[get().currency]?.name || "Canadian Dollar";
            },

            get currencyLocale() {
                return CURRENCIES[get().currency]?.locale || "en-CA";
            },

            // Actions
            setCurrency: (currency) => {
                if (CURRENCIES[currency]) {
                    set({ currency });
                    // Dispatch event for other components to listen
                    window.dispatchEvent(
                        new CustomEvent("currencyChanged", { detail: { currency } })
                    );
                }
            },

            setCountry: (country) => {
                set({ country });
                // Auto-set currency based on country
                if (COUNTRY_CURRENCY_MAP[country]) {
                    get().setCurrency(COUNTRY_CURRENCY_MAP[country]);
                }
            },

            // Initialize currency based on user location (from user data)
            initializeCurrencyFromUser: async (userCountry) => {
                const detectedCurrency = detectCurrencyFromUserLocation(userCountry);
                get().setCurrency(detectedCurrency);
                set({ country: userCountry || "CA" });
            },

            // Initialize currency based on browser locale
            initializeCurrency: async () => {
                const detectedCurrency = await detectCurrencyFromBrowserLocale();
                get().setCurrency(detectedCurrency);
            },

            // Format amount with current currency
            formatAmount: (amount, options = {}) => {
                const {
                    showSymbol = true,
                    decimals = 2,
                    locale = get().currencyLocale,
                } = options;

                const formattedAmount = new Intl.NumberFormat(locale, {
                    style: showSymbol ? "currency" : "decimal",
                    currency: get().currency,
                    minimumFractionDigits: decimals,
                    maximumFractionDigits: decimals,
                }).format(amount);

                return formattedAmount;
            },

            // Alias for formatAmount (for backward compatibility)
            formatCurrency: (amount, options = {}) => {
                return get().formatAmount(amount, options);
            },

            // Convert amount between currencies
            convertAmount: (amount, fromCurrency, toCurrency) => {
                if (!amount || fromCurrency === toCurrency) {
                    return amount;
                }

                const rates = get().exchangeRates;
                if (!rates[fromCurrency] || !rates[toCurrency]) {
                    console.warn(`Exchange rate not available for ${fromCurrency} to ${toCurrency}`);
                    return amount; // Return original amount if no rate available
                }

                // Convert to USD first, then to target currency
                const usdAmount = amount / rates[fromCurrency];
                const convertedAmount = usdAmount * rates[toCurrency];

                return convertedAmount;
            },

            // Convert amount to current currency
            convertToCurrentCurrency: (amount, fromCurrency) => {
                const currentCurrency = get().currency;
                return get().convertAmount(amount, fromCurrency, currentCurrency);
            },

            // Get available currencies list
            getAvailableCurrencies: () => {
                return Object.keys(CURRENCIES).map((code) => ({
                    code,
                    symbol: CURRENCIES[code].symbol,
                    name: CURRENCIES[code].name,
                    locale: CURRENCIES[code].locale,
                }));
            },

            fetchExchangeRates: async () => {
                try {
                    // Example: You can integrate with an exchange rate API here
                    // For now, using static rates (1 USD = base)
                    set({
                        exchangeRates: {
                            CAD: 1.35,
                            USD: 1.0,
                            EUR: 0.92,
                            GBP: 0.79,
                            SAR: 3.75,
                            AED: 3.67,
                            JPY: 148.5,
                            CNY: 7.24,
                        },
                        lastUpdated: new Date().toISOString(),
                    });
                } catch (error) {
                    console.error("Failed to fetch exchange rates:", error);
                }
            },
        }),
        {
            name: "gts-currency-storage",
            partialize: (state) => ({
                currency: state.currency,
                country: state.country,
                exchangeRates: state.exchangeRates,
                lastUpdated: state.lastUpdated,
            }),
        }
    )
);
