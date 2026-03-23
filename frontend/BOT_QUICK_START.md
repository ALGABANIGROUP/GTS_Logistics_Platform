# 🚀 Bot Routing Quick Start Guide

## Live Routes

### 🔹 Hub Dashboard (Central Control)
```
http://localhost:5173/ai-bots/hub
```
Click any bot card to launch its control panel

---

## ✅ Active Control Panels (Ready Now)

### Phase 1: Core Bots
```
/ai-bots/general-manager          👔 General Manager
/ai-bots/freight-broker            🚛 Freight Broker
/ai-bots/mapleload-canada          🇨🇦 MapleLoad Canada
/ai-bots/executive-intelligence    👑 Executive Intelligence
```

### Phase 2: Operational
```
/ai-bots/data-coordinator          📊 Data Coordinator
/ai-bots/freight-bookings          📦 Freight Bookings
/ai-bots/finance-intelligence      💰 Finance Intelligence
```

### Phase 3: Administrative
```
/ai-bots/security-question         🛡️ Security (Mock Mode)
/ai-bots/sales-intelligence        📈 Sales Intelligence
/ai-bots/legal-counsel             ⚖️ Legal Counsel
```

### Phase 4: Support
```
/ai-bots/partner-management        🤝 Partner Management (Mock Mode)
```

---

## 🔧 Development Setup

### 1. Testing a Route
```bash
# Visit in browser
http://localhost:5173/ai-bots/hub

# Or navigate directly to a bot
http://localhost:5173/ai-bots/freight-bookings
```

### 2. Adding a New Bot

**Step 1:** Create Control Panel
```jsx
// src/components/bots/YourBotControlPanel.jsx
const YourBotControlPanel = () => {
  // Follow existing panel structure
};
export default YourBotControlPanel;
```

**Step 2:** Create Wrapper
```jsx
// src/pages/ai-bots/wrappers/AIYourBotControlPage.jsx
import YourBotControlPanel from '../../../components/bots/YourBotControlPanel';
export default () => <YourBotControlPanel />;
```

**Step 3:** Add Route to App.jsx
```jsx
import AIYourBotControlPage from "./pages/ai-bots/wrappers/AIYourBotControlPage";

// In Routes section:
<Route
  path="/ai-bots/your-bot"
  element={
    <RequireAuth>
      <Layout>
        <AIYourBotControlPage />
      </Layout>
    </RequireAuth>
  }
/>
```

**Step 4:** Update Hub
```jsx
// In AIBotsHubDashboard.jsx botsRegistry:
{
  id: XX,
  name: 'Your Bot',
  description: 'Description here',
  icon: '🤖',
  path: '/ai-bots/your-bot',
  status: 'active',
  phase: 1,
  features: ['Feature 1', 'Feature 2'],
  controlPanel: 'YourBotControlPanel'
}
```

**Step 5:** Update Exports
```jsx
// src/components/bots/index.js
export { default as YourBotControlPanel } from "./YourBotControlPanel";
```

---

## 📁 Key Files

### Routes & Navigation
- `App.jsx` - Main route definitions
- `AIBotsHubDashboard.jsx` - Central hub with all 17 bots
- `BOT_ROUTING_GUIDE.js` - Complete routing documentation

### Control Panels (Ready)
- `FreightBrokerControlPanel.jsx` ✅
- `MapleLoadControlPanel.jsx` ✅
- `ExecutiveIntelligenceControlPanel.jsx` ✅
- `DataCoordinatorControlPanel.jsx` ✅
- `FreightBookingsControlPanel.jsx` ✅
- `FinanceControlPanel.jsx` ✅
- `SecurityControlPanel.jsx` ✅
- `SalesControlPanel.jsx` ✅
- `LegalControlPanel.jsx` ✅
- `PartnerManagementControlPanel.jsx` ✅

### Wrappers (Ready)
- `wrappers/AIFreightBookingsControlPage.jsx` ✅
- `wrappers/AIDataCoordinatorControlPage.jsx` ✅
- `wrappers/AIFinanceControlPage.jsx` ✅
- `wrappers/AISecurityControlPage.jsx` ✅
- `wrappers/AISalesControlPage.jsx` ✅
- `wrappers/AILegalControlPage.jsx` ✅
- `wrappers/AIPartnerManagementControlPage.jsx` ✅

---

## 🎨 Control Panel Structure

All Control Panels follow this pattern:

```jsx
const BotControlPanel = () => {
  // State
  const [activeTab, setActiveTab] = useState('dashboard');
  const [panelData, setPanelData] = useState({});
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // Data fetching
  const fetchPanelData = useCallback(async () => {
    try {
      const response = await axiosClient.get(`/api/v1/ai/bots/{BOT_KEY}/status`);
      setPanelData(response.data);
      setConnected(true);
    } catch (error) {
      setConnected(false);
    }
  }, []);
  
  // Auto-refresh
  useEffect(() => {
    fetchPanelData();
    const interval = setInterval(fetchPanelData, 30000);
    return () => clearInterval(interval);
  }, [fetchPanelData]);
  
  // Render header, tabs, content, footer
  return (/* JSX */);
};
```

---

## 🔌 API Integration

### Endpoints Used
```
GET  /api/v1/ai/bots/{BOT_KEY}/status  - Get bot status
POST /api/v1/ai/bots/{BOT_KEY}/run     - Execute action
```

### Mock Mode
When backend isn't active:
```jsx
const BACKEND_ACTIVE = false; // Set to true when backend ready

if (!BACKEND_ACTIVE) {
  // Use mock data
  setConnected(false);
  setPanelData(mockData);
}
```

---

## 🧪 Testing Checklist

- [ ] Hub dashboard loads at `/ai-bots/hub`
- [ ] All 17 bots appear in hub
- [ ] Search filter works
- [ ] Status filter (Active/Dev) works
- [ ] Clicking bot card navigates to control panel
- [ ] Control panel header displays
- [ ] Tabs are clickable
- [ ] Quick actions work (or show mock)
- [ ] Activity log updates
- [ ] Sidebar displays stats
- [ ] Footer shows last sync time

---

## 📊 Stats

| Item | Count |
|------|-------|
| Total Bots | 17 |
| Active Routes | 17 |
| Control Panels | 10 |
| Wrapper Pages | 8 |
| Hub Dashboard | 1 |

---

## 🚨 Troubleshooting

### Route Not Found
- Check App.jsx has the route
- Verify path spelling (use hyphens, not camelCase)
- Clear browser cache

### Component Not Loading
- Check import path in wrapper
- Verify component is exported in index.js
- Check console for import errors

### Data Not Showing
- Verify API endpoint exists
- Check axiosClient interceptors
- Enable mock mode if backend not ready
- Check browser network tab

### Styling Issues
- Check Tailwind CSS is loaded
- Verify dark mode classes
- Check responsive breakpoints

---

## 📖 Documentation

Full documentation at:
```
frontend/src/pages/ai-bots/BOT_ROUTING_GUIDE.js
frontend/BOT_IMPLEMENTATION_SUMMARY.md
```

---

**🎯 Status:** Production Ready  
**Last Update:** January 5, 2026  
**Version:** 1.0
