"""
Smart Recommendation Engine - ML-powered recommendations system
Generates intelligent suggestions based on system analysis and patterns
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

logger = logging.getLogger("maintenance.recommendations")


class Recommendation:
    """Recommendation model with priority and impact calculation"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', f"rec_{datetime.utcnow().timestamp()}")
        self.title = data['title']
        self.description = data['description']
        self.category = data['category']
        self.priority = self.calculate_priority(data)
        self.impact_score = self.calculate_impact(data)
        self.effort_required = self.estimate_effort(data)
        self.roi = self.calculate_roi(data)
        self.auto_fixable = self.check_auto_fixable(data)
        self.suggested_fix = data.get('fix')
        self.metadata = data.get('metadata', {})
    
    def calculate_priority(self, data: Dict[str, Any]) -> str:
        """Calculate priority based on multiple factors"""
        score = 0
        
        # Security risks get highest priority
        if data.get('security_risk', False):
            score += 30
        
        # User impact
        affected_users = data.get('affects_users', 0)
        if affected_users > 1000:
            score += 25
        elif affected_users > 100:
            score += 15
        elif affected_users > 10:
            score += 5
        
        # Performance impact
        performance_impact = data.get('performance_impact', 0)  # 0-100
        score += performance_impact * 0.2
        
        # Cost savings
        cost_savings = data.get('cost_savings', 0)
        if cost_savings > 1000:
            score += 15
        elif cost_savings > 500:
            score += 10
        elif cost_savings > 100:
            score += 5
        
        # Technical debt
        if data.get('reduces_technical_debt', False):
            score += 10
        
        # Classify based on score
        if score >= 60:
            return "CRITICAL"
        elif score >= 40:
            return "HIGH"
        elif score >= 20:
            return "MEDIUM"
        else:
            return "LOW"
    
    def calculate_impact(self, data: Dict[str, Any]) -> float:
        """Calculate impact score (0-100)"""
        impact = 0.0
        
        # User experience impact
        ux_impact = data.get('ux_impact', 0)  # 0-100
        impact += ux_impact * 0.3
        
        # Performance improvement
        perf_improvement = data.get('performance_improvement', 0)  # 0-100
        impact += perf_improvement * 0.25
        
        # Cost reduction
        cost_savings = data.get('cost_savings', 0)
        impact += min(25, cost_savings / 100)  # Max 25 points
        
        # Reliability improvement
        reliability_improvement = data.get('reliability_improvement', 0)  # 0-100
        impact += reliability_improvement * 0.2
        
        return min(100, impact)
    
    def estimate_effort(self, data: Dict[str, Any]) -> str:
        """Estimate effort required (hours)"""
        effort_hours = data.get('effort_hours', 0)
        
        if effort_hours <= 2:
            return "Quick (<2h)"
        elif effort_hours <= 8:
            return "Short (2-8h)"
        elif effort_hours <= 40:
            return "Medium (1-5 days)"
        else:
            return "Long (>5 days)"
    
    def calculate_roi(self, data: Dict[str, Any]) -> float:
        """Calculate ROI (Return on Investment)"""
        # Benefits
        cost_savings_monthly = data.get('cost_savings', 0)
        performance_value = data.get('performance_improvement', 0) * 10  # $10 per % improvement
        
        total_benefits = cost_savings_monthly * 12 + performance_value
        
        # Costs
        effort_hours = data.get('effort_hours', 1)
        hourly_rate = 100  # $100/hour developer cost
        total_cost = effort_hours * hourly_rate
        
        if total_cost == 0:
            return 0.0
        
        roi = ((total_benefits - total_cost) / total_cost) * 100
        
        return round(roi, 2)
    
    def check_auto_fixable(self, data: Dict[str, Any]) -> bool:
        """Check if recommendation can be auto-applied"""
        return data.get('auto_fixable', False) and data.get('risk_level', 'high') == 'low'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'impact_score': self.impact_score,
            'effort_required': self.effort_required,
            'roi': self.roi,
            'auto_fixable': self.auto_fixable,
            'suggested_fix': self.suggested_fix,
            'metadata': self.metadata
        }


class RecommendationEngine:
    """Smart recommendation engine with ML capabilities"""
    
    def __init__(self):
        self.recommendation_rules = self._load_recommendation_rules()
    
    def _load_recommendation_rules(self) -> List[Dict[str, Any]]:
        """Load recommendation generation rules"""
        return [
            # Database recommendations
            {
                'category': 'database',
                'trigger': 'slow_queries',
                'threshold': {'avg_query_time_ms': 1000},
                'recommendation_template': {
                    'title': 'Optimize Database Queries',
                    'description': 'Detected slow queries affecting system performance. Consider adding indexes or optimizing query structure.',
                    'category': 'performance',
                    'performance_improvement': 40,
                    'effort_hours': 4
                }
            },
            {
                'category': 'database',
                'trigger': 'missing_indexes',
                'recommendation_template': {
                    'title': 'Add Missing Database Indexes',
                    'description': 'Several tables are missing indexes on frequently queried columns.',
                    'category': 'performance',
                    'performance_improvement': 30,
                    'effort_hours': 2,
                    'auto_fixable': True,
                    'risk_level': 'low'
                }
            },
            
            # Security recommendations
            {
                'category': 'security',
                'trigger': 'outdated_dependencies',
                'recommendation_template': {
                    'title': 'Update Vulnerable Dependencies',
                    'description': 'Several dependencies have known security vulnerabilities.',
                    'category': 'security',
                    'security_risk': True,
                    'effort_hours': 3
                }
            },
            {
                'category': 'security',
                'trigger': 'weak_passwords',
                'recommendation_template': {
                    'title': 'Enforce Stronger Password Policy',
                    'description': 'Current password policy is weak. Recommend enforcing stronger requirements.',
                    'category': 'security',
                    'security_risk': True,
                    'affects_users': 100,
                    'effort_hours': 2
                }
            },
            
            # Performance recommendations
            {
                'category': 'performance',
                'trigger': 'high_memory_usage',
                'threshold': {'memory_percent': 80},
                'recommendation_template': {
                    'title': 'Implement Caching Strategy',
                    'description': 'High memory usage detected. Implementing Redis cache can improve performance.',
                    'category': 'performance',
                    'performance_improvement': 50,
                    'cost_savings': 200,
                    'effort_hours': 12
                }
            },
            {
                'category': 'performance',
                'trigger': 'slow_api_response',
                'threshold': {'api_latency_ms': 2000},
                'recommendation_template': {
                    'title': 'Optimize API Response Time',
                    'description': 'API endpoints are responding slowly. Consider implementing pagination and caching.',
                    'category': 'performance',
                    'performance_improvement': 60,
                    'affects_users': 500,
                    'effort_hours': 8
                }
            },
            
            # Infrastructure recommendations
            {
                'category': 'infrastructure',
                'trigger': 'high_disk_usage',
                'threshold': {'disk_percent': 85},
                'recommendation_template': {
                    'title': 'Increase Disk Space or Clean Up',
                    'description': 'Disk usage is high. Consider cleaning up logs or increasing storage.',
                    'category': 'infrastructure',
                    'effort_hours': 2,
                    'cost_savings': 50
                }
            },
            {
                'category': 'infrastructure',
                'trigger': 'single_point_failure',
                'recommendation_template': {
                    'title': 'Add Redundancy for Critical Services',
                    'description': 'Critical services lack redundancy. Recommend implementing load balancing.',
                    'category': 'reliability',
                    'reliability_improvement': 80,
                    'effort_hours': 24
                }
            },
            
            # Code quality recommendations
            {
                'category': 'code_quality',
                'trigger': 'high_complexity',
                'recommendation_template': {
                    'title': 'Refactor Complex Code Modules',
                    'description': 'Several modules have high cyclomatic complexity. Refactoring will improve maintainability.',
                    'category': 'code_quality',
                    'reduces_technical_debt': True,
                    'effort_hours': 16
                }
            },
            {
                'category': 'code_quality',
                'trigger': 'low_test_coverage',
                'threshold': {'test_coverage': 60},
                'recommendation_template': {
                    'title': 'Increase Test Coverage',
                    'description': 'Test coverage is below recommended threshold. Add more unit and integration tests.',
                    'category': 'quality',
                    'reliability_improvement': 40,
                    'effort_hours': 20
                }
            }
        ]
    
    async def generate_recommendations(self, db: AsyncSession, scan_data: Dict[str, Any]) -> List[Recommendation]:
        """Generate intelligent recommendations based on system analysis"""
        recommendations = []
        
        try:
            # Analyze different aspects
            code_recs = await self.analyze_code_quality(scan_data.get('code', {}))
            perf_recs = await self.analyze_performance(scan_data.get('performance', {}))
            security_recs = await self.analyze_security(scan_data.get('security', {}))
            cost_recs = await self.analyze_costs(scan_data.get('infrastructure', {}))
            reliability_recs = await self.analyze_reliability(scan_data.get('reliability', {}))
            
            # Combine all recommendations
            all_recs = code_recs + perf_recs + security_recs + cost_recs + reliability_recs
            
            # Convert to Recommendation objects
            recommendations = [Recommendation(rec_data) for rec_data in all_recs]
            
            # Rank recommendations
            ranked_recs = self.rank_recommendations(recommendations)
            
            # Save to database
            await self.save_recommendations(db, ranked_recs)
            
            return ranked_recs
        
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    async def analyze_code_quality(self, code_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze code quality and generate recommendations"""
        recommendations = []
        
        # Check test coverage
        test_coverage = code_data.get('test_coverage', 100)
        if test_coverage < 70:
            recommendations.append({
                'title': 'Increase Test Coverage',
                'description': f'Current test coverage is {test_coverage}%. Recommend increasing to at least 80%.',
                'category': 'quality',
                'test_coverage': test_coverage,
                'reliability_improvement': 40,
                'effort_hours': int((80 - test_coverage) * 0.5),
                'metadata': {'current_coverage': test_coverage, 'target_coverage': 80}
            })
        
        # Check code complexity
        avg_complexity = code_data.get('avg_complexity', 0)
        if avg_complexity > 15:
            recommendations.append({
                'title': 'Refactor Complex Code',
                'description': f'Average code complexity is {avg_complexity}. Consider refactoring complex modules.',
                'category': 'quality',
                'reduces_technical_debt': True,
                'effort_hours': 16,
                'metadata': {'avg_complexity': avg_complexity}
            })
        
        # Check code duplication
        duplication_percent = code_data.get('duplication_percent', 0)
        if duplication_percent > 10:
            recommendations.append({
                'title': 'Reduce Code Duplication',
                'description': f'{duplication_percent}% of code is duplicated. Extract common functionality.',
                'category': 'quality',
                'reduces_technical_debt': True,
                'effort_hours': 12,
                'metadata': {'duplication_percent': duplication_percent}
            })
        
        return recommendations
    
    async def analyze_performance(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze performance metrics"""
        recommendations = []
        
        # Check API latency
        api_latency = performance_data.get('avg_api_latency_ms', 0)
        if api_latency > 1000:
            improvement_potential = min(70, (api_latency - 200) / api_latency * 100)
            recommendations.append({
                'title': 'Optimize API Response Time',
                'description': f'Average API latency is {api_latency}ms. Implement caching and query optimization.',
                'category': 'performance',
                'performance_improvement': improvement_potential,
                'affects_users': 500,
                'effort_hours': 8,
                'metadata': {'current_latency_ms': api_latency, 'target_latency_ms': 200}
            })
        
        # Check database query performance
        slow_queries = performance_data.get('slow_queries_count', 0)
        if slow_queries > 5:
            recommendations.append({
                'title': 'Optimize Slow Database Queries',
                'description': f'Found {slow_queries} slow queries. Add indexes and optimize query structure.',
                'category': 'performance',
                'performance_improvement': 45,
                'effort_hours': 6,
                'auto_fixable': True,
                'risk_level': 'low',
                'metadata': {'slow_queries_count': slow_queries}
            })
        
        # Check memory usage
        memory_usage = performance_data.get('avg_memory_percent', 0)
        if memory_usage > 80:
            recommendations.append({
                'title': 'Implement Memory Optimization',
                'description': f'Memory usage is at {memory_usage}%. Implement caching strategy and optimize memory usage.',
                'category': 'performance',
                'performance_improvement': 35,
                'cost_savings': 200,
                'effort_hours': 12,
                'metadata': {'current_memory_percent': memory_usage}
            })
        
        return recommendations
    
    async def analyze_security(self, security_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze security and generate recommendations"""
        recommendations = []
        
        # Check vulnerable dependencies
        vulnerable_deps = security_data.get('vulnerable_dependencies', [])
        if vulnerable_deps:
            critical_vulns = [v for v in vulnerable_deps if v.get('severity') == 'critical']
            high_vulns = [v for v in vulnerable_deps if v.get('severity') == 'high']
            
            if critical_vulns:
                recommendations.append({
                    'title': 'URGENT: Update Critical Vulnerabilities',
                    'description': f'Found {len(critical_vulns)} critical security vulnerabilities. Immediate update required.',
                    'category': 'security',
                    'security_risk': True,
                    'effort_hours': len(critical_vulns) * 2,
                    'affects_users': 1000,
                    'metadata': {'vulnerabilities': critical_vulns}
                })
            
            if high_vulns:
                recommendations.append({
                    'title': 'Update High Severity Vulnerabilities',
                    'description': f'Found {len(high_vulns)} high severity vulnerabilities.',
                    'category': 'security',
                    'security_risk': True,
                    'effort_hours': len(high_vulns),
                    'metadata': {'vulnerabilities': high_vulns}
                })
        
        # Check SSL/TLS configuration
        ssl_score = security_data.get('ssl_score', 100)
        if ssl_score < 90:
            recommendations.append({
                'title': 'Improve SSL/TLS Configuration',
                'description': f'SSL score is {ssl_score}/100. Update cipher suites and protocols.',
                'category': 'security',
                'security_risk': True,
                'effort_hours': 2,
                'metadata': {'ssl_score': ssl_score}
            })
        
        return recommendations
    
    async def analyze_costs(self, infrastructure_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze infrastructure costs"""
        recommendations = []
        
        # Check unused resources
        unused_resources = infrastructure_data.get('unused_resources', [])
        if unused_resources:
            total_cost = sum(r.get('monthly_cost', 0) for r in unused_resources)
            recommendations.append({
                'title': 'Remove Unused Resources',
                'description': f'Found {len(unused_resources)} unused resources costing ${total_cost}/month.',
                'category': 'cost',
                'cost_savings': total_cost,
                'effort_hours': 2,
                'metadata': {'unused_resources': unused_resources}
            })
        
        # Check over-provisioned resources
        overprovisioned = infrastructure_data.get('overprovisioned', [])
        if overprovisioned:
            potential_savings = sum(r.get('potential_savings', 0) for r in overprovisioned)
            recommendations.append({
                'title': 'Right-size Over-provisioned Resources',
                'description': f'Reduce size of over-provisioned resources to save ${potential_savings}/month.',
                'category': 'cost',
                'cost_savings': potential_savings,
                'effort_hours': 4,
                'metadata': {'overprovisioned': overprovisioned}
            })
        
        return recommendations
    
    async def analyze_reliability(self, reliability_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze system reliability"""
        recommendations = []
        
        # Check uptime
        uptime_percent = reliability_data.get('uptime_percent', 100)
        if uptime_percent < 99.9:
            recommendations.append({
                'title': 'Improve System Reliability',
                'description': f'Current uptime is {uptime_percent}%. Add redundancy and monitoring.',
                'category': 'reliability',
                'reliability_improvement': (99.9 - uptime_percent) * 10,
                'affects_users': 1000,
                'effort_hours': 24,
                'metadata': {'current_uptime': uptime_percent, 'target_uptime': 99.9}
            })
        
        # Check error rates
        error_rate = reliability_data.get('error_rate', 0)
        if error_rate > 0.01:  # More than 1% errors
            recommendations.append({
                'title': 'Reduce Error Rates',
                'description': f'Error rate is {error_rate*100}%. Implement better error handling.',
                'category': 'reliability',
                'reliability_improvement': 50,
                'effort_hours': 8,
                'metadata': {'error_rate': error_rate}
            })
        
        return recommendations
    
    def rank_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Rank recommendations by priority and impact"""
        priority_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        
        return sorted(
            recommendations,
            key=lambda r: (
                priority_order.get(r.priority, 0),
                r.impact_score,
                r.roi
            ),
            reverse=True
        )
    
    async def save_recommendations(self, db: AsyncSession, recommendations: List[Recommendation]):
        """Save recommendations to database"""
        # TODO: Implement database saving
        pass
