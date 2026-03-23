# ✅ تحديث Session Timeout إلى 15 دقيقة

**التاريخ:** 2026-03-07  
**الحالة:** ✅ تم التحديث بنجاح

---

## 📊 الملفات المحدثة

### **Backend (6 ملفات)**

#### 1. ✅ `backend/utils/auth_utils.py`
```python
# قبل: ACCESS_TOKEN_EXPIRE_MINUTES = 30
# بعد:  ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Session timeout: 15 minutes of inactivity
```

#### 2. ✅ `config/settings.py`
```python
# قبل: ACCESS_TOKEN_EXPIRE_MINUTES = 30
# بعد:  ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Session timeout: 15 minutes of inactivity
```

#### 3. ✅ `backend/security/auth.py`
```python
# قبل: ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
# بعد:  ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
```

#### 4. ✅ `backend/config.py`
```python
# قبل: os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
# بعد:  os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
```

#### 5. ✅ `backend/auth/unified_auth.py`
```python
# قبل: self.ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
# بعد:  self.ACCESS_TOKEN_EXPIRE_MINUTES = 15   # Session timeout: 15 minutes of inactivity
```

#### 6. ✅ `backend/services/auth.py`
```python
# قبل: ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
# بعد:  ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Session timeout: 15 minutes of inactivity
```

#### 7. ✅ `backend/config/security_config.py`
```python
# قبل: access_token_expire_minutes: int = 30
# بعد:  access_token_expire_minutes: int = 15  # Session timeout: 15 minutes of inactivity
```

### **Frontend (Already configured ✓)**

#### `frontend/src/App.jsx`
```jsx
<InactivityWatcher timeoutMinutes={15} warningMinutesBefore={1} />
```

✅ **الـ Frontend بالفعل يستخدم 15 دقيقة!**

---

## 🔐 كيفية عمل الـ Session Timeout الآن

### **On the Backend:**
```
1. المستخدم يسجل الدخول
2. تُصدر جلسة JWT بـ expiration = 15 دقيقة
3. بعد 15 دقيقة من عدم النشاط = توقف الجلسة تلقائياً
4. من يحاول الوصول = رفض مع طلب إعادة تسجيل دخول
```

### **On the Frontend:**
```
1. المكون InactivityWatcher يراقب النشاط
2. يتابع: mouseMove, keyDown, click, scroll, touch
3. بعد 14 دقيقة = تحذير (1 دقيقة قبل الانتهاء)
4. بعد 15 دقيقة = logout تلقائي مع redirect إلى /login
```

---

## 📋 الأنشطة المراقبة (Inactivity)

يتم اعتبار المستخدم **نشطاً** عند:
- ✅ تحريك الماوس (mousemove)
- ✅ الضغط على لوحة المفاتيح (keydown)
- ✅ النقر (click)
- ✅ التمرير (scroll)
- ✅ اللمس (touchstart, touchmove)

عند أي من هذه الأنشطة = يتم إعادة تعيين المؤقت

---

## 🔔 التنبيهات والتحذيرات

### **بعد 14 دقيقة:**
```
⚠️  "You will be logged out in about 60 seconds due to inactivity."
```

### **بعد 15 دقيقة:**
```
ℹ️  "You have been logged out due to inactivity."
↪️  Redirect إلى: /login
```

---

## ⚙️ متغيرات البيئة

إذا أردت تغيير الـ timeout من البيئة:

```bash
# .env file
ACCESS_TOKEN_EXPIRE_MINUTES=15   # Backend
JWT_ACCESS_TTL_MINUTES=15        # Alternative

# أو عند البدء:
export ACCESS_TOKEN_EXPIRE_MINUTES=15
python -m uvicorn backend.main:app
```

---

## ✔️ التحقق من الإعدادات

### **على Backend:**
```python
from backend.security.auth import ACCESS_TOKEN_EXPIRE_MINUTES
print(f"Timeout: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")  # Should print: 15
```

### **على Frontend:**
```javascript
// أفتح console
console.log("Check InactivityWatcher in App.jsx for timeoutMinutes={15}")
```

---

## 📊 ملخص التغييرات

```
┌──────────────────────────────────────────────────────┐
│          SESSION TIMEOUT UPDATE SUMMARY         │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Backend Files Updated: 7 ✅                        │
│  - auth_utils.py ...................... 30 → 15    │
│  - settings.py ........................ 30 → 15    │
│  - security/auth.py ................... 30 → 15    │
│  - config.py .......................... 60 → 15    │
│  - auth/unified_auth.py ........... 1440 → 15    │
│  - services/auth.py ................... 60 → 15    │
│  - config/security_config.py ......... 30 → 15    │
│                                                      │
│  Frontend Files: Already Set ✓                       │
│  - App.jsx ..................... 15 minutes ✓      │
│                                                      │
│  New Behavior:                                       │
│  ✓ Session expires after 15 minutes of inactivity │
│  ✓ Warning at 14 minutes                          │
│  ✓ Auto logout at 15 minutes                      │
│  ✓ User must login again                          │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 🚀 الخطوات التالية

### **1️⃣ أعد تشغيل Backend:**
```bash
cd c:\Users\enjoy\dev\GTS
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload
```

### **2️⃣ تحقق من الإعدادات:**
- سجل الدخول إلى الـ Dashboard
- انتظر دون نشاط
- بعد 14 دقيقة = ستري تحذير
- بعد 15 دقيقة = سيتم logoff تلقائياً

### **3️⃣ اختبر النشاط:**
- حرك الماوس أو اضغط على لوحة المفاتيح
- يجب أن تبقى الجلسة نشطة
- يتم إعادة تعيين المؤقت

---

## 📞 المزيد من المعلومات

### **إذا أردت زيادة الوقت:**
قم بتغيير جميع القيم من `15` إلى `X` دقيقة في الملفات أعلاه

### **إذا أردت تعطيل الميزة:**
- Backend: اضبط على قيمة عالية جداً (مثل 1440)
- Frontend: اضبط `timeoutMinutes={999999}`

### **للتحكم الدقيق:**
عدّل الملفات مباشرة أو استخدم متغيرات البيئة

---

**✅ تم التحديث بنجاح!**

الآن عند تسجيل الدخول، ستكون لديك **15 دقيقة من النشاط** قبل انتهاء الجلسة تلقائياً.

🎉 **نظام جديد نشط وآمن!**
