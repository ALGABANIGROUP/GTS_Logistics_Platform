import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const IntelligentRouter = () => {
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const userData = getUserData();
        if (!userData) {
            navigate('/portal');
            return;
        }
        const { system, userType, permissions } = userData;
        const targetRoute = calculateTargetRoute(system, userType, permissions, location.pathname);
        if (targetRoute !== location.pathname) {
            navigate(targetRoute);
        }
    }, [location.pathname, navigate]);

    const getUserData = () => {
        // EN: EN API EN localStorage
        const mockUser = {
            system: 'tms',
            userType: 'carrier',
            permissions: {
                canViewTMS: true,
                canViewLoadBoard: false,
                canManageUsers: false
            }
        };
        return mockUser;
    };

    const calculateTargetRoute = (system, userType, permissions, currentPath) => {
        const routeMap = {
            tms: {
                shipper: '/tms/shipper/dashboard',
                carrier: '/tms/carrier/dashboard',
                broker: '/tms/broker/dashboard',
                admin: '/admin/dashboard?system=tms'
            },
            loadboard: {
                shipper: '/loadboard/shipper/dashboard',
                carrier: '/loadboard/carrier/dashboard',
                broker: '/loadboard/broker/dashboard',
                admin: '/admin/dashboard?system=loadboard'
            }
        };
        const defaultRoute = routeMap[system]?.[userType] || '/dashboard';
        if (userType === 'admin') {
            const urlParams = new URLSearchParams(window.location.search);
            const adminSystem = urlParams.get('system') || system;
            return `/admin/dashboard?system=${adminSystem}`;
        }
        if (!hasPermissionToAccess(system, userType, permissions, currentPath)) {
            return defaultRoute;
        }
        return currentPath;
    };

    const hasPermissionToAccess = (system, userType, permissions, path) => {
        const permissionRules = {
            '/admin': userType === 'admin',
            '/tms': permissions.canViewTMS,
            '/loadboard': permissions.canViewLoadBoard,
            '/tms/carrier': userType === 'carrier' || userType === 'admin',
            '/loadboard/broker': userType === 'broker' || userType === 'admin',
        };
        for (const [routePrefix, isAllowed] of Object.entries(permissionRules)) {
            if (path.startsWith(routePrefix) && !isAllowed) {
                return false;
            }
        }
        return true;
    };

    return null;
};

export default IntelligentRouter;
