# Real Data Integration Setup

This document explains how to configure the system to use real data instead of mock data.

## Required API Keys

Add these environment variables to your `.env` file:

### Weather API (OpenWeatherMap)
```
OPENWEATHER_API_KEY=your_openweather_api_key_here
```
- Get your free API key from: https://openweathermap.org/api
- Free tier allows 1000 calls/day

### Market Analysis API (Alpha Vantage)
```
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
```
- Get your free API key from: https://www.alphavantage.co/support/#api-key
- Free tier allows 25 calls/day

### News API (MarketAux)
```
MARKETAUX_KEY=your_marketaux_key_here
```
- Get your API key from: https://marketaux.com/
- Free tier available

### Government/Legal API (Optional)
```
GOV_API_KEY=your_gov_api_key_here
```
- For regulatory updates (Saudi Arabia, US, etc.)

## Running the Setup Scripts

After configuring the API keys, run these scripts to populate real data:

### 1. Real Incidents for Safety Manager
```bash
cd /path/to/project
python scripts/seed_real_incidents.py
```

### 2. Marketing Campaigns
```bash
python scripts/seed_marketing_campaigns.py
```

### 3. Test the Weather API
```bash
curl "http://localhost:8000/api/v1/weather/current?city=Riyadh"
```

## Services Overview

### WeatherService (`backend/services/weather_service.py`)
- Real-time weather data from OpenWeatherMap
- 5-day forecasts with risk analysis
- Automatic fallback to mock data if API fails

### MarketAnalysisService (`backend/services/market_analysis_service.py`)
- Stock market trends from Alpha Vantage
- Competitor news from MarketAux
- Real-time market intelligence

### LegalUpdatesService (`backend/services/legal_updates_service.py`)
- Regulatory updates for transportation industry
- Country-specific legal requirements
- Compliance monitoring

### LogAnalysisService (`backend/services/log_analysis_service.py`)
- Real log file analysis for security events
- Pattern matching for suspicious activities
- Automated security recommendations

### CampaignService (`backend/services/campaign_service.py`)
- Real marketing campaign management
- Database-backed campaign tracking
- Performance analytics

## Database Models

### Marketing Models (`backend/models/marketing.py`)
- Campaign: Marketing campaigns with budgets and targeting
- CampaignStatus: Draft, Active, Paused, Completed, Cancelled
- CampaignType: Promotion, Loyalty, Seasonal, Brand Awareness, Lead Generation

## Bot Updates

### Freight Broker Bot
- Now uses real database queries instead of mock data
- Carrier and shipment data from PostgreSQL
- Real-time status updates

### Weather Forecast System
- Real weather data integration
- Risk analysis based on actual forecasts
- Fallback mechanisms for reliability

## Testing

Test each service individually:

```bash
# Test weather service
python -c "from backend.services.weather_service import WeatherService; ws = WeatherService(); print(ws.get_current_weather('Riyadh'))"

# Test market analysis
python -c "from backend.services.market_analysis_service import MarketAnalysisService; ms = MarketAnalysisService(); print(ms.get_market_trends())"

# Test log analysis
python -c "from backend.services.log_analysis_service import LogAnalysisService; ls = LogAnalysisService(); print(ls.analyze_logs())"
```

## Monitoring

All services include:
- Error handling and logging
- Cache mechanisms to reduce API calls
- Fallback to mock data when APIs are unavailable
- Performance monitoring and metrics