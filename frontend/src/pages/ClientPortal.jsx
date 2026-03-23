// src/pages/ClientPortal.jsx
import React from "react";
import { Link } from "react-router-dom";
import AuthLayout from "@/components/AuthLayout";

const ClientPortal = () => {
    return (
        <AuthLayout
            title="GTS Client Portal"
            subtitle="Give your shippers and fleet partners a clean, whitelabel-ready tracking experience."
        >
            <div className="grid gap-6 md:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)] items-start">
                <div className="space-y-4 text-sm text-slate-100">
                    <p className="text-slate-200/90">
                        This view represents the whitelabel experience that your customers
                        see. It can be branded with their logo, colors, and domain while
                        still powered by the GTS engine in the background.
                    </p>

                    <ul className="space-y-2 text-[13px] text-slate-100/90">
                        <li>• Live shipment tracking with map and timeline.</li>
                        <li>• Document access (BOL, invoices, POD) per shipment.</li>
                        <li>• Secure messaging with your dispatch team.</li>
                        <li>• Simple, mobile-friendly layout for shippers.</li>
                    </ul>

                    <div className="mt-3 flex flex-wrap gap-3 text-[11px]">
                        <Link
                            to="/dashboard"
                            className="inline-flex items-center rounded-lg bg-sky-500 px-4 py-2 text-xs font-semibold text-white shadow-md hover:bg-sky-600"
                        >
                            Go to internal dashboard
                        </Link>
                        <Link
                            to="/login"
                            className="inline-flex items-center rounded-lg border border-slate-400/40 bg-slate-900/60 px-4 py-2 text-xs font-semibold text-slate-100 hover:bg-slate-800/80"
                        >
                            Back to login
                        </Link>
                    </div>
                </div>

                <div className="rounded-xl border border-slate-500/40 bg-slate-900/70 p-4 text-xs text-slate-100 shadow-lg backdrop-blur-md">
                    <div className="mb-3 flex items-center justify-between">
                        <span className="text-[11px] uppercase tracking-[0.18em] text-sky-300">
                            Whitelabel preview
                        </span>
                        <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-[10px] text-emerald-300">
                            Enterprise
                        </span>
                    </div>
                    <div className="space-y-2 text-[11px] text-slate-200/90">
                        <p>
                            Use this as a starting point for customer-facing portals. The same
                            UI can be cloned and themed per client.
                        </p>
                        <p>
                            In production you can mount this portal under a client subdomain
                            (for example{" "}
                            <span className="font-mono text-sky-300">acme.gtsdispatcher.com</span>
                            ) with their own logo and colors.
                        </p>
                    </div>
                </div>
            </div>
        </AuthLayout>
    );
};

export default ClientPortal;
