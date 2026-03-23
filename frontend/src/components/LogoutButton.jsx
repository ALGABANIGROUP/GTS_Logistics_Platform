// File: frontend/src/components/LogoutButton.jsx (UPDATE)
import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext.jsx";

const LogoutButton = () => {
    const navigate = useNavigate();
    const { logout } = useAuth();

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <button
            onClick={handleLogout}
            className="px-3 py-1.5 rounded bg-red-600 hover:bg-red-700 text-white text-sm font-medium transition"
        >
            Logout
        </button>
    );
};

export default LogoutButton;
