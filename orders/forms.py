import json

from django import forms
from django.core.validators import RegexValidator

from orders.constants import DELIVERY_TYPES
from store.models import Variant
from store.wilayas import ALGERIA_WILAYAS


phone_validator = RegexValidator(
    regex=r"^[0-9+\s]{8,20}$",
    message="رقم الهاتف غير صالح."
)


class DirectOrderForm(forms.Form):
    # الجديد: قائمة عناصر (عدة ألوان/مقاسات لنفس المنتج) بصيغة JSON
    items_json = forms.CharField(required=False, widget=forms.HiddenInput())

    # توافق قديم (منتج واحد)
    variant_id = forms.IntegerField(required=False, min_value=1, widget=forms.HiddenInput())
    qty = forms.IntegerField(min_value=1, max_value=5, required=False)

    full_name = forms.CharField(max_length=140, label="الاسم الكامل")
    phone = forms.CharField(max_length=30, label="رقم الهاتف", validators=[phone_validator])

    wilaya_code = forms.ChoiceField(label="الولاية", choices=ALGERIA_WILAYAS)
    commune_name_ar = forms.CharField(max_length=120, label="البلدية")

    delivery_type = forms.ChoiceField(label="نوع التوصيل", choices=DELIVERY_TYPES)
    customer_note = forms.CharField(
        label="ملاحظة",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ستايل موحد
        def add_class(field_name, extra=None):
            if field_name not in self.fields:
                return
            w = self.fields[field_name].widget
            w.attrs = w.attrs or {}
            w.attrs["class"] = (w.attrs.get("class", "") + " lux-input").strip()
            if extra:
                w.attrs.update(extra)

        add_class("full_name", {"placeholder": "أدخل/ي الاسم الكامل"})
        add_class("phone", {"placeholder": "مثال: 0550123456"})
        add_class("wilaya_code")
        add_class("commune_name_ar", {"placeholder": "أدخل/ي البلدية"})
        add_class("delivery_type")

        self.fields["customer_note"].widget.attrs.update({
            "class": "lux-input",
            "placeholder": "ملاحظة اختيارية..."
        })

    def clean_phone(self):
        """
        نحذف المسافات لتفادي اختلافات غير مقصودة في التخزين/التتبع.
        """
        phone = self.cleaned_data.get("phone", "")
        return "".join(str(phone).split())

    def clean(self):
        cleaned = super().clean()
        items_json = (cleaned.get("items_json") or "").strip()

        # إذا items_json موجودة => نستعملها
        if items_json:
            try:
                items = json.loads(items_json)
            except json.JSONDecodeError:
                raise forms.ValidationError("حدث خطأ في عناصر الطلب.")

            if not isinstance(items, list) or not items:
                raise forms.ValidationError("اختاري على الأقل لون/مقاس واحد.")

            for it in items:
                if not isinstance(it, dict):
                    raise forms.ValidationError("عناصر الطلب غير صالحة.")

                if "variant_id" not in it or "qty" not in it:
                    raise forms.ValidationError("عناصر الطلب غير مكتملة.")

                try:
                    vid = int(it.get("variant_id"))
                except (TypeError, ValueError):
                    raise forms.ValidationError("خيار غير صالح.")

                try:
                    q = int(it.get("qty"))
                except (TypeError, ValueError):
                    raise forms.ValidationError("كمية غير صالحة.")

                if vid <= 0:
                    raise forms.ValidationError("خيار غير صالح.")
                if q < 1 or q > 5:
                    raise forms.ValidationError("الكمية لكل خيار يجب أن تكون بين 1 و 5.")

            return cleaned

        # وإلا نرجع للنظام القديم (variant_id + qty)
        variant_id = cleaned.get("variant_id")
        qty = cleaned.get("qty")

        if not variant_id:
            raise forms.ValidationError("اختاري اللون/المقاس.")
        if not qty:
            raise forms.ValidationError("اختاري الكمية.")

        if not Variant.objects.filter(id=variant_id).exists():
            raise forms.ValidationError("الخيار غير صالح.")

        return cleaned


class TrackOrderForm(forms.Form):
    phone = forms.CharField(max_length=30, label="رقم الهاتف", validators=[phone_validator])
    code = forms.CharField(max_length=20, label="رمز الطلب")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].widget.attrs.update({"class": "lux-input", "placeholder": "رقم الهاتف"})
        self.fields["code"].widget.attrs.update({"class": "lux-input", "placeholder": "رمز الطلب"})

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        return "".join(str(phone).split())