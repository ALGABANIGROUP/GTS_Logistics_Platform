import React from "react";
import { NavLink, useNavigate, useLocation } from "react-router-dom";
import {
  ArrowLeft,
  RefreshCw,
  LayoutDashboard,
  Bot,
  Mail,
  Shield,
  User,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useAuth } from "../contexts/AuthContext.jsx";
import { useEntitlements } from "../stores/useEntitlements";
import { useUiActions } from "../contexts/UiActionsContext.jsx";
import { sidebarItems, canShow } from "../router/access";
import { isAdminRole } from "../utils/userRole";

const navItemBase =
  "group flex items-center gap-3 rounded-2xl px-3 py-3 transition glass-panel border border-white/10 hover:-translate-y-[1px]";

function SidebarItem({ to, icon: Icon, label, end = false, disabled = false }) {
  if (disabled) {
    return (
      <div
        className={`${navItemBase} cursor-not-allowed text-slate-200/60`}
        title={label}
      >
        <span className="grid h-10 w-10 place-items-center rounded-2xl bg-white/10 ring-1 ring-white/15">
          <Icon className="h-5 w-5" aria-hidden="true" />
        </span>
        <span className="text-[14px] leading-none">{label}</span>
      </div>
    );
  }

  return (
    <NavLink
      to={to}
      end={end}
      title={label}
      className={({ isActive }) =>
        [
          navItemBase,
          isActive
            ? "text-white ring-1 ring-blue-400/40 shadow-lg shadow-blue-900/30 bg-gradient-to-r from-blue-600/30 to-cyan-500/20"
            : "text-slate-200 hover:bg-white/10 hover:text-white hover:ring-white/15",
        ].join(" ")
      }
      aria-label={label}
    >
      <span className="grid h-10 w-10 place-items-center rounded-2xl bg-white/10 ring-1 ring-white/15 transition group-hover:bg-white/15 group-hover:ring-white/20">
        <Icon className="h-5 w-5" aria-hidden="true" />
      </span>
      <span className="text-[14px] leading-none">{label}</span>
    </NavLink>
  );
}

export default function Sidebar() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const entitlements = useEntitlements();
  const entitlementsLoaded = entitlements.loaded;
  const { emitRefresh } = useUiActions();
  const location = useLocation();

  const canGoBack =
    typeof window !== "undefined" && window.history && window.history.length > 1;

  const handleRefresh = () => {
    const handled = emitRefresh?.();
    if (!handled && typeof window !== "undefined") window.location.reload();
  };

  // Helper function to get icon for sidebar item
  const getIconForItem = (item) => {
    const iconMap = {
      "/dashboard": LayoutDashboard,
      "/ai-bots": Bot,
      "/emails": Mail,
      "/admin": Shield,
      "/profile": User,
      "/settings": Settings,
      "/logout": LogOut,
    };
    return iconMap[item.to] || LayoutDashboard;
  };

  const visibleItems = sidebarItems.filter((item) => canShow(item, entitlements));
  const hasAdminAccess = isAdminRole(user?.role);

  // Loading state
  if (!entitlementsLoaded) {
    return (
      <aside className="w-[260px] shrink-0 glass-sidebar text-slate-100">
        <div className="h-full flex flex-col">
          <div className="px-4 pt-5 pb-4">
            <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="min-w-0">
                    <div className="text-[14px] font-semibold leading-tight truncate">GTS Panel</div>
                    <div className="text-[11px] text-slate-200/70 leading-tight truncate">Enterprise Console</div>
                  </div>
                </div>
            </div>
          </div>
          <nav className="flex-1 px-3 pb-4 space-y-2">
            <div className="p-3 space-y-3 opacity-70">
              <div className="h-12 bg-white/10 rounded-2xl animate-pulse"></div>
              <div className="h-12 bg-white/10 rounded-2xl animate-pulse"></div>
              <div className="h-12 bg-white/10 rounded-2xl animate-pulse"></div>
              <div className="text-center text-slate-400 text-sm">Loading menu...</div>
            </div>
          </nav>
        </div>
      </aside>
    );
  }


  // Sidebar expand/collapse state (future)
  // const [collapsed, setCollapsed] = React.useState(false);

  return (
    <aside className="w-[260px] shrink-0 glass-sidebar text-slate-100 flex flex-col">
      {/* Header */}
      <div className="px-4 pt-5 pb-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="min-w-0">
            <div className="text-[14px] font-semibold leading-tight truncate">GTS LOGISTICS</div>
            <div className="text-[11px] text-slate-200/70 leading-tight truncate">Command Center</div>
          </div>
        </div>
        {/* Expand/collapse button scaffold */}
        <button type="button" className="glass-btn-secondary glass-btn-icon hover:-translate-y-[1px]" aria-label="Collapse Sidebar" title="Collapse Sidebar" disabled>
          <ChevronLeft className="h-5 w-5" aria-hidden="true" />
        </button>
      </div>

      {/* Main nav */}
      <nav className="flex-1 px-3 pb-4 space-y-2">
        <SidebarItem to="/dashboard" icon={LayoutDashboard} label="Dashboard" />
        <SidebarItem to="/ai-bots" icon={Bot} label="AI Bots" />
        <SidebarItem to="/emails" icon={Mail} label="Email Logs" />
        {hasAdminAccess ? <SidebarItem to="/admin" icon={Shield} label="Admin Panel" /> : null}
      </nav>

      {/* Bottom section - Profile, Settings, Logout */}
      <div className="px-3 py-2 space-y-1 border-t border-slate-700/50">
        <SidebarItem to="/profile" icon={User} label="Profile" />
        <SidebarItem to="/settings" icon={Settings} label="Settings" />
        <SidebarItem to="/logout" icon={LogOut} label="Logout" />
      </div>
    </aside>
  );
}
