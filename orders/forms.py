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
    variant_id = forms.IntegerField()
    qty = forms.IntegerField(min_value=1, max_value=5)

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

    def clean_variant_id(self):
        variant_id = self.cleaned_data["variant_id"]
        if not Variant.objects.filter(id=variant_id).exists():
            raise forms.ValidationError("الخيار غير صالح.")
        return variant_id

class TrackOrderForm(forms.Form):
    phone = forms.CharField(max_length=30, label="رقم الهاتف", validators=[phone_validator])
    code = forms.CharField(max_length=20, label="رمز الطلب")