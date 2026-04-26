from django import forms
from django.contrib.auth.forms import AuthenticationForm

from core.models import Review, StoreSettings
from orders.models import Order
from store.models import Category, Product, Variant


class DashboardLoginForm(AuthenticationForm):
    pass


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "is_active"]
        labels = {
            "name": "اسم القسم",
            "slug": "الرابط المختصر",
            "is_active": "نشط",
        }


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        if not data:
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        return [super().clean(d, initial) for d in data]


class ProductForm(forms.ModelForm):
    all_images = MultipleFileField(
        label="صور المنتج",
        required=False,
        widget=MultipleFileInput(attrs={
            "multiple": True,
            "class": "lux-input",
            "style": "border: 2px dashed var(--gold); padding: 30px;",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "slug" in self.fields:
            self.fields["slug"].required = False

    class Meta:
        model = Product
        fields = [
            "category", "name", "slug", "description",
            "price_dzd", "compare_at_price_dzd", "cost_price_dzd",
            "video_url", "sku", "seo_title", "seo_description", "is_active",
        ]


class VariantForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # المقاس صار اختياري
        self.fields["size"].required = False
        self.fields["size"].initial = "STD"

    def clean_size(self):
        size = (self.cleaned_data.get("size") or "").strip()
        return size or "STD"

    class Meta:
        model = Variant
        fields = ["size", "color", "color_image", "stock"]
        labels = {
            "size": "المقاس (اختياري)",
            "color": "اسم اللون",
            "color_image": "صورة اللون",
            "stock": "المخزون",
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = "__all__"


class StoreSettingsForm(forms.ModelForm):
    class Meta:
        model = StoreSettings
        fields = "__all__"


class OrderStatusUpdateForm(forms.ModelForm):
    note = forms.CharField(
        label="ملاحظة",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    class Meta:
        model = Order
        fields = ["status", "admin_note"]
        labels = {
            "status": "الحالة",
            "admin_note": "ملاحظة الإدارة",
        }