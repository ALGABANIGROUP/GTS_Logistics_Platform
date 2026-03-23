import React, { useEffect, useMemo, useState } from 'react';
import { Link, Navigate, Outlet, useLocation } from 'react-router-dom';
import {
    ChevronLeft,
    ChevronRight,
    Settings,
    Home,
    Users,
    Building,
    FileText,
    Zap,
    Plug,
    Bell,
    Flag,
    LifeBuoy,
    ClipboardList,
} from 'lucide-react';
import SystemSwitcher from '../components/SystemSwitcher.jsx';
import TopUserBar from '../components/TopUserBar.jsx';
import RootLayout from '../components/RootLayout.jsx';
import { useAuth } from '../contexts/AuthContext.jsx';
import { generateSidebarMenu, getRoleInfo } from '../router/dynamicRoutes';
import SmartSearchBar from '../components/search/SmartSearchBar.jsx';
import { getUserRole, isAdminRole } from '../utils/userRole.js';

const AdminLayout = ({ children }) => {
    const location = useLocation();
    const [isCollapsed, setIsCollapsed] = useState(false);
    const { user, permissions, isAuthenticated, authReady, loading } = useAuth();

    useEffect(() => {
        if (typeof document === "undefined") return;
        document.body.classList.add("gts-glass-lite");
        document.body.classList.remove("gts-no-bg");
        return () => {
            document.body.classList.remove("gts-glass-lite");
        };
    }, []);

    if (!authReady || loading) {
        return (
            <div className="flex min-h-screen items-center justify-center text-white">
                Loading admin workspace...
            </div>
        );
    }

    if (!isAuthenticated || !user) {
        return <Navigate to="/login" replace />;
    }

    const userRole = getUserRole(user);
    if (!isAdminRole(userRole)) {
        return <Navigate to="/dashboard" replace />;
    }

    const iconMap = {
        overview: <Home className="w-5 h-5" />,
        users: <Users className="w-5 h-5" />,
        reports: <FileText className="w-5 h-5" />,
        system: <Zap className="w-5 h-5" />,
        audit: <FileText className="w-5 h-5" />,
        settings: <Settings className="w-5 h-5" />,
        subscriptions: <Settings className="w-5 h-5" />,
        api_connections: <Plug className="w-5 h-5" />,
        tenants: <Building className="w-5 h-5" />,
        notifications: <Bell className="w-5 h-5" />,
        feature_flags: <Flag className="w-5 h-5" />,
        portal_requests: <ClipboardList className="w-5 h-5" />,
        platform_expenses: <ClipboardList className="w-5 h-5" />,
        support: <LifeBuoy className="w-5 h-5" />,
        fleet: <ClipboardList className="w-5 h-5" />,
        fleet_live_map: <Zap className="w-5 h-5" />,
    };

    const roleInfo = useMemo(() => getRoleInfo(userRole || 'admin'), [userRole]);

    // Build menu items with fallback
    const menuItems = useMemo(() => {
        try {
            const generated = generateSidebarMenu(userRole || 'admin', permissions || []);
            if (!generated || generated.length === 0) {
                // Fallback menu if generation fails
                console.warn('Menu generation returned empty, using fallback');
                return [
                    {
                        id: 'overview',
                        name: 'Dashboard',
                        path: '/admin/overview',
                        icon: <Home className="w-5 h-5" />,
                    },
                    {
                        id: 'users',
                        name: 'Users',
                        path: '/admin/users',
                        icon: <Users className="w-5 h-5" />,
                    },
                    {
                        id: 'reports',
                        name: 'Reports',
                        path: '/admin/reports',
                        icon: <FileText className="w-5 h-5" />,
                    },
                ];
            }
            return generated.map((item) => ({
                id: item.id,
                name: item.title,
                path: item.path,
                icon: iconMap[item.id] || <FileText className="w-5 h-5" />,
                subItems: item.children?.map((child) => ({
                    id: child.id,
                    name: child.title,
                    path: child.path,
                })),
            }));
        } catch (error) {
            console.error('Error generating menu:', error);
            return [];
        }
    }, [permissions, userRole]);

    const topbar = (
        <div className="w-full flex flex-wrap items-center justify-between gap-4 px-4 py-3 lg:px-6">
            <div className="flex min-w-0 items-center gap-3">
                <div className="min-w-0">
                    <div className="truncate text-sm font-semibold tracking-wide text-white">
                        Gabani Transport Solutions
                    </div>
                    <div className="flex items-center gap-2 truncate text-xs text-slate-300">
                        <span>Logistics Command Platform</span>
                        <span
                            className="rounded-full px-2 py-0.5 text-[10px] font-semibold"
                            style={{ backgroundColor: `${roleInfo.color}33`, color: roleInfo.color }}
                        >
                            {roleInfo.name}
                        </span>
                    </div>
                </div>
            </div>
            <div className="flex flex-1 justify-center px-2">
                <SmartSearchBar />
            </div>
            <div className="flex items-center gap-3">
                <SystemSwitcher className="ml-2" />
                <TopUserBar />
            </div>
        </div>
    );

    const sidebar = (
        <aside
            className={`glass-sidebar flex h-screen flex-shrink-0 flex-col overflow-hidden text-white transition-all duration-300 ${isCollapsed ? 'w-20' : 'w-64'}`}
        >
            <div className="shrink-0 border-b border-white/10 p-6">
                <div className="flex items-center justify-between">
                    {!isCollapsed && (
                        <h1 className="text-xl font-bold">Platform Admin</h1>
                    )}
                    <button
                        onClick={() => setIsCollapsed(!isCollapsed)}
                        className="p-2 rounded-lg text-slate-200 transition hover:bg-white/10 hover:text-white"
                        aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                    >
                        {isCollapsed ? (
                            <ChevronRight className="h-4 w-4" />
                        ) : (
                            <ChevronLeft className="h-4 w-4" />
                        )}
                    </button>
                </div>
            </div>
            <nav className="flex-1 space-y-2 overflow-y-auto p-4">
                <Link
                    to="/dashboard"
                    className="flex items-center rounded-lg border px-3 py-3 transition border-white/5 bg-white/5 text-slate-300 hover:border-white/12 hover:bg-white/8 hover:text-white"
                >
                    <span className="mr-3">
                        <ChevronLeft className="w-5 h-5" />
                    </span>
                    {!isCollapsed && <span>Back to Dashboard</span>}
                </Link>
                {menuItems.map((item) => {
                    const isActive = item.path === "/admin"
                        ? location.pathname === "/admin"
                        : location.pathname.startsWith(item.path);

                    return (
                        <div key={item.id}>
                            <Link
                                to={item.path}
                                className={`flex items-center rounded-lg border px-3 py-3 transition ${isActive
                                    ? 'border-white/20 bg-white/10 text-white shadow-md shadow-black/20'
                                    : 'border-white/5 bg-white/5 text-slate-300 hover:border-white/12 hover:bg-white/8 hover:text-white'
                                    }`}
                            >
                                <span className="mr-3">{item.icon}</span>
                                {!isCollapsed && <span>{item.name}</span>}
                            </Link>
                            {!isCollapsed && item.subItems && (
                                <div className="ml-8 mt-1 space-y-1">
                                    {item.subItems.map((subItem, idx) => (
                                        <Link
                                            key={idx}
                                            to={subItem.path}
                                            className="block rounded-md border border-white/5 bg-white/5 px-4 py-2 text-sm text-slate-300 transition hover:border-white/15 hover:bg-white/10 hover:text-white"
                                        >
                                            {subItem.name}
                                        </Link>
                                    ))}
                                </div>
                            )}
                        </div>
                    )
                })}
            </nav>
        </aside>
    );

    return (
        <RootLayout
            className="glass-page"
            sidebar={sidebar}
            topbar={topbar}
            footer={null}
            contentClassName="p-8"
        >
            <div className="dashboard-grid gap-6">
                {children || <Outlet />}
            </div>
        </RootLayout>
    );
};

export default AdminLayout;
