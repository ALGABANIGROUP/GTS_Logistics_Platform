/**
 * AIBotPage (Enhanced) - Unified Bot Control Page
 * Uses the new BotControlInterface for improved functionality
 */
import { useMemo } from "react";
import { Link } from "react-router-dom";
import SystemReadinessGate from "./SystemReadinessGate.jsx";
import { BotControlInterface } from "./bots";

// Bot-specific interface mapping
const BOT_INTERFACES = {
    mapleload_canada: () => import("./bots/MapleLoadCanadaInterface"),
    executive_intelligence: () => import("./bots/ExecutiveIntelligenceInterface"),
    maintenance_dev: () => import("./bots/MaintenanceDevInterface"),
    freight_bookings: () => import("./bots/FreightBookingsInterface"),
};

export default function AIBotPageEnhanced({
    botKey,
    title,
    description,
    defaultMessage = "",
    relatedLinks = [],
    metaSource = "ui",
    mode = "active",
    preview = false,
    useSpecializedInterface = true, // Flag to use specialized interfaces if available
}) {
    const botLabel = title || botKey;
    const isPreview = preview || mode === "preview";

    // Build bot config from props
    const botConfig = useMemo(() => ({
        displayName: title || botKey,
        description: description,
        mode: isPreview ? "preview" : mode,
        capabilities: [],
        commands: [],
    }), [title, botKey, description, isPreview, mode]);

    // Check if this bot has a specialized interface
    const hasSpecializedInterface = BOT_INTERFACES.hasOwnProperty(botKey);

    // For now, we always use the generic BotControlInterface
    // Specialized interfaces can be lazy-loaded if needed
    return (
        <SystemReadinessGate>
            <div className="space-y-6">
                {/* Page Header */}
                <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                        <div className="text-2xl font-semibold text-white">
                            {botLabel || "AI Bot"}
                        </div>
                        {description ? (
                            <div className="mt-1 text-sm text-slate-300">{description}</div>
                        ) : null}
                    </div>
                    <div className="flex items-center gap-2">
                        {hasSpecializedInterface && (
                            <span className="rounded-full bg-indigo-500/20 px-3 py-1 text-xs font-medium text-indigo-300">
                                ✨ Enhanced Interface
                            </span>
                        )}
                        {botKey ? (
                            <span className="rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-200">
                                {botKey}
                            </span>
                        ) : null}
                    </div>
                </div>

                {/* Related Links */}
                {relatedLinks && relatedLinks.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                        {relatedLinks.map((link, i) => (
                            <Link
                                key={i}
                                to={link.to}
                                className="flex items-center gap-1.5 rounded-lg bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-white/10 hover:text-white"
                            >
                                {link.icon && <span>{link.icon}</span>}
                                {link.label}
                            </Link>
                        ))}
                    </div>
                )}

                {/* Bot Control Interface */}
                <BotControlInterface
                    botKey={botKey}
                    botConfig={botConfig}
                    mode={isPreview ? "preview" : mode}
                />
            </div>
        </SystemReadinessGate>
    );
}
