// RoadAlertService.js - Monitor road conditions and alerts
// Manages congestion, closure, and incident detection across multiple regions

import axiosClient from '../api/axiosClient';

class RoadAlertService {
    constructor() {
        // Severity thresholds for road conditions
        this.alertThresholds = {
            closure: true,        // Road closure
            incident: true,       // Incident on road
            majorDelay: true,     // Major delay (30+ minutes)
            minorDelay: false,    // Minor delay
        };

        // Road severity classification
        this.roadSeverity = {
            closure: 'critical',      // 🔴 Full closure
            incident: 'high',         // 🟠 Incident
            majorDelay: 'high',       // 🟠 Major delay
            construction: 'medium',   // 🟡 Maintenance work
            minorDelay: 'low',        // 🟢 Minor delay
        };

        // Mock data for road conditions (TODO: Replace with real API)
        this.mockRoadData = {
            'New York': [
                {
                    id: 'I87_INCIDENT_001',
                    highway: 'Interstate 87',
                    type: 'incident',
                    severity: 'high',
                    title: 'I-87 - Traffic Incident',
                    description: 'Accident on I-87 (Major Deegan Expressway) near the Brox area',
                    location: 'New York, NY',
                    impact: 'Expected delay 15-20 minutes',
                    timestamp: new Date(),
                    affectsShipments: true,
                },
            ],
            'Boston': [],
            'Chicago': [
                {
                    id: 'I90_INCIDENT_001',
                    highway: 'Interstate 90',
                    type: 'incident',
                    severity: 'high',
                    title: 'I-90 - Multiple Vehicle Collision',
                    description: 'Multi-vehicle accident on I-90 eastbound near O\'Hare',
                    location: 'Chicago, IL',
                    impact: 'Expected delay 20-30 minutes',
                    timestamp: new Date(),
                    affectsShipments: true,
                },
            ],
            'Detroit': [
                {
                    id: 'I75_CLOSURE',
                    highway: 'Interstate 75',
                    type: 'closure',
                    severity: 'critical',
                    title: 'I-75 - Complete Closure',
                    description: 'I-75 partially closed due to emergency bridge work',
                    location: 'Detroit, MI',
                    impact: 'Mandatory diversion - Expected delay 30+ minutes',
                    timestamp: new Date(),
                    affectsShipments: true,
                },
            ],
            'Los Angeles': [
                {
                    id: 'I405_MAJOR_DELAY',
                    highway: 'Interstate 405',
                    type: 'majorDelay',
                    severity: 'high',
                    title: 'I-405 - Major Congestion',
                    description: 'Severe congestion on I-405 in the Bel Air area',
                    location: 'Los Angeles, CA',
                    impact: 'Expected delay 45+ minutes',
                    timestamp: new Date(),
                    affectsShipments: true,
                },
            ],
            'San Francisco': [],
            'Miami': [],
            'Atlanta': [
                {
                    id: 'I75_CONSTRUCTION',
                    highway: 'Interstate 75',
                    type: 'construction',
                    severity: 'medium',
                    title: 'I-75 - Road Maintenance Work',
                    description: 'Road maintenance work on I-75 southbound',
                    location: 'Atlanta, GA',
                    impact: 'Expected delay 10-15 minutes during rush hours',
                    timestamp: new Date(),
                    affectsShipments: true,
                },
            ],
            'Seattle': [
                {
                    id: 'I5_WEATHER_RELATED',
                    highway: 'Interstate 5',
                    type: 'incident',
                    severity: 'high',
                    title: 'I-5 - Poor Road Conditions Due to Weather',
                    description: 'Heavy rain and low visibility on I-5 northbound',
                    location: 'Seattle, WA',
                    impact: 'Expected delay 15-20 minutes, reduced speed advised',
                    timestamp: new Date(),
                    affectsShipments: true,
                },
            ],
            'Portland': [],
            'Vancouver': [],
            'Toronto': [
                {
                    id: 'HWY401_CLOSURE_001',
                    highway: 'Highway 401',
                    type: 'closure',
                    severity: 'critical',
                    title: 'Highway 401 - Complete Closure',
                    description: 'Highway 401 closed between Exit 69 and Exit 75 due to major accident',
                    location: 'Toronto, ON',
                    impact: 'Mandatory diversion - Expected delay 45+ minutes',
                    timestamp: new Date(),
                    affectsShipments: true,
                },
            ],
            'Jacksonville': [
                {
                    id: 'I95_MAJOR_DELAY',
                    highway: 'Interstate 95',
                    type: 'majorDelay',
                    severity: 'high',
                    title: 'I-95 - Heavy Congestion',
                    description: 'Heavy congestion on I-95 northbound after accident clearance',
                    location: 'Jacksonville, FL',
                    impact: 'Expected delay 30+ minutes',
                    timestamp: new Date(),
                    affectsShipments: true,
                },
            ],
            'Tacoma': [],
        };
    }

    // Check if there are dangerous road alerts
    isDangerousRoad(location) {
        const roadAlerts = this.mockRoadData[location] || [];
        return roadAlerts.some(alert =>
            ['closure', 'incident', 'majorDelay'].includes(alert.type)
        );
    }

    // Get all road alerts for a specific location
    getRoadAlerts(location) {
        return this.mockRoadData[location] || [];
    }

    // Get the most severe road alert for a location
    getMostSevereAlert(location) {
        const alerts = this.getRoadAlerts(location);
        if (alerts.length === 0) return null;

        const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
        return alerts.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity])[0];
    }

    // Combine road alerts with weather information
    combinedAlert(weather, roadAlert) {
        return {
            sources: ['weather', 'road'],
            severity: this._combinedSeverity(weather, roadAlert),
            message: `⚠️ Combined Alert: ${weather.description} + ${roadAlert.title}`,
            recommendation: '⛔ Avoid this route now - High risk from weather and road conditions',
            timestamp: new Date(),
            roadDetails: roadAlert,
            weatherDetails: weather,
        };
    }

    // Calculate combined severity score
    _combinedSeverity(weather, roadAlert) {
        const severityScore = {
            critical: 3,
            high: 2,
            medium: 1,
            low: 0,
        };

        const weatherScore = weather.severity === 'critical' ? 2 : weather.severity === 'high' ? 1 : 0;
        const roadScore = severityScore[roadAlert.severity] || 0;

        const combined = weatherScore + roadScore;
        if (combined >= 3) return 'EXTREME'; // Extremely dangerous
        if (combined >= 2) return 'critical'; // 🔴
        if (combined >= 1) return 'high'; // 🟠
        return 'medium';
    }

    // Send road alert to driver
    async sendRoadAlert(shipment, roadAlert, driverId) {
        try {
            const response = await axiosClient.post('/api/v1/notifications/send', {
                recipient_id: driverId,
                type: 'road_alert',
                severity: roadAlert.severity,
                title: `🚨 Road Alert: ${roadAlert.title}`,
                message: roadAlert.description,
                shipment_id: shipment.id,
                metadata: {
                    highway: roadAlert.highway,
                    location: roadAlert.location,
                    impact: roadAlert.impact,
                    alertType: roadAlert.type,
                },
            });

            console.log(
                `[ROAD_ALERT] Sent to driver ${driverId}:`,
                `Highway: ${roadAlert.highway}`,
                `Severity: ${roadAlert.severity}`,
                `Impact: ${roadAlert.impact}`
            );

            return response.data;
        } catch (error) {
            console.error('[ROAD_ALERT] Failed to send:', error);
            throw error;
        }
    }

    // Send combined weather and road alert to driver
    async sendCombinedAlert(shipment, weather, roadAlert, driverId) {
        const combined = this.combinedAlert(weather, roadAlert);

        try {
            const response = await axiosClient.post('/api/v1/notifications/send', {
                recipient_id: driverId,
                type: 'combined_alert',
                severity: combined.severity,
                title: `⚠️ Critical Alert: Poor Weather + Road Issues`,
                message: combined.message,
                shipment_id: shipment.id,
                metadata: {
                    sources: combined.sources,
                    weather: weather.description,
                    weatherTemp: weather.temp,
                    highway: roadAlert.highway,
                    roadType: roadAlert.type,
                    recommendation: combined.recommendation,
                },
            });

            console.log(
                `[COMBINED_ALERT] EXTREME SEVERITY - sent to driver ${driverId}`,
                `Weather: ${weather.description} @ ${weather.temp}°C`,
                `Road: ${roadAlert.title}`,
                `Recommendation: ${combined.recommendation}`
            );

            return response.data;
        } catch (error) {
            console.error('[COMBINED_ALERT] Failed to send:', error);
            throw error;
        }
    }

    // Monitor multiple shipments for road conditions
    async checkMultipleRoads(shipments) {
        const alerts = [];

        for (const shipment of shipments) {
            const location = shipment.currentLocation;
            const roadAlert = this.getMostSevereAlert(location);

            if (roadAlert) {
                alerts.push({
                    shipment,
                    roadAlert,
                    location,
                });
            }
        }

        return alerts;
    }

    // Get summary of problematic routes
    getSummary() {
        const summary = {};
        Object.keys(this.mockRoadData).forEach(location => {
            const alerts = this.getRoadAlerts(location);
            if (alerts.length > 0) {
                summary[location] = {
                    count: alerts.length,
                    severity: 'high',
                    alerts,
                };
            }
        });
        return summary;
    }
}

export default new RoadAlertService();
