// useShipmentWeather.js - Hook to fetch weather for each shipment location
import { useState, useEffect } from 'react';
import axiosClient from '../api/axiosClient';
import WeatherAlertService from '../services/WeatherAlertService';
import RoadAlertService from '../services/RoadAlertService';

export const useShipmentWeather = (shipments, options = {}) => {
    const [weatherData, setWeatherData] = useState({});
    const [loading, setLoading] = useState(false);
    const [alerts, setAlerts] = useState([]);
    const [roadAlerts, setRoadAlerts] = useState([]);
    const [combinedAlerts, setCombinedAlerts] = useState([]);

    const { autoAlert = true, includeRoadAlerts = true } = options; // Auto-send alerts by default

    useEffect(() => {
        if (!shipments || shipments.length === 0) return;

        const fetchWeatherForShipments = async () => {
            setLoading(true);
            const weatherCache = {};
            const alertsToSend = [];
            const roadAlertsToSend = [];
            const combinedAlertsToSend = [];

            try {
                // Get unique locations (current location, origin, or destination)
                const locationPromises = shipments.map(async (shipment) => {
                    // Determine which location to use
                    const location = shipment.current_location || shipment.currentLocation ||
                        shipment.destination || shipment.origin;

                    if (!location || weatherCache[location]) return;

                    try {
                        const response = await axiosClient.get('/api/v1/weather/current', {
                            params: { city: location, units: 'metric' },
                        });
                        const weather = response.data;
                        weatherCache[location] = weather;

                        // Check if weather is dangerous and needs alert
                        if (autoAlert && WeatherAlertService.isDangerousWeather(weather)) {
                            alertsToSend.push({ shipment, weather });
                        }

                        // Check for road alerts if enabled
                        if (includeRoadAlerts) {
                            const roadAlert = RoadAlertService.getMostSevereAlert(location);
                            if (roadAlert) {
                                roadAlertsToSend.push({ shipment, roadAlert });

                                // If both weather and road are dangerous = combined alert
                                if (autoAlert && WeatherAlertService.isDangerousWeather(weather)) {
                                    combinedAlertsToSend.push({ shipment, weather, roadAlert });
                                }
                            }
                        }
                    } catch (error) {
                        console.warn(`Failed to fetch weather for ${location}:`, error);
                        weatherCache[location] = null;
                    }
                });

                await Promise.all(locationPromises);
                setWeatherData(weatherCache);

                // Handle combined alerts first (most critical)
                if (combinedAlertsToSend.length > 0 && autoAlert) {
                    const sentCombined = [];
                    for (const { shipment, weather, roadAlert } of combinedAlertsToSend) {
                        if (shipment.driverId) {
                            try {
                                await RoadAlertService.sendCombinedAlert(shipment, weather, roadAlert, shipment.driverId);
                                sentCombined.push({
                                    shipmentId: shipment.id,
                                    type: 'combined',
                                    severity: 'critical',
                                    title: '⚠️ Critical Alert: Poor Weather + Road Issues',
                                    sources: ['weather', 'road'],
                                    driverId: shipment.driverId,
                                    timestamp: new Date(),
                                });
                            } catch (error) {
                                console.error(`Failed to send combined alert for ${shipment.id}:`, error);
                            }
                        }
                    }
                    setCombinedAlerts(sentCombined);
                }

                // Send weather-only alerts
                if (alertsToSend.length > 0) {
                    const sentAlerts = await WeatherAlertService.checkMultipleShipments(alertsToSend);
                    setAlerts(sentAlerts);
                    console.log(`Sent ${sentAlerts.length} weather alerts to drivers`);
                }

                // Send road-only alerts
                if (roadAlertsToSend.length > 0 && autoAlert && !combinedAlertsToSend.length) {
                    const sentRoad = [];
                    for (const { shipment, roadAlert } of roadAlertsToSend) {
                        if (shipment.driverId) {
                            try {
                                await RoadAlertService.sendRoadAlert(shipment, roadAlert, shipment.driverId);
                                sentRoad.push({
                                    shipmentId: shipment.id,
                                    type: 'road',
                                    severity: roadAlert.severity,
                                    title: `🚨 ${roadAlert.title}`,
                                    driverId: shipment.driverId,
                                    timestamp: new Date(),
                                });
                            } catch (error) {
                                console.error(`Failed to send road alert for ${shipment.id}:`, error);
                            }
                        }
                    }
                    setRoadAlerts(sentRoad);
                }
            } catch (error) {
                console.error('Error fetching shipment weather:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchWeatherForShipments();
    }, [shipments, autoAlert, includeRoadAlerts]);

    const getWeatherForShipment = (shipment) => {
        const location = shipment.current_location || shipment.currentLocation ||
            shipment.destination || shipment.origin;
        return weatherData[location] || null;
    };

    const checkWeatherAlert = (shipment) => {
        const weather = getWeatherForShipment(shipment);
        if (!weather) return null;

        return {
            isDangerous: WeatherAlertService.isDangerousWeather(weather),
            severity: WeatherAlertService.getAlertSeverity(weather),
            message: WeatherAlertService.generateAlertMessage(shipment, weather)
        };
    };

    return {
        weatherData,
        loading,
        alerts,
        roadAlerts,
        combinedAlerts,
        getWeatherForShipment,
        checkWeatherAlert,
        getRoadAlert: (location) => RoadAlertService.getMostSevereAlert(location),
    };
};
