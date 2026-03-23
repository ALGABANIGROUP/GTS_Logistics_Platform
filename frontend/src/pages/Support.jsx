import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function Support() {
    const navigate = useNavigate();

    useEffect(() => {
        // Redirect to Customer Service Bot
        navigate("/ai-bots/customer-service", { replace: true });
    }, [navigate]);

    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
                <div className="text-6xl mb-4">🤖</div>
                <p className="text-xl text-white">Redirecting to Customer Service Bot...</p>
            </div>
        </div>
    );
}

export default Support;
