import React from "react";
import { Link } from "react-router-dom";
import gtsLogo from "../assets/gabani_logo.png";
import { useAuth } from "../contexts/AuthContext.jsx";

const Header = () => {
    const { user, isAuthenticated } = useAuth();

    return (
        <header className="sticky top-0 z-50 border-b border-white/10 bg-black/85 backdrop-blur-md">
            <div className="container mx-auto flex items-center justify-between px-4 py-3">
                <Link to="/" className="flex items-center gap-3">
                    <img src={gtsLogo} alt="GTS Logistics" className="h-8 w-auto" />
                    <span className="hidden sm:inline text-white font-semibold text-lg">GTS Logistics</span>
                </Link>

                <nav className="flex items-center gap-4">
                    <Link to="/pricing" className="text-white/75 hover:text-white text-sm transition">
                        Pricing
                    </Link>
                    <Link to="/contact" className="text-white/75 hover:text-white text-sm transition">
                        Support
                    </Link>
                    {isAuthenticated && user ? (
                        <Link
                            to="/dashboard"
                            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-700"
                        >
                            Dashboard
                        </Link>
                    ) : (
                        <Link
                            to="/login"
                            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-700"
                        >
                            Sign In
                        </Link>
                    )}
                </nav>
            </div>
        </header>
    );
};

export default Header;
