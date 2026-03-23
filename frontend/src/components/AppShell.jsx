import React, { useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import Sidebar from "./Sidebar.jsx";
import TopUserBar from "./TopUserBar.jsx";
import SystemSwitcher from "./SystemSwitcher.jsx";
import SocialMediaFooter from "./layout/SocialMediaFooter.jsx";
import { UiActionsProvider } from "../contexts/UiActionsContext.jsx";
import RootLayout from "./RootLayout.jsx";
import { Menu, X } from "lucide-react";
import NotificationBell from "./notifications/NotificationBell.jsx";
import SmartSearchBar from "./search/SmartSearchBar.jsx";

export default function AppShell({ children }) {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true); // Always start with sidebar open

  const isAuthPage = useMemo(() => {
    return ["/", "/login", "/register", "/forgot-password"].some((p) =>
      p === "/" ? location.pathname === "/" : location.pathname.startsWith(p)
    );
  }, [location.pathname]);

  const isGlassExcluded = useMemo(() => {
    const path = location.pathname;
    const authPaths = [
      "/",
      "/login",
      "/register",
      "/forgot-password",
      "/reset-password",
      "/verify-email",
      "/request-received",
    ];
    const portalPaths = ["/portal", "/partner-portal"];
    const isAuthRoute = authPaths.some((p) =>
      p === "/" ? path === "/" : path.startsWith(p)
    );
    const isPortalRoute = portalPaths.some((p) =>
      path === p || path.startsWith(`${p}/`)
    );
    return isAuthRoute || isPortalRoute;
  }, [location.pathname]);

  useEffect(() => {
    if (typeof document === "undefined") return;
    document.body.classList.toggle("gts-glass-lite", !isGlassExcluded);
    document.body.classList.toggle("gts-no-bg", isGlassExcluded);
    return () => {
      document.body.classList.remove("gts-glass-lite");
      document.body.classList.remove("gts-no-bg");
    };
  }, [isGlassExcluded]);

  if (isAuthPage) {
    return <>{children}</>;
  }

  const showSidebar = true; // Always show sidebar
  const showTopBar = true;

  const topbar = (
    <div className="w-full flex flex-wrap items-center justify-between gap-4 px-4 py-3 lg:px-6">
      <div className="flex min-w-0 items-center gap-3">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-lg hover:bg-white/10 transition text-slate-300 hover:text-white"
          title={sidebarOpen ? "Hide sidebar" : "Show sidebar"}
        >
          {sidebarOpen ? (
            <X className="h-5 w-5" />
          ) : (
            <Menu className="h-5 w-5" />
          )}
        </button>
        <div className="min-w-0">
          <div className="truncate text-sm font-semibold tracking-wide text-white">
            Gabani Transport Solutions
          </div>
          <div className="truncate text-xs text-slate-300">
            Logistics Command Platform
          </div>
        </div>
      </div>

      <div className="flex flex-1 justify-center px-2">
        <SmartSearchBar />
      </div>

      {showTopBar ? (
        <div className="flex items-center gap-3">
          <SystemSwitcher className="ml-2" />
          <NotificationBell />
          <TopUserBar />
        </div>
      ) : null}
    </div>
  );

  return (
    <UiActionsProvider>
      <RootLayout
        className="glass-page gts-app"
        sidebar={showSidebar ? <Sidebar /> : null}
        topbar={topbar}
        footer={<SocialMediaFooter />}
        contentClassName="px-4 py-6 lg:px-6 lg:py-8"
      >
        {children}
      </RootLayout>
    </UiActionsProvider>
  );
}
