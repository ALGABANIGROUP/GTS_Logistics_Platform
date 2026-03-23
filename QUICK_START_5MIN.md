# ⚡ Quick Start Guide - Just 5 Minutes!

**The Fastest Way to Get Started Now!**

---

## 🎯 Steps (5 minutes)

### **Step 1: Read** (1 minute)
Open and read this file:

```
-> 00_READ_ME_FIRST.md
```

### **Step 2: Run the Backend Environment** (1 minute)
Open **Terminal 1** and run:

```powershell
cd c:\Users\enjoy\dev\GTS
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload
```

**Expected Result:**

```
INFO: Uvicorn running on http://127.0.0.1:8000

```

### **Step 3: Run the Frontend** (1 minute)
Open **Terminal 2** Run:

```powershell
cd c:\Users\enjoy\dev\GTS\frontend
npm run dev
```

**Expected Result:**

```
VITE v5.x.x ready in xxx ms

➜ Local: http://localhost:5173/
```

### **Step 4: Open Browser** (1 minute)
Go to:

```
http://localhost:5173
```

### **Step 5: Test** (1 minute)
Try the payment page:

```
http://localhost:5173/payments/123
```

---

## ✅ Check Status

### **Check Backend Environment:**
```bash
curl http://localhost:8000/health
```

### **Check Base Data:**
```bash
python verify_payment_tables.py

```
### **Run the Tests:**
```bash
# Backend tests:
pytest backend/tests/test_payment_models.py -v

# Frontend tests:
npm test

```

---

## 📁 Important Files

**Read in this order:**

1. ✅ `00_READ_ME_FIRST.md` ← **Start Here** (5 minutes)
2. ✅ `QUICK_START_NOW.md` (15 minutes)
3. ✅ `README_SUDAPAY.md` (30 minutes)
4. ✅ `NEXT_STEPS_ACTION_PLAN.md` (20 minutes)
5. ✅ `FILE_NAVIGATION_MAP.md` (30 minutes) (minute)

---

## 🔧 Troubleshooting Common Problems

### **Problem: Backend not running**
```bash
# Check the default environment:
.\.venv\Scripts\Activate.ps1

# Check the port:
netstat -ano | findstr:8000

# Reinstall:
pip install -r requirements.txt

### **Problem: Frontend not running**
```bash
cd frontend
npm install
npm run dev

```

### **Problem: Database error**
```bash
# Recreate tables:
python create_payment_tables.py

# Verify tables:
python verify_payment_tables.py

```

### **Problem: Port already in use**
```bash
# Change port:
python -m uvicorn backend.main:app --reload --port 8001

# Or kill process:
netstat -ano | findstr:8000
taskkill /PID <PID> /F

```

---

## 📊 Important Commands

| Command | Description | Port |

|------|------|-------|

| `python -m uvicorn backend.main:app --reload` | Run Backend | 8000 |

| `npm run dev` | Run Frontend | 5173 |

| `pytest backend/tests/ -v` | Run Backend Tests | - |

| `npm test` | Run Frontend Tests | - |

| `python verify_payment_tables.py` | Check DB Tables | - |

| `python create_payment_tables.py` | Create DB Tables | - |

---

## 🌐 Important Addresses

| Service | Address | Port |

|------|--------|-------|

| Frontend | http://localhost:5173 | 5173 |

| Backend | http://localhost:8000 | 8000 |

| API Docs | http://localhost:8000/api/docs | 8000 |

| Payment | http://localhost:5173/payments/123 | 5173 |

---

## 🚀 Your Next Goal

```
✅ Run Backend + Frontend (Now)
✅ Test Homepage (5 minutes)
✅ Read Core Files (1 hour)
⏳ Get a SUDAPAY Key (1-3 days)
⏳ Run Full Tests (3-5 days)
⏳ Launch Production (2 weeks)

```

---

## ❌ Don't Do This!

❌ Do not manually modify the database.

❌ Do not run commands without VirtualEnv.
❌ Do not use dev keys in production.
❌ Do not forget to test before launch.
❌ Do not deploy without a backup.

---

## 🎯 Final Result

```
After 5 minutes:

✅ System running locally

✅ Frontend accessible

✅ Backend responding

✅ Ready to test

After 1 hour:

✅ All basic tests passed

✅ Full documentation read

✅ Action plan clear

After 1 week:

✅ SUDAPAY integrated

✅ All tests passed

✅ Ready for staging

After 2 weeks:

✅ Production ready

✅ Monitoring active

✅ Go live! 🚀

```

---

## 📞 Quick Help

**For questions about:**
- Commands → `QUICK_START_NOW.md`
- Files → `FILE_NAVIGATION_MAP.md`
- Steps → `NEXT_STEPS_ACTION_PLAN.md`
- Security → `SUDAPAY_SECURITY_AUDIT_CHECKLIST.md`
- Launch → `SUDAPAY_PRODUCTION_DEPLOYMENT_GUIDE.md`

---

## ⏱️ Time now!

Open Terminal 1:
$: cd c:\Users\enjoy\dev\GTS
$: .\.venv\Scripts\Activate.ps1
$: python -m uvicorn backend.main:app --reload

Open Terminal 2:
$: cd c:\Users\enjoy\dev\GTS\frontend
$: npm run dev

Open Browser:
→ http://localhost:5173

---

**✅ Everything is ready!**

**🚀 Run now!**

**💯 Success guaranteed!**

---

*Quick guide - 5 minutes*

*Last updated: 2026-03-10*