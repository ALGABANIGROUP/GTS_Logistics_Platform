// useRoadAlerts.js - Hook to monitor road conditions
import { useState, useEffect, useCallback } from 'react';
import RoadAlertService from '../services/RoadAlertService';

export const useRoadAlerts = (shipments = [], options = {}) => {
    const { autoAlert = true } = options;

    const [roadAlerts, setRoadAlerts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [sentAlerts, setSentAlerts] = useState([]);

    // Fetch and check road conditions
    const checkRoadConditions = useCallback(async () => {
        if (!shipments || shipments.length === 0) return;

        setLoading(true);
        try {
            const alerts = await RoadAlertService.checkMultipleRoads(shipments);
            setRoadAlerts(alerts);

            // Auto-send alerts if autoAlert option is enabled
            if (autoAlert && alerts.length > 0) {
                const newAlerts = [];
                for (const alert of alerts) {
                    const shipment = alert.shipment;
                    const roadAlert = alert.roadAlert;
                    const driverId = shipment.driverId;

                    if (driverId) {
                        try {
                            await RoadAlertService.sendRoadAlert(shipment, roadAlert, driverId);
                            newAlerts.push({
                                shipmentId: shipment.id,
                                type: 'road',
                                severity: roadAlert.severity,
                                title: roadAlert.title,
                                message: roadAlert.description,
                                driverId,
                                timestamp: new Date(),
                            });
                        } catch (error) {
                            console.error(`Failed to send road alert for ${shipment.id}:`, error);
                        }
                    }
                }

                if (newAlerts.length > 0) {
                    setSentAlerts(prev => [...prev, ...newAlerts]);
                }
            }
        } catch (error) {
            console.error('Error checking road conditions:', error);
        } finally {
            setLoading(false);
        }
    }, [autoAlert, shipments]);

    // Get road alert for specific location
    const getRoadAlert = (location) => {
        return RoadAlertService.getMostSevereAlert(location);
    };

    // Monitor for road conditions when shipments change
    useEffect(() => {
        checkRoadConditions();
    }, [checkRoadConditions]);

    return {
        roadAlerts,
        loading,
        getRoadAlert,
        sentAlerts,
        checkRoadConditions,
    };
};

export default useRoadAlerts;
