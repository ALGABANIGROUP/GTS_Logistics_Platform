# GTS Logistics Platform - دليل المستخدم النهائي

## 🚛 GTS Logistics Platform - User Guide

**الإصدار:** 2.0.0
**التاريخ:** 31 مارس 2026
**الحالة:** جاهز للإنتاج

---

## 📋 جدول المحتويات

1. [مقدمة](#مقدمة)
2. [البدء السريع](#البدء-السريع)
3. [إعداد النظام](#إعداد-النظام)
4. [استخدام API](#استخدام-api)
5. [المراقبة والصيانة](#المراقبة-والصيانة)
6. [استكشاف الأخطاء](#استكشاف-الأخطاء)
7. [الأمان والامتثال](#الأمان-وامتثال)
8. [النسخ الاحتياطي والاستعادة](#النسخ-الاحتياطي-والاستعادة)
9. [التوسع والأداء](#التوسع-والأداء)
10. [الدعم الفني](#الدعم-الفني)

---

## مقدمة

### ما هي GTS Logistics Platform؟

GTS Logistics Platform هي منصة لوجستية متكاملة مصممة لإدارة عمليات النقل والشحن. توفر المنصة حلولاً شاملة للشاحنين، الناقلين، والوسطاء في مجال اللوجستيات.

### الميزات الرئيسية

- **🔐 أمان متقدم**: مصادقة JWT مع تحكم في الوصول
- **📊 مراقبة شاملة**: تتبع الأداء والأخطاء في الوقت الفعلي
- **🤖 ذكاء اصطناعي**: روبوتات ذكية للمساعدة في اتخاذ القرارات
- **📱 واجهات متعددة**: API، لوحة تحكم ويب، وتطبيقات جوال
- **⚡ أداء عالي**: تخزين مؤقت Redis وتحسينات قاعدة البيانات
- **🐳 نشر سهل**: حاويات Docker للنشر السريع

---

## البدء السريع

### متطلبات النظام

```bash
# المتطلبات الأساسية
Python >= 3.9
Docker >= 20.10
Docker Compose >= 1.29
PostgreSQL >= 15
Redis >= 7
```

### التثبيت السريع

```bash
# 1. تحميل المشروع
git clone https://github.com/your-org/gts-logistics.git
cd gts-logistics

# 2. إعداد متغيرات البيئة
cp .env.example .env
# قم بتحرير .env مع إعداداتك

# 3. تشغيل النظام
docker-compose up -d

# 4. التحقق من التشغيل
curl http://localhost:8000/api/v1/monitoring/health
```

### التحقق من الجاهزية

```bash
# فحص حالة النظام
curl http://localhost:8000/api/v1/monitoring/health

# فحص واجهة API
open http://localhost:8000/docs

# فحص قاعدة البيانات
docker-compose exec postgres pg_isready -U gts_user -d gts_logistics
```

---

## إعداد النظام

### إعداد متغيرات البيئة

```bash
# ملف .env الرئيسي
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://gts_user:password@postgres:5432/gts_logistics
REDIS_URL=redis://redis:6379
JWT_SECRET_KEY=your-super-secret-jwt-key
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
GTS_CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### إعداد قاعدة البيانات

```bash
# تشغيل قاعدة البيانات
docker-compose up -d postgres

# تشغيل الترحيلات
docker-compose exec backend alembic upgrade head

# إضافة البيانات الأولية
docker-compose exec backend python scripts/seed_data.py
```

### إعداد SSL/TLS

```bash
# تثبيت شهادة Let's Encrypt
certbot certonly --standalone -d api.yourdomain.com

# تحديث إعدادات Nginx
cp nginx/ssl/nginx.prod.conf nginx/nginx.conf
docker-compose restart nginx
```

---

## استخدام API

### المصادقة

```bash
# الحصول على رمز الوصول
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"

# استخدام الرمز في الطلبات
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/users/me
```

### نقاط النهاية الرئيسية

#### إدارة المستخدمين
```bash
# إنشاء مستخدم جديد
POST /api/v1/users/
{
  "username": "newuser",
  "email": "user@example.com",
  "role": "user"
}

# الحصول على قائمة المستخدمين
GET /api/v1/users/?skip=0&limit=10

# تحديث مستخدم
PUT /api/v1/users/{user_id}
{
  "email": "newemail@example.com"
}
```

#### إدارة الشحنات
```bash
# إنشاء شحنة جديدة
POST /api/v1/freight/loads/
{
  "origin": "New York",
  "destination": "Los Angeles",
  "weight": 1000,
  "commodity": "Electronics"
}

# البحث عن الشحنات
GET /api/v1/freight/loads/search?origin=New+York&destination=Los+Angeles
```

#### الذكاء الاصطناعي
```bash
# استشارة مدير عام AI
POST /api/v1/ai/general-manager/consult
{
  "query": "How to optimize fleet utilization?",
  "context": "Current fleet has 50 trucks"
}
```

### حدود المعدل (Rate Limits)

| نوع النهاية | الحد | النافذة الزمنية |
|-------------|------|------------------|
| المصادقة | 10 طلب/دقيقة | لكل IP |
| API العام | 100 طلب/دقيقة | لكل مستخدم |
| رفع الملفات | 50 طلب/ساعة | لكل مستخدم |
| العمليات الإدارية | 30 طلب/دقيقة | لكل مستخدم |

---

## المراقبة والصيانة

### لوحة المراقبة

```bash
# حالة النظام العامة
GET /api/v1/monitoring/health

# مقاييس الأداء التفصيلية
GET /api/v1/monitoring/metrics

# التنبيهات النشطة
GET /api/v1/monitoring/alerts

# إحصائيات قاعدة البيانات
GET /api/v1/monitoring/database/stats
```

### مراقبة السجلات

```bash
# عرض سجلات النظام
docker-compose logs -f backend

# سجلات قاعدة البيانات
docker-compose logs -f postgres

# سجلات Redis
docker-compose logs -f redis

# سجلات Nginx
docker-compose logs -f nginx
```

### الصيانة الدورية

```bash
# تنظيف Redis
docker-compose exec redis redis-cli FLUSHDB

# إعادة بناء فهارس قاعدة البيانات
docker-compose exec postgres psql -U gts_user -d gts_logistics -c "REINDEX DATABASE gts_logistics;"

# تحديث الاعتماديات
docker-compose exec backend pip install --upgrade -r requirements.txt
```

---

## استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### خطأ في الاتصال بقاعدة البيانات
```bash
# التحقق من حالة قاعدة البيانات
docker-compose ps postgres

# إعادة تشغيل قاعدة البيانات
docker-compose restart postgres

# فحص سجلات قاعدة البيانات
docker-compose logs postgres
```

#### خطأ في المصادقة
```bash
# التحقق من صحة رمز JWT
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/users/me

# تجديد الرمز
POST /auth/refresh
{
  "refresh_token": "your_refresh_token"
}
```

#### مشاكل الأداء
```bash
# فحص استخدام الذاكرة
docker-compose exec backend ps aux | grep gunicorn

# فحص اتصالات قاعدة البيانات
docker-compose exec postgres psql -U gts_user -d gts_logistics -c "SELECT count(*) FROM pg_stat_activity;"

# فحص Redis
docker-compose exec redis redis-cli INFO
```

#### أخطاء HTTP شائعة

| رمز الخطأ | الوصف | الحل |
|-----------|--------|------|
| 400 | طلب غير صحيح | تحقق من بنية البيانات |
| 401 | غير مصرح | تحقق من رمز المصادقة |
| 403 | محظور | تحقق من صلاحيات المستخدم |
| 404 | غير موجود | تحقق من عنوان URL |
| 429 | حد المعدل تجاوز | انتظر قبل إعادة المحاولة |
| 500 | خطأ داخلي | راجع سجلات النظام |

---

## الأمان والامتثال

### إجراءات الأمان

#### تشفير البيانات
- جميع كلمات المرور مشفرة باستخدام bcrypt
- البيانات الحساسة مشفرة في قاعدة البيانات
- اتصالات SSL/TLS مطلوبة

#### التحكم في الوصول
- مصادقة متعددة العوامل (MFA)
- مبدأ الصلاحيات الأقل (Least Privilege)
- انتهاء صلاحية الرموز تلقائياً

#### حماية من الهجمات
- حماية CSRF
- حماية XSS
- حماية SQL Injection
- حدود معدل الطلبات

### الامتثال

#### معايير الأمان
- OWASP Top 10 Compliance
- GDPR Compliance
- SOC 2 Type II Ready

#### التدقيق والسجلات
```bash
# عرض سجلات التدقيق
GET /api/v1/admin/audit/logs?user_id=123&action=create

# تصدير تقارير التدقيق
GET /api/v1/admin/audit/export?start_date=2024-01-01&end_date=2024-01-31
```

---

## النسخ الاحتياطي والاستعادة

### النسخ الاحتياطي التلقائي

```bash
# إنشاء نسخة احتياطية يدوية
docker-compose exec postgres pg_dump -U gts_user -d gts_logistics > backup_$(date +%Y%m%d_%H%M%S).sql

# ضغط النسخة الاحتياطية
gzip backup_$(date +%Y%m%d_%H%M%S).sql

# رفع إلى التخزين السحابي
aws s3 cp backup_$(date +%Y%m%d_%H%M%S).sql.gz s3://gts-backups/
```

### استعادة من النسخة الاحتياطية

```bash
# تنزيل النسخة الاحتياطية
aws s3 cp s3://gts-backups/backup_20240331.sql.gz .

# فك الضغط
gunzip backup_20240331.sql.gz

# استعادة قاعدة البيانات
docker-compose exec -T postgres psql -U gts_user -d gts_logistics < backup_20240331.sql
```

### جدولة النسخ الاحتياطي

```bash
# إضافة مهمة cron للنسخ الاحتياطي اليومي
crontab -e

# إضافة السطر التالي
0 2 * * * /path/to/gts-logistics/scripts/backup.sh
```

---

## التوسع والأداء

### تحسين الأداء

#### تحسين قاعدة البيانات
```sql
-- إنشاء فهارس للاستعلامات الشائعة
CREATE INDEX idx_loads_origin_dest ON loads(origin, destination);
CREATE INDEX idx_loads_created_at ON loads(created_at DESC);

-- تحسين استعلامات الشحنات
EXPLAIN ANALYZE SELECT * FROM loads WHERE origin = 'New York' AND status = 'active';
```

#### تحسين Redis
```bash
# ضبط TTL للمفاتيح
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru

# مراقبة استخدام Redis
docker-compose exec redis redis-cli INFO memory
```

#### تحسين التطبيق
```python
# استخدام التخزين المؤقت
from backend.utils.cache_manager import cache_manager

@cache_manager.cached(ttl=300)
async def get_expensive_data():
    # بيانات تتطلب حسابات مكلفة
    pass
```

### التوسع الأفقي

```bash
# تشغيل عدة نسخ من التطبيق
docker-compose up -d --scale backend=3

# إعداد موازن التحميل
docker-compose up -d nginx

# مراقبة التوسع
docker-compose ps
```

---

## الدعم الفني

### قنوات الدعم

- **البريد الإلكتروني**: support@gabanistore.com
- **الهاتف**: +1 (555) 123-4567
- **الدردشة المباشرة**: https://chat.gts-logistics.com
- **منتدى المجتمع**: https://community.gts-logistics.com

### مستويات الدعم

#### دعم أساسي (مجاني)
- وثائق المستخدم
- أسئلة عامة
- مشاكل شائعة

#### دعم متقدم (مدفوع)
- استكشاف أخطاء معقدة
- تحسينات الأداء
- تطوير مخصص
- دعم 24/7

### إجراءات الإبلاغ عن المشاكل

```bash
# جمع معلومات النظام
curl http://localhost:8000/api/v1/monitoring/system-info

# تصدير سجلات الأخطاء
docker-compose logs backend --tail=100 > error_logs.txt

# إنشاء تقرير التشخيص
python scripts/diagnostic_report.py
```

---

## 📞 معلومات الاتصال

**GTS Logistics Support Team**
- Email: support@gabanistore.com
- Phone: +1 (555) 123-4567
- Website: https://gts-logistics.com
- Documentation: https://docs.gts-logistics.com

**Operations Team**
- Email: operations@gabanilogistics.com
- Emergency: +1 (555) 911-0000

---

**© 2026 GTS Logistics Platform. جميع الحقوق محفوظة.**
