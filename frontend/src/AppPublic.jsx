import React, { Suspense } from "react";
import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import AuthLayout from "./layouts/AuthLayout";
import AuthLanding from "./pages/AuthLanding";
import PortalLanding from "./pages/PortalLanding";
import Register from "./pages/Register";
import RequestReceived from "./pages/RequestReceived";
import VerifyEmail from "./pages/VerifyEmail";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import PublicOnly from "./components/PublicOnly";
import AccountInactive from "./pages/auth/AccountInactive";

const LoadingFallback = () => (
  <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4" />
      <p className="text-slate-200">Loading...</p>
      <p className="text-sm text-slate-400 mt-2">Gabani Transport Solutions (GTS) Platform</p>
    </div>
  </div>
);

export default function AppPublic() {
  const AuthShell = () => (
    <AuthLayout>
      <Outlet />
    </AuthLayout>
  );

  return (
    <Suspense fallback={<LoadingFallback />}>
      <div className="app-root glass-page">
        <Routes>
          <Route element={<PublicOnly />}>
            <Route path="/" element={<PortalLanding />} />
            <Route element={<AuthShell />}>
              <Route path="/login" element={<AuthLanding />} />
            </Route>
            <Route path="/account-inactive" element={<AccountInactive />} />
            <Route path="/register" element={<Register />} />
            <Route path="/request-received" element={<RequestReceived />} />
            <Route path="/verify-email" element={<VerifyEmail />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
          </Route>
        </Routes>
      </div>
    </Suspense>
  );
}
