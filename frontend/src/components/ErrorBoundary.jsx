// frontend/src/components/ErrorBoundary.jsx

import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        // Log the error to an error reporting service
        console.error('ErrorBoundary caught an error:', error, errorInfo);

        this.setState({
            error,
            errorInfo
        });

        // You can also log to an external service here
        // logErrorToMyService(error, errorInfo);
    }

    handleRetry = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    render() {
        if (this.state.hasError) {
            // Custom error UI
            return (
                <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
                    <div className="glass-card p-8 max-w-md w-full mx-4 text-center">
                        <div className="flex justify-center mb-4">
                            <AlertTriangle className="w-16 h-16 text-red-400" />
                        </div>

                        <h1 className="text-2xl font-bold text-white mb-2">
                            Something went wrong
                        </h1>

                        <p className="text-slate-400 mb-6">
                            We encountered an unexpected error. Please try refreshing the page or contact support if the problem persists.
                        </p>

                        <div className="space-y-3">
                            <button
                                onClick={this.handleRetry}
                                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 border border-blue-400/30 rounded-lg transition-colors"
                            >
                                <RefreshCw className="w-4 h-4" />
                                Try Again
                            </button>

                            <button
                                onClick={() => window.location.href = '/'}
                                className="w-full px-4 py-2 bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 rounded-lg transition-colors"
                            >
                                Go to Home
                            </button>
                        </div>

                        {/* Show error details in development */}
                        {process.env.NODE_ENV === 'development' && (
                            <details className="mt-6 text-left">
                                <summary className="text-slate-400 cursor-pointer hover:text-slate-300">
                                    Error Details (Development)
                                </summary>
                                <pre className="mt-2 p-3 bg-slate-800/50 rounded text-xs text-red-400 overflow-auto max-h-40">
                                    {this.state.error ? this.state.error.toString() : "Unknown error"}
                                    <br />
                                    {this.state.errorInfo?.componentStack || "(componentStack not available)"}
                                </pre>
                            </details>
                        )}
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
