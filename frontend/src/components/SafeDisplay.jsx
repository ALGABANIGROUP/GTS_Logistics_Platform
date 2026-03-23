/**
 * Safe Error Display Component
 * Frontend-safe error display component
 */

import React from "react";
import { AlertCircle, X } from "lucide-react";
import { normalizeError } from "../utils/dataFormatter";

/**
 * SafeErrorDisplay - safe error display
 * @param {Object} error - the error (any type)
 * @param {Function} onDismiss - callback when the error is dismissed
 * @param {boolean} critical - whether the error is critical
 */
export const SafeErrorDisplay = ({
    error,
    onDismiss,
    critical = false,
    className = "",
}) => {
    if (!error) return null;

    // Convert error to safe text message
    const message = normalizeError(error);

    return (
        <div
            className={`bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex gap-3 items-start ${className}`.trim()}
            role="alert"
        >
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />

            <div className="flex-1">
                <p className="text-red-200 text-sm">
                    {critical ? "⚠️ Critical error: " : ""}
                    {message}
                </p>
            </div>

            {onDismiss && (
                <button
                    onClick={onDismiss}
                    className="text-red-400 hover:text-red-300 flex-shrink-0"
                    aria-label="Close"
                >
                    <X className="w-4 h-4" />
                </button>
            )}
        </div>
    );
};

/**
 * SafeSuccessDisplay - Safe display for success messages
 */
export const SafeSuccessDisplay = ({ message, onDismiss, className = "" }) => {
    if (!message) return null;

    // Convert message to safe text
    const text = typeof message === "string" ? message : String(message);

    return (
        <div
            className={`bg-green-500/10 border border-green-500/30 rounded-lg p-4 flex gap-3 items-start ${className}`.trim()}
            role="status"
        >
            <div className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5">✓</div>

            <p className="text-green-200 text-sm flex-1">{text}</p>

            {onDismiss && (
                <button
                    onClick={onDismiss}
                    className="text-green-400 hover:text-green-300 flex-shrink-0"
                    aria-label="Close"
                >
                    <X className="w-4 h-4" />
                </button>
            )}
        </div>
    );
};

/**
 * SafeDataDisplay - safe data display
 */
export const SafeDataDisplay = ({ data, className = "" }) => {
    if (data === null || data === undefined) {
        return null;
    }

    // String or number: safe directly
    if (typeof data === "string" || typeof data === "number") {
        return <div className={className}>{data}</div>;
    }

    // boolean
    if (typeof data === "boolean") {
        return <div className={className}>{data ? "Yes" : "No"}</div>;
    }

    // Array
    if (Array.isArray(data)) {
        return (
            <ul className={`list-disc list-inside ${className}`.trim()}>
                {data.map((item, idx) => (
                    <li key={idx}>
                        <SafeDataDisplay data={item} />
                    </li>
                ))}
            </ul>
        );
    }

    // Object: do not render directly
    if (typeof data === "object") {
        // Development only
        if (process.env.NODE_ENV === "development") {
            try {
                return (
                    <pre className={`text-xs bg-slate-800/50 p-2 rounded ${className}`.trim()}>
                        {JSON.stringify(data, null, 2)}
                    </pre>
                );
            } catch {
                return <div className={className}>[Object]</div>;
            }
        }
        return null;
    }

    return <div className={className}>{String(data)}</div>;
};

export default {
    SafeErrorDisplay,
    SafeSuccessDisplay,
    SafeDataDisplay,
};
