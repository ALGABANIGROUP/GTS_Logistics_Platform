import React from "react";
import { useCurrency } from "../utils/currencyHelpers";

const CurrencyDisplay = ({ amount, showCode = false, className = "" }) => {
    const { format, symbol, currency } = useCurrency();

    if (amount === null || amount === undefined) {
        return <span className={className}>-</span>;
    }

    return (
        <span className={`currency-display ${className}`}>
            {format(amount)}
            {showCode && ` ${currency}`}
        </span>
    );
};

export default CurrencyDisplay;
