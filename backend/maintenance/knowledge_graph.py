"""
Project Knowledge Graph - Dynamic knowledge base for the maintenance system
Tracks all components, dependencies, and historical issues
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

logger = logging.getLogger("maintenance.knowledge_graph")


class ProjectKnowledgeGraph:
    """Dynamic knowledge graph that maps project structure and relationships"""
    
    def __init__(self):
        self.nodes = {
            'code_components': {},      # Code modules and components
            'database_schema': {},      # Database tables and relationships
            'api_endpoints': {},        # API routes and handlers
            'dependencies': {},         # External libraries and packages
            'infrastructure': {},       # Servers, services, containers
            'user_flows': {},          # User interaction patterns
            'historical_issues': {}     # Past problems and solutions
        }
        self.relationships = []
        self.last_update = None
    
    async def update_knowledge(self, db: AsyncSession, changes: Dict[str, Any]):
        """Update the knowledge graph with new information"""
        try:
            self.detect_changes(changes)
            await self.validate_consistency(db)
            self.rebuild_relationships()
            insights = self.generate_insights()
            self.last_update = datetime.utcnow()
            
            logger.info(f"Knowledge graph updated successfully. Insights: {insights}")
            return insights
        except Exception as e:
            logger.error(f"Failed to update knowledge graph: {e}")
            return None
    
    def detect_changes(self, changes: Dict[str, Any]):
        """Detect what has changed in the system"""
        for category, data in changes.items():
            if category in self.nodes:
                self.nodes[category].update(data)
    
    async def validate_consistency(self, db: AsyncSession):
        """Validate that the knowledge graph is consistent"""
        # Check for orphaned dependencies
        # Validate API endpoint -> handler mappings
        # Ensure database schema consistency
        pass
    
    def rebuild_relationships(self):
        """Rebuild relationship edges between nodes"""
        self.relationships.clear()
        
        # Link API endpoints to code components
        for endpoint_name, endpoint_data in self.nodes['api_endpoints'].items():
            handler = endpoint_data.get('handler')
            if handler in self.nodes['code_components']:
                self.relationships.append({
                    'from': endpoint_name,
                    'to': handler,
                    'type': 'uses'
                })
        
        # Link code components to dependencies
        for component_name, component_data in self.nodes['code_components'].items():
            deps = component_data.get('dependencies', [])
            for dep in deps:
                if dep in self.nodes['dependencies']:
                    self.relationships.append({
                        'from': component_name,
                        'to': dep,
                        'type': 'depends_on'
                    })
    
    def generate_insights(self) -> Dict[str, Any]:
        """Generate insights from the knowledge graph"""
        return {
            'total_nodes': sum(len(nodes) for nodes in self.nodes.values()),
            'total_relationships': len(self.relationships),
            'critical_paths': self.find_critical_paths(),
            'bottlenecks': self.identify_bottlenecks(),
            'unused_components': self.find_unused_components()
        }
    
    def find_critical_paths(self) -> List[str]:
        """Find critical execution paths in the system"""
        critical_paths = []
        
        # Identify paths that affect multiple users/features
        for endpoint_name, endpoint_data in self.nodes['api_endpoints'].items():
            if endpoint_data.get('usage_count', 0) > 1000:
                critical_paths.append(endpoint_name)
        
        return critical_paths
    
    def identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Find components with high dependency count
        for component_name, component_data in self.nodes['code_components'].items():
            dependent_count = sum(
                1 for rel in self.relationships 
                if rel['to'] == component_name and rel['type'] == 'depends_on'
            )
            if dependent_count > 5:
                bottlenecks.append({
                    'component': component_name,
                    'dependent_count': dependent_count,
                    'type': 'high_coupling'
                })
        
        return bottlenecks
    
    def find_unused_components(self) -> List[str]:
        """Find components that are not being used"""
        unused = []
        
        for component_name in self.nodes['code_components'].keys():
            is_used = any(
                rel['to'] == component_name or rel['from'] == component_name
                for rel in self.relationships
            )
            if not is_used:
                unused.append(component_name)
        
        return unused
    
    def get_component_impact(self, component_name: str) -> Dict[str, Any]:
        """Calculate the impact of a component failure"""
        affected_components = []
        affected_endpoints = []
        
        # Find all components that depend on this one
        for rel in self.relationships:
            if rel['to'] == component_name and rel['type'] == 'depends_on':
                affected_components.append(rel['from'])
        
        # Find all endpoints that use affected components
        for rel in self.relationships:
            if rel['to'] in affected_components and rel['type'] == 'uses':
                affected_endpoints.append(rel['from'])
        
        return {
            'component': component_name,
            'affected_components': affected_components,
            'affected_endpoints': affected_endpoints,
            'impact_score': len(affected_components) + len(affected_endpoints) * 2
        }
    
    def query_similar_issues(self, issue_description: str) -> List[Dict[str, Any]]:
        """Find similar historical issues"""
        similar_issues = []
        
        # Simple keyword matching (can be enhanced with ML)
        keywords = set(issue_description.lower().split())
        
        for issue_id, issue_data in self.nodes['historical_issues'].items():
            issue_keywords = set(issue_data.get('description', '').lower().split())
            similarity = len(keywords & issue_keywords) / len(keywords | issue_keywords) if keywords | issue_keywords else 0
            
            if similarity > 0.3:  # 30% similarity threshold
                similar_issues.append({
                    'issue_id': issue_id,
                    'similarity': similarity,
                    'solution': issue_data.get('solution'),
                    'success_rate': issue_data.get('success_rate', 0)
                })
        
        return sorted(similar_issues, key=lambda x: x['similarity'], reverse=True)


class HealthMonitoringSystem:
    """Advanced health monitoring with predictive capabilities"""
    
    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {
            'cpu_percent': {'warning': 70, 'critical': 90},
            'memory_percent': {'warning': 75, 'critical': 90},
            'disk_percent': {'warning': 80, 'critical': 95},
            'db_latency_ms': {'warning': 1000, 'critical': 3000},
            'error_rate': {'warning': 0.05, 'critical': 0.10}
        }
    
    async def run_health_checks(self, db: AsyncSession) -> Dict[str, Any]:
        """Run comprehensive health checks"""
        from .service import HealthCollector
        
        system_metrics = await HealthCollector.collect_system_metrics()
        db_metrics = await HealthCollector.collect_database_metrics(db)
        bot_metrics = await HealthCollector.collect_bot_metrics()
        
        all_metrics = {**system_metrics, **db_metrics, 'bots': bot_metrics}
        self.metrics_history.append({
            'timestamp': datetime.utcnow(),
            'metrics': all_metrics
        })
        
        # Keep only last 1000 entries
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        # Analyze trends
        trends = self.analyze_trends()
        predictions = self.predict_issues()
        
        return {
            'current_metrics': all_metrics,
            'trends': trends,
            'predictions': predictions,
            'health_score': self.calculate_health_score(all_metrics)
        }
    
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze metric trends over time"""
        if len(self.metrics_history) < 10:
            return {'status': 'insufficient_data'}
        
        recent_metrics = self.metrics_history[-10:]
        
        # Calculate trend direction for key metrics
        cpu_trend = self._calculate_trend([m['metrics'].get('cpu_percent', 0) for m in recent_metrics])
        memory_trend = self._calculate_trend([m['metrics'].get('memory_percent', 0) for m in recent_metrics])
        
        return {
            'cpu_trend': cpu_trend,
            'memory_trend': memory_trend,
            'overall_trend': 'improving' if cpu_trend == 'decreasing' and memory_trend == 'decreasing' else 'degrading'
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate if values are increasing, decreasing, or stable"""
        if len(values) < 2:
            return 'stable'
        
        avg_first_half = sum(values[:len(values)//2]) / (len(values)//2)
        avg_second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        diff_percent = ((avg_second_half - avg_first_half) / avg_first_half * 100) if avg_first_half > 0 else 0
        
        if diff_percent > 10:
            return 'increasing'
        elif diff_percent < -10:
            return 'decreasing'
        else:
            return 'stable'
    
    def predict_issues(self) -> List[Dict[str, Any]]:
        """Predict potential issues based on trends"""
        predictions = []
        
        if len(self.metrics_history) < 20:
            return predictions
        
        recent = self.metrics_history[-20:]
        
        # Predict memory exhaustion
        memory_values = [m['metrics'].get('memory_percent', 0) for m in recent]
        if self._calculate_trend(memory_values) == 'increasing':
            avg_increase = (memory_values[-1] - memory_values[0]) / len(memory_values)
            if avg_increase > 0.5:  # More than 0.5% per check
                predictions.append({
                    'type': 'memory_exhaustion',
                    'severity': 'warning',
                    'eta_minutes': int((95 - memory_values[-1]) / avg_increase),
                    'recommendation': 'Consider clearing caches or restarting services'
                })
        
        return predictions
    
    def calculate_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall system health score (0-100)"""
        score = 100.0
        
        # CPU penalty
        cpu = metrics.get('cpu_percent', 0)
        if cpu > 90:
            score -= 30
        elif cpu > 70:
            score -= 15
        
        # Memory penalty
        memory = metrics.get('memory_percent', 0)
        if memory > 90:
            score -= 30
        elif memory > 75:
            score -= 15
        
        # DB latency penalty
        db_latency = metrics.get('db_latency_ms', 0)
        if db_latency > 3000:
            score -= 25
        elif db_latency > 1000:
            score -= 10
        
        return max(0, min(100, score))
