# 🔧 Frontend-Backend Connection Troubleshooting Guide

## Current Issue
When attempting to use the application, error messages appear such as:
- `❌ NETWORK ERROR DETECTED`
- `🌐 Backend Not Responding`
- `Connection refused` or `ERR_NETWORK`

## Possible Causes

### 1️⃣ Backend Server is Not Running
**Solution:**
```bash
# From the main project directory
uvicorn backend.main:app --reload

# Or use the command in VS Code
Ctrl + Shift + B then select "Start Backend (FastAPI)"
```

**Verification:**
```
http://127.0.0.1:8000/api/v1/system/health
```

You should receive a JSON message like:
```json
{"status":"ok","environment":"development","database":{"status":"connected"}}
```

### 2️⃣ Frontend is Not Running
**Solution:**
```bash
# From the frontend directory
npm run dev

# Or use the command in VS Code
Ctrl + Shift + B then select "Start Frontend (Vite)"
```

**Verification:**
```
http://127.0.0.1:5173
```

You should see the GTS application interface

### 3️⃣ Environment Settings are Incorrect

Check the `frontend/.env` file:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

**Must be:**
- ✅ `http://127.0.0.1:8000` (for local development)
- ❌ Empty or `undefined`
- ❌ `localhost:8000` (without http://)

### 4️⃣ CORS Settings are Incorrect

Check the `backend/main.py` file (around line 685):
```python
DEFAULT_CORS_ORIGINS = [
    "http://127.0.0.1:5173",    # ✅ Must exist
    "http://localhost:5173",    # ✅ Must exist
    ...
]
```

## Detailed Troubleshooting Steps

### Step 1: Check Backend Server
```bash
# In Terminal
curl http://127.0.0.1:8000/api/v1/system/health

# You should receive:
# {"status":"ok","environment":"development","database":{"status":"connected"}}
```

### Step 2: Check CORS
```bash
curl -X OPTIONS http://127.0.0.1:8000/api/v1/system/health \
  -H "Origin: http://127.0.0.1:5173" \
  -H "Access-Control-Request-Method: GET" \
  -v
```

You should see in the response:
```
Access-Control-Allow-Origin: http://127.0.0.1:5173
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

### Step 3: Use the Test Tool
Open your browser and navigate to:
```
http://127.0.0.1:5173/test-connection.html
```

This page tests:
- ✅ Health Check
- ✅ CORS Preflight
- ✅ All main endpoints
- ✅ AI Chat connection

### Step 4: Check Browser Console
1. Open DevTools: `F12`
2. Go to Console
3. Look for these messages:
   - 🔧 `Axios Client Configuration` - If shown, axiosClient is working
   - ✅ `Backend connected successfully` - Connection is successful
   - ❌ `NETWORK ERROR DETECTED` - Connection issue

### Step 5: Check Backend Server Logs
Look at the Terminal window where the backend is running:
```
[INFO] Uvicorn running on http://127.0.0.1:8000
```

Look for errors such as:
```
ERROR: Could not import module
ERROR: Database connection failed
ERROR: CORS error
```

## Common Issues and Solutions

### Issue: ERR_NETWORK After Starting Servers
**Solution:**
1. Open DevTools: `F12`
2. Copy the Health Check link
3. Paste it in the browser address bar: `http://127.0.0.1:8000/api/v1/system/health`
4. If it works here but not in the app, the problem is in JavaScript

### Issue: 404 Not Found
**Means:** Endpoint does not exist
**Solution:**
1. Check the URL spelling
2. Ensure the backend has this endpoint (files in `backend/routes/`)

### Issue: 502 Bad Gateway
**Means:** Backend is stopped or crashed
**Solution:**
1. Restart the backend server
2. Check Uvicorn logs
3. Look for Tracebacks (error messages) in Terminal

### Issue: CORS error in Console
```
Access to XMLHttpRequest at 'http://127.0.0.1:8000/' from origin 'http://127.0.0.1:5173' 
has been blocked by CORS policy
```

**Solution:**
1. Check `DEFAULT_CORS_ORIGINS` in `backend/main.py`
2. Ensure `http://127.0.0.1:5173` is in the list
3. Restart the backend server

## Endpoint Testing

### Test Health Status
```bash
curl http://127.0.0.1:8000/api/v1/system/health
```

### Test Health Check Action
```bash
curl -X POST http://127.0.0.1:8000/api/v1/system/actions/health-check \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Test AI Chat
```bash
curl -X POST http://127.0.0.1:8000/api/v1/ai/maintenance/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","context":{}}'
```

### Test Performance Profile
```bash
curl -X POST http://127.0.0.1:8000/api/v1/system/actions/performance-profile \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Final Checklist

- [ ] Backend is running (test `http://127.0.0.1:8000/api/v1/system/health`)
- [ ] Frontend is running (open `http://127.0.0.1:5173`)
- [ ] `VITE_API_BASE_URL=http://127.0.0.1:8000` in `frontend/.env`
- [ ] `http://127.0.0.1:5173` exists in `DEFAULT_CORS_ORIGINS` in `backend/main.py`
- [ ] `Ctrl+Shift+R` to clear cache and refresh
- [ ] Open DevTools (`F12`) and check Console
- [ ] No errors in DevTools
- [ ] Test using `http://127.0.0.1:5173/test-connection.html`

## Quick Commands Reference

```bash
# Start Backend
cd c:\Users\enjoy\Music\GTS\ Logistics\ origin
uvicorn backend.main:app --reload

# Start Frontend (in new terminal)
cd c:\Users\enjoy\Music\GTS\ Logistics\ origin\frontend
npm run dev

# Test Backend Health
curl http://127.0.0.1:8000/api/v1/system/health

# Clear Frontend Cache and Refresh
# In browser: Ctrl + Shift + R

# Open Connection Test Page
# In browser: http://127.0.0.1:5173/test-connection.html
```

## Contact Support
If the problem persists:
1. Take a screenshot of DevTools Console errors
2. Take a screenshot of backend Terminal logs
3. Send both screenshots along with a description of the issue

---

**Note:** All these instructions are for local development. For production environments, settings may differ based on the deployment environment.
