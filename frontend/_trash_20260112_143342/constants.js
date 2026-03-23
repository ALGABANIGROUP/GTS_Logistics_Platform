export const SHIPMENT_STATUSES = {
    CREATED: { ar: 'Created', en: 'Created', color: 'default' },
    ASSIGNED: { ar: 'Assigned', en: 'Assigned', color: 'info' },
    PICKED_UP: { ar: 'Picked Up', en: 'Picked Up', color: 'warning' },
    IN_TRANSIT: { ar: 'In Transit', en: 'In Transit', color: 'primary' },
    DELIVERED: { ar: 'Delivered', en: 'Delivered', color: 'success' },
    CANCELLED: { ar: 'Cancelled', en: 'Cancelled', color: 'error' }
};

export const ALERT_TYPES = {
    INFO: { color: 'info', icon: 'info' },
    WARNING: { color: 'warning', icon: 'warning' },
    ERROR: { color: 'error', icon: 'error' },
    SUCCESS: { color: 'success', icon: 'check_circle' }
};

export const DRIVER_STATUS = {
    AVAILABLE: 'available',
    BUSY: 'busy',
    OFFLINE: 'Offline',
    ON_BREAK: 'on break'
};

export const MAP_CONFIG = {
    DEFAULT_CENTER: [24.7136, 46.6753],
    DEFAULT_ZOOM: 12,
    API_KEY: process.env.REACT_APP_MAP_API_KEY || 'YOUR_MAP_API_KEY'
};
