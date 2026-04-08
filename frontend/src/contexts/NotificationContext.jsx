// frontend/src/contexts/NotificationContext.jsx
// Advanced interactive notification system

import React, { createContext, useContext, useState, useCallback } from 'react';
import { Snackbar, Alert, AlertTitle, Slide, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';

// Create context
const NotificationContext = createContext(null);

// Custom hook to use notification
export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within NotificationProvider');
  }
  return context;
};

// Get icon based on severity
const getIcon = (severity) => {
  switch (severity) {
    case 'success':
      return <CheckCircleIcon sx={{ mr: 1 }} />;
    case 'error':
      return <ErrorIcon sx={{ mr: 1 }} />;
    case 'warning':
      return <WarningIcon sx={{ mr: 1 }} />;
    default:
      return <InfoIcon sx={{ mr: 1 }} />;
  }
};

// Notification Provider Component
export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [open, setOpen] = useState(false);
  const [currentNotification, setCurrentNotification] = useState(null);

  const showNotification = useCallback((message, severity = 'info', title = null, autoHideDuration = 5000) => {
    const newNotification = {
      id: Date.now(),
      message,
      severity,
      title,
      autoHideDuration,
      timestamp: new Date().toISOString()
    };

    setNotifications(prev => [...prev, newNotification]);
    setCurrentNotification(newNotification);
    setOpen(true);

    // Auto hide
    setTimeout(() => {
      setOpen(false);
    }, autoHideDuration);
  }, []);

  const showSuccess = useCallback((message, title = 'Success') => {
    showNotification(message, 'success', title, 4000);
  }, [showNotification]);

  const showError = useCallback((message, title = 'Error') => {
    showNotification(message, 'error', title, 6000);
  }, [showNotification]);

  const showWarning = useCallback((message, title = 'Warning') => {
    showNotification(message, 'warning', title, 5000);
  }, [showNotification]);

  const showInfo = useCallback((message, title = 'Info') => {
    showNotification(message, 'info', title, 4000);
  }, [showNotification]);

  const handleClose = () => {
    setOpen(false);
  };

  const handleExited = () => {
    setCurrentNotification(null);
  };

  const value = {
    showNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    notifications
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}

      {/* Single notification at a time for better UX */}
      {currentNotification && (
        <Snackbar
          key={currentNotification.id}
          open={open}
          autoHideDuration={currentNotification.autoHideDuration}
          onClose={handleClose}
          TransitionProps={{ onExited: handleExited }}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          sx={{ zIndex: 9999, mt: 7 }}
        >
          <Alert
            severity={currentNotification.severity}
            icon={getIcon(currentNotification.severity)}
            action={
              <IconButton
                aria-label="close"
                color="inherit"
                size="small"
                onClick={handleClose}
              >
                <CloseIcon fontSize="inherit" />
              </IconButton>
            }
            sx={{
              width: '100%',
              minWidth: 300,
              boxShadow: 3,
              borderRadius: 2,
              '& .MuiAlert-message': {
                wordBreak: 'break-word'
              }
            }}
          >
            {currentNotification.title && <AlertTitle>{currentNotification.title}</AlertTitle>}
            {currentNotification.message}
          </Alert>
        </Snackbar>
      )}
    </NotificationContext.Provider>
  );
};

// Default export for backward compatibility
export default NotificationProvider;
