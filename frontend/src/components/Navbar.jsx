import React, { useEffect } from "react";
import { usePlatformStore } from "../stores/usePlatformStore";

export default function Navbar() {
  const { platformName, platformLogo, fetchPlatformSettings } = usePlatformStore();

  useEffect(() => {
    fetchPlatformSettings();
  }, [fetchPlatformSettings]);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-white/10 bg-slate-950/70 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center gap-3 px-5 py-4 lg:px-8">
        <div className="flex items-center gap-3 min-w-0">
          {platformLogo && (
            <img
              src={platformLogo}
              alt="Platform Logo"
              className="h-10 w-10 rounded-lg object-contain"
              style={{ backgroundColor: "rgba(255,255,255,0.05)" }}
            />
          )}
          <div className="min-w-0">
            <div className="text-sm font-semibold tracking-wide text-slate-100">
              {platformName}
            </div>
            <div className="text-xs text-slate-400">
              Logistics Command Platform
            </div>
          </div>
        </div>

        <div className="ml-auto flex items-center gap-2">
          <span className="hidden sm:inline-flex items-center rounded-full border border-emerald-400/25 bg-emerald-500/10 px-3 py-1 text-[11px] font-medium text-emerald-200">
            System Online
          </span>
        </div>
      </div>
    </header>
  );
}
