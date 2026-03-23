# Frontend Update Guide for Executive Intelligence Bot

## Current Implementation

The [ExecutiveIntelligenceControlPanel.jsx](d:\GTS\frontend\src\components\bots\ExecutiveIntelligenceControlPanel.jsx) currently uses:

1. **Generic Bot API**: `/api/v1/ai/bots/executive_intelligence/run`
2. **Analytics API**: `/api/v1/analytics/kpis`

## New Specialized API Endpoints Available

The backend now provides **8 dedicated endpoints** for richer functionality:

### Available Endpoints

```javascript
// 1. Health Check (no auth)
GET /api/v1/ai/bots/executive-intelligence/health

// 2. Bot Status & Metrics
GET /api/v1/ai/bots/executive-intelligence/status

// 3. Executive KPIs
GET /api/v1/ai/bots/executive-intelligence/kpis

// 4. Generate Executive Report
POST /api/v1/ai/bots/executive-intelligence/generate-report
{
  "report_type": "executive_summary",
  "period": "weekly",
  "departments": ["sales", "operations", "finance"],
  "include_forecast": true
}

// 5. Analyze Performance
POST /api/v1/ai/bots/executive-intelligence/analyze-performance
{
  "kpi_type": "financial",
  "compare_period": "previous_month",
  "depth": "detailed"
}

// 6. Market Analysis
POST /api/v1/ai/bots/executive-intelligence/market-analysis
{
  "market_scope": "domestic",
  "competitors": ["all"],
  "time_horizon": "quarterly"
}

// 7. Strategic Recommendations
POST /api/v1/ai/bots/executive-intelligence/strategic-recommendations
{
  "focus_areas": ["growth", "efficiency", "innovation"],
  "risk_tolerance": "medium",
  "time_frame": "6_months"
}

// 8. Bot Capabilities
GET /api/v1/ai/bots/executive-intelligence/capabilities
```

## Recommended Updates

### Option 1: Keep Current Implementation (Generic API)
**No changes needed** - the generic API still works:
```javascript
await axiosClient.post(`/api/v1/ai/bots/${BOT_KEY}/run`, {
  action: "status"
});
```

### Option 2: Use Specialized Endpoints (Recommended)
**Better performance and richer responses**:

```javascript
// Replace loadPanelData() implementation:
const loadPanelData = useCallback(async () => {
    if (isPreview) return;
    setLoading(true);
    try {
        const [statusRes, kpisRes] = await Promise.all([
            // Use specialized status endpoint
            axiosClient.get(`/api/v1/ai/bots/executive-intelligence/status`).catch(() => null),
            // Use specialized KPIs endpoint
            axiosClient.get("/api/v1/ai/bots/executive-intelligence/kpis").catch(() => null),
        ]);

        if (statusRes?.data) {
            // statusRes.data contains:
            // {
            //   status: "active",
            //   metrics: { reports_generated: 156, accuracy_rate: "94%", ... },
            //   performance: { success_rate: "96%", avg_execution_time: "3.8s" }
            // }
            setConnected(true);
        }
        
        if (kpisRes?.data) {
            // kpisRes.data contains:
            // {
            //   financial_kpis: [...],
            //   operational_kpis: [...],
            //   strategic_kpis: [...]
            // }
            setPanelData(prev => ({
                ...prev,
                kpis: {
                    financial: kpisRes.data.financial_kpis,
                    operational: kpisRes.data.operational_kpis,
                }
            }));
        }
        
        setLastUpdate(new Date());
    } catch (err) {
        console.warn("Panel data load error:", err);
    } finally {
        setLoading(false);
    }
}, [isPreview]);
```

### Add New Handler Functions

```javascript
// Add these handlers to the component:

const handleGenerateReport = async (reportOptions) => {
    setLoading(true);
    try {
        const response = await axiosClient.post(
            '/api/v1/ai/bots/executive-intelligence/generate-report',
            reportOptions
        );
        
        // response.data contains:
        // {
        //   success: true,
        //   execution_id: "exec_report_123...",
        //   status: "completed",
        //   data: { /* full report */ }
        // }
        
        return response.data;
    } catch (error) {
        console.error('Report generation failed:', error);
        throw error;
    } finally {
        setLoading(false);
    }
};

const handleAnalyzePerformance = async (analysisOptions) => {
    setLoading(true);
    try {
        const response = await axiosClient.post(
            '/api/v1/ai/bots/executive-intelligence/analyze-performance',
            analysisOptions
        );
        return response.data;
    } catch (error) {
        console.error('Performance analysis failed:', error);
        throw error;
    } finally {
        setLoading(false);
    }
};

const handleMarketAnalysis = async (marketOptions) => {
    setLoading(true);
    try {
        const response = await axiosClient.post(
            '/api/v1/ai/bots/executive-intelligence/market-analysis',
            marketOptions
        );
        return response.data;
    } catch (error) {
        console.error('Market analysis failed:', error);
        throw error;
    } finally {
        setLoading(false);
    }
};

const handleStrategicRecommendations = async (recommendationOptions) => {
    setLoading(true);
    try {
        const response = await axiosClient.post(
            '/api/v1/ai/bots/executive-intelligence/strategic-recommendations',
            recommendationOptions
        );
        return response.data;
    } catch (error) {
        console.error('Recommendations failed:', error);
        throw error;
    } finally {
        setLoading(false);
    }
};
```

## Benefits of Using Specialized Endpoints

1. **Richer Data**: Each endpoint returns structured data specific to that action
2. **Better Performance**: Optimized queries for each use case
3. **Type Safety**: Pydantic validation on backend ensures data integrity
4. **Error Handling**: Better error messages and status codes
5. **Extensibility**: Easy to add new fields without breaking generic API

## Migration Strategy

### Phase 1: Add Parallel Support (No Breaking Changes)
- Keep existing generic API calls working
- Add new specialized endpoint calls alongside
- Test both implementations

### Phase 2: Switch to Specialized Endpoints
- Update all handlers to use new endpoints
- Remove generic API fallbacks
- Update tests

### Phase 3: Deprecate Generic API
- Mark generic endpoints as deprecated
- Update documentation
- Monitor usage

## Testing

```bash
# Start backend
cd d:\GTS
.\run-dev.ps1

# Start frontend
cd d:\GTS\frontend
npm run dev

# Test specialized endpoints
.\test_executive_intelligence_api.ps1
```

## Example: Full Integration

```javascript
// In ExecutiveIntelligenceControlPanel.jsx

// Load initial data
useEffect(() => {
    const fetchInitialData = async () => {
        try {
            const [status, kpis, capabilities] = await Promise.all([
                axiosClient.get('/api/v1/ai/bots/executive-intelligence/status'),
                axiosClient.get('/api/v1/ai/bots/executive-intelligence/kpis'),
                axiosClient.get('/api/v1/ai/bots/executive-intelligence/capabilities'),
            ]);
            
            // Update state with real data
            setPanelData({
                status: status.data,
                kpis: kpis.data,
                capabilities: capabilities.data,
            });
            
            setConnected(true);
        } catch (error) {
            console.error('Failed to load data:', error);
            setConnected(false);
        }
    };
    
    if (!isPreview) {
        fetchInitialData();
    }
}, [isPreview]);

// Button handler example
const onGenerateReportClick = async () => {
    const reportData = await handleGenerateReport({
        report_type: 'executive_summary',
        period: 'weekly',
        departments: ['sales', 'operations', 'finance'],
        include_forecast: true
    });
    
    // Display report in UI
    setLastResult(reportData);
};
```

## Summary

✅ **Backend API is ready** with 8 specialized endpoints  
✅ **Frontend can optionally upgrade** to use specialized endpoints  
✅ **No breaking changes** - generic API still works  
✅ **Better UX** with specialized endpoints (richer data, better errors)  

**Decision**: Keep current implementation OR upgrade to specialized endpoints (both work!)
