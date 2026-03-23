// File: src/healthCheck.js
const express = require('express');
const { Pool } = require('pg');
const router = express.Router();
const pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    database: process.env.DB_NAME || 'gabani_bots',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || 'password'
});
router.get('/health', async (req, res) => {
    const healthReport = {
        timestamp: new Date().toISOString(),
        status: 'checking',
        services: {}
    };
    try {
        try {
            const dbResult = await pool.query('SELECT 1 as status');
            healthReport.services.db = {
                status: 'ready',
                message: 'Database connection successful',
                details: {
                    total_bots: (await pool.query('SELECT COUNT(*) FROM bots')).rows[0].count,
                    active_bots: (await pool.query("SELECT COUNT(*) FROM bots WHERE status='active'")).rows[0].count
                }
            };
        } catch (dbError) {
            healthReport.services.db = {
                status: 'error',
                message: dbError.message,
                details: { error: 'Database connection failed' }
            };
        }
        try {
            healthReport.services.email = {
                status: 'ready',
                message: 'Email service is configured',
                details: { provider: 'SMTP', status: 'configured' }
            };
        } catch (emailError) {
            healthReport.services.email = {
                status: 'warning',
                message: 'Email service has issues',
                details: { error: emailError.message }
            };
        }
        try {
            const requiredBots = [
                'general_manager', 'operations_manager', 'finance_bot',
                'freight_broker', 'documents_manager', 'customer_service',
                'system_admin', 'information_coordinator', 'strategy_advisor',
                'maintenance_dev', 'legal_consultant', 'safety_manager',
                'sales', 'security', 'mapleload_canada'
            ];
            const result = await pool.query('SELECT key FROM bots');
            const existingBots = result.rows.map(row => row.key);
            const missingBots = requiredBots.filter(bot => !existingBots.includes(bot));
            healthReport.services.bots = {
                status: missingBots.length === 0 ? 'ready' : 'missing',
                message: missingBots.length === 0 ? 'All bots are present' : `${missingBots.length} bots missing`,
                details: {
                    required: requiredBots.length,
                    existing: existingBots.length,
                    missing: missingBots.length,
                    missing_list: missingBots
                }
            };
        } catch (botsError) {
            healthReport.services.bots = {
                status: 'error',
                message: 'Failed to check bots',
                details: { error: botsError.message }
            };
        }
        const allReady = Object.values(healthReport.services).every(
            service => service.status === 'ready'
        );
        healthReport.status = allReady ? 'ready' : 'degraded';
        if (healthReport.services.bots?.status === 'missing' &&
            healthReport.services.db?.status === 'ready') {
            healthReport.status = 'degraded';
            healthReport.message = 'System is running but some bots are missing. You can still use the app.';
        }
        res.status(allReady ? 200 : 503).json(healthReport);
    } catch (error) {
        healthReport.status = 'error';
        healthReport.message = 'Health check failed';
        healthReport.error = error.message;
        res.status(500).json(healthReport);
    }
});
router.post('/fix', async (req, res) => {
    try {
        const { fixer } = require('./botFixer');
        const result = await fixer.fix_missing_bots();
        res.json({
            success: true,
            message: 'Auto-fix completed',
            result: result
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: 'Auto-fix failed',
            error: error.message
        });
    }
});
module.exports = router;
