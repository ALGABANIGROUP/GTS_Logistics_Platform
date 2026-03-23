import axiosClient from '../api/axiosClient';

/**
 * Security Manager Service - Real API Integration
 * Connects to backend security monitoring and bot management endpoints
 */

class SecurityService {
    /**
     * Get security dashboard statistics
     */
    async getStats() {
        try {
            const response = await axiosClient.get('/api/v1/bots/stats');
            return {
                totalEvents: response.data.total_runs || 0,
                securityAlerts: response.data.failed_runs || 0,
                incidentsDetected: response.data.critical_events || 0,
                preventedAttacks: response.data.prevented_attacks || 0,
                usersBlocked: response.data.blocked_users || 0,
                botsMonitored: response.data.active_bots || 0
            };
        } catch (error) {
            console.error('Failed to fetch security stats:', error);
            throw error;
        }
    }

    /**
     * Get all registered bots with their security status
     */
    async getBots() {
        try {
            const response = await axiosClient.get('/api/v1/bots');
            return response.data.bots || [];
        } catch (error) {
            console.error('Failed to fetch bots:', error);
            throw error;
        }
    }

    /**
     * Get bot execution history (security events log)
     */
    async getBotHistory(limit = 50) {
        try {
            const response = await axiosClient.get('/api/v1/bots/history', {
                params: { limit }
            });
            return response.data.runs || [];
        } catch (error) {
            console.error('Failed to fetch bot history:', error);
            throw error;
        }
    }

    /**
     * Get security alerts (transform from bot runs)
     */
    async getSecurityAlerts() {
        try {
            const history = await this.getBotHistory(100);

            // Transform bot runs into security alerts
            const alerts = history
                .filter(run => run.status === 'failed' || run.error || run.severity)
                .map(run => ({
                    id: run.id || `ALERT_${run.bot_name}_${Date.now()}`,
                    type: this._mapBotToAlertType(run.bot_name),
                    severity: this._mapSeverity(run.status, run.error),
                    timestamp: run.started_at || run.created_at || new Date().toISOString(),
                    description: run.error || run.result?.error || `Security event from ${run.bot_name}`,
                    affectedEntities: this._extractAffectedEntities(run),
                    status: this._mapRunStatus(run.status),
                    botName: run.bot_name
                }));

            return alerts;
        } catch (error) {
            console.error('Failed to fetch security alerts:', error);
            return [];
        }
    }

    /**
     * Get security incidents (critical failed runs)
     */
    async getIncidents() {
        try {
            const history = await this.getBotHistory(50);

            const incidents = history
                .filter(run => run.status === 'failed' && run.error)
                .map(run => ({
                    id: `INC_${run.id}`,
                    title: `${run.bot_name} Failure`,
                    severity: 'HIGH',
                    status: 'DETECTED',
                    detectedAt: run.started_at || new Date().toISOString(),
                    affectedSystems: [run.bot_name, 'API'],
                    description: run.error,
                    botName: run.bot_name
                }));

            return incidents;
        } catch (error) {
            console.error('Failed to fetch incidents:', error);
            return [];
        }
    }

    /**
     * Execute security action on alert
     */
    async investigateAlert(alertId) {
        try {
            // Log investigation action
            console.log(`Investigating alert: ${alertId}`);

            // In real implementation, this would trigger bot investigation
            const response = await axiosClient.post('/api/v1/commands/human', {
                command: `investigate security alert ${alertId}`,
                bot_name: 'security_manager',
                params: { alert_id: alertId }
            });

            return response.data;
        } catch (error) {
            console.error('Failed to investigate alert:', error);
            throw error;
        }
    }

    /**
     * Mark alert as resolved
     */
    async resolveAlert(alertId) {
        try {
            console.log(`Resolving alert: ${alertId}`);

            const response = await axiosClient.post('/api/v1/commands/human', {
                command: `resolve security alert ${alertId}`,
                bot_name: 'security_manager',
                params: { alert_id: alertId, action: 'resolve' }
            });

            return response.data;
        } catch (error) {
            console.error('Failed to resolve alert:', error);
            throw error;
        }
    }

    /**
     * Create new security incident
     */
    async createIncident(incidentData) {
        try {
            const response = await axiosClient.post('/api/v1/commands/human', {
                command: `create security incident: ${incidentData.title}`,
                bot_name: 'security_manager',
                params: incidentData
            });

            return response.data;
        } catch (error) {
            console.error('Failed to create incident:', error);
            throw error;
        }
    }

    /**
     * View incident details
     */
    async getIncidentDetails(incidentId) {
        try {
            const response = await axiosClient.get(`/api/v1/bots/history`);
            const runs = response.data.runs || [];

            // Find the specific incident
            const incident = runs.find(run =>
                `INC_${run.id}` === incidentId || run.id === incidentId
            );

            return incident || null;
        } catch (error) {
            console.error('Failed to get incident details:', error);
            throw error;
        }
    }

    /**
     * Generate security report
     */
    async generateReport(incidentId, reportType = 'detailed') {
        try {
            const response = await axiosClient.post('/api/v1/commands/human', {
                command: `generate ${reportType} security report for incident ${incidentId}`,
                bot_name: 'security_manager',
                params: { incident_id: incidentId, report_type: reportType }
            });

            return response.data;
        } catch (error) {
            console.error('Failed to generate report:', error);
            throw error;
        }
    }

    /**
     * Get bot monitoring data
     */
    async getBotMonitoring() {
        try {
            const bots = await this.getBots();

            return bots.map(bot => ({
                name: bot.name || bot.bot_name,
                status: bot.is_active ? 'Active' : 'Inactive',
                risk: this._calculateRiskLevel(bot),
                permissions: bot.permissions?.length || 0,
                lastRun: bot.last_run_at,
                errorRate: bot.error_rate || 0,
                automation_level: bot.automation_level
            }));
        } catch (error) {
            console.error('Failed to fetch bot monitoring:', error);
            return [];
        }
    }

    /**
     * Get driver activity monitoring data
     */
    async getDriverMonitoring() {
        try {
            // This would connect to driver monitoring endpoint
            const response = await axiosClient.get('/api/v1/drivers/activity');
            return response.data.drivers || [];
        } catch (error) {
            // Return empty if endpoint doesn't exist yet
            console.warn('Driver monitoring endpoint not available:', error);
            return [];
        }
    }

    /**
     * Get API traffic analysis
     */
    async getTrafficAnalysis() {
        try {
            const stats = await this.getStats();
            const history = await this.getBotHistory(100);

            // Calculate metrics from bot runs
            const recentRuns = history.filter(run => {
                const runTime = new Date(run.started_at || run.created_at);
                const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
                return runTime > fiveMinutesAgo;
            });

            const failedRuns = history.filter(run => run.status === 'failed');

            return {
                requestsPerMin: Math.round(recentRuns.length / 5),
                errorRate: failedRuns.length > 0
                    ? ((failedRuns.length / history.length) * 100).toFixed(1)
                    : '0.0',
                blockedIPs: stats.usersBlocked || 0,
                failedLogins: stats.securityAlerts || 0
            };
        } catch (error) {
            console.error('Failed to get traffic analysis:', error);
            return {
                requestsPerMin: 0,
                errorRate: '0.0',
                blockedIPs: 0,
                failedLogins: 0
            };
        }
    }

    /**
     * Get compliance status
     */
    async getComplianceStatus() {
        try {
            const bots = await this.getBots();
            const activeBots = bots.filter(b => b.is_active);

            // Calculate compliance score based on bot health
            const healthyBots = activeBots.filter(b => !b.error_rate || b.error_rate < 0.1);
            const complianceScore = activeBots.length > 0
                ? Math.round((healthyBots.length / activeBots.length) * 100)
                : 100;

            return {
                score: complianceScore,
                standard: 'ISO 27001',
                controls: {
                    informationSecurity: complianceScore >= 90 ? 100 : complianceScore,
                    accessControl: complianceScore >= 85 ? 95 : complianceScore - 5,
                    incidentManagement: complianceScore >= 80 ? 75 : complianceScore - 15
                }
            };
        } catch (error) {
            console.error('Failed to get compliance status:', error);
            return {
                score: 0,
                standard: 'ISO 27001',
                controls: {
                    informationSecurity: 0,
                    accessControl: 0,
                    incidentManagement: 0
                }
            };
        }
    }

    /**
     * Get audit logs
     */
    async getAuditLogs(limit = 10) {
        try {
            const history = await this.getBotHistory(limit);

            return history.map(run => ({
                action: `Bot execution: ${run.bot_name}`,
                user: run.user_email || 'System',
                time: this._formatTimeAgo(run.started_at || run.created_at),
                timestamp: run.started_at || run.created_at
            }));
        } catch (error) {
            console.error('Failed to get audit logs:', error);
            return [];
        }
    }

    /**
     * Get security recommendations
     */
    async getRecommendations() {
        try {
            const bots = await this.getBots();
            const alerts = await this.getSecurityAlerts();

            const recommendations = [];

            // Check for bots with high error rates
            const problematicBots = bots.filter(b => b.error_rate && b.error_rate > 0.1);
            if (problematicBots.length > 0) {
                recommendations.push({
                    priority: 'HIGH',
                    message: `${problematicBots.length} bot(s) have high error rates - review and optimize`
                });
            }

            // Check for recent security alerts
            const recentAlerts = alerts.filter(a => {
                const alertTime = new Date(a.timestamp);
                const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
                return alertTime > oneDayAgo;
            });

            if (recentAlerts.length > 5) {
                recommendations.push({
                    priority: 'MEDIUM',
                    message: 'High alert volume detected - consider strengthening security policies'
                });
            }

            // Check for inactive bots
            const inactiveBots = bots.filter(b => !b.is_active);
            if (inactiveBots.length > 0) {
                recommendations.push({
                    priority: 'LOW',
                    message: `${inactiveBots.length} bot(s) are inactive - review and clean up if not needed`
                });
            }

            // Default recommendation if all is well
            if (recommendations.length === 0) {
                recommendations.push({
                    priority: 'INFO',
                    message: 'Security status is healthy - continue routine monitoring'
                });
            }

            return recommendations;
        } catch (error) {
            console.error('Failed to get recommendations:', error);
            return [{
                priority: 'INFO',
                message: 'Unable to generate recommendations at this time'
            }];
        }
    }

    // Helper methods
    _mapBotToAlertType(botName) {
        const mapping = {
            'security_manager': 'Security Monitoring',
            'freight_broker': 'Shipment Security',
            'finance_bot': 'Financial Security',
            'documents_manager': 'Document Security',
            'sales_bot': 'Access Control'
        };
        return mapping[botName] || 'System Alert';
    }

    _mapSeverity(status, error) {
        if (status === 'failed' && error) {
            if (error.toLowerCase().includes('critical') || error.toLowerCase().includes('security')) {
                return 'CRITICAL';
            }
            if (error.toLowerCase().includes('error') || error.toLowerCase().includes('failed')) {
                return 'HIGH';
            }
            return 'MEDIUM';
        }
        return 'LOW';
    }

    _mapRunStatus(status) {
        const mapping = {
            'running': 'INVESTIGATING',
            'completed': 'RESOLVED',
            'failed': 'NEW',
            'pending': 'NEW'
        };
        return mapping[status] || 'NEW';
    }

    _extractAffectedEntities(run) {
        const entities = [];

        if (run.user_email) entities.push(run.user_email);
        if (run.bot_name) entities.push(run.bot_name);

        // Extract from result/error
        if (run.result && typeof run.result === 'object') {
            if (run.result.user_id) entities.push(run.result.user_id);
            if (run.result.affected) entities.push(...run.result.affected);
        }

        return entities.length > 0 ? entities : ['system'];
    }

    _calculateRiskLevel(bot) {
        if (!bot.is_active) return 'LOW';
        if (bot.error_rate && bot.error_rate > 0.2) return 'HIGH';
        if (bot.error_rate && bot.error_rate > 0.1) return 'MEDIUM';
        return 'LOW';
    }

    _formatTimeAgo(timestamp) {
        if (!timestamp) return 'unknown';

        const now = new Date();
        const time = new Date(timestamp);
        const diffMs = now - time;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
        return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    }
}

export default new SecurityService();
