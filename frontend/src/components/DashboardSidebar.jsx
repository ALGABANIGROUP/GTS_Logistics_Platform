// frontend/src/components/DashboardSidebar.jsx
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Dashboard as DashboardIcon,
  SmartToy as AIIcon,
  Notifications as NotificationsIcon,
  Email as EmailIcon,
  AdminPanelSettings as AdminIcon
} from '@mui/icons-material';

const menuItems = [
  { id: 'dashboard', label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
  { id: 'ai-bots', label: 'AI Bots', path: '/ai-bots', icon: <AIIcon /> },
  { id: 'notifications', label: 'Notifications', path: '/dashboard/notifications', icon: <NotificationsIcon /> },
  { id: 'email-logs', label: 'Email Logs', path: '/email-logs', icon: <EmailIcon /> },
  { id: 'admin', label: 'Admin Panel', path: '/admin', icon: <AdminIcon /> }
];

const DashboardSidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="glass-sidebar flex h-screen w-64 flex-shrink-0 flex-col overflow-hidden text-white">
      <div className="flex items-center gap-3 p-6">
        <div className="min-w-0">
          <div className="truncate text-lg font-bold tracking-wide text-white">
            GTS LOGISTICS
          </div>
          <div className="truncate text-xs text-slate-300">
            Command Center
          </div>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto px-3 py-2">
        <nav className="space-y-1">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.id}
                onClick={() => navigate(item.path)}
                className={`group flex w-full items-center gap-3 rounded-2xl px-3 py-3 transition glass-panel border border-white/10 hover:-translate-y-[1px] ${
                  isActive
                    ? "text-white ring-1 ring-blue-400/40 shadow-lg shadow-blue-900/30 bg-gradient-to-r from-blue-600/30 to-cyan-500/20"
                    : "text-slate-200 hover:bg-white/10 hover:text-white hover:ring-white/15"
                }`}
                title={item.label}
              >
                <span className="grid h-10 w-10 place-items-center rounded-2xl bg-white/10 ring-1 ring-white/15">
                  {item.icon}
                </span>
                <span className="text-[14px] leading-none">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

export default DashboardSidebar;