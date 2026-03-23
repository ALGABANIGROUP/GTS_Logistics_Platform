import { Navigate, useLocation } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import PropTypes from 'prop-types';
import { useAuth } from '../../contexts/AuthContext';
import { getUserRole } from '../../utils/userRole';

const PrivateRoute = ({ children, allowedRoles = [] }) => {
    const location = useLocation();
    const { authReady, isAuthenticated, user } = useAuth();

    if (!authReady) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <CircularProgress />
            </Box>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    // Check roles if specified
    if (allowedRoles.length > 0) {
        const role = getUserRole(user);
        if (!allowedRoles.includes(role)) {
            return <Navigate to="/unauthorized" replace />;
        }
    }

    return children;
};

PrivateRoute.propTypes = {
    children: PropTypes.node.isRequired,
    allowedRoles: PropTypes.arrayOf(PropTypes.string),
};

export default PrivateRoute;
