// WeatherAlertService.js - Automatic weather alerts for drivers
import axiosClient from '../api/axiosClient';

class WeatherAlertService {
    constructor() {
        this.alertThresholds = {
            temperature: { min: -10, max: 45 }, // °C
            windSpeed: 50, // km/h
            dangerousConditions: ['rain', 'snow', 'storm', 'thunderstorm', 'heavy', 'extreme']
        };
    }

    /**
     * Check if weather is dangerous
     */
    isDangerousWeather(weather) {
        if (!weather || weather.fallback) return false;

        const { temp, wind_speed, description } = weather;
        const desc = (description || '').toLowerCase();

        // Check temperature extremes
        if (temp < this.alertThresholds.temperature.min ||
            temp > this.alertThresholds.temperature.max) {
            return true;
        }

        // Check wind speed
        if (wind_speed > this.alertThresholds.windSpeed) {
            return true;
        }

        // Check dangerous conditions
        const isDangerous = this.alertThresholds.dangerousConditions.some(
            condition => desc.includes(condition)
        );

        return isDangerous;
    }

    /**
     * Get alert severity level
     */
    getAlertSeverity(weather) {
        if (!weather) return null;

        const { temp, wind_speed, description } = weather;
        const desc = (description || '').toLowerCase();

        // Critical conditions
        if (desc.includes('extreme') || desc.includes('severe') ||
            temp < -15 || temp > 50 || wind_speed > 80) {
            return 'critical';
        }

        // High severity
        if (desc.includes('heavy') || desc.includes('storm') ||
            temp < -5 || temp > 42 || wind_speed > 60) {
            return 'high';
        }

        // Medium severity
        if (desc.includes('rain') || desc.includes('snow') ||
            temp < 0 || temp > 38 || wind_speed > 45) {
            return 'medium';
        }

        return 'low';
    }

    /**
     * Generate alert message for driver
     */
    generateAlertMessage(shipment, weather) {
        const location = shipment.currentLocation || shipment.destination;
        const severity = this.getAlertSeverity(weather);
        const { temp, description, wind_speed } = weather;

        let message = `⚠️ Weather Alert - ${location}\n\n`;
        message += `Shipment: ${shipment.id}\n`;
        message += `Condition: ${description}\n`;
        message += `Temperature: ${Math.round(temp)}°C\n`;

        if (wind_speed > 40) {
            message += `Wind: ${Math.round(wind_speed)} km/h\n`;
        }

        message += `\n`;

        // Add safety recommendations
        switch (severity) {
            case 'critical':
                message += '🚨 CRITICAL: Consider delaying shipment. Contact dispatch immediately.';
                break;
            case 'high':
                message += '⚠️ HIGH RISK: Drive with extreme caution. Reduce speed.';
                break;
            case 'medium':
                message += '⚠️ CAUTION: Weather may affect delivery. Drive safely.';
                break;
            default:
                message += 'ℹ️ Monitor weather conditions during route.';
        }

        return { message, severity, location };
    }

    /**
     * Send alert to driver
     */
    async sendAlertToDriver(shipment, weather, driverId) {
        try {
            const alert = this.generateAlertMessage(shipment, weather);

            // Send notification via API
            const response = await axiosClient.post('/api/v1/notifications/send', {
                recipient_id: driverId,
                type: 'weather_alert',
                severity: alert.severity,
                title: `Weather Alert - ${alert.location}`,
                message: alert.message,
                shipment_id: shipment.id,
                metadata: {
                    location: alert.location,
                    weather: {
                        temp: weather.temp,
                        description: weather.description,
                        wind_speed: weather.wind_speed
                    }
                }
            });

            console.log(`Weather alert sent to driver ${driverId} for shipment ${shipment.id}`);
            return response.data;
        } catch (error) {
            console.error('Failed to send weather alert:', error);
            return null;
        }
    }

    /**
     * Check shipment weather and send alert if needed
     */
    async checkAndAlertShipment(shipment, weather) {
        if (!weather || !this.isDangerousWeather(weather)) {
            return null;
        }

        const driverId = shipment.driver_id || shipment.driverId;
        if (!driverId) {
            console.warn(`No driver assigned to shipment ${shipment.id}`);
            return null;
        }

        return await this.sendAlertToDriver(shipment, weather, driverId);
    }

    /**
     * Batch check multiple shipments
     */
    async checkMultipleShipments(shipmentsWithWeather) {
        const alerts = [];

        for (const { shipment, weather } of shipmentsWithWeather) {
            const alert = await this.checkAndAlertShipment(shipment, weather);
            if (alert) {
                alerts.push(alert);
            }
        }

        return alerts;
    }
}

export default new WeatherAlertService();
