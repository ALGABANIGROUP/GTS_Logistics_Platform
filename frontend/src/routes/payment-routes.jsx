/**
 * Payment Routes Configuration
 * Define all payment routes and routing to appropriate components
 * 
 * Routes:
 * - /payments/:invoiceId             - Payment page
 * - /payments/success                - Success page
 * - /payments/failed                 - Failure page
 * 
 * Features:
 * - Route protection with user information
 * - Comprehensive error handling
 * - English language support
 * 
 * Author: GTS Development Team
 * Date: March 2026
 */

import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { PaymentPage } from '../pages/Payment/PaymentPage';
import { PaymentSuccessPage } from '../pages/Payment/PaymentSuccessPage';
import { PaymentFailedPage } from '../pages/Payment/PaymentFailedPage';
import { readAuthToken } from '../utils/authStorage';

/**
 * Payment Routes Configuration Array
 * Use this in your main application (App.jsx or Router.jsx)
 */
export const paymentRoutes = [
    {
        path: '/payments',
        element: <Outlet />,
        children: [
            {
                path: ':invoiceId',
                element: <PaymentPage />,
                meta: {
                    title: 'Payment',
                    description: 'Secure payment page',
                    requiresAuth: true,
                },
            },
            {
                path: 'success',
                element: <PaymentSuccessPage />,
                meta: {
                    title: 'Payment Successful',
                    description: 'Payment Confirmation',
                    requiresAuth: false,
                },
            },
            {
                path: 'failed',
                element: <PaymentFailedPage />,
                meta: {
                    title: 'Payment Failed',
                    description: 'Payment Processing Failed',
                    requiresAuth: false,
                },
            },
        ],
    },
];

/**
 * Integration Example for Router
 * 
 * In your App.jsx or Router.tsx file:
 * 
 * import { createBrowserRouter } from 'react-router-dom';
 * import { paymentRoutes } from './routes/payment-routes';
 * 
 * const router = createBrowserRouter([
 *   {
 *     path: '/',
 *     element: <Layout />,
 *     children: [
 *       // ... other routes
 *       ...paymentRoutes,
 *       // ... other routes
 *     ],
 *   },
 * ]);
 * 
 * export default router;
 */

/**
 * Navigation Helper Functions
 * Helper functions for navigation between payment pages
 */
export const PaymentNavigation = {
    /**
     * Navigate to Payment Page
     * Navigate to payment page
     */
    goToPayment: (navigate, invoiceId) => {
        navigate(`/payments/${invoiceId}`);
    },

    /**
     * Navigate to Success Page
     * Navigate to success page
     */
    goToSuccess: (navigate, paymentId, invoiceId) => {
        navigate(
            `/payments/success?payment_id=${paymentId}&invoice_id=${invoiceId}`
        );
    },

    /**
     * Navigate to Failed Page
     * Navigate to failed page
     */
    goToFailed: (navigate, paymentId, invoiceId, reason = 'unknown') => {
        navigate(
            `/payments/failed?payment_id=${paymentId}&invoice_id=${invoiceId}&reason=${reason}`
        );
    },
};

/**
 * Protected Route Component
 * Component to protect routes with user information
 */
export function ProtectedPaymentRoute({ element, requiresAuth = true }) {
    const [isAuthenticated, setIsAuthenticated] = React.useState(null);

    React.useEffect(() => {
        // Check authentication status
        const token = readAuthToken();
        setIsAuthenticated(!!token);
    }, []);

    if (isAuthenticated === null) {
        // Loading
        return <div className="loading">Loading...</div>;
    }

    if (requiresAuth && !isAuthenticated) {
        // Not authenticated
        return <Navigate to="/login" replace />;
    }

    return element;
}

/**
 * Payment Context
 * Provide context for the application with payment information
 */
export const PaymentContext = React.createContext({
    currentPayment: null,
    currentInvoice: null,
    setCurrentPayment: () => { },
    setCurrentInvoice: () => { },
});

/**
 * Payment Provider Component
 * Context provider for payment application
 */
export function PaymentProvider({ children }) {
    const [currentPayment, setCurrentPayment] = React.useState(null);
    const [currentInvoice, setCurrentInvoice] = React.useState(null);

    const value = {
        currentPayment,
        currentInvoice,
        setCurrentPayment,
        setCurrentInvoice,
    };

    return (
        <PaymentContext.Provider value={value}>
            {children}
        </PaymentContext.Provider>
    );
}

/**
 * usePaymentContext Custom Hook
 * Custom hook to access payment context
 */
export function usePaymentContext() {
    const context = React.useContext(PaymentContext);
    if (!context) {
        throw new Error('usePaymentContext must be used within PaymentProvider');
    }
    return context;
}

/**
 * Export All Components
 * Export all components for use
 */
export {
    PaymentPage,
    PaymentSuccessPage,
    PaymentFailedPage,
};

/**
 * Payment Routes Documentation
 * 
 * Usage Examples:
 * 
 * 1. Basic Route Integration:
 * ═══════════════════════════════════════
 * import { paymentRoutes } from './routes/payment-routes';
 * 
 * const router = createBrowserRouter([
 *   { path: '/', element: <Home /> },
 *   ...paymentRoutes,
 * ]);
 * 
 * 2. Navigation:
 * ═══════════════════════════════════════
 * import { useNavigate } from 'react-router-dom';
 * import { PaymentNavigation } from './routes/payment-routes';
 * 
 * function MyComponent() {
 *   const navigate = useNavigate();
 *   
 *   const handlePay = () => {
 *     PaymentNavigation.goToPayment(navigate, 123);
 *   };
 * }
 * 
 * 3. With Context:
 * ═══════════════════════════════════════
 * import { PaymentProvider } from './routes/payment-routes';
 * 
 * function App() {
 *   return (
 *     <PaymentProvider>
 *       <Router />
 *     </PaymentProvider>
 *   );
 * }
 * 
 * 4. Using Hook in Component:
 * ═══════════════════════════════════════
 * import { usePaymentContext } from './routes/payment-routes';
 * 
 * function PaymentComponent() {
 *   const { currentPayment, setCurrentPayment } = usePaymentContext();
 *   
 *   // Use currentPayment and setCurrentPayment
 * }
 * 
 * Flow Diagram:
 * ═══════════════════════════════════════
 *
 * User Clicks Pay
 *        ↓
 *   /payments/:invoiceId
 *        ↓
 *   PaymentPage component
 *        ↓
 *   Stripe-only payment instructions rendered
 *        ↓
 *   User clicks "Pay Now"
 *        ↓
 *   API call to create payment
 *        ↓
 *   Success → /payments/success
 *   Failure → /payments/failed
 *
 * Environment Variables Needed:
 * ═══════════════════════════════════════
 * VITE_API_BASE_URL=https://api.gtsdispatcher.com
 * REACT_APP_PAYMENT_GATEWAY=stripe
 * REACT_APP_DEFAULT_CURRENCY=USD
 * 
 * Mobile Screen Sizes:
 * ═══════════════════════════════════════
 * - iPhone: 375px
 * - iPad: 768px
 * - Desktop: 1024px+
 * All components are responsive
 */

export default paymentRoutes;
