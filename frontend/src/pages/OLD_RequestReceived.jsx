import React, { useMemo, useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

import portalBg from "@/assets/PortalLanding-DLRewip6.png";

function useQuery() {
    const { search } = useLocation();
    return useMemo(() => new URLSearchParams(search), [search]);
}

export default function RequestReceived() {
    const location = useLocation();
    const query = useQuery();
    const [showSuccess, setShowSuccess] = useState(false);
    const requestId = location.state?.requestId || query.get("requestId") || query.get("id");

    useEffect(() => {
        if (typeof window !== "undefined" && sessionStorage.getItem("access_request_submitted")) {
            setShowSuccess(true);
            sessionStorage.removeItem("access_request_submitted");
        } else {
            setShowSuccess(false);
        }
    }, []);

    if (!showSuccess) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-black/60 text-white text-xl">
                Access request not found or already viewed.
            </div>
        );
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center px-4 py-8 fixed inset-0" style={{ backgroundImage: `url(${portalBg})` }}>
            <div className="bg-white/80 rounded-xl shadow-lg p-8 max-w-md w-full flex flex-col items-center">
                <div className="text-2xl font-bold text-emerald-700 mb-2">Your request has been received successfully.</div>
                <div className="text-slate-700 mb-4 text-center">
                    Your application will be reviewed by management and you will be contacted via email shortly.<br />
                    Request number: <span className="font-mono text-emerald-900">{requestId || "-"}</span>
                </div>
                <div className="mt-6 flex flex-col gap-3 w-full">
                    <Link
                        to="/login"
                        className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-center py-2.5 font-semibold transition-all"
                    >
                        Login
                    </Link>
                    <Link
                        to="/"
                        className="w-full rounded-lg bg-white/10 hover:bg-white/15 text-emerald-900 text-center py-2.5 font-semibold transition-all"
                    >
                        Back to the portal
                    </Link>
                </div>
            </div>
        </div>
    );
}
