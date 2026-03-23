/**
 * Enhanced Error Boundary - Error handling container
 * Handles React errors and converts them to safe messages
 */

import React from "react";
import { AlertTriangle, RefreshCw, Bug } from "lucide-react";
import { normalizeError } from "../utils/dataFormatter";

class EnhancedErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
            errorCount: 0,
            isCritical: false,
        };

        this.handleRetry = this.handleRetry.bind(this);
        this.handleReset = this.handleReset.bind(this);
    }

    static getDerivedStateFromError(error) {
        return {
            hasError: true,
            error,
            errorCount: (prev) => (prev || 0) + 1,
        };
    }

    componentDidCatch(error, errorInfo) {
        const errorCount = this.state.errorCount || 1;
        const isCritical = errorCount > 3; // After 3 consecutive errors, treat as critical

        // Log to console in development
        if (process.env.NODE_ENV === "development") {
            console.error("🔴 ErrorBoundary caught:", error);
            console.error("📍 Component Stack:", errorInfo?.componentStack);
        }

        // Normalize the error message
        const normalizedMessage = normalizeError(error);

        this.setState({
            errorInfo,
            isCritical,
        });

        // Optional: Send to error tracking service (Sentry)
        if (typeof window !== "undefined" && window.Sentry) {
            window.Sentry.captureException(error, {
                contexts: {
                    react: {
                        componentStack: errorInfo?.componentStack,
                        critical: isCritical,
                    },
                },
            });
        }
    }

    handleRetry() {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null,
        });
    }

    handleReset() {
        // Reload page
        window.location.href = "/";
    }

    render() {
        if (this.state.hasError) {
            const { error, errorInfo, isCritical } = this.state;
            const errorMessage = normalizeError(error);

            return (
                <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
                    <div className="glass-card p-8 max-w-lg w-full mx-auto text-center border border-red-500/20">
                        {/* Icon */}
                        <div className="flex justify-center mb-6">
                            {isCritical ? (
                                <Bug className="w-16 h-16 text-red-500 animate-pulse" />
                            ) : (
                                <AlertTriangle className="w-16 h-16 text-red-400" />
                            )}
                        </div>

                        {/* Title */}
                        <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">
                            {isCritical ? "⚠️ Critical Error" : "❌ An Error Occurred"}
                        </h1>

                        {/* Message */}
                        <p className="text-slate-300 mb-2 text-sm md:text-base">
                            {isCritical
                                ? "It appears there is a recurring issue. Please reload the page."
                                : "An unexpected error occurred in the application."}
                        </p>

                        {/* Normalized Error */}
                        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6 text-left">
                            <p className="text-red-200 text-sm font-mono break-words">
                                {errorMessage}
                            </p>
                        </div>

                        {/* Actions */}
                        <div className="space-y-3 mb-6">
                            {!isCritical && (
                                <button
                                    onClick={this.handleRetry}
                                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 border border-blue-400/30 rounded-lg transition-colors font-medium"
                                >
                                    <RefreshCw className="w-4 h-4" />
                                    Retry
                                </button>
                            )}

                            <button
                                onClick={this.handleReset}
                                className="w-full px-4 py-2 bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 rounded-lg transition-colors font-medium"
                            >
                                {isCritical ? "Reload page" : "Back to home"}
                            </button>
                        </div>

                        {/* Development Info */}
                        {process.env.NODE_ENV === "development" && (
                            <details className="text-left">
                                <summary className="text-slate-400 cursor-pointer hover:text-slate-300 text-sm font-medium">
                                    🐛 Developer Details
                                </summary>

                                {/* Error Details */}
                                <div className="mt-4 space-y-4">
                                    <div>
                                        <h3 className="text-xs font-bold text-red-400 mb-2 uppercase">
                                            Error Message:
                                        </h3>
                                        <pre className="bg-slate-800/50 p-3 rounded text-xs text-red-300 overflow-auto max-h-32 border border-slate-700">
                                            {error?.toString()}
                                        </pre>
                                    </div>

                                    <div>
                                        <h3 className="text-xs font-bold text-blue-400 mb-2 uppercase">
                                            Component Stack:
                                        </h3>
                                        <pre className="bg-slate-800/50 p-3 rounded text-xs text-blue-300 overflow-auto max-h-32 border border-slate-700">
                                            {errorInfo?.componentStack ||
                                                "(Stack info unavailable)"}
                                        </pre>
                                    </div>

                                    {error?.stack && (
                                        <div>
                                            <h3 className="text-xs font-bold text-yellow-400 mb-2 uppercase">
                                                Stack Trace:
                                            </h3>
                                            <pre className="bg-slate-800/50 p-3 rounded text-xs text-yellow-300 overflow-auto max-h-32 border border-slate-700">
                                                {error.stack}
                                            </pre>
                                        </div>
                                    )}
                                </div>
                            </details>
                        )}

                        {/* Support */}
                        <div className="mt-6 pt-6 border-t border-slate-700">
                            <p className="text-slate-400 text-xs">
                                If the issue persists, please contact:
                                <a
                                    href="mailto:support@gts-logistics.com"
                                    className="text-blue-400 hover:text-blue-300 mr-1"
                                >
                                    support@gts-logistics.com
                                </a>
                            </p>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default EnhancedErrorBoundary;
