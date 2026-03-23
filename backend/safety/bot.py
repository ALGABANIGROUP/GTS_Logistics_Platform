"""
Safety Manager Bot - Advanced Safety Management System
Real-time safety monitoring, analysis, and incident management
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import json
import logging

logger = logging.getLogger(__name__)


class SafetyManagerBot:
    """Advanced Safety Manager Bot for comprehensive transportation safety monitoring"""
    
    def __init__(self):
        from .traffic_analysis import TrafficAnalyzer
        from .weather_forecast import WeatherForecaster
        from .reports_generator import SafetyReportGenerator
        from .alerts_system import SafetyAlertSystem
        
        self.traffic_analyzer = TrafficAnalyzer()
        self.weather_forecaster = WeatherForecaster()
        self.report_generator = SafetyReportGenerator()
        self.alert_system = SafetyAlertSystem()
        self.active_monitors = {}
        
    async def initialize(self):
        """Initialize bot and fetch initial data"""
        logger.info("Starting Safety Manager Bot initialization...")
        
        await self.update_traffic_data()
        await self.update_weather_forecasts()
        await self.analyze_current_safety_status()
        
        logger.info("Safety Manager Bot ready for operation")
        
    async def run_safety_check(self, route_coordinates: List[List[float]], 
                              vehicle_data: Dict, driver_id: int):
        """Execute comprehensive safety check for a route"""
        
        safety_score = 100
        warnings = []
        recommendations = []
        
        # 1. Traffic analysis on route
        traffic_analysis = await self.traffic_analyzer.analyze_route(route_coordinates)
        
        if traffic_analysis.get('congestion_level') == 'high':
            safety_score -= 20
            warnings.append({
                "type": "traffic_congestion",
                "severity": "medium",
                "message": "High traffic congestion detected on route",
                "location": traffic_analysis.get('congestion_points', [])[0] if traffic_analysis.get('congestion_points') else None
            })
            
        # 2. Weather analysis
        weather_analysis = await self.weather_forecaster.check_route_weather(
            route_coordinates,
            vehicle_data.get('departure_time', datetime.utcnow())
        )
        
        for weather_hazard in weather_analysis.get('hazards', []):
            if weather_hazard['severity'] == 'severe':
                safety_score -= 30
                warnings.append({
                    "type": "weather_hazard",
                    "severity": "high",
                    "message": f"Severe weather condition: {weather_hazard['type']}",
                    "expected_time": weather_hazard.get('time'),
                    "location": weather_hazard.get('location')
                })
                recommendations.append({
                    "action": "delay_trip",
                    "priority": "high",
                    "reason": f"Postpone trip due to {weather_hazard['type']}"
                })
                
        # 3. Driver behavior analysis
        driver_behavior = await self.analyze_driver_behavior(driver_id)
        
        if driver_behavior.get('risk_score', 0) > 70:
            safety_score -= 15
            warnings.append({
                "type": "driver_risk",
                "severity": "medium",
                "message": "Driver has high-risk history",
                "details": driver_behavior.get('risk_factors', [])
            })
            recommendations.append({
                "action": "additional_supervision",
                "priority": "medium",
                "reason": "Driver risk level is elevated"
            })
            
        # 4. Vehicle safety check
        vehicle_check = await self.check_vehicle_safety(vehicle_data.get('vehicle_id'))
        
        if vehicle_check.get('inspection_score', 100) < 80:
            safety_score -= 25
            warnings.append({
                "type": "vehicle_safety",
                "severity": "high",
                "message": "Vehicle safety inspection issues detected",
                "issues": vehicle_check.get('issues', [])
            })
            recommendations.append({
                "action": "vehicle_maintenance",
                "priority": "high",
                "reason": "Technical issues require maintenance"
            })
            
        # 5. Time and condition factors
        time_analysis = self.analyze_time_factors(
            vehicle_data.get('departure_time'),
            vehicle_data.get('estimated_duration')
        )
        
        if time_analysis.get('is_night_trip'):
            safety_score -= 10
            recommendations.append({
                "action": "extra_caution",
                "priority": "low",
                "reason": "Night driving requires extra caution"
            })
            
        # 6. Generate comprehensive report
        safety_report = {
            "safety_score": max(0, safety_score),
            "risk_level": self.calculate_risk_level(safety_score),
            "warnings": warnings,
            "recommendations": recommendations,
            "route_analysis": {
                "traffic": traffic_analysis,
                "weather": weather_analysis,
                "time_factors": time_analysis
            },
            "driver_analysis": driver_behavior,
            "vehicle_analysis": vehicle_check,
            "generated_at": datetime.utcnow().isoformat(),
            "valid_until": (datetime.utcnow() + timedelta(hours=2)).isoformat()
        }
        
        # 7. Send alerts if high risk
        if safety_score < 70:
            await self.alert_system.send_safety_alert(
                driver_id=driver_id,
                vehicle_id=vehicle_data.get('vehicle_id'),
                report=safety_report
            )
            
        return safety_report
        
    async def analyze_driver_behavior(self, driver_id: int) -> Dict:
        """Analyze driver behavior and risk factors"""
        
        try:
            risk_score = 0
            risk_factors = []
            
            # Analyze incidents (if driver ID provided)
            # In real implementation, query database
            incidents_count = 0
            speed_violations = 0
            driving_hours = 0
            
            if incidents_count > 0:
                risk_score += incidents_count * 20
                risk_factors.append(f"{incidents_count} incidents in past year")
                
            if speed_violations > 3:
                risk_score += min(speed_violations * 5, 40)
                risk_factors.append(f"{speed_violations} speed violations")
                
            if driving_hours > 60:
                risk_score += 30
                risk_factors.append(f"High driving hours: {driving_hours} hours/week")
                
            return {
                "risk_score": min(risk_score, 100),
                "risk_factors": risk_factors,
                "total_incidents": incidents_count,
                "speed_violations": speed_violations,
                "weekly_hours": driving_hours,
                "driver_rating": 5.0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing driver behavior: {e}")
            return {"risk_score": 0, "risk_factors": []}
            
    async def check_vehicle_safety(self, vehicle_id: int) -> Dict:
        """Check vehicle safety status and inspection"""
        
        try:
            issues = []
            score = 100
            
            inspection_age = -1  # In reality, query last inspection date
            
            if inspection_age > 30:
                score -= 20
                issues.append(f"Inspection expired {inspection_age} days ago")
                
            return {
                "inspection_score": max(0, score),
                "issues": issues,
                "status": "safe" if score >= 80 else "needs_attention" if score >= 60 else "unsafe",
                "last_inspection": datetime.utcnow().isoformat(),
                "inspector": "System",
                "next_inspection_due": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking vehicle safety: {e}")
            return {
                "inspection_score": 0,
                "issues": [f"Error: {str(e)}"],
                "status": "unknown"
            }
            
    def analyze_time_factors(self, departure_time: datetime, duration: int) -> Dict:
        """Analyze time-related safety factors"""
        
        departure = departure_time or datetime.utcnow()
        arrival = departure + timedelta(hours=duration or 1)
        
        is_night_trip = False
        is_rush_hour = False
        time_warnings = []
        
        if 20 <= departure.hour <= 23 or 0 <= departure.hour <= 6:
            is_night_trip = True
            time_warnings.append("Trip scheduled during late night hours")
            
        if (7 <= departure.hour <= 9) or (16 <= departure.hour <= 18):
            is_rush_hour = True
            time_warnings.append("Trip during peak traffic hours")
            
        trip_hours = duration or 1
        if trip_hours > 8:
            time_warnings.append(f"Long trip duration ({trip_hours} hours)")
            
        return {
            "is_night_trip": is_night_trip,
            "is_rush_hour": is_rush_hour,
            "departure_time": departure.isoformat(),
            "estimated_arrival": arrival.isoformat(),
            "trip_duration_hours": trip_hours,
            "warnings": time_warnings
        }
        
    def calculate_risk_level(self, safety_score: int) -> str:
        """Determine risk level based on safety score"""
        
        if safety_score >= 85:
            return "low"
        elif safety_score >= 70:
            return "medium"
        elif safety_score >= 50:
            return "high"
        else:
            return "severe"
            
    async def update_traffic_data(self):
        """Update traffic data from sources"""
        
        logger.info("Updating traffic data...")
        await self.traffic_analyzer.refresh_data()
        
    async def update_weather_forecasts(self):
        """Update weather forecasts"""
        
        logger.info("Updating weather forecasts...")
        await self.weather_forecaster.update_forecasts()
        
    async def analyze_current_safety_status(self):
        """Analyze current system-wide safety status"""
        
        logger.info("Analyzing current safety status...")
        
        try:
            recent_incidents = 0
            risky_drivers = 0
            unsafe_vehicles = 0
            
            logger.info(f"Safety Statistics:")
            logger.info(f"  - Recent incidents (7 days): {recent_incidents}")
            logger.info(f"  - High-risk drivers: {risky_drivers}")
            logger.info(f"  - Unsafe vehicles: {unsafe_vehicles}")
            
        except Exception as e:
            logger.error(f"Error analyzing safety status: {e}")
            
    async def generate_safety_report(self, period: str = "daily") -> Dict:
        """Generate comprehensive safety report"""
        
        return await self.report_generator.generate_report(period)
        
    async def monitor_real_time(self):
        """Monitor safety in real-time"""
        
        logger.info("Starting real-time monitoring...")
        
        while True:
            try:
                await self.monitor_active_shipments()
                await self.monitor_weather_changes()
                await self.monitor_traffic_alerts()
                
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(30)
                
    async def monitor_active_shipments(self):
        """Monitor active shipments for safety"""
        
        try:
            # In real implementation, query active shipments
            pass
        except Exception as e:
            logger.error(f"Error monitoring shipments: {e}")
            
    async def monitor_weather_changes(self):
        """Monitor for significant weather changes"""
        
        try:
            await self.update_weather_forecasts()
        except Exception as e:
            logger.error(f"Error monitoring weather: {e}")
            
    async def monitor_traffic_alerts(self):
        """Monitor for traffic-related alerts"""
        
        try:
            await self.update_traffic_data()
        except Exception as e:
            logger.error(f"Error monitoring traffic: {e}")


# Global bot instance
safety_bot = SafetyManagerBot()
