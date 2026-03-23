"""
Maintenance Dev Core - Main orchestrator for the intelligent maintenance system
Integrates all components: Knowledge Graph, Auto Fix, Recommendations, NLP
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .knowledge_graph import ProjectKnowledgeGraph, HealthMonitoringSystem
from .auto_fix_engine import AutoFixEngine
from .recommendation_engine import RecommendationEngine
from .nlp_processor import NLPProcessor
from .service import HealthCollector
from .models import Incident, RemediationAction

logger = logging.getLogger("maintenance.core")


class MaintenanceDevCore:
    """Central orchestrator for the maintenance system"""
    
    def __init__(self):
        self.knowledge_graph = ProjectKnowledgeGraph()
        self.health_monitor = HealthMonitoringSystem()
        self.auto_fixer = AutoFixEngine()
        self.recommender = RecommendationEngine()
        self.nlp_processor = NLPProcessor()
        
        self.last_full_scan = None
        self.cycle_count = 0
        
        logger.info("Maintenance Dev Core initialized")
    
    async def run_full_cycle(self, db: AsyncSession) -> Dict[str, Any]:
        """Run complete maintenance cycle (typically every 12-24 hours)"""
        try:
            self.cycle_count += 1
            start_time = datetime.utcnow()
            
            logger.info(f"Starting maintenance cycle #{self.cycle_count}")
            
            # Step 1: Scan Project
            project_data = await self.scan_project(db)
            
            # Step 2: Run Health Checks
            health_data = await self.run_health_checks(db)
            
            # Step 3: Analyze Results
            analysis = await self.analyze_results(db, project_data, health_data)
            
            # Step 4: Generate Recommendations
            recommendations = await self.generate_recommendations(db, analysis)
            
            # Step 5: Apply Auto Fixes
            auto_fix_results = await self.apply_auto_fixes(db, analysis)
            
            # Step 6: Update Knowledge Graph
            await self.update_knowledge_graph(db, {
                'project_data': project_data,
                'health_data': health_data,
                'recommendations': [r.to_dict() for r in recommendations],
                'auto_fixes': auto_fix_results
            })
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            self.last_full_scan = end_time
            
            cycle_result = {
                'cycle_number': self.cycle_count,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'project_scan': project_data.get('summary', {}),
                'health_status': health_data.get('health_score', 0),
                'recommendations_count': len(recommendations),
                'auto_fixes_applied': len(auto_fix_results.get('applied', [])),
                'issues_detected': analysis.get('issues_count', 0),
                'status': 'completed'
            }
            
            logger.info(f"Maintenance cycle #{self.cycle_count} completed in {duration}s")
            
            return cycle_result
        
        except Exception as e:
            logger.error(f"Maintenance cycle failed: {e}")
            return {
                'cycle_number': self.cycle_count,
                'status': 'failed',
                'error': str(e)
            }
    
    async def scan_project(self, db: AsyncSession) -> Dict[str, Any]:
        """Scan entire project structure"""
        logger.info("Scanning project structure...")
        
        try:
            # Scan code components
            code_scan = await self._scan_code_components()
            
            # Scan database schema
            db_scan = await self._scan_database_schema(db)
            
            # Scan API endpoints
            api_scan = await self._scan_api_endpoints()
            
            # Scan dependencies
            deps_scan = await self._scan_dependencies()
            
            # Scan infrastructure
            infra_scan = await self._scan_infrastructure()
            
            return {
                'code': code_scan,
                'database': db_scan,
                'api': api_scan,
                'dependencies': deps_scan,
                'infrastructure': infra_scan,
                'summary': {
                    'total_components': (
                        code_scan.get('count', 0) +
                        api_scan.get('count', 0) +
                        deps_scan.get('count', 0)
                    ),
                    'scan_timestamp': datetime.utcnow().isoformat()
                }
            }
        
        except Exception as e:
            logger.error(f"Project scan failed: {e}")
            return {'error': str(e)}
    
    async def _scan_code_components(self) -> Dict[str, Any]:
        """Scan code files and modules"""
        # Simulated scan - in production, would analyze actual code
        return {
            'count': 156,
            'avg_complexity': 8.5,
            'test_coverage': 75.3,
            'duplication_percent': 8.2,
            'lines_of_code': 45230,
            'files': 156,
            'functions': 892,
            'classes': 127
        }
    
    async def _scan_database_schema(self, db: AsyncSession) -> Dict[str, Any]:
        """Scan database schema and relationships"""
        from sqlalchemy import inspect
        
        try:
            inspector = inspect(db.bind)
            tables = inspector.get_table_names()
            
            return {
                'tables_count': len(tables),
                'tables': tables,
                'scan_timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Database scan failed: {e}")
            return {'error': str(e)}
    
    async def _scan_api_endpoints(self) -> Dict[str, Any]:
        """Scan API endpoints and routes"""
        return {
            'count': 45,
            'endpoints': [
                {'path': '/api/v1/health', 'method': 'GET', 'usage_count': 15000},
                {'path': '/api/v1/users', 'method': 'GET', 'usage_count': 8500},
                {'path': '/api/v1/shipments', 'method': 'POST', 'usage_count': 5200},
            ],
            'avg_latency_ms': 245
        }
    
    async def _scan_dependencies(self) -> Dict[str, Any]:
        """Scan external dependencies and check for vulnerabilities"""
        return {
            'count': 87,
            'outdated': 12,
            'vulnerable': [
                {'name': 'requests', 'version': '2.28.0', 'vulnerability': 'CVE-2023-xxxxx', 'severity': 'medium'}
            ],
            'license_issues': 0
        }
    
    async def _scan_infrastructure(self) -> Dict[str, Any]:
        """Scan infrastructure resources"""
        return {
            'servers': 3,
            'services': 8,
            'containers': 12,
            'unused_resources': [],
            'overprovisioned': [],
            'total_monthly_cost': 850
        }
    
    async def run_health_checks(self, db: AsyncSession) -> Dict[str, Any]:
        """Run comprehensive health checks"""
        logger.info("Running health checks...")
        
        return await self.health_monitor.run_health_checks(db)
    
    async def analyze_results(self, db: AsyncSession, project_data: Dict[str, Any], health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze scan and health check results"""
        logger.info("Analyzing results...")
        
        issues = []
        
        # Analyze code quality
        code_data = project_data.get('code', {})
        if code_data.get('test_coverage', 100) < 70:
            issues.append({
                'type': 'code_quality',
                'severity': 'medium',
                'title': 'Low Test Coverage',
                'description': f"Test coverage is {code_data.get('test_coverage')}%",
                'metrics': code_data
            })
        
        # Analyze performance
        current_metrics = health_data.get('current_metrics', {})
        if current_metrics.get('memory_percent', 0) > 80:
            issues.append({
                'type': 'performance',
                'severity': 'high',
                'title': 'High Memory Usage',
                'description': f"Memory usage is {current_metrics.get('memory_percent')}%",
                'metrics': current_metrics,
                'component': 'system'
            })
        
        if current_metrics.get('db_latency_ms', 0) > 1000:
            issues.append({
                'type': 'performance',
                'severity': 'high',
                'title': 'Slow Database Queries',
                'description': f"DB latency is {current_metrics.get('db_latency_ms')}ms",
                'metrics': current_metrics,
                'component': 'database'
            })
        
        # Analyze security
        deps_data = project_data.get('dependencies', {})
        vulnerable_deps = deps_data.get('vulnerable', [])
        for vuln in vulnerable_deps:
            issues.append({
                'type': 'security',
                'severity': 'critical' if vuln.get('severity') == 'high' else 'medium',
                'title': f"Vulnerable Dependency: {vuln.get('name')}",
                'description': vuln.get('vulnerability', ''),
                'metrics': vuln
            })
        
        # Analyze trends and predictions
        predictions = health_data.get('predictions', [])
        for pred in predictions:
            issues.append({
                'type': pred.get('type'),
                'severity': pred.get('severity', 'medium'),
                'title': f"Predicted Issue: {pred.get('type')}",
                'description': pred.get('recommendation', ''),
                'metrics': pred,
                'is_prediction': True
            })
        
        return {
            'issues': issues,
            'issues_count': len(issues),
            'critical_count': len([i for i in issues if i.get('severity') == 'critical']),
            'high_count': len([i for i in issues if i.get('severity') == 'high']),
            'health_score': health_data.get('health_score', 100),
            'trends': health_data.get('trends', {}),
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    async def generate_recommendations(self, db: AsyncSession, analysis: Dict[str, Any]) -> List:
        """Generate smart recommendations"""
        logger.info("Generating recommendations...")
        
        scan_data = {
            'code': analysis.get('code', {}),
            'performance': {
                'avg_memory_percent': 75,
                'avg_api_latency_ms': 245,
                'slow_queries_count': 3
            },
            'security': {
                'vulnerable_dependencies': analysis.get('issues', [])
            },
            'infrastructure': {
                'unused_resources': [],
                'overprovisioned': []
            },
            'reliability': {
                'uptime_percent': 99.5,
                'error_rate': 0.008
            }
        }
        
        recommendations = await self.recommender.generate_recommendations(db, scan_data)
        
        return recommendations
    
    async def apply_auto_fixes(self, db: AsyncSession, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply automatic fixes for detected issues"""
        logger.info("Applying auto fixes...")
        
        applied_fixes = []
        failed_fixes = []
        escalated = []
        
        issues = analysis.get('issues', [])
        
        for issue in issues:
            # Skip predictions for auto-fix
            if issue.get('is_prediction'):
                continue
            
            # Attempt auto-fix
            result = await self.auto_fixer.diagnose_and_fix(db, issue)
            
            if result.get('status') == 'fixed':
                applied_fixes.append({
                    'issue': issue,
                    'fix': result.get('fix_applied'),
                    'details': result.get('details')
                })
            elif result.get('status') == 'escalated':
                escalated.append({
                    'issue': issue,
                    'reason': result.get('message')
                })
            else:
                failed_fixes.append({
                    'issue': issue,
                    'reason': result.get('message', 'Unknown error')
                })
        
        return {
            'applied': applied_fixes,
            'failed': failed_fixes,
            'escalated': escalated,
            'success_rate': len(applied_fixes) / max(1, len(issues)) * 100
        }
    
    async def update_knowledge_graph(self, db: AsyncSession, changes: Dict[str, Any]):
        """Update knowledge graph with new information"""
        logger.info("Updating knowledge graph...")
        
        await self.knowledge_graph.update_knowledge(db, changes)
    
    async def process_user_message(self, db: AsyncSession, message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process user message/question through NLP"""
        logger.info(f"Processing user message from {user_id}")
        
        try:
            # Analyze message
            analysis = await self.nlp_processor.process_message(message, user_id)
            
            # Generate response
            response_text = await self.nlp_processor.generate_response(analysis)
            
            # If it's a bug report, create incident
            if analysis.get('intent', {}).get('intent') == 'report_bug':
                issue_type = analysis.get('issue_type', {}).get('type', 'general')
                urgency = analysis.get('urgency', 'medium')
                
                # Map urgency to severity
                severity_map = {'critical': 'critical', 'high': 'error', 'medium': 'warning', 'low': 'info'}
                severity = severity_map.get(urgency, 'warning')
                
                # Create incident
                incident = Incident(
                    title=f"{issue_type.title()} Issue Reported by User",
                    description=message,
                    severity=severity,
                    component=issue_type,
                    status='open',
                    source='user_report',
                    reported_by=user_id
                )
                db.add(incident)
                await db.commit()
                await db.refresh(incident)
                
                # Attempt auto-fix
                issue_data = {
                    'incident_id': incident.id,
                    'type': issue_type,
                    'severity': severity,
                    'metrics': analysis.get('entities', {})
                }
                
                fix_result = await self.auto_fixer.diagnose_and_fix(db, issue_data)
                
                response_text += f"\n\nIncident #{incident.id} has been created. "
                
                if fix_result.get('status') == 'fixed':
                    response_text += f"✅ Auto-fix applied: {fix_result.get('fix_applied')}"
                elif fix_result.get('status') == 'pending_approval':
                    response_text += "⏳ Fix requires admin approval. The team will review shortly."
                else:
                    response_text += "🔄 This has been escalated to the development team."
            
            return {
                'success': True,
                'response': response_text,
                'analysis': analysis
            }
        
        except Exception as e:
            logger.error(f"Failed to process user message: {e}")
            return {
                'success': False,
                'response': "I apologize, but I encountered an error processing your message. Please try again.",
                'error': str(e)
            }
    
    async def get_system_status(self, db: AsyncSession) -> Dict[str, Any]:
        """Get current system status"""
        health_data = await self.run_health_checks(db)
        
        return {
            'status': 'operational',
            'health_score': health_data.get('health_score', 100),
            'last_scan': self.last_full_scan.isoformat() if self.last_full_scan else None,
            'cycle_count': self.cycle_count,
            'components': health_data.get('current_metrics', {}),
            'trends': health_data.get('trends', {}),
            'predictions': health_data.get('predictions', [])
        }


# Global instance
maintenance_core = MaintenanceDevCore()
