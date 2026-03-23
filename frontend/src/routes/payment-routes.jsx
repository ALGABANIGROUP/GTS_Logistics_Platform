/**
 * Payment Routes Configuration
 * تحديد جميع مسارات الدفع والتوجيه للمكونات المناسبة
 * 
 * المسارات:
 * - /payments/:invoiceId             - صفحة الدفع
 * - /payments/success                - صفحة النجاح
 * - /payments/failed                 - صفحة الفشل
 * 
 * المميزات:
 * - حماية المسارات بمعلومات المستخدم
 * - معالجة الأخطاء الشاملة
 * - دعم اللغة العربية
 * 
 * Author: GTS Development Team
 * Date: March 2026
 */

import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { PaymentPage } from '../pages/Payment/PaymentPage';
import { PaymentSuccessPage } from '../pages/Payment/PaymentSuccessPage';
import { PaymentFailedPage } from '../pages/Payment/PaymentFailedPage';
import SUDAPayBotDashboard from '../pages/ai-bots/SUDAPayBotDashboard';
import { SudaPaymentForm } from '../components/SudaPaymentForm';
import { readAuthToken } from '../utils/authStorage';

/**
 * Payment Routes Configuration Array
 * استخدم هذا في تطبيقك الرئيسي (App.jsx أو Router.jsx)
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
                    title: 'الدفع',
                    description: 'صفحة الدفع الآمنة',
                    requiresAuth: true,
                },
            },
            {
                path: 'history',
                element: <SUDAPayBotDashboard />,
                meta: {
                    title: 'Payment History',
                    description: 'Payment activity and transaction history',
                    requiresAuth: true,
                },
            },
            {
                path: 'success',
                element: <PaymentSuccessPage />,
                meta: {
                    title: 'تم الدفع بنجاح',
                    description: 'تأكيد الدفع',
                    requiresAuth: false,
                },
            },
            {
                path: 'failed',
                element: <PaymentFailedPage />,
                meta: {
                    title: 'فشل الدفع',
                    description: 'معالجة فشل العملية',
                    requiresAuth: false,
                },
            },
        ],
    },
];

/**
 * Integration Example for Router
 * 
 * في ملف App.jsx أو Router.tsx الخاص بك:
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
 * دوال مساعدة للتنقل بين صفحات الدفع
 */
export const PaymentNavigation = {
    /**
     * Navigate to Payment Page
     * التنقل إلى صفحة الدفع
     */
    goToPayment: (navigate, invoiceId) => {
        navigate(`/payments/${invoiceId}`);
    },

    /**
     * Navigate to Success Page
     * التنقل إلى صفحة النجاح
     */
    goToSuccess: (navigate, paymentId, invoiceId) => {
        navigate(
            `/payments/success?payment_id=${paymentId}&invoice_id=${invoiceId}`
        );
    },

    /**
     * Navigate to Failed Page
     * التنقل إلى صفحة الفشل
     */
    goToFailed: (navigate, paymentId, invoiceId, reason = 'unknown') => {
        navigate(
            `/payments/failed?payment_id=${paymentId}&invoice_id=${invoiceId}&reason=${reason}`
        );
    },
};

/**
 * Protected Route Component
 * مكون لحماية المسارات بمعلومات المستخدم
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
        return <div className="loading">جاري التحميل...</div>;
    }

    if (requiresAuth && !isAuthenticated) {
        // Not authenticated
        return <Navigate to="/login" replace />;
    }

    return element;
}

/**
 * Payment Context
 * توفير سياق للتطبيق بمعلومات الدفع
 */
export const PaymentContext = React.createContext({
    currentPayment: null,
    currentInvoice: null,
    setCurrentPayment: () => { },
    setCurrentInvoice: () => { },
});

/**
 * Payment Provider Component
 * مزود السياق لتطبيق الدفع
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
 * هوك مخصص للوصول إلى سياق الدفع
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
 * تصدير جميع المكونات للاستخدام
 */
export {
    PaymentPage,
    PaymentSuccessPage,
    PaymentFailedPage,
    SudaPaymentForm,
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
 *   SudaPaymentForm rendered
 *        ↓
 *   User clicks "الدفع الآن"
 *        ↓
 *   API call to create payment
 *        ↓
 *   Success → /payments/success
 *   Failure → /payments/failed
 *
 * Environment Variables Needed:
 * ═══════════════════════════════════════
 * REACT_APP_API_BASE_URL=http://localhost:8000
 * REACT_APP_PAYMENT_GATEWAY=sudapay
 * REACT_APP_DEFAULT_CURRENCY=SDG
 * 
 * Mobile Screen Sizes:
 * ═══════════════════════════════════════
 * - iPhone: 375px
 * - iPad: 768px
 * - Desktop: 1024px+
 * All components are responsive
 */

export default paymentRoutes;
