// frontend/src/lib/advanced-alert-system.js
class AdvancedAlertSystem {
    constructor() {
        this.alertRules = new Map();
        this.notificationChannels = new Set();
        this.alertHistory = [];
    }

    // Add custom alert rules
    addAlertRule(rule) {
        const ruleId = generateId();
        this.alertRules.set(ruleId, {
            id: ruleId,
            ...rule,
            triggered: false,
            lastTriggered: null
        });

        return ruleId;
    }

    // Check alert rules
    checkAlerts(context) {
        this.alertRules.forEach((rule) => {
            if (this.evaluateRule(rule, context)) {
                this.triggerAlert(rule, context);
            }
        });
    }

    // Evaluate a rule
    evaluateRule(rule, context) {
        switch (rule.condition) {
            case 'threshold':
                return context.value > rule.threshold;

            case 'anomaly':
                return this.detectAnomaly(context);

            case 'pattern':
                return this.detectPattern(rule.pattern, context);

            case 'composite':
                return this.evaluateCompositeRule(rule, context);

            default:
                return false;
        }
    }

    // Detect anomaly
    detectAnomaly(context) {
        const historicalData = this.getHistoricalData(context.metric, '24h');
        if (historicalData.length < 10) return false;

        const mean =
            historicalData.reduce((a, b) => a + b, 0) / historicalData.length;

        const stdDev = Math.sqrt(
            historicalData.reduce((a, b) => a + Math.pow(b - mean, 2), 0) /
            historicalData.length
        );

        return Math.abs(context.value - mean) > 2 * stdDev;
    }

    // Trigger alert
    async triggerAlert(rule, context) {
        const alert = {
            id: generateId(),
            ruleId: rule.id,
            severity: rule.severity,
            message: this.formatAlertMessage(rule, context),
            context,
            timestamp: new Date(),
            acknowledged: false
        };

        this.alertHistory.push(alert);

        // Send through enabled channels
        for (const channel of this.notificationChannels) {
            await this.sendNotification(channel, alert);
        }

        // Update rule status
        rule.triggered = true;
        rule.lastTriggered = new Date();

        return alert;
    }

    // Format alert messages
    formatAlertMessage(rule, context) {
        const templates = {
            threshold: `🚨 Threshold exceeded: ${context.metric} = ${context.value} (limit: ${rule.threshold})`,
            anomaly: `⚠️ Anomaly detected: ${context.metric} = ${context.value}`,
            pattern: `🔍 Pattern detected: ${context.metric}`
        };

        return templates[rule.condition] || `Alert: ${context.metric}`;
    }
}
