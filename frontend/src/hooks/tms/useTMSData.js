import { useState, useCallback } from 'react';
import * as tmsApi from '../../utils/tms/api';

export const useTMSData = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const refreshData = useCallback(async (endpoint, params = {}) => {
        setLoading(true);
        setError(null);
        try {
            let data;
            switch (endpoint) {
                case 'dashboard':
                    data = await tmsApi.getDashboardData();
                    break;
                case 'shipments':
                    data = await tmsApi.getActiveShipments(params);
                    break;
                case 'shipment':
                    data = await tmsApi.getShipmentDetails(params.shipmentId);
                    break;
                default:
                    throw new Error('Endpoint unknown');
            }
            return data;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const updateShipmentStatus = useCallback(async (shipmentId, newStatus) => {
        try {
            return await tmsApi.updateShipmentStatus(shipmentId, newStatus);
        } catch (err) {
            setError(`Status update failed: ${err.message}`);
            throw err;
        }
    }, []);

    return {
        loading,
        error,
        refreshData,
        updateShipmentStatus
    };
};
