// frontend/src/components/security/InactivityWatcher.jsx
import React, { useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { useAuth } from "../../contexts/AuthContext.jsx";

const InactivityWatcher = ({
    timeoutMinutes = 30,
    warningMinutesBefore = 2,
}) => {
    const auth = useAuth ? useAuth() : null;
    const navigate = useNavigate();
    const location = useLocation();

    const logoutTimerRef = useRef(null);
    const warningTimerRef = useRef(null);
    const lastActivityRef = useRef(Date.now());

    const clearTimers = () => {
        if (logoutTimerRef.current) {
            clearTimeout(logoutTimerRef.current);
            logoutTimerRef.current = null;
        }
        if (warningTimerRef.current) {
            clearTimeout(warningTimerRef.current);
            warningTimerRef.current = null;
        }
    };

    const performLogout = () => {
        clearTimers();

        const logoutFn =
            auth?.logout || auth?.signOut || auth?.clearSession || null;

        try {
            if (logoutFn) {
                logoutFn();
            } else if (auth?.setUser) {
                auth.setUser(null);
            }
        } catch (e) {
            console.error("[InactivityWatcher] logout error:", e);
        }

        toast.info("You have been logged out due to inactivity.");
        navigate("/login", { replace: true });
    };

    const scheduleTimers = () => {
        clearTimers();

        const timeoutMs = timeoutMinutes * 60 * 1000;
        const warningMs = Math.max(
            0,
            (timeoutMinutes - warningMinutesBefore) * 60 * 1000
        );

        if (warningMs > 0) {
            warningTimerRef.current = setTimeout(() => {
                const idleMs = Date.now() - lastActivityRef.current;
                const remainingSeconds = Math.max(
                    0,
                    Math.round((timeoutMs - idleMs) / 1000)
                );
                toast.warning(
                    `You will be logged out in about ${remainingSeconds} seconds due to inactivity.`
                );
            }, warningMs);
        }

        logoutTimerRef.current = setTimeout(() => {
            performLogout();
        }, timeoutMs);
    };

    useEffect(() => {
        if (!auth || !auth.isAuthenticated) {
            clearTimers();
            return;
        }

        lastActivityRef.current = Date.now();
        scheduleTimers();

        const handleActivity = () => {
            lastActivityRef.current = Date.now();
            scheduleTimers();
        };

        const events = [
            "mousemove",
            "keydown",
            "click",
            "scroll",
            "touchstart",
            "touchmove",
        ];

        events.forEach((evt) => window.addEventListener(evt, handleActivity));

        return () => {
            clearTimers();
            events.forEach((evt) => window.removeEventListener(evt, handleActivity));
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [auth?.isAuthenticated, location.pathname]);

    return null;
};

export default InactivityWatcher;
