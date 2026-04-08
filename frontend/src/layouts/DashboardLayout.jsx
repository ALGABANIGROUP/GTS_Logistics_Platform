import React from "react";
import Footer from "../components/ui/Footer.jsx";

export default function DashboardLayout({ children }) {
    return (
        <div className="dashboard-bg min-h-screen flex flex-col">
            <div className="flex-1">
                {children}
            </div>
            <Footer />
        </div>
    );
}
