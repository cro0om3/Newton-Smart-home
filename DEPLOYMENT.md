# دليل النشر - Newton Smart Home

## خيارات النشر المتاحة

هذا الدليل يغطي ثلاثة خيارات رئيسية للنشر:

1. **Docker (موصى به)** - للنشر المرن على أي خادم أو خدمة سحابية
2. **Azure Container Apps / App Service** - للنشر على Azure
3. **Streamlit Cloud** - للنشر السريع المجاني

---

## 1️⃣ النشر باستخدام Docker (الخيار الأول)

### المتطلبات

- Docker Desktop مثبّت
- حساب GitHub (للنشر التلقائي)

### البناء المحلي

```powershell
# بناء الصورة
docker build -t newton-smart-home:local .

# تشغيل الحاوية
docker run -p 8501:8501 -v ${PWD}/data:/app/data newton-smart-home:local
```

الوصول: `http://localhost:8501`

### النشر التلقائي عبر GitHub Actions

1. **تفعيل Workflow permissions:**
   - Settings → Actions → General
   - فعّل "Read and write permissions"

2. **رفع التعديلات:**

```powershell
git add .
git commit -m "Add Docker deployment"
git push origin main
```

3. **سحب الصورة من GitHub Container Registry:**

```powershell
docker pull ghcr.io/cro0om3/newton-smart-home:latest
docker run -p 8501:8501 -v ${PWD}/data:/app/data ghcr.io/cro0om3/newton-smart-home:latest
```

### النشر على Azure Container Apps

```powershell
az login
az group create --name newton-rg --location uaenorth
az containerapp env create --name newton-env --resource-group newton-rg --location uaenorth
az containerapp create `
  --name newton-app `
  --resource-group newton-rg `
  --environment newton-env `
  --image ghcr.io/cro0om3/newton-smart-home:latest `
  --target-port 8501 `
  --ingress external `
  --cpu 1.0 --memory 2.0Gi
```

---

## 2️⃣ Streamlit Cloud (نشر سريع مجاني)

### المتطلبات

- Python 3.10+
- حساب Streamlit Cloud
- ConvertAPI secret (للـ PDF conversion)

### الخطوات

1. ارفع الكود لـ GitHub
2. في Streamlit Cloud: New app → اختر المستودع
3. أضف Secrets (Deployment → Advanced → Secrets):

```toml
CONVERTAPI_SECRET = "your-secret-key"
```

### السلوك

- يستخدم WeasyPrint محلياً أو ConvertAPI كـ fallback على Streamlit Cloud

---

## 3️⃣ الاختبار المحلي

```powershell
# إنشاء بيئة افتراضية
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل التطبيق
streamlit run main.py
```

الوصول: `http://localhost:8501`

---

## 🔧 استكشاف الأخطاء

### Docker: الصورة لا تُبنى

```powershell
# بناء مع عرض التفاصيل
docker build --progress=plain -t newton-smart-home:local .
```

### التطبيق لا يعمل

```powershell
# عرض السجلات
docker logs <container-id>
```

### تحويل PDF لا يعمل

- تحقق من تثبيت Playwright browsers (موجود في Dockerfile)
- راجع سجلات التطبيق

---

## 📝 ملاحظات مهمة

1. **الأمان:** غيّر أرقام PIN الافتراضية فوراً
2. **الأداء:** الحد الأدنى: 1 CPU + 2GB RAM
3. **النسخ الاحتياطي:** احفظ مجلد `data/` دورياً

---

## 📞 الدعم

للمساعدة:

- افتح Issue في المستودع
- راجع `README.md` للتوثيق الكامل
