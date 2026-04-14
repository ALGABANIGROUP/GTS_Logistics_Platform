// frontend/src/App.jsx
import React, { Suspense, useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import Layout from "./components/Layout";
import RequireAuth from "./components/RequireAuth";
import RequireModule from "./components/RequireModule";
import RequireFeature from "./components/RequireFeature";
import CookieConsent from "./components/CookieConsent";
import NotFound from "./pages/NotFound";
import PageTitleUpdater from "./components/PageTitleUpdater";

// Auth context
import { useAuth } from "./contexts/AuthContext.jsx";

// Notification context
import { NotificationProvider } from "./contexts/NotificationContext.jsx";

// Currency store
import { useCurrencyStore } from "./stores/useCurrencyStore";

// Inactivity watcher (auto logout on idle)
import InactivityWatcher from "./components/security/InactivityWatcher.jsx";

const AIBots = React.lazy(() => import("./pages/AIBots"));
const Dashboard = React.lazy(() => import("./pages/Dashboard"));
const AIFreightBroker = React.lazy(() => import("./pages/ai-bots/AIFreightBroker"));
const AIGeneralManager = React.lazy(() => import("./pages/ai-bots/AIGeneralManager"));
const AIInformationCoordinator = React.lazy(() => import("./pages/ai-bots/AIInformationCoordinator"));
const AILegalConsultant = React.lazy(() => import("./pages/ai-bots/AILegalConsultant"));
const AIOperationsManager = React.lazy(() => import("./pages/ai-bots/AIOperationsManager"));
const AISafetyManager = React.lazy(() => import("./pages/ai-bots/AISafetyManager"));
const AISalesTeam = React.lazy(() => import("./pages/ai-bots/AISalesTeam"));
const SalesTeam = React.lazy(() => import("./pages/SalesTeam"));
const AIStrategyAdvisor = React.lazy(() => import("./pages/ai-bots/AIStrategyAdvisor"));
const AISystemAdmin = React.lazy(() => import("./pages/ai-bots/AISystemAdmin"));
const AIBotControl = React.lazy(() => import("./pages/ai-bots/AIBotControl"));
const SafetyManager = React.lazy(() => import("./pages/SafetyManager"));
const AICustomerService = React.lazy(() => import("./pages/ai-bots/AICustomerService"));
const AIDocumentsManager = React.lazy(() => import("./pages/ai-bots/AIDocumentsManager"));
const AIDocumentsManagerPanel = React.lazy(() => import("./pages/ai-bots/AIDocumentsManagerPanel"));
const AIFinanceBot = React.lazy(() => import("./pages/ai-bots/AIFinanceBot"));
const PaymentBotDashboard = React.lazy(() => import("./pages/ai-bots/PaymentBotDashboard"));
const PaymentPage = React.lazy(() => import("./pages/Payment/PaymentPage"));
const PaymentSuccessPage = React.lazy(() => import("./pages/Payment/PaymentSuccessPage"));
const PaymentFailedPage = React.lazy(() => import("./pages/Payment/PaymentFailedPage"));
const PaymentLinkPage = React.lazy(() => import("./pages/Payment/PaymentLinkPage"));
const PaymentLinkDemo = React.lazy(() => import("./pages/Payment/PaymentLinkDemo"));
const AIDispatcherDashboard = React.lazy(() => import("./pages/ai-bots/AIDispatcherDashboard"));
const AIMapleLoadCanadaBot = React.lazy(() => import("./pages/ai-bots/AIMapleLoadCanadaBot"));
const AIExecutiveIntelligenceBot = React.lazy(() => import("./pages/ai-bots/AIExecutiveIntelligenceBot"));
const AIFreightBookingsBot = React.lazy(() => import("./pages/ai-bots/AIFreightBookingsBot"));
const AIMaintenanceDevBotEnhanced = React.lazy(() => import("./pages/ai-bots/AIMaintenanceDevBotEnhanced"));
const AIBotsHubDashboard = React.lazy(() => import("./pages/ai-bots/AIBotsHubDashboard"));
const AIGeneralManagerControlPage = React.lazy(() => import("./pages/ai-bots/AIGeneralManagerControlPage"));
const AIFreightBookingsControlPage = React.lazy(() => import("./pages/ai-bots/wrappers/AIFreightBookingsControlPage"));
const AIDataCoordinatorControlPage = React.lazy(() => import("./pages/ai-bots/wrappers/AIDataCoordinatorControlPage"));
const AIFinanceControlPage = React.lazy(() => import("./pages/ai-bots/wrappers/AIFinanceControlPage"));
const AISecurityControlPage = React.lazy(() => import("./pages/ai-bots/wrappers/AISecurityControlPage"));
const AISalesControlPage = React.lazy(() => import("./pages/ai-bots/wrappers/AISalesControlPage"));
const About = React.lazy(() => import("./pages/About"));
const Resources = React.lazy(() => import("./pages/Resources"));
const AILegalControlPage = React.lazy(() => import("./pages/ai-bots/wrappers/AILegalControlPage"));
const AIPartnerManagementControlPage = React.lazy(() => import("./pages/ai-bots/wrappers/AIPartnerManagementControlPage"));
const AiBotsLayout = React.lazy(() => import("./pages/ai-bots/AiBotsLayout"));
const AIFreightBrokerLayout = React.lazy(() => import("./pages/ai-freight-broker/AIFreightBrokerLayout"));
const AIFreightBrokerDashboard = React.lazy(() => import("./pages/ai-freight-broker/AIFreightBrokerDashboard"));
const ShipmentsPage = React.lazy(() => import("./pages/ai-freight-broker/ShipmentsPage"));
const AiFreightMapPage = React.lazy(() => import("./pages/ai-freight-broker/MapPage"));
const SafetyWorkspaceLayout = React.lazy(() => import("./pages/ai-bots/SafetyWorkspaceLayout"));
const SafetyDashboardWorkspace = React.lazy(() => import("./pages/ai-bots/SafetyDashboardWorkspace"));
const SafetyDriverMonitorPage = React.lazy(() => import("./pages/ai-bots/SafetyDriverMonitorPage"));
const SafetyVehicleSensorsPage = React.lazy(() => import("./pages/ai-bots/SafetyVehicleSensorsPage"));
const CarriersWorkspaceLayout = React.lazy(() => import("./pages/ai-bots/CarriersWorkspaceLayout"));
const CarriersDashboard = React.lazy(() => import("./pages/ai-bots/CarriersDashboard"));
const CarriersList = React.lazy(() => import("./pages/ai-bots/CarriersList"));
const CarriersRates = React.lazy(() => import("./pages/ai-bots/CarriersRates"));
const CarriersContracts = React.lazy(() => import("./pages/ai-bots/CarriersContracts"));
const ShippersWorkspaceLayout = React.lazy(() => import("./pages/ai-bots/ShippersWorkspaceLayout"));
const ShippersDashboard = React.lazy(() => import("./pages/ai-bots/ShippersDashboard"));
const ShippersList = React.lazy(() => import("./pages/ai-bots/ShippersList"));
const ShippersShipments = React.lazy(() => import("./pages/ai-bots/ShippersShipments"));
const ShippersInvoices = React.lazy(() => import("./pages/ai-bots/ShippersInvoices"));
const FreightBrokerPanel = React.lazy(() => import("./pages/FreightBrokerPanel"));
const Login = React.lazy(() => import("./pages/Login"));
const LogoutPage = React.lazy(() => import("./pages/LogoutPage"));
const AIGeneralManagerComponent = React.lazy(() => import("./components/bots/AIGeneralManager"));
const AIOperationsManagerComponent = React.lazy(() => import("./components/bots/AIOperationsManager"));
const AIFinanceBotComponent = React.lazy(() => import("./components/bots/AIFinanceBot"));
const AIFreightBrokerComponent = React.lazy(() => import("./components/bots/AIFreightBroker"));
const AIDocumentsManagerComponent = React.lazy(() => import("./components/bots/AIDocumentsManager"));
const AICustomerServiceComponent = React.lazy(() => import("./components/bots/AICustomerService"));
const CustomerServiceDemo = React.lazy(() => import("./pages/CustomerServiceDemo"));
const AISystemAdminComponent = React.lazy(() => import("./components/bots/AISystemAdmin"));
const AIInformationCoordinatorComponent = React.lazy(() => import("./components/bots/AIInformationCoordinator"));
const AIDevMaintenanceComponent = React.lazy(() => import("./components/bots/AIDevMaintenance"));
const AILegalConsultantComponent = React.lazy(() => import("./components/bots/AILegalConsultant"));
const AISafetyManagerComponent = React.lazy(() => import("./components/bots/AISafetyManager"));
const AISystemManager = React.lazy(() => import("./pages/ai-bots/AISystemManager"));
const AISalesTeamComponent = React.lazy(() => import("./components/bots/AISalesTeam"));
const AISecurityManagerComponent = React.lazy(() => import("./components/bots/AISecurityManager"));
const FreightPulseDashboard = React.lazy(() => import("./pages/FreightPulseDashboard"));
const AIPartnerManagerComponent = React.lazy(() => import("./components/bots/AIPartnerManager"));
const FreightBrokerDashboard = React.lazy(() => import("./components/bots/FreightBrokerDashboard"));
const FreightBrokerControlPanel = React.lazy(() => import("./components/bots/FreightBrokerControlPanel"));
const FreightBookingsInterface = React.lazy(() => import("./components/bots/FreightBookingsInterface"));
const Register = React.lazy(() => import("./pages/Register"));
const RequestReceived = React.lazy(() => import("./pages/RequestReceived"));
const VerifyEmail = React.lazy(() => import("./pages/VerifyEmail"));
const ForgotPassword = React.lazy(() => import("./pages/ForgotPassword"));
const ResetPassword = React.lazy(() => import("./pages/ResetPassword"));
const ActivateAccount = React.lazy(() => import("./pages/ActivateAccount"));
const AccountInactive = React.lazy(() => import("./pages/auth/AccountInactive"));
const Unauthorized = React.lazy(() => import("./pages/Unauthorized"));
const EmailLog = React.lazy(() => import("./components/EmailLog"));
const Emails = React.lazy(() => import("./pages/Emails"));
const Shipments = React.lazy(() => import("./pages/Shipments"));
const AddShipment = React.lazy(() => import("./pages/AddShipment"));
const Drivers = React.lazy(() => import("./pages/Drivers"));
const Finance = React.lazy(() => import("./pages/Finance"));
const MapPage = React.lazy(() => import("./pages/Map"));
const UnifiedShipmentMap = React.lazy(() => import("./components/UnifiedShipmentMap"));
const Dispatch = React.lazy(() => import("./pages/Dispatch"));
const LoadBoardMarket = React.lazy(() => import("./pages/loadboard/Market"));
const Operations = React.lazy(() => import("./pages/Operations"));
const DocumentUpload = React.lazy(() => import("./pages/DocumentUpload"));
const DocumentIntelligenceDashboard = React.lazy(() => import("./pages/DocumentIntelligenceDashboard"));
const EditDocument = React.lazy(() => import("./pages/EditDocument"));
const Documents = React.lazy(() => import("./pages/Documents"));
const DevWindow = React.lazy(() => import("./pages/DevWindow"));
const DevMaintenanceDashboard = React.lazy(() => import("./pages/DevMaintenanceDashboard"));
const ReportsDashboard = React.lazy(() => import("./pages/ReportsDashboard"));
const CommunicationsDashboard = React.lazy(() => import("./pages/CommunicationsDashboard"));
const MarketIntelligenceDashboard = React.lazy(() => import("./pages/MarketIntelligenceDashboard"));
const Account = React.lazy(() => import("./pages/Account"));
const AdminOverview = React.lazy(() => import("./pages/admin/AdminOverview"));
const AdminLayout = React.lazy(() => import("./layouts/AdminLayout"));
const FleetManagement = React.lazy(() => import("./pages/admin/FleetManagement"));
const FleetLiveMap = React.lazy(() => import("./pages/admin/FleetLiveMap"));
const AdminDrivers = React.lazy(() => import("./pages/admin/Drivers"));
const OperationsManager = React.lazy(() => import("./pages/admin/OperationsManager"));
const StrategyAdvisor = React.lazy(() => import("./pages/admin/StrategyAdvisor"));
const MarketingBot = React.lazy(() => import("./pages/admin/MarketingBot"));
const AICallManager = React.lazy(() => import("./pages/admin/AICallManager"));
const DevBotSettings = React.lazy(() => import("./pages/admin/DevBotSettings"));
const CarrierScoreboard = React.lazy(() => import("./pages/admin/CarrierScoreboard"));
const AIGeneralManagerAdmin = React.lazy(() => import("./pages/admin/AIGeneralManager"));
const SupportCenter = React.lazy(() => import("./pages/admin/SupportCenter"));
const SupportTickets = React.lazy(() => import("./pages/admin/SupportTickets"));
const SystemHealth = React.lazy(() => import("./pages/admin/SystemHealth"));
const OrchestrationDashboard = React.lazy(() => import("./pages/admin/OrchestrationDashboard"));
const PartnersListPage = React.lazy(() => import("./pages/admin/PartnersListPage"));
const PartnerDetailsPage = React.lazy(() => import("./pages/admin/PartnerDetailsPage"));
const Partners = React.lazy(() => import("./pages/admin/Partners"));
const AdminFooterSettings = React.lazy(() => import("./pages/admin/AdminFooterSettings"));
const AdminUsers = React.lazy(() => import("./pages/admin/AdminUsers"));
const MaintenanceCenterPage = React.lazy(() => import("./pages/admin/MaintenanceCenterPage"));
const APIConnectionsManager = React.lazy(() => import("./pages/APIConnectionsManager"));
const TaskManager = React.lazy(() => import("./pages/TaskManager"));
const TheVIZIONDashboard = React.lazy(() => import("./pages/admin/TheVIZIONDashboard"));

// Support System Routes
import { getSupportRoutes } from "./pages/support/routes";
const AutomaticDashboard = React.lazy(() => import("./pages/admin/AutomaticDashboard"));
const BotOS = React.lazy(() => import("./pages/admin/BotOS"));
const Governance = React.lazy(() => import("./pages/admin/Governance"));
const PlatformExpenses = React.lazy(() => import("./pages/admin/PlatformExpenses"));
// import TMSDashboard from "./pages/tms/TMSDashboard.jsx"; // Removed (TMS deleted)
// import TMSOnboarding from "./pages/TMSOnboarding.jsx"; // Removed (TMS deleted)
const PortalRequests = React.lazy(() => import("./pages/admin/PortalRequests.jsx"));
const AdminNotifications = React.lazy(() => import("./pages/admin/AdminNotifications.jsx"));
const RequestAuditLog = React.lazy(() => import("./pages/admin/RequestAuditLog.jsx"));
const TMSAccess = React.lazy(() => import("./pages/admin/TMSAccess.jsx"));
// import TenantSocialSettings from "./pages/tms/TenantSocialSettings"; // Removed (TMS deleted)

// ===== Enterprise Portal Landing =====
const PortalLanding = React.lazy(() => import("./pages/PortalLanding"));
const SystemSelector = React.lazy(() => import("./pages/SystemSelector"));

// ===== Partner Portal & Agreement =====
const PartnerDashboardPage = React.lazy(() => import("./pages/partner/PartnerDashboardPage.jsx"));
const PartnerClientsPage = React.lazy(() => import("./pages/partner/PartnerClientsPage.jsx"));
const PartnerOrdersPage = React.lazy(() => import("./pages/partner/PartnerOrdersPage.jsx"));
const PartnerRevenuePage = React.lazy(() => import("./pages/partner/PartnerRevenuePage.jsx"));
const PartnerPayoutsPage = React.lazy(() => import("./pages/partner/PartnerPayoutsPage.jsx"));
const PartnerSettingsPage = React.lazy(() => import("./pages/partner/PartnerSettingsPage.jsx"));
const PartnerAgreementPage = React.lazy(() => import("./pages/partner/PartnerAgreementPage.jsx"));
const PlatformSettings = React.lazy(() => import("./pages/admin/PlatformSettings"));
const TenantManagement = React.lazy(() => import("./pages/admin/TenantManagement"));
const AuditLogs = React.lazy(() => import("./components/AuditLogs"));
const FeatureFlagsManager = React.lazy(() => import("./components/FeatureFlagsManager"));
const PricingManagement = React.lazy(() => import("./pages/PricingManagement"));
const SystemSetup = React.lazy(() => import("./pages/SystemSetup"));
const TermsAndConditions = React.lazy(() => import("./pages/TermsAndConditions"));
const BotFeatures = React.lazy(() => import("./pages/BotFeatures"));
const UserSettings = React.lazy(() => import("./pages/UserSettings"));
const NotificationsPage = React.lazy(() => import("./pages/notifications/Notifications.jsx"));
const DashboardNotifications = React.lazy(() => import("./pages/dashboard/Notifications.jsx"));
const Pricing = React.lazy(() => import("./pages/Pricing"));
const Products = React.lazy(() => import("./pages/Products"));
const Privacy = React.lazy(() => import("./pages/Privacy"));
const Terms = React.lazy(() => import("./pages/Terms"));
const Legal = React.lazy(() => import("./pages/Legal"));
const Contact = React.lazy(() => import("./pages/Contact"));
const PublicSupport = React.lazy(() => import("./pages/PublicSupport"));
const PublicContentPage = React.lazy(() => import("./pages/PublicContentPage"));

/** Simple error boundary so the app doesn't go blank-white on runtime errors */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("[App] Error boundary caught:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 border border-red-200">
            <div className="text-center">
              <div className="text-red-500 text-6xl mb-4">⚠️</div>
              <h1 className="text-2xl font-bold text-red-700 mb-2">
                Application Error
              </h1>
              <p className="text-gray-600 mb-4">
                Sorry, an unexpected error occurred. Please refresh the page or
                try again later.
              </p>
              <div className="bg-red-50 p-3 rounded text-sm text-red-800 mb-4">
                <details>
                  <summary className="cursor-pointer font-medium">
                    Error Details
                  </summary>
                  <pre className="whitespace-pre-wrap mt-2 text-xs">
                    {String(this.state.error?.message || "Unknown error")}
                  </pre>
                </details>
              </div>
              <button
                onClick={() => window.location.reload()}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200"
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

// Loading Component
const LoadingFallback = () => (
  <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4" />
      <p className="text-slate-200">Loading...</p>
      <p className="text-sm text-slate-400 mt-2">Gabani Transport Solutions (GTS) Platform</p>
    </div>
  </div>
);

// AuthChecker now does nothing except returning children (no redirects, no hooks)
const AuthChecker = ({ children }) => {
  return children;
};

const LandingGate = () => {
  const { isAuthenticated, loading, authReady } = useAuth();
  const location = useLocation();
  const resetToken = React.useMemo(() => {
    const params = new URLSearchParams(location.search);
    const rawHash = location.hash?.startsWith("#")
      ? location.hash.slice(1)
      : location.hash || "";
    const hashQuery = rawHash.includes("?")
      ? rawHash.split("?", 2)[1]
      : rawHash;
    const hashParams = new URLSearchParams(hashQuery || "");
    return (
      params.get("token") ||
      params.get("reset_token") ||
      params.get("reset") ||
      hashParams.get("token") ||
      hashParams.get("reset_token") ||
      hashParams.get("reset")
    );
  }, [location.search, location.hash]);

  if (!authReady) {
    return <LoadingFallback />;
  }

  if (resetToken) {
    return <ResetPassword />;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <PortalLanding />;
};

const App = () => {
  const { initializeCurrency, fetchExchangeRates, setCurrency, setCountry } = useCurrencyStore();

  // Initialize currency on app load
  useEffect(() => {
    // Force reset to CAD if no saved preference or reset old data
    const saved = localStorage.getItem('gts-currency-storage');
    if (!saved) {
      setCurrency('CAD');
      setCountry('CA');
    }
    initializeCurrency();
    fetchExchangeRates();
  }, []);

  return (
    <ErrorBoundary>
      <NotificationProvider>
        {/* Inactivity watcher: auto-logout after idle time */}
        <InactivityWatcher timeoutMinutes={120} warningMinutesBefore={5} />

      <AuthChecker>
        <Suspense fallback={<LoadingFallback />}>
          {/* Page Title Updater */}
          <PageTitleUpdater />
          {/* Toast Notifications */}
          <ToastContainer
            position="top-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="light"
          />
          <CookieConsent />

          <div className="app-root glass-page">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<PortalLanding />} />
              <Route path="/about" element={<About />} />
              <Route path="/resources" element={<Resources />} />
              <Route path="/pricing" element={<Navigate to="/register" replace />} />
              <Route path="/products" element={<Products />} />
              <Route path="/privacy" element={<Privacy />} />
              <Route path="/terms" element={<Terms />} />
              <Route path="/legal" element={<Legal />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/blog" element={<PublicContentPage />} />
              <Route path="/blog/:slug" element={<PublicContentPage />} />
              <Route path="/podcasts" element={<PublicContentPage />} />
              <Route path="/podcast/:slug" element={<PublicContentPage />} />
              <Route path="/webinars" element={<PublicContentPage />} />
              <Route path="/webinars/:slug" element={<PublicContentPage />} />
              <Route path="/stories" element={<PublicContentPage />} />
              <Route path="/press" element={<PublicContentPage />} />
              <Route path="/community" element={<PublicContentPage />} />
              <Route path="/alerts" element={<PublicContentPage />} />
              <Route path="/emergency" element={<PublicContentPage />} />
              <Route path="/partners" element={<PublicContentPage />} />
              <Route path="/fraud-prevention" element={<PublicContentPage />} />
              <Route path="/find-loads" element={<PublicContentPage />} />
              <Route path="/resources/:slug" element={<PublicContentPage />} />
              <Route path="/tools/:toolSlug" element={<PublicContentPage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/logout" element={<LogoutPage />} />
              <Route path="/account-inactive" element={<AccountInactive />} />
              <Route path="/register" element={<Register />} />
              <Route path="/request-received" element={<RequestReceived />} />
              <Route path="/verify-email" element={<VerifyEmail />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/activate/:token" element={<ActivateAccount />} />

              <Route path="/support" element={<PublicSupport />} />

              {/* System Selector - choose system after login */}
              <Route
                path="/select-system"
                element={
                  <RequireAuth>
                    <SystemSelector />
                  </RequireAuth>
                }
              />

              {/* ===== Partner Agreement (protected) ===== */}
              <Route
                path="/partner-agreement"
                element={
                  <RequireAuth>
                    <Layout>
                      <PartnerAgreementPage />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* ===== Partner Portal Protected Routes ===== */}
              <Route
                path="/partner-portal"
                element={
                  <RequireAuth>
                    <Layout>
                      <PartnerDashboardPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/partner-portal/clients"
                element={
                  <RequireAuth>
                    <Layout>
                      <PartnerClientsPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/partner-portal/orders"
                element={
                  <RequireAuth>
                    <Layout>
                      <PartnerOrdersPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/partner-portal/revenue"
                element={
                  <RequireAuth>
                    <Layout>
                      <PartnerRevenuePage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/partner-portal/payouts"
                element={
                  <RequireAuth>
                    <Layout>
                      <PartnerPayoutsPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/partner-portal/settings"
                element={
                  <RequireAuth>
                    <Layout>
                      <PartnerSettingsPage />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Protected Routes (existing) */}
              <Route
                path="/dashboard"
                element={
                  <RequireAuth>
                    <Layout>
                      <Dashboard />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/dashboard/notifications"
                element={
                  <RequireAuth>
                    <Layout>
                      <DashboardNotifications />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/communications"
                element={
                  <RequireAuth>
                    <Layout>
                      <CommunicationsDashboard />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/settings"
                element={<UserSettings />}
              />
              <Route
                path="/task-manager"
                element={
                  <RequireAuth>
                    <Layout>
                      <TaskManager />
                    </Layout>
                  </RequireAuth>
                }
              />



              {/* TMS Onboarding removed (TMS deleted) */}

              {/* TMS Dashboard removed (TMS deleted) */}

              {/* Account route */}
              <Route
                path="/account"
                element={
                  <RequireAuth>
                    <Layout>
                      <Account />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/unauthorized"
                element={
                  <Layout>
                    <Unauthorized />
                  </Layout>
                }
              />
              <Route path="/admin/unified-dashboard" element={<Navigate to="/admin/overview" replace />} />
              <Route path="/app-store" element={<Navigate to="/contact" replace />} />
              <Route path="/google-play" element={<Navigate to="/contact" replace />} />
              <Route path="/tms" element={<Navigate to="/dashboard" replace />} />
              <Route path="/tms/dashboard" element={<Navigate to="/dashboard" replace />} />
              <Route path="/finance/platform-expenses" element={<Navigate to="/admin/platform-expenses" replace />} />
              <Route path="/finance/ai-analysis" element={<Navigate to="/ai-bots/finance" replace />} />
              <Route path="/ai-bots/trainer" element={<Navigate to="/ai-bots/control?bot=trainer_bot" replace />} />

              {/* AI Bots Routes */}
              <Route
                path="/ai-bots"
                element={
                  <RequireAuth>
                    <Layout>
                      <AiBotsLayout />
                    </Layout>
                  </RequireAuth>
                }
              >
                <Route index element={<AIBots />} />
                <Route path="bot-os" element={<BotOS />} />
              </Route>
              <Route
                path="/ai-bots/hub"
                element={
                  <RequireAuth>
                    <Layout>
                      <RequireFeature featureKey="ai.basic">
                        <AIBotsHubDashboard />
                      </RequireFeature>
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Unified Freight Broker Control Panel */}
              <Route
                path="/freight-broker"
                element={
                  <RequireAuth>
                    <FreightBrokerPanel />
                  </RequireAuth>
                }
              />

              {/* Public Pricing Route */}
              <Route
                path="/pricing"
                element={
                  <Layout>
                    <Pricing />
                  </Layout>
                }
              />

              {/* Pricing Management Route */}
              <Route
                path="/pricing-management"
                element={
                  <RequireAuth>
                    <Navigate to="/admin/subscriptions" replace />
                  </RequireAuth>
                }
              />

              {/* System Setup Route */}
              <Route
                path="/system-setup"
                element={
                  <RequireAuth>
                    <Layout>
                      <SystemSetup />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Bot Features Route */}
              <Route
                path="/bot-features"
                element={
                  <RequireAuth>
                    <Layout>
                      <BotFeatures />
                    </Layout>
                  </RequireAuth>
                }
              />



              {/* Control Panel Routes */}
              <Route
                path="/ai-bots/general-manager"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIGeneralManagerControlPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/freight-bookings"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIFreightBookingsControlPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/data-coordinator"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIDataCoordinatorControlPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/finance-intelligence"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIFinanceControlPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/security-question"
                element={
                  <RequireAuth>
                    <Layout>
                      <AISecurityControlPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/sales-intelligence"
                element={
                  <RequireAuth>
                    <Layout>
                      <AISalesControlPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/legal-counsel"
                element={
                  <RequireAuth>
                    <Layout>
                      <AILegalControlPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/partner-management"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIPartnerManagementControlPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/freight"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIFreightBroker />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-freight-broker"
                element={<Navigate to="/ai-bots/freight_broker" replace />}
              />
              <Route
                path="/ai-freight-broker/shipments"
                element={<Navigate to="/ai-bots/freight_broker/shipments" replace />}
              />
              <Route
                path="/ai-freight-broker/map"
                element={<Navigate to="/ai-bots/freight_broker/map" replace />}
              />
              <Route
                path="/freight"
                element={<Navigate to="/ai-bots/freight_broker" replace />}
              />
              <Route
                path="/freight/dashboard"
                element={<Navigate to="/ai-bots/freight_broker" replace />}
              />
              <Route
                path="/freight/shipments"
                element={<Navigate to="/ai-bots/freight_broker/shipments" replace />}
              />
              <Route
                path="/freight/map"
                element={<Navigate to="/ai-bots/freight_broker/map" replace />}
              />
              <Route
                path="/freight/live-map"
                element={<Navigate to="/ai-bots/freight_broker/live-map" replace />}
              />
              <Route
                path="/ai-bots/general"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIGeneralManagerControlPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/information"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIInformationCoordinator />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/legal"
                element={
                  <RequireAuth>
                    <Layout>
                      <AILegalConsultant />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/maintenance-dashboard"
                element={
                  <RequireAuth>
                    <Layout>
                      <DevMaintenanceDashboard />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/maintenance"
                element={
                  <RequireAuth>
                    <Navigate to="/ai-bots/maintenance-dashboard" replace />
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/operations"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIOperationsManager />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/aid-dispatcher"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIDispatcherDashboard />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/safety"
                element={
                  <RequireAuth>
                    <Layout>
                      <SafetyWorkspaceLayout />
                    </Layout>
                  </RequireAuth>
                }
              >
                <Route index element={<Navigate to="/ai-bots/safety/dashboard" replace />} />
                <Route path="dashboard" element={<SafetyDashboardWorkspace />} />
                <Route
                  path="incidents"
                  element={
                    <FleetManagement
                      basePath="/ai-bots/safety"
                      initialTab="incidents"
                      visibleTabs={["incidents"]}
                      badge="Safety Operations"
                      title="Safety Incident Log"
                      description="Record, review, and resolve safety incidents across fleet operations."
                      showFleetActions={false}
                    />
                  }
                />
                <Route path="drivers/monitor" element={<SafetyDriverMonitorPage />} />
                <Route path="vehicles/sensors" element={<SafetyVehicleSensorsPage />} />
              </Route>
              <Route
                path="/ai-bots/safety_manager"
                element={
                  <RequireAuth>
                    <Navigate to="/ai-bots/safety/dashboard" replace />
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/system-manager"
                element={
                  <RequireAuth>
                    <Layout>
                      <AISystemManager />
                    </Layout>
                  </RequireAuth>
                }
              />
              {/* Carriers Routes */}
              <Route
                path="/ai-bots/carriers"
                element={
                  <RequireAuth>
                    <Layout>
                      <CarriersWorkspaceLayout />
                    </Layout>
                  </RequireAuth>
                }
              >
                <Route index element={<Navigate to="/ai-bots/carriers/dashboard" replace />} />
                <Route path="dashboard" element={<CarriersDashboard />} />
                <Route path="list" element={<CarriersList />} />
                <Route path="rates" element={<CarriersRates />} />
                <Route path="contracts" element={<CarriersContracts />} />
              </Route>
              {/* Shippers Routes */}
              <Route
                path="/ai-bots/shippers"
                element={
                  <RequireAuth>
                    <Layout>
                      <ShippersWorkspaceLayout />
                    </Layout>
                  </RequireAuth>
                }
              >
                <Route index element={<Navigate to="/ai-bots/shippers/dashboard" replace />} />
                <Route path="dashboard" element={<ShippersDashboard />} />
                <Route path="list" element={<ShippersList />} />
                <Route path="shipments" element={<ShippersShipments />} />
                <Route path="invoices" element={<ShippersInvoices />} />
              </Route>
              <Route
                path="/ai-bots/sales"
                element={
                  <RequireAuth allowedRoles={['super_admin', 'admin', 'manager', 'user', 'partner']}>
                    <Layout>
                      <SalesTeam />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/sales-team"
                element={
                  <RequireAuth allowedRoles={['super_admin', 'admin', 'manager', 'user', 'partner']}>
                    <Layout>
                      <SalesTeam />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/Sales_Team"
                element={<Navigate to="/ai-bots/sales" replace />}
              />

              {/* Testing Routes - Remove after verification */}
              <Route
                path="/sales-team-test"
                element={
                  <Layout>
                    <SalesTeam />
                  </Layout>
                }
              />
              <Route
                path="/public-sales"
                element={<SalesTeam />}
              />
              <Route
                path="/ai-bots/strategy"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIStrategyAdvisor />
                    </Layout>
                  </RequireAuth>
                }
              />
              {/* Backward compatibility: merge old path to canonical to avoid conflicts */}
              <Route
                path="/ai-bots/strategy-advisor-bot"
                element={<Navigate to="/ai-bots/strategy" replace />}
              />
              <Route
                path="/ai-bots/system-admin"
                element={
                  <RequireAuth allowedRoles={['admin', 'system_admin', 'super_admin', 'owner']}>
                    <Layout>
                      <AISystemAdmin />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/control"
                element={
                  <RequireAuth>
                    <Layout>
                      <RequireFeature featureKey="ai.basic">
                        <AIBotControl />
                      </RequireFeature>
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/customer-service-demo"
                element={
                  <RequireAuth>
                    <Layout>
                      <CustomerServiceDemo />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/customer-service"
                element={
                  <RequireAuth>
                    <Layout>
                      <AICustomerService />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/documents"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIDocumentsManagerPanel />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/documents/upload"
                element={
                  <RequireAuth>
                    <Layout>
                      <DocumentUpload />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/documents/intelligence"
                element={
                  <RequireAuth>
                    <Layout>
                      <DocumentIntelligenceDashboard />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/documents/edit/:id"
                element={
                  <RequireAuth>
                    <Layout>
                      <EditDocument />
                    </Layout>
                  </RequireAuth>
                }
              />


              {/* New Enhanced Bot Routes */}
              <Route
                path="/ai-bots/mapleload-canada"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIMapleLoadCanadaBot />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/executive-intelligence"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIExecutiveIntelligenceBot />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/freight-bookings"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIFreightBookingsBot />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/maintenance-enhanced"
                element={
                  <RequireAuth>
                    <Navigate to="/ai-bots/maintenance-dashboard" replace />
                  </RequireAuth>
                }
              />

              {/* Finance & Operations Routes */}
              {/* ===== AI BOTS PANEL & BOT COMPONENT ROUTES ===== */}

              {/* General Manager Bot */}
              <Route
                path="/ai-bots/general-manager"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIGeneralManagerComponent />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Operations Manager Bot */}
              <Route
                path="/ai-bots/operations-manager"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIOperationsManagerComponent />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Finance Bot */}
              <Route
                path="/ai-bots/finance-bot"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIFinanceBotComponent />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Freight Broker Bot - Old */}
              <Route
                path="/ai-bots/freight-broker-bot"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIFreightBrokerComponent />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Freight Broker Dashboard */}
              <Route
                path="/ai-bots/freight_broker"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIFreightBrokerLayout />
                    </Layout>
                  </RequireAuth>
                }
              >
                <Route index element={<AIFreightBrokerDashboard />} />
                <Route path="dashboard" element={<Navigate to="/ai-bots/freight_broker" replace />} />
                <Route path="shipments" element={<ShipmentsPage />} />
                <Route path="map" element={<AiFreightMapPage />} />
                <Route path="live-map" element={<FleetLiveMap />} />
                <Route path="vehicles" element={<FleetManagement basePath="/ai-bots/freight_broker" initialTab="vehicles" visibleTabs={["vehicles"]} badge="Freight Broker Fleet" title="Vehicle Management" description="Manage fleet vehicles used by the freight broker operation." />} />
                <Route path="drivers" element={<FleetManagement basePath="/ai-bots/freight_broker" initialTab="drivers" visibleTabs={["drivers"]} badge="Freight Broker Fleet" title="Driver Management" description="Manage active drivers, readiness, licensing, and availability." />} />
                <Route path="assignments" element={<FleetManagement basePath="/ai-bots/freight_broker" initialTab="assignments" visibleTabs={["assignments"]} badge="Freight Broker Fleet" title="Driver to Vehicle Assignments" description="Coordinate active driver-to-vehicle assignments for freight operations." />} />
                <Route path="fleet" element={<Navigate to="/ai-bots/freight_broker/vehicles" replace />} />
                <Route path="fleet/drivers" element={<Navigate to="/ai-bots/freight_broker/drivers" replace />} />
                <Route path="fleet/vehicles" element={<Navigate to="/ai-bots/freight_broker/vehicles" replace />} />
                <Route path="fleet/assignments" element={<Navigate to="/ai-bots/freight_broker/assignments" replace />} />
                <Route path="fleet/incidents" element={<Navigate to="/ai-bots/safety/incidents" replace />} />
                <Route path="fleet/live-map" element={<Navigate to="/ai-bots/freight_broker/live-map" replace />} />
              </Route>

              {/* Freight Broker Control Panel */}
              <Route
                path="/ai-bots/freight_broker/control"
                element={
                  <RequireAuth>
                    <Layout>
                      <FreightBrokerControlPanel />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Freight Bookings Interface */}
              <Route
                path="/ai-bots/freight_bookings"
                element={
                  <RequireAuth>
                    <Layout>
                      <FreightBookingsInterface />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Documents Manager Bot */}
              <Route
                path="/ai-bots/documents-manager-bot"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIDocumentsManagerComponent />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Customer Service Bot */}
              <Route
                path="/ai-bots/customer-service-bot"
                element={
                  <RequireAuth>
                    <Layout>
                      <AICustomerServiceComponent />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* System Admin Bot */}
              <Route
                path="/ai-bots/system-admin-bot"
                element={
                  <RequireAuth allowedRoles={['admin', 'system_admin', 'super_admin', 'owner']}>
                    <Layout>
                      <AISystemAdminComponent />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Information Coordinator Bot */}
              <Route
                path="/ai-bots/information-coordinator-bot"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIInformationCoordinatorComponent />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Strategy Advisor Bot */}
              {/* Removed duplicate route to avoid confusion; use /ai-bots/strategy */}

              {/* Dev Maintenance Bot (CTO) */}
              <Route
                path="/ai-bots/dev-maintenance-bot"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIDevMaintenanceComponent />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Legal Consultant Bot */}
              <Route
                path="/ai-bots/legal-consultant-bot"
                element={
                  <RequireAuth>
                    <Layout>
                      <AILegalConsultantComponent />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Safety Manager Bot */}
              <Route
                path="/ai-bots/safety-manager-bot"
                element={
                  <RequireAuth>
                    <Layout>
                      <AISafetyManagerComponent />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Sales Team Bot */}
              <Route
                path="/ai-bots/sales-team-bot"
                element={
                  <RequireAuth>
                    <Layout>
                      <AISalesTeamComponent />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Security Manager Bot */}
              <Route
                path="/ai-bots/security-manager-bot"
                element={
                  <RequireAuth>
                    <Layout>
                      <AISecurityManagerComponent />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/security_manager"
                element={
                  <RequireAuth>
                    <Layout>
                      <AISecurityManagerComponent />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Hidden Partner Manager Bot */}
              <Route
                path="/internal/partner-manager"
                element={
                  <RequireAuth>
                    <Layout>
                      <AIPartnerManagerComponent />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/platform-expenses"
                element={
                  <RequireAuth>
                    <Layout>
                      <PlatformExpenses />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/emails/logs"
                element={
                  <RequireAuth>
                    <Layout>
                      <EmailLog />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/shipments"
                element={
                  <RequireAuth>
                    <Layout>
                      <RequireFeature featureKey="tms.core">
                        <Shipments />
                      </RequireFeature>
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/shipments/new"
                element={
                  <RequireAuth>
                    <Layout>
                      <RequireFeature featureKey="tms.core">
                        <AddShipment />
                      </RequireFeature>
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/dispatch"
                element={
                  <RequireAuth>
                    <Layout>
                      <RequireFeature featureKey="dispatcher.core">
                        <Dispatch />
                      </RequireFeature>
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/drivers"
                element={
                  <RequireAuth>
                    <Layout>
                      <RequireFeature featureKey="dispatcher.core">
                        <Drivers />
                      </RequireFeature>
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/loadboard"
                element={
                  <RequireAuth>
                    <Layout>
                      <RequireFeature featureKey="loadboard.core">
                        <LoadBoardMarket />
                      </RequireFeature>
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/finance"
                element={
                  <RequireAuth>
                    <Layout>
                      <Finance />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/expenses"
                element={
                  <RequireAuth>
                    <Layout>
                      <PlatformExpenses />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Operations live dashboard */}
              <Route
                path="/operations"
                element={
                  <RequireAuth>
                    <Layout>
                      <Operations />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Map Pages */}
              <Route
                path="/map"
                element={
                  <RequireAuth>
                    <Layout>
                      <MapPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/shipment-map"
                element={
                  <RequireAuth>
                    <Layout>
                      <RequireModule moduleKey="tms">
                        <RequireFeature featureKeys={["tms.core", "tms.shipments"]}>
                          <UnifiedShipmentMap />
                        </RequireFeature>
                      </RequireModule>
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Documents Center */}
              <Route
                path="/documents"
                element={
                  <RequireAuth>
                    <Layout>
                      <Documents />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/documents/upload"
                element={
                  <RequireAuth>
                    <Layout>
                      <DocumentUpload />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/documents/intelligence"
                element={
                  <RequireAuth>
                    <Layout>
                      <DocumentIntelligenceDashboard />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/documents/edit/:id"
                element={
                  <RequireAuth>
                    <Layout>
                      <EditDocument />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Development & Maintenance */}
              <Route
                path="/dev-maintenance"
                element={
                  <RequireAuth>
                    <Layout>
                      <DevMaintenanceDashboard />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/dev"
                element={
                  <RequireAuth>
                    <Layout>
                      <DevWindow />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/dev-window"
                element={
                  <RequireAuth>
                    <Layout>
                      <DevWindow />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Reports - Moved to Admin */}
              <Route
                path="/reports"
                element={<Navigate to="/admin/reports" replace />}
              />

              <Route
                path="/ai-bots/maintenance/reports"
                element={<Navigate to="/admin/reports" replace />}
              />
              <Route
                path="/ai-bots/maintenance/ReportsDashboard"
                element={<Navigate to="/admin/reports" replace />}
              />
              {/* User Profile and Settings */}
              <Route
                path="/profile"
                element={
                  <RequireAuth>
                    <Layout>
                      <UserSettings />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/settings"
                element={
                  <RequireAuth>
                    <Layout>
                      <UserSettings />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Email Logs */}
              <Route
                path="/emails"
                element={
                  <RequireAuth>
                    <Layout>
                      <RequireFeature
                        featureKeys={["email.core", "email.logs"]}
                        mode="all"
                        fallback={
                          <div className="mx-auto max-w-3xl rounded-2xl border border-slate-800 bg-slate-900/80 p-6 text-slate-100 shadow-xl">
                            <h1 className="text-xl font-semibold">Email Logs Unavailable</h1>
                            <p className="mt-2 text-sm text-slate-300">
                              You need both <code>email.core</code> and <code>email.logs</code>
                              access to open this page.
                            </p>
                          </div>
                        }
                      >
                        <Emails />
                      </RequireFeature>
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route path="/email" element={<Navigate to="/emails" replace />} />
              <Route path="/email-logs" element={<Navigate to="/emails" replace />} />

              {/* Notifications Center */}
              <Route
                path="/notifications"
                element={
                  <RequireAuth>
                    <Layout>
                      <NotificationsPage />
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* Finance specific routes */}
              <Route
                path="/ai-bots/finance"
                element={
                  <RequireAuth>
                    <Layout>
                      <RequireFeature featureKeys={["finance_bot"]}>
                        <AIFinanceBot />
                      </RequireFeature>
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/finance_bot"
                element={
                  <RequireAuth>
                    <Layout>
                      <RequireFeature featureKeys={["finance_bot"]}>
                        <AIFinanceBot />
                      </RequireFeature>
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/payment"
                element={
                  <RequireAuth>
                    <Layout>
                      <PaymentBotDashboard />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/ai-bots/payment-gateway"
                element={
                  <RequireAuth>
                    <Layout>
                      <PaymentBotDashboard />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/pay-demo"
                element={
                  <Layout>
                    <PaymentLinkDemo />
                  </Layout>
                }
              />
              <Route
                path="/pay/:paymentId"
                element={
                  <Layout>
                    <PaymentLinkPage />
                  </Layout>
                }
              />
              <Route
                path="/payments/:invoiceId"
                element={
                  <RequireAuth>
                    <Layout>
                      <PaymentPage />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/payments/success"
                element={
                  <Layout>
                    <PaymentSuccessPage />
                  </Layout>
                }
              />
              <Route
                path="/payments/failed"
                element={
                  <Layout>
                    <PaymentFailedPage />
                  </Layout>
                }
              />
              <Route
                path="/payments/history"
                element={
                  <RequireAuth>
                    <Layout>
                      <PaymentBotDashboard />
                    </Layout>
                  </RequireAuth>
                }
              />
              <Route
                path="/finance/reports"
                element={
                  <RequireAuth>
                    <Layout>
                      <RequireFeature featureKeys={["financial_reports"]}>
                        <Finance />
                      </RequireFeature>
                    </Layout>
                  </RequireAuth>
                }
              />

              {/* ===== Admin / Enterprise Routes ===== */}
              <Route
                path="/admin"
                element={
                  <RequireAuth allowedRoles={['admin', 'super_admin']}>
                    <AdminLayout />
                  </RequireAuth>
                }
              >
                <Route index element={<Navigate to="overview" replace />} />
                <Route path="overview" element={<AdminOverview />} />
                <Route path="users" element={<AdminUsers />} />
                <Route path="settings" element={<PlatformSettings />} />
                <Route path="subscriptions" element={<PricingManagement />} />
                <Route path="tenants" element={<TenantManagement />} />
                <Route path="audit-logs" element={<AuditLogs />} />
                <Route path="feature-flags" element={<FeatureFlagsManager />} />
                <Route path="portal-requests" element={<PortalRequests />} />
                <Route path="notifications" element={<AdminNotifications />} />
                <Route path="requests/:requestId/audit-log" element={<RequestAuditLog />} />
                <Route path="tms-access" element={<TMSAccess />} />
                <Route path="governance" element={<Governance />} />
                <Route path="platform-expenses" element={<PlatformExpenses />} />
                <Route path="fleet" element={<Navigate to="/ai-bots/freight_broker/vehicles" replace />} />
                <Route path="fleet/live-map" element={<Navigate to="/ai-bots/freight_broker/live-map" replace />} />
                <Route path="drivers" element={<AdminDrivers />} />
                <Route path="operations" element={<OperationsManager />} />
                <Route path="orchestration" element={<OrchestrationDashboard />} />
                <Route path="partners" element={<Partners />} />
                <Route path="logistics-partners" element={<Partners />} />
                <Route path="ai/general-manager" element={<AIGeneralManagerAdmin />} />
                <Route path="ai/strategy-advisor" element={<StrategyAdvisor />} />
                <Route path="ai/marketing-bot" element={<MarketingBot />} />
                <Route path="ai/call-manager" element={<AICallManager />} />
                <Route path="dev/settings" element={<DevBotSettings />} />
                <Route path="carriers" element={<CarrierScoreboard />} />
                <Route path="support" element={<SupportCenter />} />
                <Route path="support/tickets" element={<SupportTickets />} />
                <Route path="system-health" element={<SystemHealth />} />
                <Route path="settings/footer" element={<AdminFooterSettings />} />
                <Route path="org" element={<Navigate to="/admin" replace />} />
                <Route path="platform-settings" element={<Navigate to="/admin/settings" replace />} />
                <Route path="system" element={<Navigate to="/admin/system-health" replace />} />
                <Route path="system/monitor" element={<Navigate to="/admin/system-health" replace />} />
                <Route path="users-roles" element={<Navigate to="/admin/users" replace />} />
                <Route path="Users&Roles" element={<Navigate to="/admin/users" replace />} />
                <Route path="Admin-Users" element={<Navigate to="/admin/users" replace />} />
                <Route path="maintenance-center" element={<MaintenanceCenterPage />} />
                <Route path="api-connections" element={<APIConnectionsManager />} />
                <Route path="TheVIZION" element={<TheVIZIONDashboard />} />
                <Route path="TheVIZION/task-manager" element={<TaskManager />} />
                {/* Market Intelligence */}
                <Route path="market-intelligence" element={<MarketIntelligenceDashboard />} />
                {/* Reports */}
                <Route path="reports" element={<ReportsDashboard />} />
              </Route>



              {/* Terms and Conditions */}
              <Route
                path="/terms-and-conditions"
                element={<TermsAndConditions />}
              />

              {/* Support System Routes */}
              {getSupportRoutes()}

              {/* 404 - Protected */}
              <Route
                path="*"
                element={
                  <RequireAuth>
                    <Layout>
                      <NotFound />
                    </Layout>
                  </RequireAuth>
                }
              />
            </Routes>
          </div>
        </Suspense>
      </AuthChecker>
      </NotificationProvider>
    </ErrorBoundary>
  );
};

export default App;
