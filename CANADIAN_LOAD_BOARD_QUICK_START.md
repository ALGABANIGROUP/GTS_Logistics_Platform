# 🚛 Canadian Freight Broker Load Board - Quick Start

## Overview
Complete freight load board with Canadian cross-border logistics support. TruckerPath-style interface for searching, booking, and managing freight loads across Canada and the US.

## 🚀 Quick Access

### Frontend URL
```
http://localhost:5173/freight-broker/loads
```

### API Endpoints
```
http://localhost:8000/api/v1/freight/canadian-loads
http://localhost:8000/api/v1/freight/canadian-market-rates
http://localhost:8000/api/v1/freight/backhaul-opportunities
```

## 💻 Launch Instructions

### Start Backend
```powershell
python -m uvicorn backend.main:app --reload
```

### Start Frontend
```powershell
cd frontend
npm run dev
```

### Open Interface
```
http://localhost:5173/freight-broker/loads
```

## 📋 Demo Data
6 sample Canadian loads included:

| Origin | Destination | Distance | Rate (CAD) | Trailer |
|--------|------------|----------|------------|---------|
| Grande Cache, AB | Grand Island, NE | 1619 mi | $2,425 | Flatbed |
| Edmonton, AB | Edgeley, ND | 983 mi | $2,425 | Step Deck |
| Edmonton, AB | Perris, CA | 1740 mi | -- | Reefer |
| Edmonton, AB | Waterloo, NE | 1431 mi | $2,000 | Van |
| Edmonton, AB | Twin Falls, ID | 1028 mi | $1,800 | Van |
| Edmonton, AB | Idaho Falls, ID | 880 mi | $1,500 | Van |

## ✨ Key Features

### 🧭 Route Builder
- Multi-route configuration
- Canadian province selection
- Deadhead distance tracking (DH-P, DH-D)
- Trailer type specifications
- Weight/length parameters

### 📦 Load Board
- Real-time search and filtering
- Origin/destination filters
- Trailer type filtering
- Daily free views (4 unlocks/day)
- Rate per mile display
- Profit calculations

### 💰 Profit Analysis
- Line haul rate (CAD)
- Operating cost: $2.00 CAD/km
- Profit = Rate - (Distance × $2.00)
- Market rate comparisons

### 🎯 AI Recommendations
- Personalized load matching
- Based on search history
- Equipment preferences
- Backhaul opportunities

### 📞 Contact Management
- Broker information
- MC/DOT numbers
- Direct phone/email
- Unlock system (4 free/day)

## 🔧 Test Workflow

### 1. Build Route
```
1. Select "Alberta (AB)" as Pick Up
2. Choose US state as Drop Off
3. Select "Van" trailer type
4. Enter weight/length
5. Click "Search"
```

### 2. Browse Results
```
1. View load list in center panel
2. Check rates and distances
3. Identify profitable loads
4. Note broker names
```

### 3. View Details
```
1. Click any load card
2. See trip details in right panel
3. Review profit analysis
4. Check broker credentials
5. View backhaul opportunities
```

### 4. Unlock Contact
```
1. Click "Unlock" button
2. Uses 1 daily free view
3. Reveals phone and email
4. Shows MC/DOT numbers
```

### 5. Book Load
```
1. Click "Book Load" button
2. Get confirmation ID
3. Booking sent to broker
```

## 🌐 API Testing

### Search Loads
```powershell
curl "http://localhost:8000/api/v1/freight/canadian-loads?origin=Edmonton&destination=Nebraska"
```

### Get Market Rates
```powershell
curl "http://localhost:8000/api/v1/freight/canadian-market-rates?origin_province=AB&destination_province=NE&trailer_type=Van"
```

### Book Load
```powershell
curl -X POST "http://localhost:8000/api/v1/freight/canadian-loads/book" `
  -H "Content-Type: application/json" `
  -d '{\"load_id\": \"LD001\", \"truck_id\": \"TRK123\"}'
```

### Backhaul Search
```powershell
curl "http://localhost:8000/api/v1/freight/backhaul-opportunities?current_location=Grand%20Island%2C%20NE&home_base=Edmonton%2C%20AB&trailer_type=Van"
```

## 📍 Canadian Provinces Supported
All 13 Canadian provinces and territories:
- Alberta (AB)
- British Columbia (BC)
- Manitoba (MB)
- New Brunswick (NB)
- Newfoundland and Labrador (NL)
- Nova Scotia (NS)
- Ontario (ON)
- Prince Edward Island (PE)
- Quebec (QC)
- Saskatchewan (SK)
- Northwest Territories (NT)
- Nunavut (NU)
- Yukon (YT)

## 🚛 Trailer Types
- **Van (V)**: Dry van, enclosed
- **Flatbed (F)**: Open deck
- **Reefer (R)**: Refrigerated
- **Tanker (T)**: Liquid transport
- **Step Deck (SD)**: Lowboy
- **Double Drop (DD)**: Extra low
- **Dry Bulk (DB)**: Pneumatic

## 💵 Profit Calculation

### Formula
```
Operating Cost = Distance (mi) × $2.00 CAD/km × 1.609 km/mi
Profit = Line Haul Rate - Operating Cost
Rate per Mile = Line Haul Rate ÷ Distance
```

### Example
```
Load: Edmonton, AB → Grand Island, NE
Distance: 1619 miles
Rate: $2,425 CAD
Operating Cost: 1619 × 2.00 × 1.609 = $5,209 CAD
Profit: $2,425 - $5,209 = -$2,784 CAD
Status: ❌ Unprofitable (negotiate higher rate)
```

## 🔐 Daily Free Views System
- **4 free load unlocks per day**
- Unlocking reveals:
  - Full broker contact (phone, email)
  - MC number (Motor Carrier)
  - DOT number (Department of Transportation)
- Resets at midnight UTC
- Upgrade for unlimited views

## 🎨 UI Components

### Load Card
- Posted age indicator (e.g., "21h")
- Rate badge (green = posted, gray = call for rate)
- Origin/destination markers 📍
- Distance and weight specs
- Trailer type badge
- Broker name

### Search Bar
- Origin input field
- Destination input field
- Search button 🔍
- Results count badge

### Trip Details Panel
- Route visualization (pickup → dropoff)
- Load specifications table
- Rate & profit analysis
- Broker contact card
- Backhaul opportunities
- Action buttons (Book, Contact)

### Route Builder
- Add/remove route rows
- Province dropdowns
- Deadhead distance inputs
- Trailer type selector
- Weight/length inputs
- Search button per route

## 🔗 Load Board Integrations

### Supported Platforms
1. **TruckerPath** - North American freight
2. **DAT One** - US/Canada cross-border
3. **Loadlink** - Canadian-specific
4. **TruckMiles** - Canadian route optimization

### Setup (Future)
```env
TRUCKERPATH_API_KEY=your_key_here
DAT_API_KEY=your_key_here
LOADLINK_API_KEY=your_key_here
TRUCKMILES_API_KEY=your_key_here
```

## 🐛 Troubleshooting

### Backend Won't Start
```powershell
# Check port 8000
netstat -ano | findstr :8000

# Kill process if occupied
taskkill /PID <PID> /F

# Restart backend
python -m uvicorn backend.main:app --reload
```

### Frontend Won't Load
```powershell
# Check port 5173
netstat -ano | findstr :5173

# Reinstall dependencies
cd frontend
npm install
npm run dev
```

### API Returns 404
Check backend logs for:
```
[main] freight_broker_canada routes mounted at /api/v1/freight/*
```

If missing:
1. Verify `backend/routes/freight_broker_canada.py` exists
2. Check import in `backend/main.py`
3. Restart backend

### No Loads Showing
Demo mode uses mock data. Check:
- `mockLoads` array in `FreightBrokerControl.jsx`
- Console for JavaScript errors
- Network tab for failed API calls

## 📚 Related Documentation
- [Canadian Freight Integration](./CANADIAN_FREIGHT_BROKER_INTEGRATION.md) - Complete technical docs
- [API Reference](./API_REFERENCE_COMPLETE.md) - All API endpoints
- [AI Bots Panel Index](./AI_BOTS_PANEL_INDEX.md) - Bot system overview

## 🎯 Next Steps

1. **Test Interface** ✅
   - Navigate to `/freight-broker/loads`
   - Try all features
   - Verify calculations

2. **Integrate Live Data** 🔄
   - Obtain load board API keys
   - Configure integration service
   - Test real load fetching

3. **Customize** 🎨
   - Adjust profit formulas
   - Modify daily free views limit
   - Add company branding
   - Configure rate alerts

4. **Go Live** 🚀
   - Deploy to production
   - Train users
   - Monitor usage
   - Collect feedback

## 📞 Support
- **Technical**: support@gabanistore.com
- **Operations**: operations@gabanilogistics.com
- **Platform**: Check `backend/logs/` for errors

---

**Status**: ✅ Ready for Testing  
**Version**: 1.0.0  
**Mode**: Demo (Mock Data)  
**Last Updated**: February 12, 2026

**Note**: Currently running with sample data. Enable live integrations by adding API keys to environment variables.
