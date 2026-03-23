# 🔧 EN Frontend EN Backend

## EN:
- `❌ NETWORK ERROR DETECTED`
- `🌐 Backend Not Responding`
- `Connection refused` EN `ERR_NETWORK`

## EN

### 1️⃣ EN (Backend) EN
**EN:**
```bash
# EN
uvicorn backend.main:app --reload

# EN VS Code
Ctrl + Shift + B EN "Start Backend (FastAPI)"
```

**EN:**
```
http://127.0.0.1:8000/api/v1/system/health
```

EN JSON EN:
```json
{"status":"ok","environment":"development","database":{"status":"connected"}}
```

### 2️⃣ EN (Frontend) EN
**EN:**
```bash
# EN frontend
npm run dev

# EN VS Code
Ctrl + Shift + B EN "Start Frontend (Vite)"
```

**EN:**
```
http://127.0.0.1:5173
```

EN GTS

### 3️⃣ EN `frontend/.env`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

**EN:**
- ✅ `http://127.0.0.1:8000` (EN)
- ❌ EN `undefined`
- ❌ `localhost:8000` (EN http://)

### 4️⃣ EN CORS EN `backend/main.py` (EN 685):
```python
DEFAULT_CORS_ORIGINS = [
    "http://127.0.0.1:5173",    # ✅ EN
    "http://localhost:5173",    # ✅ EN
    ...
]
```

## EN

### EN 1: EN
```bash
# EN Terminal
curl http://127.0.0.1:8000/api/v1/system/health

# EN:
# {"status":"ok","environment":"development","database":{"status":"connected"}}
```

### EN 2: EN CORS
```bash
curl -X OPTIONS http://127.0.0.1:8000/api/v1/system/health \
  -H "Origin: http://127.0.0.1:5173" \
  -H "Access-Control-Request-Method: GET" \
  -v
```

EN:
```
Access-Control-Allow-Origin: http://127.0.0.1:5173
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

### EN 3: EN:
```
http://127.0.0.1:5173/test-connection.html
```

EN:
- ✅ Health Check
- ✅ CORS Preflight
- ✅ EN
- ✅ EN AI Chat

### EN 4: EN
1. EN DevTools: `F12`
2. EN Console
3. EN:
   - 🔧 `Axios Client Configuration` - EN axiosClient EN
   - ✅ `Backend connected successfully` - EN
   - ❌ `NETWORK ERROR DETECTED` - EN

### EN 5: EN Terminal EN:
```
[INFO] Uvicorn running on http://127.0.0.1:8000
```

EN:
```
ERROR: Could not import module
ERROR: Database connection failed
ERROR: CORS error
```

## EN

### EN: ERR_NETWORK EN
**EN:**
1. EN DevTools: `F12`
2. EN Health Check
3. EN: `http://127.0.0.1:8000/api/v1/system/health`
4. EN JavaScript

### EN: 404 Not Found
**EN:** EN
**EN:**
1. EN URL
2. EN `backend/routes/`)

### EN: 502 Bad Gateway
**EN:** EN
**EN:**
1. EN
2. EN Uvicorn
3. EN Tracebacks (EN Terminal

### EN: CORS error EN Console
```
Access to XMLHttpRequest at 'http://127.0.0.1:8000/' from origin 'http://127.0.0.1:5173' 
has been blocked by CORS policy
```

**EN:**
1. EN `DEFAULT_CORS_ORIGINS` EN `backend/main.py`
2. EN `http://127.0.0.1:5173` EN
3. EN

## EN

- [ ] EN `http://127.0.0.1:8000/api/v1/system/health`)
- [ ] EN `http://127.0.0.1:5173`)
- [ ] `VITE_API_BASE_URL=http://127.0.0.1:8000` EN `frontend/.env`
- [ ] `http://127.0.0.1:5173` EN `DEFAULT_CORS_ORIGINS` EN `backend/main.py`
- [ ] `Ctrl+Shift+R` EN
- [ ] EN DevTools (`F12`) EN Console
- [ ] EN DevTools
- [ ] EN `http://127.0.0.1:5173/test-connection.html`

## EN:
1. EN DevTools (Console)
2. EN Terminal EN
3. EN

---

**EN:** EN. EN (Production)EN.
