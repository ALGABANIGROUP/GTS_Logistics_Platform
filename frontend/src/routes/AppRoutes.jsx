import { Routes, Route, Navigate } from "react-router-dom";
import AuthLanding from "../pages/AuthLanding";
import Dashboard from "../pages/Dashboard";
import AccountInactive from "../pages/auth/AccountInactive";
import PricingPage from "../pages/PricingPage";
import { useAuth } from "../contexts/AuthContext";
import RequireAuth from "../components/RequireAuth";
import Unauthorized from "../pages/Unauthorized";

function RootRoute() {
    const { isAuthenticated, loading, accountStatus } = useAuth();
    if (loading) return null;
    if (isAuthenticated && accountStatus && accountStatus !== "active") {
        return <AccountInactive />;
    }
    return isAuthenticated ? <Dashboard /> : <AuthLanding />;
}

export default function AppRoutes() {
    return (
        <Routes>
            <Route path="/" element={<RootRoute />} />
            <Route path="/login" element={<AuthLanding />} />
            <Route path="/account-inactive" element={<AccountInactive />} />
            <Route path="/register" element={<Navigate to="/login" replace />} />
            <Route path="/unauthorized" element={<Unauthorized />} />
            <Route
                path="/pricing"
                element={<PricingPage />}
            />
            <Route
                path="/pricing-management"
                element={
                    <RequireAuth roles={["admin", "super_admin"]}>
                        <PricingPage />
                    </RequireAuth>
                }
            />
            {/* fallback */}
            <Route path="*" element={<RootRoute />} />
        </Routes>
    );
}
