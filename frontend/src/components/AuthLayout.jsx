import React from "react";
import portalBg from "../assets/bg_login.png";

/**
 * AuthLayout
 * - Background: image only + overlay (no glass/blur on background)
 * - Glass effect: only inside the content card
 */
export default function AuthLayout({
  title,
  subtitle,
  footer,
  children,
  showBackToPortal = true,
  onBack,
}) {
  return (
    <div
      className="min-h-screen w-full bg-cover bg-center bg-no-repeat relative"
      style={{ backgroundImage: `url(${portalBg})` }}
    >
      {/* Overlay only (no blur) */}
      <div className="absolute inset-0 bg-black/45" />

      <div className="relative z-10 min-h-screen flex items-center justify-center px-4 py-10">
        <div className="w-full max-w-md">
          {/* Header */}
          {title || subtitle ? (
            <div className="text-center mb-8">
              {title ? (
                <h2 className="text-white text-3xl font-bold">{title}</h2>
              ) : null}
              {subtitle ? (
                <p className="text-white/70 mt-2 text-sm leading-relaxed">
                  {subtitle}
                </p>
              ) : null}
            </div>
          ) : null}

          {/* Card (glass effect only here) */}
          <div className="rounded-2xl border border-white/20 bg-white/10 backdrop-blur-xl shadow-2xl p-8">
            {children}

            {(footer || showBackToPortal) && (
              <div className="mt-6 pt-6 border-t border-white/10">
                {footer ? <div className="mb-4">{footer}</div> : null}

                {showBackToPortal && (
                  <button
                    type="button"
                    onClick={onBack}
                    className="w-full text-white/70 hover:text-white transition text-sm"
                  >
                    ← Back to Portal
                  </button>
                )}
              </div>
            )}
          </div>

          <p className="text-center text-white/40 text-xs mt-6">
            Secure workspace. Authorization is required.
          </p>
        </div>
      </div>
    </div>
  );
}
