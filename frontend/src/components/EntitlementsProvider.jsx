import React, { useEffect } from "react";
import { useEntitlements } from "../stores/useEntitlements";
import { useAuth } from "../contexts/AuthContext.jsx";

export default function EntitlementsProvider({ children }) {
    const auth = useAuth();
    const isAuthenticated = Boolean(auth?.isAuthenticated);
    const init = useEntitlements((s) => s.init);

    useEffect(() => {
        if (!isAuthenticated) return;
        if (typeof init === "function") init();
    }, [isAuthenticated, init]);

    return <>{children}</>;
}
