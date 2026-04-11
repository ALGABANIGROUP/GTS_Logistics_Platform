import React from "react";
import ReactDOM from "react-dom/client";
import * as Sentry from "@sentry/react";
import "./index.css";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext.jsx";
import { SystemReadinessProvider } from "./contexts/SystemReadinessContext.jsx";
import { TranslationProvider } from "./contexts/TranslationContext.jsx";
import { NotificationProvider } from "./contexts/NotificationContext.jsx";
import EntitlementsProvider from "./components/EntitlementsProvider.jsx";
import ErrorBoundary from "./components/ErrorBoundary.jsx";
import BodyClassGate from "./components/BodyClassGate.jsx";
import { installNetworkRuntime } from "./bootstrap/networkRuntime.js";
import appPackage from "../package.json";
import "./styles/theme.css";
import "./styles/glassmorphism.css";
import "./styles/buttons.css";
import "./styles/glass.css";
import "./styles/truck-orbit-spinner.css";

const APP_VERSION = appPackage?.version || "1.0.0-rc.1";
const GA_MEASUREMENT_ID = import.meta.env.VITE_GA_MEASUREMENT_ID;
const COOKIE_CONSENT_STORAGE_KEY = "cookie_consent";

const readStoredCookieConsent = () => {
  try {
    return window.localStorage.getItem(COOKIE_CONSENT_STORAGE_KEY);
  } catch {
    return null;
  }
};

const buildConsentPayload = (status) => ({
  ad_storage: status,
  ad_user_data: status,
  ad_personalization: status,
  analytics_storage: status,
  functionality_storage: status,
  personalization_storage: status,
  security_storage: "granted",
});

const ensureGoogleTagScript = (measurementId) => {
  if (document.querySelector(`script[data-gtag-id="${measurementId}"]`)) {
    return;
  }

  const gtagScript = document.createElement("script");
  gtagScript.async = true;
  gtagScript.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
  gtagScript.dataset.gtagId = measurementId;
  document.head.appendChild(gtagScript);
};

const configureGoogleAnalytics = (measurementId) => {
  if (window.__GTS_GA_CONFIGURED__ === measurementId) {
    return;
  }

  ensureGoogleTagScript(measurementId);
  window.gtag("js", new Date());
  window.gtag("config", measurementId, {
    send_page_view: true,
    anonymize_ip: true,
  });
  window.__GTS_GA_CONFIGURED__ = measurementId;
};

const STAGE0_CLEAR_KEYS = ["auth_context", "user", "entitlements"];
if (typeof window !== "undefined") {
  try {
    if (!window.localStorage.getItem("gts_stage0_cleared")) {
      STAGE0_CLEAR_KEYS.forEach((key) => window.localStorage.removeItem(key));
      window.localStorage.setItem("gts_stage0_cleared", "1");
    }
    window.__GTS_DISABLE_DEV_TOKEN__ = true;
  } catch {
    // ignore storage errors
  }
}

if (typeof window !== "undefined" && GA_MEASUREMENT_ID) {
  window.dataLayer = window.dataLayer || [];
  window.gtag =
    window.gtag ||
    function gtag() {
      window.dataLayer.push(arguments);
    };

  window.__GTS_UPDATE_GOOGLE_CONSENT__ = (status) => {
    const normalizedStatus = status === "granted" ? "granted" : "denied";
    window.gtag("consent", "update", buildConsentPayload(normalizedStatus));

    if (normalizedStatus === "granted") {
      configureGoogleAnalytics(GA_MEASUREMENT_ID);
    }
  };

  window.gtag("consent", "default", {
    ...buildConsentPayload("denied"),
    wait_for_update: 500,
  });

  const storedConsent = readStoredCookieConsent();
  if (storedConsent === "accepted") {
    window.__GTS_UPDATE_GOOGLE_CONSENT__("granted");
  } else if (storedConsent === "declined") {
    window.__GTS_UPDATE_GOOGLE_CONSENT__("denied");
  }
}

installNetworkRuntime();

// Initialize Sentry for error monitoring and performance tracking
const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN;
const SENTRY_ENV = import.meta.env.VITE_SENTRY_ENVIRONMENT || "development";
const TRACES = Number(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE || 0);
const REPLAY_SESSION = Number(
  import.meta.env.VITE_SENTRY_REPLAY_SESSION_SAMPLE_RATE || 0
);
const REPLAY_ON_ERROR = Number(
  import.meta.env.VITE_SENTRY_REPLAY_ON_ERROR_SAMPLE_RATE || 0
);

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: SENTRY_ENV,
    tracesSampleRate: TRACES,
    replaysSessionSampleRate: REPLAY_SESSION,
    replaysOnErrorSampleRate: REPLAY_ON_ERROR,
    sendDefaultPii: false,
    beforeSend(event) {
      if (event.request?.headers) {
        delete event.request.headers["authorization"];
        delete event.request.headers["Authorization"];
      }
      return event;
    },
  });

  // Make Sentry available globally for context setting
  window.Sentry = Sentry;
}

const App = React.lazy(() => import("./App.jsx"));

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <BodyClassGate />
        <AuthProvider>
          <SystemReadinessProvider>
            <TranslationProvider>
              <NotificationProvider>
                <EntitlementsProvider>
                  <React.Suspense
                    fallback={
                      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center">
                        <div className="text-center">
                          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4" />
                          <p className="text-slate-200">Loading...</p>
                          <p className="text-sm text-slate-400 mt-2">
                            Gabani Transport Solutions (GTS) Platform
                          </p>
                        </div>
                      </div>
                    }
                  >
                    <App />
                  </React.Suspense>
                </EntitlementsProvider>
              </NotificationProvider>
            </TranslationProvider>
          </SystemReadinessProvider>
        </AuthProvider>
        <div className="pointer-events-none fixed bottom-2 left-2 z-[9999] rounded-md border border-white/15 bg-slate-950/80 px-2 py-1 text-[11px] font-semibold text-slate-200 backdrop-blur">
          v{APP_VERSION}
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
);
