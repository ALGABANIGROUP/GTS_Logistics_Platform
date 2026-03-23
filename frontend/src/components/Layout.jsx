import React, { Suspense, useEffect } from "react";
import { useLocation } from "react-router-dom";
import AppShell from "./AppShell.jsx";
import { useAuth } from "../contexts/AuthContext";
import { useCurrencyStore } from "../stores/useCurrencyStore";

const AdminLayout = React.lazy(() => import("../layouts/AdminLayout.jsx"));

export default function Layout({ children }) {
  const location = useLocation();
  const { user } = useAuth();
  const { initializeCurrencyFromUser } = useCurrencyStore();

  // Sync currency with user's country
  useEffect(() => {
    if (user?.country) {
      initializeCurrencyFromUser(user.country);
    }
  }, [user?.country, initializeCurrencyFromUser]);

  if (location.pathname.startsWith("/admin")) {
    return (
      <Suspense fallback={<AppShell>{children}</AppShell>}>
        <AdminLayout>{children}</AdminLayout>
      </Suspense>
    );
  }
  return <AppShell>{children}</AppShell>;
}
Layout.displayName = "Layout";
