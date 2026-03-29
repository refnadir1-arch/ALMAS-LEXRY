# ALMAS LUXRY

متجر أزياء نسائية فاخر بالعربية RTL مع طلب مباشر بدون سلة ولوحة تحكم احترافية.

## الميزات
- طلب مباشر لمنتج واحد فقط
- الاسم الكامل + الهاتف + الولاية + البلدية
- Size + Color + Quantity
- الدفع عند الاستلام فقط
- التوصيل:
  - إلى باب المنزل: 800 دج
  - إلى مكتب التوصيل: 500 دج
- تتبع الطلب بالهاتف + رمز الطلب
- لوحة تحكم مخصصة
- Reviews وآراء زبونات
- CTA عائم ثابت

## الصور
ضع الصور التالية داخل:
- `static/images/logo.png`
- `static/images/hero-woman.png`

## التشغيل
```bash
python -m venv .venv
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# أو cp .env.example .env

python manage.py migrate
python manage.py seed_demo
python manage.py runserver