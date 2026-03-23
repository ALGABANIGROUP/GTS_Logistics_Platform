<template>
  <div class="legal-dashboard">
    <header class="header">
      <div class="title">
        <div class="icon">LC</div>
        <div>
          <h1>AI Legal Consultant</h1>
          <p>Tax, Corporate, Transport, IP</p>
          <div class="tags">
            <span class="tag tax">TAX</span>
            <span class="tag corporate">CORP</span>
            <span class="tag transport">TRANSPORT</span>
            <span class="tag ip">IP</span>
          </div>
        </div>
      </div>
      <div class="status">
        <span class="badge">Advanced Mode</span>
        <span class="muted">Last updated: {{ lastUpdated }}</span>
        <button class="btn primary" type="button" @click="openOperationManagerChat">
          Operations Manager
        </button>
      </div>
    </header>

    <div class="columns">
      <div class="column">
        <section class="card">
          <h2>Document Review</h2>
          <div class="upload">
            <input
              ref="fileInput"
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.txt,.rtf,.xlsx,.xls"
              style="display: none"
              @change="handleFileSelect"
            >
            <div class="drop" @dragover.prevent @drop="handleFileDrop">
              <strong>Drop documents here</strong>
              <p>
                or
                <button class="link" type="button" @click="triggerFileInput">browse</button>
              </p>
              <span class="muted">Contracts, policies, and tax docs up to 20MB</span>
            </div>
            <ul v-if="selectedFiles.length" class="file-list">
              <li v-for="file in selectedFiles" :key="file.name">
                <span class="file-name">{{ file.name }}</span>
                <span class="muted">({{ formatFileSize(file.size) }})</span>
                <button class="btn ghost small" type="button" @click="removeFile(file)">Remove</button>
              </li>
            </ul>
          </div>
          <div class="row">
            <button class="btn primary" type="button" :disabled="!selectedFiles.length" @click="analyzeDocuments">
              Analyze
            </button>
            <button class="btn" type="button" @click="clearFiles">Clear</button>
            <button class="btn" type="button" :disabled="!selectedFiles.length" @click="analyzeBulkDocuments">
              Bulk analyze
            </button>
          </div>
        </section>

        <section class="card">
          <h2>Gabani Transport Solutions (GTS) Laws</h2>
          <div class="filters">
            <input v-model="lawSearchQuery" type="text" placeholder="Search laws" class="input">
            <select v-model="selectedRegion" class="input">
              <option value="all">All regions</option>
              <option value="middle_east">Middle East</option>
              <option value="europe">Europe</option>
              <option value="asia">Asia</option>
              <option value="america">Americas</option>
              <option value="africa">Africa</option>
            </select>
            <select v-model="selectedLawType" class="input">
              <option value="all">All types</option>
              <option value="road">Road</option>
              <option value="air">Air</option>
              <option value="sea">Sea</option>
              <option value="rail">Rail</option>
              <option value="multi">Multimodal</option>
            </select>
          </div>
          <div class="law-grid">
            <article
              v-for="law in filteredLaws"
              :key="law.id"
              class="law-card"
              :class="{ highlight: law.highlighted }"
              @click="viewLawDetails(law)"
            >
              <div class="law-head">
                <span class="law-code">{{ law.country }}</span>
                <span class="muted">{{ law.year }}</span>
              </div>
              <h3>{{ law.countryName }}</h3>
              <p>{{ law.title }}</p>
              <div class="law-meta">
                <span class="pill">{{ law.type }}</span>
                <span class="pill muted">{{ law.regionLabel }}</span>
              </div>
              <div class="law-tags">
                <span v-for="tag in law.tags" :key="tag" class="tag small">{{ tag }}</span>
              </div>
              <div class="row">
                <button class="btn small" type="button" @click.stop="compareWithLocalLaw(law)">Compare</button>
                <button class="btn ghost small" type="button" @click.stop="downloadLaw(law)">Download</button>
              </div>
            </article>
          </div>
          <div class="pager">
            <button class="btn small" type="button" :disabled="lawsPage === 1" @click="prevLawsPage">Prev</button>
            <span class="muted">Page {{ lawsPage }} of {{ totalLawsPages }}</span>
            <button class="btn small" type="button" :disabled="lawsPage === totalLawsPages" @click="nextLawsPage">Next</button>
          </div>
        </section>

        <section class="card">
          <h2>Analysis Results</h2>
          <div v-if="analysisResults" class="analysis">
            <div class="summary">
              <div>
                <span class="muted">Field</span>
                <strong>{{ analysisResults.field }}</strong>
              </div>
              <div>
                <span class="muted">Analyzed at</span>
                <strong>{{ analysisResults.analyzedAt }}</strong>
              </div>
              <div>
                <span class="muted">Clauses</span>
                <strong>{{ analysisResults.clauses }}</strong>
              </div>
            </div>
            <div class="risk">
              <div class="risk-score">{{ analysisResults.risk }}%</div>
              <div class="risk-bar">
                <div class="risk-fill" :class="riskClass(analysisResults.risk)" :style="{ width: analysisResults.risk + '%' }"></div>
              </div>
              <div class="risk-grid">
                <div>Tax: {{ analysisResults.taxRisk }}%</div>
                <div>Contract: {{ analysisResults.contractRisk }}%</div>
                <div>Compliance: {{ analysisResults.complianceRisk }}%</div>
              </div>
            </div>
            <div class="findings">
              <h3>Key findings</h3>
              <article v-for="finding in analysisResults.findings" :key="finding.id" class="finding" :class="finding.severity">
                <header>
                  <strong>{{ finding.title }}</strong>
                  <span class="pill">{{ finding.severity }}</span>
                  <span class="pill muted">{{ finding.category }}</span>
                </header>
                <p>{{ finding.description }}</p>
                <p v-if="finding.reference" class="muted">Reference: {{ finding.reference }}</p>
                <p v-if="finding.recommendation" class="muted">Recommendation: {{ finding.recommendation }}</p>
              </article>
            </div>
            <div class="compliance">
              <h3>Compliance matrix</h3>
              <div class="compliance-row" v-for="item in analysisResults.compliance" :key="item.name">
                <span>{{ item.name }}</span>
                <span class="status-line">
                  <span class="dot" :class="item.status"></span>
                  {{ statusLabel(item.status) }}
                </span>
                <button class="btn ghost small" type="button" @click="viewRegulationDetails(item)">Details</button>
              </div>
            </div>
          </div>
          <div v-else class="empty">
            No analysis yet. Upload a document to begin.
          </div>
        </section>
      </div>

      <div class="column">
        <section class="card">
          <h2>Control Center</h2>
          <div class="field-grid">
            <button
              v-for="field in legalFields"
              :key="field.id"
              class="field"
              :class="{ active: selectedField && selectedField.id === field.id }"
              type="button"
              @click="selectLegalField(field)"
            >
              <span>{{ field.icon }}</span>
              <strong>{{ field.name }}</strong>
              <span class="muted">{{ field.count }}</span>
            </button>
          </div>
          <div class="action-grid">
            <button
              v-for="action in legalActions"
              :key="action.id"
              class="action"
              :class="{ active: selectedAction && selectedAction.id === action.id }"
              type="button"
              @click="selectAction(action)"
            >
              {{ action.label }}
              <span v-if="action.premium" class="premium">PRO</span>
            </button>
          </div>
          <textarea
            v-model="botMessage"
            class="input"
            rows="3"
            placeholder="Describe the legal task. Example: review a cross-border contract."
          ></textarea>
          <div class="quick">
            <button v-for="query in quickQueries" :key="query" class="btn ghost small" type="button" @click="botMessage = query">
              {{ query }}
            </button>
          </div>
          <div class="box">
            <h3>Operations manager</h3>
            <select v-model="selectedOMRequestType" class="input">
              <option value="legal_review">Legal review</option>
              <option value="contract_drafting">Contract drafting</option>
              <option value="compliance_audit">Compliance audit</option>
              <option value="dispute_resolution">Dispute resolution</option>
              <option value="international_law">International law</option>
            </select>
            <textarea v-model="omMessage" class="input" rows="2" placeholder="Message to operations manager"></textarea>
            <div class="row">
              <button class="btn primary" type="button" @click="sendToOperationManager">Send</button>
              <button class="btn" type="button" @click="viewOMRequests">View requests</button>
            </div>
            <div v-if="recentOMRequests.length" class="request-list">
              <div v-for="request in recentOMRequests" :key="request.id" class="request">
                <div class="row">
                  <strong>{{ request.type }}</strong>
                  <span class="pill">{{ request.status }}</span>
                </div>
                <p>{{ request.message }}</p>
                <span class="muted">{{ request.date }} - {{ request.id }}</span>
              </div>
            </div>
          </div>
          <div class="box">
            <div class="row">
              <h3>Advanced context (JSON)</h3>
              <button class="btn ghost small" type="button" @click="toggleJsonEditor">
                {{ showJsonEditor ? 'Hide' : 'Show' }}
              </button>
              <button class="btn small" type="button" @click="validateJson">Validate</button>
            </div>
            <textarea v-if="showJsonEditor" v-model="advancedContext" class="input" rows="5"></textarea>
            <div class="quick">
              <button class="btn ghost small" type="button" @click="loadPreset('tax_review')">Tax review</button>
              <button class="btn ghost small" type="button" @click="loadPreset('transport_contract')">Transport contract</button>
              <button class="btn ghost small" type="button" @click="loadPreset('corporate_compliance')">Corporate compliance</button>
            </div>
          </div>
          <div class="row">
            <button class="btn primary" type="button" :disabled="isRunning" @click="runLegalConsultant">
              Run legal consultant
            </button>
            <button class="btn" type="button" @click="refreshLegalStatus">Refresh status</button>
          </div>
        </section>

        <section class="card">
          <h2>Activity Logs</h2>
          <div class="filter-row">
            <button
              v-for="filter in logFilters"
              :key="filter.value"
              class="btn ghost small"
              type="button"
              :class="{ active: activeLogFilters.includes(filter.value) }"
              @click="toggleLogFilter(filter.value)"
            >
              {{ filter.label }}
            </button>
          </div>
          <div class="log-list">
            <div v-if="!filteredLogs.length" class="muted">No activity yet.</div>
            <article v-for="log in filteredLogs" :key="log.id" class="log" :class="log.type">
              <div class="row">
                <strong>{{ log.message }}</strong>
                <span class="muted">{{ log.timestamp }}</span>
              </div>
              <span class="pill">{{ logTypeLabel(log.type) }}</span>
              <span v-if="log.document" class="muted">{{ log.document }}</span>
            </article>
          </div>
          <div class="row">
            <button class="btn" type="button" @click="exportLegalLogs">Export logs</button>
            <button class="btn ghost" type="button" @click="clearLogs">Clear</button>
          </div>
        </section>

        <section class="card">
          <h2>System Overview</h2>
          <div class="info-grid">
            <div>
              <span class="muted">Status</span>
              <strong>Integrated</strong>
            </div>
            <div>
              <span class="muted">Version</span>
              <strong>2.0.0</strong>
            </div>
            <div>
              <span class="muted">Countries</span>
              <strong>120</strong>
            </div>
            <div>
              <span class="muted">Documents reviewed</span>
              <strong>{{ analyzedDocuments }}</strong>
            </div>
          </div>
          <div class="stats">
            <div>
              <span>Tax</span>
              <div class="bar"><div class="fill tax" :style="{ width: stats.tax + '%' }"></div></div>
            </div>
            <div>
              <span>Transport</span>
              <div class="bar"><div class="fill transport" :style="{ width: stats.transport + '%' }"></div></div>
            </div>
            <div>
              <span>Corporate</span>
              <div class="bar"><div class="fill corporate" :style="{ width: stats.corporate + '%' }"></div></div>
            </div>
          </div>
          <p class="note">All requests are routed through operations management.</p>
        </section>
      </div>
    </div>

    <div v-if="showOMChat" class="modal">
      <div class="modal-card">
        <div class="row">
          <strong>Operations manager chat</strong>
          <button class="btn ghost small" type="button" @click="closeOMChat">Close</button>
        </div>
        <div class="chat">
          <div v-for="msg in omChatMessages" :key="msg.id" class="chat-msg" :class="msg.sender">
            <span class="muted">{{ senderLabel(msg.sender) }}</span>
            <p>{{ msg.content }}</p>
            <span class="muted">{{ msg.time }}</span>
          </div>
        </div>
        <div class="row">
          <textarea v-model="omChatInput" class="input" rows="2" placeholder="Write a message"></textarea>
          <button class="btn primary" type="button" @click="sendOMChatMessage">Send</button>
        </div>
      </div>
    </div>

    <div v-if="notification" class="toast" :class="notification.type">
      <span>{{ notification.message }}</span>
      <button class="btn ghost small" type="button" @click="notification = null">Close</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const fileInput = ref(null)
const selectedFiles = ref([])
const analysisResults = ref(null)
const botMessage = ref('')
const advancedContext = ref('')
const showJsonEditor = ref(true)
const isRunning = ref(false)
const selectedAction = ref(null)
const selectedField = ref(null)
const activeLogFilters = ref(['all'])
const showOMChat = ref(false)
const lawSearchQuery = ref('')
const selectedRegion = ref('all')
const selectedLawType = ref('all')
const lawsPage = ref(1)
const lawsPerPage = 6
const omChatInput = ref('')
const selectedOMRequestType = ref('legal_review')
const omMessage = ref('')
const notification = ref(null)

const laws = ref([
  {
    id: 1,
    country: 'SA',
    countryName: 'Saudi Arabia',
    title: 'Road Transport Regulations',
    type: 'Road',
    typeKey: 'road',
    region: 'middle_east',
    regionLabel: 'Middle East',
    year: 2023,
    tags: ['logistics', 'safety'],
    highlighted: true,
  },
  {
    id: 2,
    country: 'AE',
    countryName: 'United Arab Emirates',
    title: 'Maritime Transport Code',
    type: 'Sea',
    typeKey: 'sea',
    region: 'middle_east',
    regionLabel: 'Middle East',
    year: 2022,
    tags: ['ports', 'cargo'],
  },
  {
    id: 3,
    country: 'DE',
    countryName: 'Germany',
    title: 'Air Cargo Law',
    type: 'Air',
    typeKey: 'air',
    region: 'europe',
    regionLabel: 'Europe',
    year: 2022,
    tags: ['aviation', 'cargo'],
  },
  {
    id: 4,
    country: 'CN',
    countryName: 'China',
    title: 'Multimodal Transport Rules',
    type: 'Multimodal',
    typeKey: 'multi',
    region: 'asia',
    regionLabel: 'Asia',
    year: 2023,
    tags: ['rail', 'road', 'sea'],
  },
  {
    id: 5,
    country: 'US',
    countryName: 'United States',
    title: 'Motor Carrier Safety Regulations',
    type: 'Road',
    typeKey: 'road',
    region: 'america',
    regionLabel: 'Americas',
    year: 2023,
    tags: ['safety', 'compliance'],
  },
  {
    id: 6,
    country: 'GB',
    countryName: 'United Kingdom',
    title: 'International Transport Framework',
    type: 'Multimodal',
    typeKey: 'multi',
    region: 'europe',
    regionLabel: 'Europe',
    year: 2023,
    tags: ['international', 'customs'],
  },
])

const legalFields = ref([
  { id: 1, name: 'Tax', icon: 'TAX', count: 2450 },
  { id: 2, name: 'Transport', icon: 'TRN', count: 3200 },
  { id: 3, name: 'Corporate', icon: 'CORP', count: 1870 },
  { id: 4, name: 'IP', icon: 'IP', count: 1250 },
])

const legalActions = ref([
  { id: 1, label: 'Contract review', type: 'contract_review', premium: false },
  { id: 2, label: 'Compliance check', type: 'compliance_check', premium: false },
  { id: 3, label: 'Risk assessment', type: 'risk_assessment', premium: false },
  { id: 4, label: 'Law comparison', type: 'law_review', premium: true },
])

const quickQueries = ref([
  'Review confidentiality clauses',
  'Check tax implications',
  'Compare Saudi and UAE transport law',
  'Validate GDPR compliance',
])

const logFilters = ref([
  { value: 'all', label: 'All' },
  { value: 'analysis', label: 'Analysis' },
  { value: 'compliance', label: 'Compliance' },
  { value: 'tax', label: 'Tax' },
  { value: 'contract', label: 'Contract' },
])

const logs = ref([
  {
    id: 1,
    timestamp: '09:45:23',
    type: 'analysis',
    message: 'Reviewed a cross-border transport contract',
    document: 'transport_contract.pdf',
  },
  {
    id: 2,
    timestamp: '09:30:15',
    type: 'compliance',
    message: 'GDPR compliance check completed',
    document: 'privacy_policy.docx',
  },
])

const omRequests = ref([
  {
    id: 'OM-2024-001',
    type: 'Legal review',
    message: 'Review a cross-border shipping contract',
    status: 'Complete',
    date: '2024-01-15',
  },
  {
    id: 'OM-2024-002',
    type: 'Contract drafting',
    message: 'Draft a logistics partnership agreement',
    status: 'In review',
    date: '2024-01-16',
  },
])

const omChatMessages = ref([
  {
    id: 1,
    sender: 'user',
    content: 'I need a legal review for a German transport contract.',
    time: '10:30',
  },
  {
    id: 2,
    sender: 'om',
    content: 'Request received. Assigning to EU transport specialist.',
    time: '10:32',
  },
])

const analyzedDocuments = ref(1247)
const stats = ref({ tax: 85, transport: 92, corporate: 78 })

const lastUpdated = computed(() => new Date().toLocaleString('en-US'))

const filteredLawBase = computed(() => {
  let filtered = laws.value
  if (lawSearchQuery.value) {
    const query = lawSearchQuery.value.toLowerCase()
    filtered = filtered.filter((law) =>
      law.countryName.toLowerCase().includes(query) ||
      law.title.toLowerCase().includes(query) ||
      law.tags.some((tag) => tag.toLowerCase().includes(query))
    )
  }
  if (selectedRegion.value !== 'all') {
    filtered = filtered.filter((law) => law.region === selectedRegion.value)
  }
  if (selectedLawType.value !== 'all') {
    filtered = filtered.filter((law) => law.typeKey === selectedLawType.value)
  }
  return filtered
})

const filteredLaws = computed(() => {
  const start = (lawsPage.value - 1) * lawsPerPage
  const end = start + lawsPerPage
  return filteredLawBase.value.slice(start, end)
})

const totalLawsPages = computed(() => {
  return Math.max(1, Math.ceil(filteredLawBase.value.length / lawsPerPage))
})

const recentOMRequests = computed(() => omRequests.value.slice(0, 3))

const filteredLogs = computed(() => {
  if (activeLogFilters.value.includes('all')) {
    return logs.value
  }
  return logs.value.filter((log) => activeLogFilters.value.includes(log.type))
})

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

const notify = (message, type = 'info') => {
  notification.value = { message, type }
  setTimeout(() => {
    notification.value = null
  }, 4000)
}
const riskClass = (score) => {
  if (score < 30) return 'low'
  if (score < 70) return 'medium'
  return 'high'
}

const statusLabel = (status) => {
  const labels = {
    compliant: 'Compliant',
    non_compliant: 'Non-compliant',
    requires_review: 'Needs review',
    partial: 'Partial',
  }
  return labels[status] || status
}

const logTypeLabel = (type) => {
  const labels = {
    analysis: 'Analysis',
    compliance: 'Compliance',
    tax: 'Tax',
    contract: 'Contract',
  }
  return labels[type] || type
}

const senderLabel = (sender) => (sender === 'user' ? 'You' : 'Operations manager')

const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  if (files.length > 10) {
    notify('You can upload up to 10 files.', 'warning')
    files.splice(10)
  }
  files.forEach((file) => {
    if (file.size > 20 * 1024 * 1024) {
      notify(`File too large: ${file.name}`, 'warning')
      return
    }
    if (!selectedFiles.value.some((f) => f.name === file.name)) {
      selectedFiles.value.push(file)
    }
  })
  event.target.value = ''
}

const handleFileDrop = (event) => {
  event.preventDefault()
  const files = Array.from(event.dataTransfer.files).filter((file) =>
    ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.xlsx', '.xls'].some((ext) =>
      file.name.toLowerCase().endsWith(ext)
    )
  )
  if (files.length) {
    handleFileSelect({ target: { files } })
  }
}

const removeFile = (fileToRemove) => {
  selectedFiles.value = selectedFiles.value.filter((file) => file !== fileToRemove)
}

const clearFiles = () => {
  selectedFiles.value = []
  analysisResults.value = null
}

const analyzeDocuments = async () => {
  if (!selectedFiles.value.length) {
    notify('Select files before analysis.', 'warning')
    return
  }
  isRunning.value = true
  notify('Running legal analysis...', 'info')
  try {
    await new Promise((resolve) => setTimeout(resolve, 2000))
    analysisResults.value = {
      field: selectedField.value ? selectedField.value.name : 'General',
      clauses: 28,
      risk: 62,
      taxRisk: 48,
      contractRisk: 70,
      complianceRisk: 58,
      analyzedAt: new Date().toLocaleString('en-US'),
      findings: [
        {
          id: 1,
          title: 'Ambiguous liability clause',
          severity: 'high',
          category: 'Transport',
          description: 'Liability allocation is unclear for multi-leg shipments.',
          reference: 'IMC 2023 Section 12',
          recommendation: 'Define liability per leg and carrier handoff.',
        },
        {
          id: 2,
          title: 'Tax exposure not defined',
          severity: 'medium',
          category: 'Tax',
          description: 'Contract omits responsibility for transit taxes.',
          reference: 'VAT Regulation Article 8',
          recommendation: 'Allocate tax obligations for transit jurisdictions.',
        },
      ],
      compliance: [
        { name: 'Saudi Road Transport Law', status: 'compliant' },
        { name: 'International Transport Convention', status: 'partial' },
        { name: 'GDPR', status: 'requires_review' },
        { name: 'Unified Customs Code', status: 'non_compliant' },
      ],
    }
    logs.value.unshift({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString('en-US'),
      type: 'analysis',
      message: `Analyzed ${selectedFiles.value.length} document(s)`,
      document: selectedFiles.value.map((f) => f.name).join(', '),
    })
    analyzedDocuments.value += selectedFiles.value.length
    notify('Analysis complete.', 'success')
  } catch (error) {
    notify('Analysis failed.', 'error')
  } finally {
    isRunning.value = false
  }
}

const analyzeBulkDocuments = async () => {
  notify('Starting bulk analysis...', 'info')
  await analyzeDocuments()
}

const selectLegalField = (field) => {
  selectedField.value = field
  notify(`Selected field: ${field.name}`, 'info')
}

const selectAction = (action) => {
  selectedAction.value = action
  botMessage.value = `Action: ${action.label}`
  notify(`Selected action: ${action.label}`, 'info')
}

const runLegalConsultant = async () => {
  if (!botMessage.value.trim() && !advancedContext.value.trim()) {
    notify('Add a request message or context.', 'warning')
    return
  }
  isRunning.value = true
  notify('Processing request...', 'info')
  try {
    const context = advancedContext.value.trim() ? JSON.parse(advancedContext.value) : {}
    const message = botMessage.value.trim() || 'General request'
    await new Promise((resolve) => setTimeout(resolve, 1500))
    logs.value.unshift({
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString('en-US'),
      type: selectedAction.value ? selectedAction.value.type : 'analysis',
      message,
      document: context.document || null,
    })
    notify('Request completed.', 'success')
  } catch (error) {
    notify('Request failed.', 'error')
  } finally {
    isRunning.value = false
  }
}

const refreshLegalStatus = () => {
  analyzedDocuments.value += Math.floor(Math.random() * 4)
  stats.value.tax = Math.min(100, stats.value.tax + 1)
  stats.value.transport = Math.min(100, stats.value.transport + 1)
  stats.value.corporate = Math.min(100, stats.value.corporate + 1)
  notify('Status updated.', 'success')
}

const toggleJsonEditor = () => {
  showJsonEditor.value = !showJsonEditor.value
}

const validateJson = () => {
  try {
    JSON.parse(advancedContext.value)
    notify('JSON is valid.', 'success')
  } catch (error) {
    notify(`Invalid JSON: ${error.message}`, 'error')
  }
}

const loadPreset = (preset) => {
  const presets = {
    tax_review: { jurisdiction: 'saudi_arabia', legal_fields: ['tax'], review_depth: 'detailed' },
    transport_contract: { jurisdiction: 'multi', legal_fields: ['transport'], review_depth: 'comprehensive' },
    corporate_compliance: { jurisdiction: 'uae', legal_fields: ['corporate'], review_depth: 'audit' },
  }
  advancedContext.value = JSON.stringify(presets[preset], null, 2)
  notify(`Loaded preset: ${preset}`, 'info')
}

const toggleLogFilter = (filter) => {
  if (filter === 'all') {
    activeLogFilters.value = ['all']
    return
  }
  activeLogFilters.value = activeLogFilters.value.filter((f) => f !== 'all')
  if (activeLogFilters.value.includes(filter)) {
    activeLogFilters.value = activeLogFilters.value.filter((f) => f !== filter)
  } else {
    activeLogFilters.value.push(filter)
  }
  if (!activeLogFilters.value.length) {
    activeLogFilters.value = ['all']
  }
}

const viewLawDetails = (law) => {
  notify(`Viewing details for ${law.title}`, 'info')
}

const compareWithLocalLaw = (law) => {
  notify(`Comparing ${law.countryName} law with local rules`, 'info')
}

const downloadLaw = (law) => {
  notify(`Preparing download: ${law.title}`, 'info')
}

const prevLawsPage = () => {
  if (lawsPage.value > 1) lawsPage.value -= 1
}

const nextLawsPage = () => {
  if (lawsPage.value < totalLawsPages.value) lawsPage.value += 1
}

const openOperationManagerChat = () => {
  showOMChat.value = true
}

const closeOMChat = () => {
  showOMChat.value = false
}

const sendOMChatMessage = () => {
  if (!omChatInput.value.trim()) return
  omChatMessages.value.push({
    id: Date.now(),
    sender: 'user',
    content: omChatInput.value,
    time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
  })
  omChatInput.value = ''
  setTimeout(() => {
    omChatMessages.value.push({
      id: Date.now() + 1,
      sender: 'om',
      content: 'Request received. We will reply within one business day.',
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    })
  }, 800)
}

const sendToOperationManager = () => {
  if (!omMessage.value.trim() && !analysisResults.value) {
    notify('Add a message or analysis before sending.', 'warning')
    return
  }
  const requestId = `OM-${Date.now()}`
  omRequests.value.unshift({
    id: requestId,
    type: selectedOMRequestType.value,
    message: omMessage.value || 'Legal analysis attached',
    status: 'Received',
    date: new Date().toLocaleDateString('en-US'),
  })
  omMessage.value = ''
  notify('Sent to operations manager.', 'success')
}

const viewOMRequests = () => {
  notify('Loading request history...', 'info')
}

const viewRegulationDetails = (item) => {
  notify(`Viewing ${item.name}`, 'info')
}

const exportLegalLogs = () => {
  const data = {
    logs: logs.value,
    exportDate: new Date().toISOString(),
  }
  const dataStr = JSON.stringify(data, null, 2)
  const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`
  const fileName = `legal-logs-${new Date().toISOString().slice(0, 10)}.json`
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', fileName)
  linkElement.click()
  notify('Exported logs.', 'success')
}

const clearLogs = () => {
  logs.value = []
  notify('Logs cleared.', 'info')
}

onMounted(() => {
  selectedField.value = legalFields.value[0]
  selectedAction.value = legalActions.value[0]
})
</script>

<style scoped>
.legal-dashboard {
  min-height: 100vh;
  padding: 24px;
  background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
  color: #0f172a;
}

.header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: center;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 20px;
  padding: 24px 28px;
  margin-bottom: 24px;
  box-shadow: 0 12px 20px rgba(15, 23, 42, 0.2);
}

.title {
  display: flex;
  gap: 18px;
  align-items: center;
}

.icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb 0%, #1e293b 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
}

.tags {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
}

.tag.tax { background: #f59e0b; }
.tag.corporate { background: #10b981; }
.tag.transport { background: #3b82f6; }
.tag.ip { background: #7c3aed; }
.tag.small { font-size: 11px; padding: 2px 8px; }

.status {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}

.status-line {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.badge {
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  color: #fff;
  padding: 6px 14px;
  border-radius: 999px;
  font-weight: 700;
}

.muted {
  color: #64748b;
  font-size: 12px;
}

.columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 10px 18px rgba(15, 23, 42, 0.15);
}

h2 {
  margin: 0 0 16px;
  font-size: 18px;
}

.upload .drop {
  border: 2px dashed #cbd5f5;
  border-radius: 16px;
  padding: 16px;
  text-align: center;
  background: #f8fafc;
  margin-bottom: 12px;
}

.link {
  border: none;
  background: none;
  color: #2563eb;
  font-weight: 700;
  cursor: pointer;
  text-decoration: underline;
}

.file-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-list li {
  display: flex;
  gap: 12px;
  align-items: center;
}

.file-name {
  flex: 1;
  font-weight: 600;
}

.row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.btn {
  border: none;
  padding: 8px 14px;
  border-radius: 10px;
  background: #e2e8f0;
  cursor: pointer;
  font-weight: 600;
}

.btn.primary {
  background: linear-gradient(135deg, #2563eb 0%, #1e3a8a 100%);
  color: #fff;
}

.btn.ghost {
  background: transparent;
  border: 1px solid #e2e8f0;
}

.btn.small {
  padding: 6px 10px;
  font-size: 12px;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}

.input {
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid #cbd5f5;
  width: 100%;
  font-family: inherit;
}

.law-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.law-card {
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 12px;
  background: #fff;
}

.law-card.highlight { border-color: #f59e0b; }

.law-head {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.law-code {
  font-weight: 800;
}

.law-meta {
  display: flex;
  gap: 6px;
  margin: 8px 0;
}

.pill {
  padding: 2px 8px;
  border-radius: 999px;
  background: #e2e8f0;
  font-size: 11px;
}

.pager {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.analysis .summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.risk {
  background: #f8fafc;
  border-radius: 14px;
  padding: 12px;
  margin-bottom: 12px;
}

.risk-score {
  font-size: 26px;
  font-weight: 800;
}

.risk-bar {
  height: 10px;
  background: #e2e8f0;
  border-radius: 999px;
  overflow: hidden;
  margin: 8px 0;
}

.risk-fill { height: 100%; }
.risk-fill.low { background: #10b981; }
.risk-fill.medium { background: #f59e0b; }
.risk-fill.high { background: #ef4444; }

.risk-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 6px;
}

.finding {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 10px;
  margin-top: 8px;
}

.finding.high { border-left: 4px solid #f59e0b; }
.finding.medium { border-left: 4px solid #fbbf24; }

.compliance-row {
  display: grid;
  grid-template-columns: 2fr 1fr auto;
  gap: 8px;
  align-items: center;
  padding: 6px 0;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.dot.compliant { background: #10b981; }
.dot.non_compliant { background: #ef4444; }
.dot.requires_review { background: #f59e0b; }
.dot.partial { background: #7c3aed; }

.empty {
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.field-grid,
.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}

.field,
.action {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 10px;
  background: #fff;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field.active,
.action.active {
  border-color: #2563eb;
  background: #eff6ff;
}

.premium {
  background: #f59e0b;
  color: #fff;
  padding: 2px 6px;
  border-radius: 999px;
  font-size: 10px;
}

.quick {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 8px 0 12px;
}

.box {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px;
  margin-top: 12px;
  background: #f8fafc;
}

.request {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 8px;
  margin-top: 8px;
  background: #fff;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}

.log {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 10px;
  background: #fff;
}

.log.analysis { border-left: 4px solid #2563eb; }
.log.compliance { border-left: 4px solid #10b981; }
.log.tax { border-left: 4px solid #f59e0b; }
.log.contract { border-left: 4px solid #7c3aed; }

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.stats {
  display: grid;
  gap: 10px;
}

.bar {
  height: 8px;
  background: #e2e8f0;
  border-radius: 999px;
  overflow: hidden;
}

.fill { height: 100%; }
.fill.tax { background: #f59e0b; }
.fill.transport { background: #3b82f6; }
.fill.corporate { background: #10b981; }

.note {
  margin-top: 12px;
  font-size: 12px;
  color: #475569;
}

.modal {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: #fff;
  border-radius: 18px;
  padding: 18px;
  width: min(90%, 540px);
}

.chat {
  max-height: 240px;
  overflow-y: auto;
  margin: 12px 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chat-msg {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 8px;
  background: #f8fafc;
}

.chat-msg.user { background: #eff6ff; }

.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: #fff;
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 10px 20px rgba(15, 23, 42, 0.2);
  display: flex;
  gap: 12px;
  align-items: center;
  z-index: 1001;
}

.toast.success { border-left: 4px solid #10b981; }
.toast.error { border-left: 4px solid #ef4444; }
.toast.warning { border-left: 4px solid #f59e0b; }
.toast.info { border-left: 4px solid #3b82f6; }

@media (max-width: 1000px) {
  .columns { grid-template-columns: 1fr; }
  .status { align-items: flex-start; }
}

@media (max-width: 640px) {
  .header { flex-direction: column; align-items: flex-start; }
}
</style>
