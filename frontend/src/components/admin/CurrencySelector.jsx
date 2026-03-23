import React from "react";
import { useCurrencyStore } from "../../stores/useCurrencyStore";
import "./CurrencySelector.css";

const CurrencySelector = () => {
    const {
        currency,
        country,
        currencySymbol,
        currencyName,
        setCurrency,
        setCountry,
        getAvailableCurrencies,
    } = useCurrencyStore();

    const currencies = getAvailableCurrencies ? getAvailableCurrencies() : [];

    const handleCurrencyChange = (e) => {
        setCurrency(e.target.value);
    };

    const COUNTRIES = [
        { code: "CA", name: "Canada", flag: "🇨🇦" },
        { code: "US", name: "United States", flag: "🇺🇸" },
        { code: "GB", name: "United Kingdom", flag: "🇬🇧" },
        { code: "SA", name: "Saudi Arabia", flag: "🇸🇦" },
        { code: "AE", name: "United Arab Emirates", flag: "🇦🇪" },
        { code: "DE", name: "Germany", flag: "🇩🇪" },
        { code: "FR", name: "France", flag: "🇫🇷" },
        { code: "JP", name: "Japan", flag: "🇯🇵" },
        { code: "CN", name: "China", flag: "🇨🇳" },
    ];

    return (
        <div className="currency-selector">
            <div className="currency-selector-header">
                <h3>Regional Settings</h3>
                <p>Configure your preferred currency and region</p>
            </div>

            <div className="currency-selector-content">
                <div className="setting-group">
                    <label htmlFor="country-select">
                        <span className="label-icon">🌍</span>
                        Country/Region
                    </label>
                    <select
                        id="country-select"
                        value={country}
                        onChange={(e) => setCountry(e.target.value)}
                        className="setting-select"
                    >
                        {COUNTRIES.map((c) => (
                            <option key={c.code} value={c.code}>
                                {c.flag} {c.name}
                            </option>
                        ))}
                    </select>
                    <p className="setting-hint">Auto-sets currency based on your location</p>
                </div>

                <div className="setting-group">
                    <label htmlFor="currency-select">
                        <span className="label-icon">💰</span>
                        Currency
                    </label>
                    <select
                        id="currency-select"
                        value={currency}
                        onChange={handleCurrencyChange}
                        className="setting-select"
                    >
                        {currencies.map((curr) => (
                            <option key={curr.code} value={curr.code}>
                                {curr.symbol} {curr.code} - {curr.name}
                            </option>
                        ))}
                    </select>
                    <p className="setting-hint">
                        All prices and amounts will be displayed in this currency
                    </p>
                </div>

                <div className="currency-preview">
                    <div className="preview-label">Preview:</div>
                    <div className="preview-amount">
                        <span className="preview-symbol">{currencySymbol}</span>
                        <span className="preview-value">1,234.56</span>
                        <span className="preview-code">{currency}</span>
                    </div>
                    <div className="preview-description">{currencyName}</div>
                </div>
            </div>
        </div>
    );
};

export default CurrencySelector;
