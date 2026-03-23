import React, { useState } from "react";
import { useCurrencyStore } from "../stores/useCurrencyStore";

const CurrencyConverter = ({ className = "" }) => {
    const {
        currency,
        exchangeRates,
        getAvailableCurrencies,
        formatAmount,
        convertAmount
    } = useCurrencyStore();

    const [amount, setAmount] = useState("");
    const [fromCurrency, setFromCurrency] = useState("USD");
    const [toCurrency, setToCurrency] = useState(currency);
    const [result, setResult] = useState(null);

    const currencies = getAvailableCurrencies ? getAvailableCurrencies() : [];

    const handleConvert = () => {
        const numAmount = parseFloat(amount);
        if (!numAmount || isNaN(numAmount)) {
            setResult(null);
            return;
        }

        const converted = convertAmount(numAmount, fromCurrency, toCurrency);
        setResult({
            original: numAmount,
            converted: converted,
            from: fromCurrency,
            to: toCurrency
        });
    };

    const handleSwap = () => {
        const temp = fromCurrency;
        setFromCurrency(toCurrency);
        setToCurrency(temp);
        setResult(null);
    };

    return (
        <div className={`currency-converter bg-slate-800/50 rounded-lg p-6 border border-slate-600/30 ${className}`}>
            <h3 className="text-lg font-semibold text-slate-200 mb-4">
                🔄 محول العملات
            </h3>

            <div className="space-y-4">
                {/* Amount Input */}
                <div>
                    <label className="block text-sm text-slate-300 mb-2">
                        المبلغ
                    </label>
                    <input
                        type="number"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                        placeholder="أدخل المبلغ"
                        className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/30 rounded-lg text-slate-200 placeholder-slate-400 focus:outline-none focus:border-blue-400"
                    />
                </div>

                {/* From Currency */}
                <div>
                    <label className="block text-sm text-slate-300 mb-2">
                        من العملة
                    </label>
                    <select
                        value={fromCurrency}
                        onChange={(e) => setFromCurrency(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/30 rounded-lg text-slate-200 focus:outline-none focus:border-blue-400"
                    >
                        {currencies.map((curr) => (
                            <option key={curr.code} value={curr.code}>
                                {curr.symbol} {curr.code} - {curr.name}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Swap Button */}
                <div className="flex justify-center">
                    <button
                        onClick={handleSwap}
                        className="px-4 py-2 bg-blue-500/20 text-blue-300 rounded-lg hover:bg-blue-500/30 transition-colors"
                        title="تبديل العملات"
                    >
                        ⇅ تبديل
                    </button>
                </div>

                {/* To Currency */}
                <div>
                    <label className="block text-sm text-slate-300 mb-2">
                        إلى العملة
                    </label>
                    <select
                        value={toCurrency}
                        onChange={(e) => setToCurrency(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/30 rounded-lg text-slate-200 focus:outline-none focus:border-blue-400"
                    >
                        {currencies.map((curr) => (
                            <option key={curr.code} value={curr.code}>
                                {curr.symbol} {curr.code} - {curr.name}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Convert Button */}
                <button
                    onClick={handleConvert}
                    disabled={!amount}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors"
                >
                    تحويل
                </button>

                {/* Result */}
                {result && (
                    <div className="mt-4 p-4 bg-slate-700/30 rounded-lg border border-slate-600/20">
                        <div className="text-sm text-slate-300 mb-2">النتيجة:</div>
                        <div className="text-lg font-semibold text-slate-200">
                            {formatAmount(result.original, result.from)} = {formatAmount(result.converted, result.to)}
                        </div>
                        <div className="text-xs text-slate-400 mt-1">
                            معدل التحويل: 1 {result.from} = {(result.converted / result.original).toFixed(4)} {result.to}
                        </div>
                    </div>
                )}

                {/* Exchange Rates Info */}
                <div className="mt-4 text-xs text-slate-400">
                    <div>آخر تحديث: {exchangeRates.lastUpdated ? new Date(exchangeRates.lastUpdated).toLocaleString('ar-SA') : 'غير محدث'}</div>
                    <div>المعدلات ثابتة للعرض التوضيحي - يمكن ربطها بـ API خارجي</div>
                </div>
            </div>
        </div>
    );
};

export default CurrencyConverter;