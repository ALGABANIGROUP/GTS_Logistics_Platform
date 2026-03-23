import React from "react";

export default function GlassCard({ children, className = "", onClick, style }) {
    return (
        <div
            className={[
                "rounded-2xl border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl p-6 md:p-8",
                className,
            ]
                .filter(Boolean)
                .join(" ")}
            onClick={onClick}
            style={style}
        >
            {children}
        </div>
    );
}
