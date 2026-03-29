from django import forms
from django.contrib.auth.forms import AuthenticationForm

from core.models import StoreSettings, Review
from orders.constants import ORDER_STATUSES
from store.models import Category, Product, Variant


class DashboardLoginForm(AuthenticationForm):
    username = forms.CharField(label="اسم المستخدم")
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "is_active"]
        labels = {
            "name": "اسم القسم",
            "slug": "الرابط المختصر",
            "is_active": "مفعّل",
        }


class ProductForm(forms.ModelForm):
    image = forms.ImageField(label="الصورة الرئيسية", required=False)
    extra_images = forms.FileField(
        label="صورة إضافية",
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/*"}),
    )

    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "slug",
            "description",
            "price_dzd",
            "compare_at_price_dzd",
            "cost_price_dzd",
            "video_url",
            "sku",
            "seo_title",
            "seo_description",
            "is_active",
        ]
        labels = {
            "category": "القسم",
            "name": "اسم المنتج",
            "slug": "الرابط المختصر",
            "description": "الوصف",
            "price_dzd": "السعر",
            "compare_at_price_dzd": "مقارنة بالسعر",
            "cost_price_dzd": "سعر التكلفة",
            "video_url": "رابط الفيديو",
            "sku": "رمز المنتج SKU",
            "seo_title": "عنوان SEO",
            "seo_description": "وصف SEO",
            "is_active": "إظهار المنتج",
        }

    def clean(self):
        cleaned = super().clean()
        price = cleaned.get("price_dzd")
        compare_price = cleaned.get("compare_at_price_dzd")

        if price and compare_price and compare_price <= price:
            self.add_error("compare_at_price_dzd", "يجب أن يكون السعر قبل التخفيض أكبر من السعر الحالي.")

        return cleaned


class VariantForm(forms.ModelForm):
    class Meta:
        model = Variant
        fields = ["size", "color", "stock"]
        labels = {
            "size": "المقاس",
            "color": "اللون",
            "stock": "المخزون",
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["name", "stars", "text", "is_active"]
        labels = {
            "name": "الاسم",
            "stars": "عدد النجوم",
            "text": "الرأي",
            "is_active": "ظاهر في الموقع",
        }


class StoreSettingsForm(forms.ModelForm):
    class Meta:
        model = StoreSettings
        fields = [
            "store_name",
            "phone",
            "whatsapp",
            "address",
            "shipping_home_fee_dzd",
            "shipping_office_fee_dzd",
            "hero_title",
            "hero_subtitle",
            "instagram_url",
            "facebook_url",
            "tiktok_url",
        ]
        labels = {
            "store_name": "اسم المتجر",
            "phone": "الهاتف",
            "whatsapp": "واتساب",
            "address": "العنوان",
            "shipping_home_fee_dzd": "توصيل المنزل",
            "shipping_office_fee_dzd": "توصيل المكتب",
            "hero_title": "عنوان الواجهة",
            "hero_subtitle": "وصف الواجهة",
            "instagram_url": "إنستغرام",
            "facebook_url": "فيسبوك",
            "tiktok_url": "تيك توك",
        }


class OrderStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(label="الحالة", choices=ORDER_STATUSES)
    note = forms.CharField(label="ملاحظة الحالة", required=False, max_length=255)
    admin_note = forms.CharField(
        label="ملاحظة داخلية",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3})
    )