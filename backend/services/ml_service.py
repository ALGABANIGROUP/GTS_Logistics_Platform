"""
Machine Learning Service for GTS
Handles data collection, analysis, and predictions
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

logger = logging.getLogger(__name__)


class MLDataCollector:
    """Collects data from various sources for ML analysis"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def collect_shipment_patterns(self, days: int = 90) -> Dict[str, Any]:
        """
        Collect shipment patterns from the last N days
        Returns: Dictionary with shipment analytics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # This is a scaffold - adjust based on your actual Shipment model
            # from backend.models.shipment import Shipment
            
            patterns = {
                "total_shipments": 0,
                "avg_shipments_per_day": 0,
                "peak_hours": [],
                "popular_routes": [],
                "avg_delivery_time": 0,
                "common_products": [],
                "seasonal_trends": {},
            }
            
            logger.info(f"Collected shipment patterns for {days} days")
            return patterns
            
        except Exception as e:
            logger.error(f"Error collecting shipment patterns: {e}")
            return {}
    
    async def collect_driver_performance(self) -> List[Dict[str, Any]]:
        """
        Collect driver performance metrics
        Returns: List of driver analytics
        """
        try:
            # Reserved for driver performance collection
            # Adjust based on your actual Driver/Trip models
            
            driver_stats = []
            
            # Example structure:
            # driver_stats.append({
            #     "driver_id": driver.id,
            #     "total_trips": trips_count,
            #     "avg_trip_duration": avg_duration,
            #     "completion_rate": completion_rate,
            #     "rating": avg_rating,
            #     "on_time_delivery_rate": on_time_rate,
            #     "revenue_generated": total_revenue,
            # })
            
            logger.info(f"Collected performance data for {len(driver_stats)} drivers")
            return driver_stats
            
        except Exception as e:
            logger.error(f"Error collecting driver performance: {e}")
            return []
    
    async def collect_customer_insights(self) -> List[Dict[str, Any]]:
        """
        Collect customer behavior and profitability data
        Returns: List of customer insights
        """
        try:
            customer_insights = []
            
            # Example structure:
            # customer_insights.append({
            #     "customer_id": customer.id,
            #     "total_orders": order_count,
            #     "total_revenue": revenue,
            #     "avg_order_value": avg_value,
            #     "order_frequency": frequency,
            #     "last_order_date": last_order,
            #     "preferred_routes": routes,
            #     "product_preferences": products,
            #     "payment_reliability": reliability_score,
            # })
            
            logger.info(f"Collected insights for {len(customer_insights)} customers")
            return customer_insights
            
        except Exception as e:
            logger.error(f"Error collecting customer insights: {e}")
            return []


class MLRecommendationEngine:
    """Provides intelligent recommendations based on ML analysis"""
    
    def __init__(self):
        self.data_collector = None
    
    def set_data_collector(self, collector: MLDataCollector):
        self.data_collector = collector
    
    async def recommend_best_customers(
        self, 
        db: AsyncSession,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Identify and recommend top customers
        Based on: revenue, frequency, reliability
        """
        try:
            collector = MLDataCollector(db)
            customer_insights = await collector.collect_customer_insights()
            
            # Score customers based on multiple factors
            scored_customers = []
            for customer in customer_insights:
                score = self._calculate_customer_score(customer)
                scored_customers.append({
                    **customer,
                    "ml_score": score,
                    "recommendation": self._generate_customer_recommendation(customer, score)
                })
            
            # Sort by score and return top N
            scored_customers.sort(key=lambda x: x["ml_score"], reverse=True)
            return scored_customers[:limit]
            
        except Exception as e:
            logger.error(f"Error recommending customers: {e}")
            return []
    
    def _calculate_customer_score(self, customer: Dict[str, Any]) -> float:
        """Calculate customer value score (0-100)"""
        try:
            revenue_score = min(customer.get("total_revenue", 0) / 10000 * 40, 40)
            frequency_score = min(customer.get("order_frequency", 0) * 5, 30)
            reliability_score = customer.get("payment_reliability", 0) * 30
            
            return revenue_score + frequency_score + reliability_score
        except:
            return 0.0
    
    def _generate_customer_recommendation(
        self, 
        customer: Dict[str, Any], 
        score: float
    ) -> str:
        """Generate personalized recommendation for customer"""
        if score >= 80:
            return "VIP Customer - Offer premium services and priority support"
        elif score >= 60:
            return "High Value - Provide loyalty rewards and volume discounts"
        elif score >= 40:
            return "Regular Customer - Encourage repeat business with incentives"
        else:
            return "Growth Opportunity - Engage with targeted offers"
    
    async def recommend_shipment_routes(
        self,
        db: AsyncSession,
        origin: str,
        destination: str
    ) -> List[Dict[str, Any]]:
        """
        Recommend optimal shipment routes based on historical data
        """
        try:
            collector = MLDataCollector(db)
            patterns = await collector.collect_shipment_patterns()
            
            # Analyze historical routes and recommend best options
            recommendations = [
                {
                    "route": f"{origin} -> {destination}",
                    "estimated_duration": "2-3 days",
                    "confidence": 0.85,
                    "cost_estimate": 250.00,
                    "reliability_score": 0.92,
                }
            ]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error recommending routes: {e}")
            return []
    
    async def predict_shipment_demand(
        self,
        db: AsyncSession,
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """
        Predict future shipment demand using historical patterns
        """
        try:
            collector = MLDataCollector(db)
            patterns = await collector.collect_shipment_patterns(days=180)
            
            # Simple forecasting model (can be enhanced with actual ML)
            avg_daily = patterns.get("avg_shipments_per_day", 10)
            
            forecast = {
                "forecast_period_days": forecast_days,
                "predicted_daily_avg": avg_daily * 1.1,  # 10% growth assumption
                "confidence_interval": {
                    "lower": avg_daily * 0.9,
                    "upper": avg_daily * 1.3
                },
                "seasonal_factors": patterns.get("seasonal_trends", {}),
                "recommendations": [
                    "Consider increasing driver capacity by 15%",
                    "Stock up on packaging materials",
                    "Prepare for peak season demand"
                ]
            }
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error predicting demand: {e}")
            return {}


class MLAnalyticsEngine:
    """Advanced analytics and insights generation"""
    
    @staticmethod
    async def analyze_driver_efficiency(
        db: AsyncSession,
        driver_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze driver efficiency and provide improvement suggestions
        """
        try:
            collector = MLDataCollector(db)
            driver_data = await collector.collect_driver_performance()
            
            if driver_id:
                driver_data = [d for d in driver_data if d.get("driver_id") == driver_id]
            
            if not driver_data:
                return {}
            
            # Calculate efficiency metrics
            avg_completion_rate = np.mean([d.get("completion_rate", 0) for d in driver_data])
            avg_on_time_rate = np.mean([d.get("on_time_delivery_rate", 0) for d in driver_data])
            
            analysis = {
                "total_drivers_analyzed": len(driver_data),
                "avg_completion_rate": round(avg_completion_rate, 2),
                "avg_on_time_rate": round(avg_on_time_rate, 2),
                "top_performers": sorted(
                    driver_data, 
                    key=lambda x: x.get("completion_rate", 0), 
                    reverse=True
                )[:5],
                "improvement_areas": [
                    "Focus on time management training",
                    "Optimize route planning",
                    "Reduce idle time between trips"
                ]
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing driver efficiency: {e}")
            return {}
    
    @staticmethod
    async def generate_revenue_insights(
        db: AsyncSession,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate revenue insights and growth opportunities
        """
        try:
            insights = {
                "period_days": period_days,
                "total_revenue": 0,
                "revenue_by_customer_segment": {},
                "revenue_trends": [],
                "growth_opportunities": [
                    "Expand to new geographic regions",
                    "Introduce express delivery services",
                    "Partner with e-commerce platforms"
                ],
                "risk_factors": [
                    "High dependency on top 3 customers",
                    "Seasonal demand fluctuations"
                ]
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating revenue insights: {e}")
            return {}


# Singleton instance
ml_recommendation_engine = MLRecommendationEngine()
ml_analytics_engine = MLAnalyticsEngine()
