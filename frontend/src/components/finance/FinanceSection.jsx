import React from "react";

export default function FinanceSection({ title, subtitle, children }) {
    return (
        <section className="mb-6">
            {(title || subtitle) && (
                <div className="mb-3">
                    {title && (
                        <h2 className="text-lg font-semibold text-white">{title}</h2>
                    )}
                    {subtitle && (
                        <p className="text-sm text-slate-200 mt-0.5">{subtitle}</p>
                    )}
                </div>
            )}

            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 text-slate-900">
                {children}
            </div>
        </section>
    );
}
