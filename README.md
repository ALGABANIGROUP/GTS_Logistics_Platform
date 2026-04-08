# GTS Logistics Platform 🚛

**منصة GTS للخدمات اللوجستية والشحن** - نظام SaaS متطور لإدارة الشحنات، الوساطة في النقل، وأتمتة العمليات اللوجستية.

## 🌟 المميزات الرئيسية

- 🤖 **بوتات ذكية متخصصة**: 5 بوتات ذكية لإدارة مختلف جوانب الأعمال
- 📊 **لوحة تحكم متقدمة**: واجهة حديثة لمراقبة العمليات في الوقت الفعلي
- 🔍 **نظام بحث وSEO**: محرك بحث متقدم مع دعم الذكاء الاصطناعي
- 📱 **واجهة برمجة تطبيقات شاملة**: API متكامل للتكامل مع الأنظمة الخارجية
- 🔒 **أمان متقدم**: نظام مصادقة JWT مع تشفير البيانات
- 📈 **تحليلات الأداء**: مراقبة شاملة للأداء والأمان

## 🚀 البدء السريع

### الطريقة الأسهل - التشغيل المباشر

```bash
# تشغيل السكريبت التلقائي
./quick_start.sh
```

أو يدوياً:

```bash
# تفعيل البيئة الافتراضية
source backend/.venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements-simple.txt

# تشغيل الخادم
uvicorn backend.main_simple:app --host 0.0.0.0 --port 8000 --reload
```

### الطريقة المتقدمة - Docker

```bash
# تشغيل البيئة التطويرية
docker-compose -f docker-compose.dev.yml up --build
```

## 📋 المتطلبات

- Python 3.8+
- pip (مدير الحزم)
- Git
- (اختياري) Docker و Docker Compose

## 📁 هيكل المشروع

```
GTS-new/
├── backend/                 # الخادم الخلفي (FastAPI)
│   ├── main.py             # الخادم الرئيسي
│   ├── main_simple.py      # الخادم المبسط للتطوير
│   └── .venv/              # البيئة الافتراضية
├── frontend/                # الواجهة الأمامية (React + Vite)
├── search-seo-system/       # نظام البحث وSEO
├── docs/                    # الوثائق والتقارير
├── uploads/                 # ملفات المرفوعة
├── .env                     # متغيرات البيئة
└── requirements-simple.txt  # المتطلبات الأساسية
```

## 🔧 الإعداد والتكوين

### 1. تحضير البيئة

```bash
# استنساخ المشروع
git clone <repository-url>
cd GTS-new

# تشغيل السكريبت التلقائي
./quick_start.sh
```

### 2. متغيرات البيئة

قم بتحديث ملف `.env` بالقيم المناسبة:

```env
# قاعدة البيانات
DATABASE_URL=sqlite:///./gts_development.db

# مفاتيح API
OPENAI_API_KEY=your_openai_key_here
SENTRY_DSN=your_sentry_dsn_here

# إعدادات JWT
JWT_SECRET_KEY=your_jwt_secret_here
JWT_ALGORITHM=HS256

# إعدادات التطبيق
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. تشغيل الخادم

```bash
# التشغيل المباشر
uvicorn backend.main_simple:app --host 0.0.0.0 --port 8000 --reload

# أو باستخدام Docker
docker-compose -f docker-compose.dev.yml up --build
```

## 🌐 الوصول للتطبيق

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Frontend**: http://localhost:5173 (إذا كان يعمل)

## 🤖 البوتات الذكية

1. **مدير المبيعات العام** - إدارة العملاء والمبيعات
2. **وسيط الشحن** - إدارة الشحنات والنقل
3. **مدير المالية** - إدارة الفواتير والمدفوعات
4. **مدير الوثائق** - معالجة الوثائق والعقود
5. **بوت خدمة العملاء** - دعم العملاء والاستفسارات

## 📊 مراقبة الأداء

```bash
# تشغيل تحليل الأداء
python analyze_performance.py

# تحليل الذاكرة
python analyze_memsnap.py

# اختبار الأمان
python security_audit.py
```

## 🐛 استكشاف الأخطاء

إذا واجهت مشاكل:

1. تحقق من ملف `TROUBLESHOOTING_GUIDE.md`
2. شغل اختبار البيئة: `./test_environment.bat`
3. راجع السجلات في `backend/logs/`

## 📚 الوثائق

- [دليل المستخدم النهائي](USER_GUIDE.md)
- [دليل الدعم الفني](SUPPORT_TRAINING_GUIDE.md)
- [دليل التحسينات](PERFORMANCE_SECURITY_IMPROVEMENTS.md)
- [دليل التطوير](DEVELOPMENT_SETUP.md)
- [دليل استكشاف الأخطاء](TROUBLESHOOTING_GUIDE.md)

## 🤝 المساهمة

نرحب بالمساهمات! يرجى قراءة [دليل المساهمة](CONTRIBUTING.md) للمزيد من التفاصيل.

## 📞 الدعم

- **الدعم الفني**: support@gabanistore.com
- **العمليات**: operations@gabanilogistics.com
- **المنصة**: تحقق من السجلات في `backend/logs/`

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

---

**تم تطوير منصة GTS بنجاح! 🎉**

---

## Current Project Snapshot

- Documentation refresh date: **2026-03-21**
- Documentation version: **2026.03.21-docs**
- Frontend bot registry: **21 bots**, **21 active**
- New payment surfaces: **Payment Gateway Dashboard**, **SUDAPAY Payment Gateway**, **AI Finance Bot**
- Partner Manager status: **Active** and routed through `/ai-bots/partner-management`
- Operations additions: **Carriers** and **Shippers** workspaces with integrated frontend services
- Verified frontend build: **`npm run build` passed**
- Verified backend doc-related syntax checks: **`python -m py_compile backend/ai/bot_subscription_manager.py` passed**

## Key Active Routes

- `/ai-bots/hub`
- `/ai-bots/payment`
- `/ai-bots/sudapay`
- `/ai-bots/finance`
- `/ai-bots/partner-management`
- `/ai-bots/carriers/*`
- `/ai-bots/shippers/*`
- `/payments/:invoiceId`
- `/payments/history`

## Latest Confirmed Changes Included In This Refresh

- Added the shared frontend bot registry and cleaned the hub display.
- Added and activated **Payment Gateway Dashboard** as a distinct bot entry.
- Kept **SUDAPAY** as its own payment-focused bot view.
- Activated **AI Partner Manager** across registries, dashboards, and routing.
- Added payment and finance summary helpers used by the dashboard.
- Added/update carrier and shipper frontend workspaces and service integrations.
- Updated bot alias handling so payment and partner routes resolve consistently.

## Platform Highlights

- Unified AI bot hub and routed bot control pages
- Active payment stack with `Payment Gateway Dashboard`, `SUDAPAY`, and `AI Finance Bot`
- Active `AI Partner Manager`
- Carriers and Shippers workspaces with connected frontend services
- Finance and payment summaries derived from real invoice and payment feeds

## Where To Start

- `00_READ_ME_FIRST.md`
- `AI_BOTS_PANEL_INDEX.md`
- `PAYMENT_GATEWAY_INDEX.md`
- `API_CONNECTIONS_DOCUMENTATION_INDEX.md`

## Standard Local Commands

```bash
# frontend
cd frontend
npm install
npm run dev
npm run build

# backend
python -m uvicorn backend.main:app --reload
```

## Maintainer Note

This README was refreshed to match the current codebase state on **2026-03-21**.
