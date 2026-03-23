import { useEffect } from "react";
import truckBg from "../assets/bg_login.png";

export default function AuthLayout({ children }) {
    useEffect(() => {
        if (typeof document === "undefined") return undefined;
        const body = document.body;
        if (!body) return undefined;
        body.classList.add("gts-no-bg");
        return () => body.classList.remove("gts-no-bg");
    }, []);

    return (
        <div className="auth-shell min-h-screen h-screen w-full overflow-hidden overscroll-none relative">
            <div
                className="absolute inset-0"
                style={{
                    backgroundImage: `url(${truckBg})`,
                    backgroundSize: "cover",
                    backgroundPosition: "left center",
                    backgroundRepeat: "no-repeat",
                }}
            />
            <div className="absolute inset-0 z-0 pointer-events-none bg-gradient-to-b from-black/35 to-black/10" />
            <div className="relative z-10 h-full w-full flex items-center justify-center pt-24 sm:pt-28">
                {children}
            </div>
        </div>
    );
}
