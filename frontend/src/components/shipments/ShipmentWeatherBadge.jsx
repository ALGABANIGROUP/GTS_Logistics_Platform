// ShipmentWeatherBadge.jsx - Small weather badge for shipments
import React from 'react';
import { Cloud, CloudRain, CloudSnow, Sun, Wind, AlertTriangle, AlertCircle, Zap } from 'lucide-react';
import WeatherAlertService from '../../services/WeatherAlertService';
import RoadAlertService from '../../services/RoadAlertService';

const ShipmentWeatherBadge = ({ weather, location, showAlert = true }) => {
    if (!weather || weather.fallback) {
        return null; // Don't show if weather unavailable
    }

    const isDangerous = WeatherAlertService.isDangerousWeather(weather);
    const severity = WeatherAlertService.getAlertSeverity(weather);

    // Check for road alerts
    const roadAlert = RoadAlertService.getMostSevereAlert(location);
    const hasRoadIssue = !!roadAlert;

    const getWeatherIcon = (description) => {
        const desc = (description || '').toLowerCase();
        if (desc.includes('rain')) return <CloudRain className="h-3 w-3" />;
        if (desc.includes('snow')) return <CloudSnow className="h-3 w-3" />;
        if (desc.includes('cloud')) return <Cloud className="h-3 w-3" />;
        if (desc.includes('wind')) return <Wind className="h-3 w-3" />;
        return <Sun className="h-3 w-3" />;
    };

    const getSeverityColor = () => {
        // If both weather and road are dangerous = extreme
        if (isDangerous && hasRoadIssue && roadAlert.severity === 'critical') {
            return 'bg-red-950/80 text-red-100 border border-red-600';
        }

        // Combined alert color
        if (isDangerous && hasRoadIssue) {
            return 'bg-orange-900/70 text-orange-100 border border-orange-600';
        }

        if (!isDangerous && hasRoadIssue) {
            // Road alert only
            switch (roadAlert.severity) {
                case 'critical':
                    return 'bg-red-900/70 text-red-100 border border-red-500/50';
                case 'high':
                    return 'bg-orange-900/70 text-orange-100 border border-orange-500/50';
                case 'medium':
                    return 'bg-amber-900/70 text-amber-100 border border-amber-500/50';
                default:
                    return 'bg-slate-800/50 text-slate-300';
            }
        }

        // Weather alert only
        if (isDangerous) {
            switch (severity) {
                case 'critical':
                    return 'bg-red-900/70 text-red-100 border border-red-500/50';
                case 'high':
                    return 'bg-orange-900/70 text-orange-100 border border-orange-500/50';
                case 'medium':
                    return 'bg-amber-900/70 text-amber-100 border border-amber-500/50';
                default:
                    return 'bg-slate-800/50 text-slate-300';
            }
        }

        return 'bg-slate-800/50 text-slate-300';
    };

    const getAlertIcon = () => {
        // Combined alert icon
        if (isDangerous && hasRoadIssue) {
            return <Zap className="h-3 w-3 animate-pulse text-yellow-400" />;
        }

        // Road alert icon
        if (hasRoadIssue) {
            return <AlertCircle className="h-3 w-3 animate-pulse" />;
        }

        // Weather alert icon
        if (isDangerous) {
            return <AlertTriangle className="h-3 w-3 animate-pulse" />;
        }

        return null;
    };

    return (
        <div className={`flex items-center gap-1 rounded-md px-2 py-0.5 text-xs ${getSeverityColor()}`}>
            {(isDangerous || hasRoadIssue) && showAlert && getAlertIcon()}
            {getWeatherIcon(weather.description)}
            <span>{Math.round(weather.temp)}°C</span>
            {(isDangerous || hasRoadIssue) && showAlert && (
                <span className="ml-1 font-semibold">!</span>
            )}
        </div>
    );
};

export default ShipmentWeatherBadge;
