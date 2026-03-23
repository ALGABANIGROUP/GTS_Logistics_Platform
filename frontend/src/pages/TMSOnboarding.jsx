import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function TMSOnboarding() {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(0);

    const steps = [
        {
            title: "Welcome to GTS TMS",
            subtitle: "Transport Management System",
            content: (
                <div className="space-y-4">
                    <p className="text-slate-300">
                        The TMS (Transport Management System) is your unified command center for managing freight operations, shipments, and logistics coordination.
                    </p>
                    <div className="rounded-lg bg-blue-500/10 border border-blue-400/30 p-3">
                        <p className="text-sm text-blue-200">
                            This is your first time accessing TMS. Let's walk you through the key features.
                        </p>
                    </div>
                </div>
            ),
        },
        {
            title: "Dashboard Overview",
            subtitle: "Your operational hub",
            content: (
                <div className="space-y-3">
                    <p className="text-slate-300">
                        The TMS Dashboard displays:
                    </p>
                    <ul className="space-y-2 text-sm text-slate-300">
                        <li className="flex gap-2">
                            <span className="text-emerald-400">✓</span>
                            <span><strong>System Status</strong> — Current TMS health and availability</span>
                        </li>
                        <li className="flex gap-2">
                            <span className="text-emerald-400">✓</span>
                            <span><strong>Available Bots</strong> — AI assistants ready to execute operations</span>
                        </li>
                        <li className="flex gap-2">
                            <span className="text-emerald-400">✓</span>
                            <span><strong>Shipment Lifecycle</strong> — Track loads from creation to delivery</span>
                        </li>
                        <li className="flex gap-2">
                            <span className="text-emerald-400">✓</span>
                            <span><strong>Bot Execution</strong> — Run automated tasks on-demand</span>
                        </li>
                    </ul>
                </div>
            ),
        },
        {
            title: "Key Features",
            subtitle: "What you can do with TMS",
            content: (
                <div className="space-y-3">
                    <div className="rounded-lg bg-slate-900/50 border border-white/10 p-3">
                        <p className="font-semibold text-white mb-1">Freight Broker Bot</p>
                        <p className="text-sm text-slate-300">Automate load matching and carrier assignments</p>
                    </div>
                    <div className="rounded-lg bg-slate-900/50 border border-white/10 p-3">
                        <p className="font-semibold text-white mb-1">Finance Bot</p>
                        <p className="text-sm text-slate-300">Track invoices, expenses, and profitability per shipment</p>
                    </div>
                    <div className="rounded-lg bg-slate-900/50 border border-white/10 p-3">
                        <p className="font-semibold text-white mb-1">Operations Manager</p>
                        <p className="text-sm text-slate-300">Coordinate resources, scheduling, and real-time updates</p>
                    </div>
                </div>
            ),
        },
        {
            title: "Getting Started",
            subtitle: "First steps",
            content: (
                <div className="space-y-4">
                    <ol className="space-y-3 text-sm text-slate-300">
                        <li className="flex gap-3">
                            <span className="font-semibold text-blue-400 min-w-fit">1. Navigate</span>
                            <span>Go to the TMS section from the main sidebar menu</span>
                        </li>
                        <li className="flex gap-3">
                            <span className="font-semibold text-blue-400 min-w-fit">2. Review</span>
                            <span>Check the System Status and available bots</span>
                        </li>
                        <li className="flex gap-3">
                            <span className="font-semibold text-blue-400 min-w-fit">3. Execute</span>
                            <span>Select a bot and provide input parameters</span>
                        </li>
                        <li className="flex gap-3">
                            <span className="font-semibold text-blue-400 min-w-fit">4. Monitor</span>
                            <span>Track bot execution status and results in real-time</span>
                        </li>
                    </ol>
                    <div className="rounded-lg bg-amber-500/10 border border-amber-400/30 p-3">
                        <p className="text-sm text-amber-200">
                            💡 <strong>Tip:</strong> Most bots run on a schedule. You can also trigger them manually from the TMS dashboard.
                        </p>
                    </div>
                </div>
            ),
        },
        {
            title: "Need Help?",
            subtitle: "Support and resources",
            content: (
                <div className="space-y-3">
                    <p className="text-slate-300">
                        If you have questions or need assistance:
                    </p>
                    <ul className="space-y-2 text-sm text-slate-300">
                        <li className="flex gap-2">
                            <span className="text-blue-400">→</span>
                            <span>Check the <strong>Support Center</strong> in Admin for FAQs</span>
                        </li>
                        <li className="flex gap-2">
                            <span className="text-blue-400">→</span>
                            <span>View <strong>Bot Documentation</strong> before executing</span>
                        </li>
                        <li className="flex gap-2">
                            <span className="text-blue-400">→</span>
                            <span>Contact support@example.com for urgent issues</span>
                        </li>
                    </ul>
                </div>
            ),
        },
    ];

    const step = steps[currentStep];
    const isLast = currentStep === steps.length - 1;

    return (
        <div className="min-h-screen bg-slate-950 p-6">
            <div className="max-w-2xl mx-auto">
                {/* Header */}
                <div className="mb-8 text-center">
                    <h1 className="text-3xl font-bold text-white mb-2">{step.title}</h1>
                    <p className="text-slate-400">{step.subtitle}</p>
                </div>

                {/* Progress bar */}
                <div className="mb-8 flex gap-2">
                    {steps.map((_, i) => (
                        <div
                            key={i}
                            className={`flex-1 h-1 rounded-full transition ${i <= currentStep ? "bg-blue-500" : "bg-slate-700"
                                }`}
                        />
                    ))}
                </div>

                {/* Content */}
                <div className="mb-8 rounded-xl border border-white/15 bg-white/5 p-6 backdrop-blur">
                    {step.content}
                </div>

                {/* Navigation */}
                <div className="flex items-center justify-between gap-4">
                    <button
                        onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
                        disabled={currentStep === 0}
                        className="px-4 py-2 rounded-lg border border-white/15 text-slate-100 hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                    >
                        Previous
                    </button>

                    <span className="text-sm text-slate-400">
                        {currentStep + 1} / {steps.length}
                    </span>

                    {isLast ? (
                        <button
                            onClick={() => navigate("/tms")}
                            className="px-6 py-2 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 text-sm font-medium shadow-lg shadow-emerald-600/25"
                        >
                            Go to TMS Dashboard
                        </button>
                    ) : (
                        <button
                            onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
                            className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-500 text-sm font-medium"
                        >
                            Next
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
