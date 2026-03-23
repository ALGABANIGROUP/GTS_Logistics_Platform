import React from "react";
import { useCurrencyStore } from "../stores/useCurrencyStore";

const CurrencySwitcher = ({ className = "" }) => {
    const { currency, setCurrency, getAvailableCurrencies, currencySymbol, setCountry } =
        useCurrencyStore();

    const currencies = getAvailableCurrencies ? getAvailableCurrencies() : [];

    const handleReset = () => {
        setCurrency('CAD');
        setCountry('CA');
        window.location.reload();
    };

    return (
        <div className={`currency-switcher ${className}`}>
            <div className="flex items-center gap-2">
                <span className="text-sm text-slate-300">Currency:</span>
                <select
                    value={currency}
                    onChange={(e) => setCurrency(e.target.value)}
                    className="px-3 py-1.5 bg-slate-800/50 border border-slate-600/30 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-400 transition-colors"
                >
                    {currencies.map((curr) => (
                        <option key={curr.code} value={curr.code}>
                            {curr.symbol} {curr.code}
                        </option>
                    ))}
                </select>
                {currency !== 'CAD' && (
                    <button
                        onClick={handleReset}
                        className="px-2 py-1 text-xs bg-blue-500/20 text-blue-300 rounded hover:bg-blue-500/30 transition-colors"
                        title="Reset to CAD"
                    >
                        Reset
                    </button>
                )}
            </div>
        </div>
    );
};

export default CurrencySwitcher;
