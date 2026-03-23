# 🍁 MapleLoad Canada Bot - Quick Reference Guide

## 🚀 Getting Started

### 1. Start Backend Server
```powershell
cd d:\GTS
. .\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Start Frontend Dev Server
```powershell
cd d:\GTS\frontend
npm run dev
```

### 3. Access the Bot
- **Frontend**: http://127.0.0.1:5173/ai-bots/mapleload-canada
- **API Docs**: http://127.0.0.1:8000/docs
- **Backend**: http://127.0.0.1:8000

---

## 📡 API Quick Reference

### Base URL
```
http://127.0.0.1:8000/api/v1/ai/bots/mapleload-canada
```

### Public Endpoints (No Auth)
```
GET /health              → Health check
```

### Protected Endpoints (Require JWT)
```
GET    /status           → Bot status & capabilities
GET    /capabilities     → Available capabilities
POST   /market-intelligence
POST   /carrier-discovery
GET    /carriers/{province}
POST   /freight-sourcing
GET    /available-loads
POST   /outreach-campaign
POST   /lead-generation
POST   /predictive-analytics
POST   /smart-matching
POST   /advanced-report
GET    /rate-analysis
GET    /capacity-forecast
GET    /cross-border-analysis
GET    /integrations
GET    /dashboard
POST   /batch-operation
```

---

## 📊 Features Overview

### 1. 📈 Market Intelligence
- Canadian market analysis
- Regional breakdown
- Top routes analysis
- Strategic insights

### 2. 🚚 Carrier Discovery
- Find carriers by province
- Performance ratings
- Fleet information
- Specializations

### 3. 📦 Freight Sourcing
- Available loads
- Rate optimization
- Best routes
- Profit estimation

### 4. 🤝 Smart Matching
- AI algorithm selection (Hybrid, Neural Network, Random Forest, Gradient Boosting)
- Optimization goals (Profit, Speed, Reliability, Balanced)
- Match scoring
- Revenue potential

### 5. 🔮 Predictive Analytics
- Demand forecasting
- Pricing trends
- Capacity planning
- Market predictions

### 6. 📧 Outreach Automation
- Campaign creation
- Email sequences
- Follow-up scheduling
- Response tracking

### 7. 🎯 Lead Generation
- Qualified lead identification
- Industry targeting
- Conversion scoring
- Revenue potential calculation

### 8. 📑 Advanced Reporting
- Performance analytics
- Financial insights
- Market intelligence
- Carrier performance reports

### 9. 🔌 Integrations
- Salesforce CRM
- QuickBooks
- Google Sheets
- Slack
- API management

---

## 🎯 Frontend Usage

### Tab Navigation
Click the tabs at the top to switch between different bot functions:
- 📊 Market Intelligence
- 🚚 Carrier Discovery
- 📦 Freight Sourcing
- 🤝 Smart Matching
- 🔮 Predictive Analytics
- 📧 Outreach Automation
- 🎯 Lead Generation
- 📑 Advanced Reports
- 🔌 Integrations

### Executing Bot Functions
1. Select desired tab
2. Configure options (if applicable)
3. Click "Run" or "Execute" button
4. Wait for results (typically <1 second)
5. View results in Results Panel

### Results Panel
- Shows execution status (✅ Success / ❌ Error)
- Displays JSON response data
- Shows execution ID
- Can be closed with ✕ button

---

## 🔍 Example Requests

### Market Intelligence
```bash
curl -X POST http://127.0.0.1:8000/api/v1/ai/bots/mapleload-canada/market-intelligence \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Carrier Discovery
```bash
curl -X POST http://127.0.0.1:8000/api/v1/ai/bots/mapleload-canada/carrier-discovery \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"province": "ontario"}'
```

### Smart Matching
```bash
curl -X POST http://127.0.0.1:8000/api/v1/ai/bots/mapleload-canada/smart-matching \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"algorithm": "hybrid", "optimization_goal": "balanced"}'
```

---

## 🧪 Testing

### Run All Tests
```powershell
.\test_mapleload_canada_bot.ps1
```

### Manual Health Check
```bash
curl http://127.0.0.1:8000/api/v1/ai/bots/mapleload-canada/health
```

### Get Bot Status
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8000/api/v1/ai/bots/mapleload-canada/status
```

---

## 📁 Key Files

| File | Purpose | Type |
|------|---------|------|
| backend/bots/mapleload_canada.py | Bot logic | Python |
| backend/routes/mapleload_canada_routes.py | API endpoints | Python |
| frontend/src/components/bots/MapleLoadCanadaControl.jsx | UI component | React/JSX |
| frontend/src/components/bots/MapleLoadCanadaControl.css | Styling | CSS |
| test_mapleload_canada_bot.ps1 | Test suite | PowerShell |

---

## 🎨 Design Features

### Color Scheme
- 🟠 Orange (#FF5722) - Primary/Brand
- 🔵 Blue (#2196F3) - Secondary
- 🟢 Green (#4CAF50) - Success
- 🟣 Purple (#9C27B0) - Accent

### Layout
- Responsive grid design
- Mobile-first approach
- Dark mode support
- Glassmorphism effects

---

## 🔐 Authentication

### Getting a Token
1. Login at http://127.0.0.1:5173/login
2. Token automatically stored in localStorage
3. Automatically included in all API requests

### Using Token in Requests
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

## ⚙️ Configuration

### Environment Variables
```bash
# Backend
ASYNC_DATABASE_URL=postgresql+asyncpg://...
OPENAI_API_KEY=sk-...
ENV=development

# Frontend
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## 🚨 Troubleshooting

### Backend Won't Start
```
Error: Could not connect to database
Fix: Ensure PostgreSQL is running and DATABASE_URL is set
```

### Frontend 401 Errors
```
Error: 401 Unauthorized on API endpoints
Fix: Ensure JWT token is valid and browser has localStorage enabled
```

### CORS Errors
```
Error: Access to XMLHttpRequest blocked by CORS policy
Fix: Verify VITE_API_BASE_URL matches backend URL
```

### Missing Routes
```
Error: 404 on /api/v1/ai/bots/mapleload-canada/*
Fix: Ensure backend is running and routes are mounted in main.py
```

---

## 📊 Performance Tips

1. **Batch Operations**: Use `/batch-operation` for multiple requests
2. **Caching**: Frontend caches bot status for 60 seconds
3. **Async**: All backend operations are non-blocking
4. **Response Size**: Results panel shows formatted JSON

---

## 🔗 Related Documentation

- Full Implementation Guide: [MAPLELOAD_CANADA_IMPLEMENTATION.md](MAPLELOAD_CANADA_IMPLEMENTATION.md)
- API Documentation: http://127.0.0.1:8000/docs
- GTS Copilot Instructions: [.github/copilot-instructions.md](.github/copilot-instructions.md)

---

## 📞 Support

### Common Questions

**Q: How do I change the matching algorithm?**
A: In the Smart Matching tab, select from the dropdown: Hybrid (recommended), Neural Network, Random Forest, or Gradient Boosting.

**Q: Can I export results?**
A: Results can be copied from the Results Panel JSON. Full export features coming in v3.0.

**Q: Does the bot work offline?**
A: No, it requires connection to backend API. Ensure both servers are running.

**Q: Can multiple users access simultaneously?**
A: Yes, each user has their own session via JWT tokens.

---

## 🚀 Version

**MapleLoad Canada Bot v2.0.0**
- Released: January 5, 2025
- Status: ✅ Production Ready
- Last Updated: January 5, 2025

---

**Happy Trading! 🍁📦💰**
