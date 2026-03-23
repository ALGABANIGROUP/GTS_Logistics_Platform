<template>
  <div class="maintenance-dashboard">
    <div class="dashboard-header">
      <div class="bot-header-info">
        <div class="bot-icon">MA</div>
        <div>
          <h1>AI Dev Maintenance Bot (CTO)</h1>
          <p class="bot-subtitle">Maintains system health and suggests engineering improvements.</p>
        </div>
      </div>
      <div class="bot-status-indicator">
        <span class="status-badge active">Active</span>
        <span class="last-updated">Last updated: {{ lastUpdated }}</span>
      </div>
    </div>

    <div class="dashboard-grid">
      <div class="dashboard-column">
        <div class="card system-health-card">
          <h3>System Health</h3>

          <div class="health-metrics">
            <div class="metric-item">
              <div class="metric-label">System Performance</div>
              <div class="metric-value">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: systemPerformance + '%' }"></div>
                </div>
                <span class="metric-percentage">{{ systemPerformance }}%</span>
              </div>
            </div>

            <div class="metric-item">
              <div class="metric-label">Memory Usage</div>
              <div class="metric-value">
                <div class="progress-bar">
                  <div class="progress-fill memory" :style="{ width: memoryUsage + '%' }"></div>
                </div>
                <span class="metric-percentage">{{ memoryUsage }}%</span>
              </div>
            </div>

            <div class="metric-item">
              <div class="metric-label">Uptime</div>
              <div class="metric-value">
                <span class="uptime-value">{{ uptime }}</span>
              </div>
            </div>
          </div>

          <div class="system-stats">
            <div class="stat-box">
              <div class="stat-value">{{ activeBots }}</div>
              <div class="stat-label">Active Bots</div>
            </div>
            <div class="stat-box">
              <div class="stat-value">{{ systemErrors }}</div>
              <div class="stat-label">Errors</div>
            </div>
            <div class="stat-box">
              <div class="stat-value">{{ pendingUpdates }}</div>
              <div class="stat-label">Updates</div>
            </div>
          </div>
        </div>

        <div class="card bots-status-card">
          <h3>Bots Status</h3>
          <div class="bots-list">
            <div v-for="bot in botsStatus" :key="bot.id" class="bot-status-item">
              <span class="bot-name">{{ bot.name }}</span>
              <span :class="['status-dot', bot.status]"></span>
              <span class="bot-status-text">{{ getStatusText(bot.status) }}</span>
            </div>
          </div>
          <button class="refresh-bots-btn" @click="refreshBotsStatus">
            Refresh Status
          </button>
        </div>
      </div>

      <div class="dashboard-column">
        <div class="card control-card">
          <h3>Direct Control</h3>

          <div class="control-buttons">
            <button class="control-btn primary" @click="runSystemHealthCheck">
              System Health Check
            </button>

            <button class="control-btn secondary" @click="runPerformanceOptimization">
              Optimize Performance
            </button>

            <button class="control-btn warning" @click="clearSystemCache">
              Clear Cache
            </button>

            <button class="control-btn danger" @click="restartAllBots" :disabled="isRestarting">
              Restart All Bots
              <span v-if="isRestarting" class="loading-spinner"></span>
            </button>
          </div>

          <div class="message-section">
            <h4>Message to Bot</h4>
            <textarea
              v-model="botMessage"
              placeholder="Type your message to the bot here. Example: Check finance bot and send a report."
              class="message-input"
              rows="3"
            ></textarea>

            <div class="quick-messages">
              <button
                v-for="msg in quickMessages"
                :key="msg"
                @click="botMessage = msg"
                class="quick-message-btn"
              >
                {{ msg }}
              </button>
            </div>
          </div>

          <div class="advanced-context-section">
            <div class="section-header">
              <h4>Advanced Context (JSON)</h4>
              <button class="toggle-btn" @click="toggleJsonEditor">
                {{ showJsonEditor ? 'Hide' : 'Show' }}
              </button>
            </div>

            <div v-if="showJsonEditor" class="json-editor-container">
              <textarea
                v-model="advancedContext"
                placeholder='{"priority": "high", "scope": "all", "mode": "diagnostic"}'
                class="json-input"
                rows="5"
              ></textarea>

              <div class="json-presets">
                <button @click="loadPreset('diagnostic')" class="preset-btn">
                  Diagnostic Preset
                </button>
                <button @click="loadPreset('optimization')" class="preset-btn">
                  Optimization Preset
                </button>
                <button @click="loadPreset('security')" class="preset-btn">
                  Security Preset
                </button>
              </div>
            </div>
          </div>

          <div class="run-bot-section">
            <button class="run-bot-btn" @click="runBot" :disabled="isRunning">
              Run Bot
              <span v-if="isRunning" class="loading-spinner"></span>
            </button>

            <button class="refresh-status-btn" @click="refreshStatus">
              Refresh Status
            </button>
          </div>
        </div>

        <div class="card logs-card">
          <div class="logs-header">
            <h3>Logs and Results</h3>
            <button class="clear-logs-btn" @click="clearLogs">Clear</button>
          </div>

          <div class="logs-content" ref="logsContainer">
            <div v-if="logs.length === 0" class="empty-logs">
              <p>No logs yet. Run the bot to see results.</p>
            </div>

            <div v-else class="logs-list">
              <div
                v-for="log in logs"
                :key="log.id"
                :class="['log-entry', log.type]"
              >
                <div class="log-timestamp">{{ log.timestamp }}</div>
                <div class="log-message">{{ log.message }}</div>
                <div class="log-details" v-if="log.details">
                  <pre>{{ JSON.stringify(log.details, null, 2) }}</pre>
                </div>
              </div>
            </div>
          </div>

          <div class="logs-actions">
            <button @click="exportLogs" class="export-btn">Export Logs</button>
            <button @click="autoScroll = !autoScroll" class="toggle-scroll-btn">
              {{ autoScroll ? 'Stop Scroll' : 'Auto Scroll' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="notification" class="notification" :class="notification.type">
      <span>{{ notification.message }}</span>
      <button @click="notification = null" class="close-notification">x</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';

const botMessage = ref('');
const advancedContext = ref('');
const showJsonEditor = ref(true);
const isRunning = ref(false);
const isRestarting = ref(false);
const autoScroll = ref(true);
const notification = ref(null);
const logsContainer = ref(null);

const systemPerformance = ref(92);
const memoryUsage = ref(67);
const uptime = ref('15 days, 4 hours');
const activeBots = ref(14);
const systemErrors = ref(2);
const pendingUpdates = ref(3);

const logs = ref([
  {
    id: 1,
    timestamp: '10:30:15',
    type: 'info',
    message: 'System health check completed successfully.',
    details: { checked: 15, issues: 0 }
  },
  {
    id: 2,
    timestamp: '10:28:45',
    type: 'warning',
    message: 'Marketing bot memory usage is high.',
    details: { bot: 'marketing_manager', memory: '85%' }
  }
]);

const botsStatus = ref([
  { id: 1, name: 'General Manager', status: 'active' },
  { id: 2, name: 'Operations Manager', status: 'active' },
  { id: 3, name: 'Finance Bot', status: 'active' },
  { id: 4, name: 'Freight Broker', status: 'warning' },
  { id: 5, name: 'Documents Manager', status: 'active' },
  { id: 6, name: 'Customer Service', status: 'active' },
  { id: 7, name: 'System Admin', status: 'active' },
  { id: 8, name: 'Information Coordinator', status: 'inactive' }
]);

const quickMessages = ref([
  'Check all bots health',
  'Optimize system performance',
  'Scan for pending updates',
  'Clear temporary files',
  'Generate maintenance report'
]);

const lastUpdated = computed(() => {
  return new Date().toLocaleString('en-US');
});

const getStatusText = (status) => {
  const statusMap = {
    active: 'Active',
    inactive: 'Inactive',
    warning: 'Warning',
    error: 'Error'
  };
  return statusMap[status] || status;
};

let notificationTimer = null;
const showNotification = (message, type = 'info') => {
  notification.value = { message, type };
  if (notificationTimer) {
    clearTimeout(notificationTimer);
  }
  notificationTimer = setTimeout(() => {
    notification.value = null;
  }, 5000);
};

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const addLog = async (entry) => {
  logs.value.unshift(entry);
  await nextTick();
  if (autoScroll.value && logsContainer.value) {
    logsContainer.value.scrollTop = 0;
  }
};

const runSystemHealthCheck = async () => {
  isRunning.value = true;
  showNotification('Running system health check...', 'info');

  try {
    await sleep(2000);
    await addLog({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString('en-US'),
      type: 'info',
      message: 'System health check completed successfully.',
      details: {
        totalBots: 15,
        healthyBots: 13,
        warnings: 2,
        errors: 0
      }
    });
    showNotification('Health check completed.', 'success');
  } catch (error) {
    showNotification('Health check failed.', 'error');
  } finally {
    isRunning.value = false;
  }
};

const runPerformanceOptimization = async () => {
  isRunning.value = true;
  showNotification('Optimizing system performance...', 'info');

  try {
    await sleep(1500);
    systemPerformance.value = Math.min(100, systemPerformance.value + 5);
    memoryUsage.value = Math.max(0, memoryUsage.value - 10);

    await addLog({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString('en-US'),
      type: 'success',
      message: 'Performance optimization completed.',
      details: {
        performanceBoost: '+5%',
        memoryReduction: '-10%'
      }
    });

    showNotification('Performance optimized.', 'success');
  } catch (error) {
    showNotification('Optimization failed.', 'error');
  } finally {
    isRunning.value = false;
  }
};

const clearSystemCache = async () => {
  isRunning.value = true;
  showNotification('Clearing cache...', 'info');

  try {
    await sleep(1000);
    memoryUsage.value = Math.max(0, memoryUsage.value - 15);

    await addLog({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString('en-US'),
      type: 'success',
      message: 'Cache cleared successfully.',
      details: {
        memoryFreed: '15%',
        totalCleaned: '2.4 GB'
      }
    });

    showNotification('Cache cleared.', 'success');
  } catch (error) {
    showNotification('Cache clear failed.', 'error');
  } finally {
    isRunning.value = false;
  }
};

const restartAllBots = async () => {
  isRestarting.value = true;
  showNotification('Restarting all bots...', 'warning');

  try {
    await sleep(3000);
    botsStatus.value = botsStatus.value.map((bot) => ({
      ...bot,
      status: 'active'
    }));
    activeBots.value = botsStatus.value.filter((b) => b.status === 'active').length;

    await addLog({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString('en-US'),
      type: 'success',
      message: 'All bots restarted successfully.',
      details: {
        restartedBots: botsStatus.value.length,
        timeTaken: '3 seconds'
      }
    });

    showNotification('Bots restarted.', 'success');
  } catch (error) {
    showNotification('Restart failed.', 'error');
  } finally {
    isRestarting.value = false;
  }
};

const refreshBotsStatus = async () => {
  showNotification('Refreshing bot status...', 'info');

  try {
    await sleep(1000);
    botsStatus.value = botsStatus.value.map((bot) => ({
      ...bot,
      status: Math.random() > 0.2 ? 'active' : 'warning'
    }));
    activeBots.value = botsStatus.value.filter((b) => b.status === 'active').length;

    showNotification('Bot status refreshed.', 'success');
  } catch (error) {
    showNotification('Status refresh failed.', 'error');
  }
};

const runBot = async () => {
  if (!botMessage.value.trim() && !advancedContext.value.trim()) {
    showNotification('Please enter a message or JSON context.', 'warning');
    return;
  }

  isRunning.value = true;
  showNotification('Running bot task...', 'info');

  let context = {};
  if (advancedContext.value.trim()) {
    try {
      context = JSON.parse(advancedContext.value);
    } catch (error) {
      showNotification('Invalid JSON context.', 'error');
      isRunning.value = false;
      return;
    }
  }

  try {
    const message = botMessage.value.trim() || 'Run requested task';
    await sleep(2500);

    await addLog({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString('en-US'),
      type: 'success',
      message: `Command executed: ${message}`,
      details: {
        command: message,
        context,
        executionTime: '2.5 seconds',
        result: 'Success'
      }
    });

    botMessage.value = '';
    advancedContext.value = '';

    showNotification('Command executed.', 'success');
  } catch (error) {
    await addLog({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString('en-US'),
      type: 'error',
      message: 'Command failed.',
      details: {
        error: error.message || 'Unknown error'
      }
    });

    showNotification('Command failed.', 'error');
  } finally {
    isRunning.value = false;
  }
};

const refreshStatus = () => {
  showNotification('Refreshing system status...', 'info');

  systemPerformance.value = Math.floor(Math.random() * 20) + 80;
  memoryUsage.value = Math.floor(Math.random() * 30) + 50;
  systemErrors.value = Math.floor(Math.random() * 5);
  pendingUpdates.value = Math.floor(Math.random() * 10);

  setTimeout(() => {
    showNotification('Status refreshed.', 'success');
  }, 1000);
};

const toggleJsonEditor = () => {
  showJsonEditor.value = !showJsonEditor.value;
};

const loadPreset = (preset) => {
  const presets = {
    diagnostic: {
      priority: 'high',
      scope: 'all',
      mode: 'diagnostic',
      includeLogs: true,
      generateReport: true
    },
    optimization: {
      priority: 'medium',
      scope: 'performance',
      mode: 'optimization',
      targets: ['memory', 'cpu', 'storage'],
      autoFix: true
    },
    security: {
      priority: 'critical',
      scope: 'security',
      mode: 'scan',
      checks: ['vulnerabilities', 'permissions', 'logs'],
      reportFormat: 'detailed'
    }
  };

  advancedContext.value = JSON.stringify(presets[preset], null, 2);
  showNotification(`Preset loaded: ${preset}`, 'info');
};

const clearLogs = () => {
  logs.value = [];
  showNotification('Logs cleared.', 'info');
};

const exportLogs = () => {
  const dataStr = JSON.stringify(logs.value, null, 2);
  const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

  const exportFileDefaultName = `maintenance-logs-${new Date().toISOString().slice(0, 10)}.json`;

  const linkElement = document.createElement('a');
  linkElement.setAttribute('href', dataUri);
  linkElement.setAttribute('download', exportFileDefaultName);
  linkElement.click();

  showNotification('Logs exported.', 'success');
};

let autoRefreshInterval;

onMounted(() => {
  autoRefreshInterval = setInterval(() => {
    refreshStatus();
  }, 30000);
});

onUnmounted(() => {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
  }
  if (notificationTimer) {
    clearTimeout(notificationTimer);
  }
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap');

.maintenance-dashboard {
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.dashboard-header {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.bot-header-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.bot-icon {
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.bot-header-info h1 {
  margin: 0;
  color: #2d3748;
  font-size: 28px;
}

.bot-subtitle {
  margin: 8px 0 0 0;
  color: #718096;
  font-size: 16px;
}

.bot-status-indicator {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.status-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 14px;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.last-updated {
  color: #718096;
  font-size: 14px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 24px;
}

.card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.card h3 {
  margin: 0 0 20px 0;
  color: #2d3748;
  font-size: 20px;
  font-weight: 700;
}

.health-metrics {
  margin-bottom: 24px;
}

.metric-item {
  margin-bottom: 16px;
}

.metric-label {
  font-size: 14px;
  color: #4a5568;
  margin-bottom: 8px;
  font-weight: 600;
}

.metric-value {
  display: flex;
  align-items: center;
  gap: 16px;
}

.progress-bar {
  flex: 1;
  height: 10px;
  background: #e2e8f0;
  border-radius: 5px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  border-radius: 5px;
}

.progress-fill.memory {
  background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
}

.metric-percentage {
  font-weight: 700;
  color: #2d3748;
  min-width: 40px;
}

.uptime-value {
  font-size: 18px;
  font-weight: 700;
  color: #2d3748;
}

.system-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-box {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  border: 1px solid #e2e8f0;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: #667eea;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #718096;
  font-weight: 600;
}

.bots-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.bot-status-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
  gap: 12px;
}

.bot-status-item:last-child {
  border-bottom: none;
}

.bot-name {
  flex: 1;
  font-weight: 600;
  color: #4a5568;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-dot.active {
  background: #48bb78;
}

.status-dot.inactive {
  background: #a0aec0;
}

.status-dot.warning {
  background: #ed8936;
}

.status-dot.error {
  background: #f56565;
}

.bot-status-text {
  font-size: 12px;
  color: #718096;
  min-width: 60px;
}

.refresh-bots-btn {
  width: 100%;
  padding: 12px;
  background: #e2e8f0;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  color: #4a5568;
  transition: all 0.3s;
}

.refresh-bots-btn:hover {
  background: #cbd5e0;
}

.control-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 24px;
}

.control-btn {
  padding: 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
}

.control-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.control-btn.secondary {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
}

.control-btn.warning {
  background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
  color: white;
}

.control-btn.danger {
  background: linear-gradient(135deg, #f56565 0%, #c53030 100%);
  color: white;
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.message-section {
  margin-bottom: 24px;
}

.message-section h4 {
  margin: 0 0 12px 0;
  color: #4a5568;
  font-size: 16px;
  font-weight: 600;
}

.message-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  margin-bottom: 12px;
  font-family: inherit;
}

.message-input:focus {
  outline: none;
  border-color: #667eea;
}

.quick-messages {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-message-btn {
  padding: 8px 12px;
  background: #e2e8f0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  color: #4a5568;
  transition: all 0.3s;
}

.quick-message-btn:hover {
  background: #cbd5e0;
}

.advanced-context-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header h4 {
  margin: 0;
  color: #4a5568;
  font-size: 16px;
  font-weight: 600;
}

.toggle-btn {
  padding: 6px 12px;
  background: #e2e8f0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  color: #4a5568;
}

.json-editor-container {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e2e8f0;
}

.json-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  font-size: 14px;
  font-family: monospace;
  resize: vertical;
  margin-bottom: 12px;
  background: white;
}

.json-presets {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preset-btn {
  padding: 8px 12px;
  background: #e2e8f0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  color: #4a5568;
  transition: all 0.3s;
}

.preset-btn:hover {
  background: #cbd5e0;
}

.run-bot-section {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.run-bot-btn {
  flex: 2;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
}

.run-bot-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(102, 126, 234, 0.2);
}

.run-bot-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-status-btn {
  flex: 1;
  padding: 16px;
  background: #e2e8f0;
  color: #4a5568;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  font-size: 16px;
  transition: all 0.3s;
}

.refresh-status-btn:hover {
  background: #cbd5e0;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.logs-header h3 {
  margin: 0;
}

.clear-logs-btn {
  padding: 6px 12px;
  background: #fed7d7;
  color: #c53030;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
}

.logs-content {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.empty-logs {
  text-align: center;
  padding: 40px 20px;
  color: #a0aec0;
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.log-entry {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  border-left: 4px solid #e2e8f0;
}

.log-entry.info {
  border-left-color: #4299e1;
}

.log-entry.success {
  border-left-color: #48bb78;
}

.log-entry.warning {
  border-left-color: #ed8936;
}

.log-entry.error {
  border-left-color: #f56565;
}

.log-timestamp {
  font-size: 12px;
  color: #718096;
  margin-bottom: 4px;
}

.log-message {
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 8px;
}

.log-details pre {
  font-size: 12px;
  background: white;
  padding: 8px;
  border-radius: 4px;
  margin: 0;
  overflow-x: auto;
  border: 1px solid #e2e8f0;
}

.logs-actions {
  display: flex;
  gap: 8px;
}

.export-btn, .toggle-scroll-btn {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
}

.export-btn {
  background: #c6f6d5;
  color: #22543d;
}

.toggle-scroll-btn {
  background: #e2e8f0;
  color: #4a5568;
}

.notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 16px 24px;
  border-radius: 8px;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

.notification.success {
  border-left: 4px solid #48bb78;
}

.notification.error {
  border-left: 4px solid #f56565;
}

.notification.warning {
  border-left: 4px solid #ed8936;
}

.notification.info {
  border-left: 4px solid #4299e1;
}

.close-notification {
  background: none;
  border: none;
  color: #718096;
  cursor: pointer;
  font-size: 18px;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }

  .bot-header-info {
    flex-direction: column;
    text-align: center;
  }

  .bot-status-indicator {
    align-items: center;
  }

  .control-buttons {
    grid-template-columns: 1fr;
  }

  .system-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
