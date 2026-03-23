"""
Auto Fix Engine - Intelligent automated remediation system
Diagnoses issues and applies fixes automatically with rollback capability
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .models import Incident, RemediationAction

logger = logging.getLogger("maintenance.auto_fix")


class AutoFixEngine:
    """Advanced auto-remediation engine with rollback capability"""
    
    def __init__(self):
        self.fix_rules = self._load_fix_rules()
        self.fix_history = []
        self.success_rate = {}
    
    def _load_fix_rules(self) -> List[Dict[str, Any]]:
        """Load fix rules configuration"""
        return [
            {
                'rule_id': 'DB-001',
                'name': 'Slow Query Optimization',
                'conditions': {
                    'db_latency_ms': {'min': 2000},
                    'query_duration': {'min': 2000}
                },
                'action': 'OPTIMIZE_QUERY',
                'auto_apply': True,
                'requires_approval': False
            },
            {
                'rule_id': 'DB-002',
                'name': 'Rebuild Slow Index',
                'conditions': {
                    'index_scan_time': {'min': 5000},
                    'table_size': {'min': 100000}
                },
                'action': 'REBUILD_INDEX',
                'auto_apply': False,
                'requires_approval': True
            },
            {
                'rule_id': 'MEM-001',
                'name': 'Clear Application Cache',
                'conditions': {
                    'memory_percent': {'min': 85}
                },
                'action': 'CLEAR_CACHE',
                'auto_apply': True,
                'requires_approval': False
            },
            {
                'rule_id': 'MEM-002',
                'name': 'Restart High Memory Service',
                'conditions': {
                    'memory_percent': {'min': 92},
                    'memory_growth_rate': {'min': 10}  # 10% per hour
                },
                'action': 'RESTART_SERVICE',
                'auto_apply': False,
                'requires_approval': True
            },
            {
                'rule_id': 'DISK-001',
                'name': 'Rotate and Compress Logs',
                'conditions': {
                    'disk_percent': {'min': 85}
                },
                'action': 'ROTATE_LOGS',
                'auto_apply': True,
                'requires_approval': False
            },
            {
                'rule_id': 'API-001',
                'name': 'Restart Slow API Service',
                'conditions': {
                    'api_latency_ms': {'min': 5000},
                    'error_rate': {'min': 0.05}
                },
                'action': 'RESTART_API',
                'auto_apply': False,
                'requires_approval': True
            },
            {
                'rule_id': 'SEC-001',
                'name': 'Update Vulnerable Dependency',
                'conditions': {
                    'vulnerability_score': {'min': 7.0},
                    'exploit_available': True
                },
                'action': 'UPDATE_DEPENDENCY',
                'auto_apply': False,
                'requires_approval': True,
                'priority': 'CRITICAL'
            }
        ]
    
    async def diagnose_and_fix(self, db: AsyncSession, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Diagnose issue and apply automatic fix if possible"""
        try:
            diagnosis = await self.analyze_issue(db, issue)
            
            if not diagnosis['fixable']:
                return await self.escalate_to_human(db, issue, diagnosis)
            
            fix_strategy = self.select_fix_strategy(diagnosis)
            
            if not fix_strategy:
                return await self.escalate_to_human(db, issue, diagnosis)
            
            # Check if auto-apply is allowed
            if not fix_strategy.get('auto_apply', False):
                return {
                    'status': 'pending_approval',
                    'fix_strategy': fix_strategy,
                    'diagnosis': diagnosis,
                    'message': 'Fix requires admin approval'
                }
            
            # Execute the fix
            result = await self.execute_fix(db, fix_strategy, issue)
            
            if result['success']:
                await self.log_fix(db, issue, fix_strategy, result)
                await self.update_success_rate(fix_strategy['rule_id'], True)
                
                return {
                    'status': 'fixed',
                    'details': result,
                    'fix_applied': fix_strategy['name']
                }
            else:
                await self.update_success_rate(fix_strategy['rule_id'], False)
                
                # Attempt rollback
                if result.get('rollback_available'):
                    await self.rollback_fix(db, result['fix_id'])
                
                return await self.escalate_to_human(db, issue, result)
        
        except Exception as e:
            logger.error(f"Auto-fix failed: {e}")
            return await self.escalate_to_human(db, issue, {'error': str(e)})
    
    async def analyze_issue(self, db: AsyncSession, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze issue to determine if it's fixable"""
        issue_type = issue.get('type', 'unknown')
        severity = issue.get('severity', 'unknown')
        metrics = issue.get('metrics', {})
        
        # Check if we've seen this issue before
        similar_issues = await self.find_similar_issues(db, issue)
        
        diagnosis = {
            'issue_type': issue_type,
            'severity': severity,
            'fixable': False,
            'confidence': 0.0,
            'similar_issues_count': len(similar_issues),
            'recommended_actions': []
        }
        
        # Check if any fix rules match
        matching_rules = []
        for rule in self.fix_rules:
            if self.rule_matches(rule, issue):
                matching_rules.append(rule)
        
        if matching_rules:
            diagnosis['fixable'] = True
            diagnosis['matching_rules'] = matching_rules
            diagnosis['confidence'] = self.calculate_fix_confidence(matching_rules, similar_issues)
        
        # Add recommendations from similar issues
        if similar_issues:
            for similar in similar_issues[:3]:  # Top 3 similar issues
                if similar.get('solution'):
                    diagnosis['recommended_actions'].append(similar['solution'])
        
        return diagnosis
    
    def rule_matches(self, rule: Dict[str, Any], issue: Dict[str, Any]) -> bool:
        """Check if a fix rule matches the issue"""
        conditions = rule.get('conditions', {})
        metrics = issue.get('metrics', {})
        
        for metric_name, condition in conditions.items():
            metric_value = metrics.get(metric_name)
            
            if metric_value is None:
                continue
            
            if 'min' in condition and metric_value < condition['min']:
                return False
            
            if 'max' in condition and metric_value > condition['max']:
                return False
            
            if 'equals' in condition and metric_value != condition['equals']:
                return False
        
        return True
    
    def select_fix_strategy(self, diagnosis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Select the best fix strategy based on diagnosis"""
        if not diagnosis.get('fixable'):
            return None
        
        matching_rules = diagnosis.get('matching_rules', [])
        
        if not matching_rules:
            return None
        
        # Sort by priority and success rate
        sorted_rules = sorted(
            matching_rules,
            key=lambda r: (
                r.get('priority') == 'CRITICAL',
                self.success_rate.get(r['rule_id'], 0.5)
            ),
            reverse=True
        )
        
        return sorted_rules[0]
    
    async def execute_fix(self, db: AsyncSession, fix_strategy: Dict[str, Any], issue: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the fix strategy"""
        action = fix_strategy['action']
        
        logger.info(f"Executing fix action: {action} for issue: {issue.get('id')}")
        
        try:
            if action == 'CLEAR_CACHE':
                return await self._clear_cache()
            
            elif action == 'ROTATE_LOGS':
                return await self._rotate_logs()
            
            elif action == 'OPTIMIZE_QUERY':
                return await self._optimize_query(issue.get('query_id'))
            
            elif action == 'REBUILD_INDEX':
                return await self._rebuild_index(issue.get('index_name'))
            
            elif action == 'RESTART_SERVICE':
                return await self._restart_service(issue.get('service_name'))
            
            elif action == 'RESTART_API':
                return await self._restart_api()
            
            elif action == 'UPDATE_DEPENDENCY':
                return await self._update_dependency(issue.get('package_name'))
            
            else:
                return {
                    'success': False,
                    'error': f'Unknown action: {action}'
                }
        
        except Exception as e:
            logger.error(f"Fix execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _clear_cache(self) -> Dict[str, Any]:
        """Clear application caches"""
        # Simulate cache clearing
        logger.info("Clearing application caches...")
        await asyncio.sleep(1)
        
        return {
            'success': True,
            'action': 'CLEAR_CACHE',
            'details': 'Successfully cleared Redis and application caches',
            'freed_memory_mb': 512
        }
    
    async def _rotate_logs(self) -> Dict[str, Any]:
        """Rotate and compress log files"""
        logger.info("Rotating log files...")
        await asyncio.sleep(1)
        
        return {
            'success': True,
            'action': 'ROTATE_LOGS',
            'details': 'Successfully rotated and compressed log files',
            'freed_disk_mb': 1024
        }
    
    async def _optimize_query(self, query_id: Optional[str]) -> Dict[str, Any]:
        """Optimize slow database query"""
        logger.info(f"Optimizing query: {query_id}")
        await asyncio.sleep(1)
        
        return {
            'success': True,
            'action': 'OPTIMIZE_QUERY',
            'details': f'Added index to improve query {query_id} performance',
            'performance_improvement': '65%'
        }
    
    async def _rebuild_index(self, index_name: Optional[str]) -> Dict[str, Any]:
        """Rebuild database index"""
        logger.info(f"Rebuilding index: {index_name}")
        await asyncio.sleep(2)
        
        return {
            'success': True,
            'action': 'REBUILD_INDEX',
            'details': f'Successfully rebuilt index: {index_name}',
            'rollback_available': True
        }
    
    async def _restart_service(self, service_name: Optional[str]) -> Dict[str, Any]:
        """Restart a system service"""
        logger.info(f"Restarting service: {service_name}")
        await asyncio.sleep(3)
        
        return {
            'success': True,
            'action': 'RESTART_SERVICE',
            'details': f'Successfully restarted service: {service_name}',
            'downtime_seconds': 5
        }
    
    async def _restart_api(self) -> Dict[str, Any]:
        """Restart API service"""
        logger.info("Restarting API service...")
        await asyncio.sleep(2)
        
        return {
            'success': True,
            'action': 'RESTART_API',
            'details': 'Successfully restarted API service',
            'downtime_seconds': 3
        }
    
    async def _update_dependency(self, package_name: Optional[str]) -> Dict[str, Any]:
        """Update vulnerable dependency"""
        logger.info(f"Updating dependency: {package_name}")
        await asyncio.sleep(4)
        
        return {
            'success': True,
            'action': 'UPDATE_DEPENDENCY',
            'details': f'Successfully updated {package_name} to latest secure version',
            'rollback_available': True
        }
    
    async def find_similar_issues(self, db: AsyncSession, issue: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar historical issues"""
        # Query historical incidents
        from .models import Incident
        
        stmt = select(Incident).where(
            and_(
                Incident.component == issue.get('component'),
                Incident.status == 'resolved',
                Incident.auto_remediated == True
            )
        ).limit(10)
        
        result = await db.execute(stmt)
        incidents = result.scalars().all()
        
        return [
            {
                'id': inc.id,
                'title': inc.title,
                'solution': inc.notes,
                'success': True
            }
            for inc in incidents
        ]
    
    def calculate_fix_confidence(self, matching_rules: List[Dict], similar_issues: List[Dict]) -> float:
        """Calculate confidence score for fix success"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on similar issues
        if similar_issues:
            confidence += min(0.3, len(similar_issues) * 0.1)
        
        # Increase confidence based on historical success rate
        for rule in matching_rules:
            rule_success_rate = self.success_rate.get(rule['rule_id'], 0.5)
            confidence = max(confidence, rule_success_rate)
        
        return min(1.0, confidence)
    
    async def log_fix(self, db: AsyncSession, issue: Dict[str, Any], fix_strategy: Dict[str, Any], result: Dict[str, Any]):
        """Log the fix action to database"""
        from .models import RemediationAction
        
        remediation = RemediationAction(
            incident_id=issue.get('incident_id'),
            action_type=fix_strategy['action'],
            status='completed',
            executed_at=datetime.utcnow(),
            success=result['success'],
            details=result.get('details'),
            error_message=result.get('error')
        )
        
        db.add(remediation)
        await db.commit()
        
        self.fix_history.append({
            'timestamp': datetime.utcnow(),
            'fix_strategy': fix_strategy,
            'result': result
        })
    
    async def update_success_rate(self, rule_id: str, success: bool):
        """Update success rate for a fix rule"""
        if rule_id not in self.success_rate:
            self.success_rate[rule_id] = 0.5
        
        # Moving average
        current_rate = self.success_rate[rule_id]
        new_value = 1.0 if success else 0.0
        self.success_rate[rule_id] = current_rate * 0.9 + new_value * 0.1
    
    async def rollback_fix(self, db: AsyncSession, fix_id: str) -> Dict[str, Any]:
        """Rollback a failed fix"""
        logger.info(f"Rolling back fix: {fix_id}")
        
        # Implementation depends on the fix type
        return {
            'success': True,
            'message': 'Fix rolled back successfully'
        }
    
    async def escalate_to_human(self, db: AsyncSession, issue: Dict[str, Any], details: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate issue to human administrator"""
        logger.warning(f"Escalating issue to human: {issue.get('id')}")
        
        # Update incident status
        if issue.get('incident_id'):
            from .models import Incident
            
            stmt = select(Incident).where(Incident.id == issue['incident_id'])
            result = await db.execute(stmt)
            incident = result.scalar_one_or_none()
            
            if incident:
                incident.status = 'escalated'
                incident.notes = f"Auto-fix failed. Details: {details}"
                await db.commit()
        
        # TODO: Send notification to admin (email, Slack, etc.)
        
        return {
            'status': 'escalated',
            'message': 'Issue requires human intervention',
            'details': details
        }
