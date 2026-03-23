import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const LogoutPage = () => {
    const navigate = useNavigate();
    const { logout } = useAuth();

    useEffect(() => {
        const performLogout = async () => {
            try {
                // Call the logout function from auth context
                if (logout) {
                    await logout();
                }

                // Redirect to login after a short delay
                setTimeout(() => {
                    navigate("/login", { replace: true });
                }, 500);
            } catch (error) {
                console.error("Logout error:", error);
                // Still redirect even if there's an error
                navigate("/login", { replace: true });
            }
        };

        performLogout();
    }, [navigate, logout]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
            <div className="text-center">
                <div className="mb-4">
                    <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-blue-500/10 mb-4">
                        <svg
                            className="h-6 w-6 text-blue-500 animate-spin"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                        >
                            <circle
                                className="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="currentColor"
                                strokeWidth="4"
                            ></circle>
                            <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            ></path>
                        </svg>
                    </div>
                </div>
                <h1 className="text-2xl font-bold text-white mb-2">Logging out...</h1>
                <p className="text-slate-400">You will be redirected shortly</p>
            </div>
        </div>
    );
};

export default LogoutPage;
