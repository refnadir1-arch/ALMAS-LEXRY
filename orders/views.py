import random
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from core.models import StoreSettings
from orders.forms import DirectOrderForm, TrackOrderForm
from orders.models import Order, OrderStatusHistory
from store.models import Product, Variant
from store.wilayas import ALGERIA_WILAYAS

def generate_order_code():
    while True:
        code = f"ALM{random.randint(100000, 999999)}"
        if not Order.objects.filter(code=code).exists():
            return code

def direct_order(request, product_id):
    product = get_object_or_404(
        Product.objects.prefetch_related("variants", "images"),
        id=product_id,
        is_active=True
    )
    settings_obj = StoreSettings.get_solo()
    variants = product.variants.all().order_by("size", "color")

    if request.method == "POST":
        form = DirectOrderForm(request.POST)
        if form.is_valid():
            variant = get_object_or_404(Variant, id=form.cleaned_data["variant_id"], product=product)
            qty = form.cleaned_data["qty"]

            if variant.stock < qty:
                form.add_error(None, "هذا الخيار غير متوفر بهذه الكمية.")
            else:
                wilaya_code = form.cleaned_data["wilaya_code"]
                wilaya_name = dict(ALGERIA_WILAYAS).get(wilaya_code, "")
                delivery_type = form.cleaned_data["delivery_type"]

                shipping_fee = (
                    settings_obj.shipping_home_fee_dzd
                    if delivery_type == "HOME"
                    else settings_obj.shipping_office_fee_dzd
                )
                unit_price = product.final_price_dzd
                total = (unit_price * qty) + shipping_fee

                with transaction.atomic():
                    updated = Variant.objects.filter(id=variant.id, stock__gte=qty).update(stock=F("stock") - qty)
                    if updated == 0:
                        form.add_error(None, "نفدت الكمية المتاحة، المرجو اختيار كمية أقل.")
                    else:
                        order = Order.objects.create(
                            code=generate_order_code(),
                            product=product,
                            variant=variant,
                            full_name=form.cleaned_data["full_name"],
                            phone=form.cleaned_data["phone"],
                            wilaya_code=wilaya_code,
                            wilaya_name_ar=wilaya_name,
                            commune_name_ar=form.cleaned_data["commune_name_ar"],
                            qty=qty,
                            delivery_type=delivery_type,
                            unit_price_dzd=unit_price,
                            shipping_fee_dzd=shipping_fee,
                            total_dzd=total,
                            customer_note=form.cleaned_data.get("customer_note", ""),
                            status="NEW",
                        )
                        OrderStatusHistory.objects.create(
                            order=order,
                            status="NEW",
                            note="تم إنشاء الطلب"
                        )
                        Product.objects.filter(id=product.id).update(sales_count=F("sales_count") + qty)
                        return redirect("order_success", code=order.code)
    else:
        first_variant = variants.filter(stock__gt=0).first()
        form = DirectOrderForm(initial={
            "variant_id": first_variant.id if first_variant else "",
            "qty": 1,
        })

    return render(request, "orders/order_form.html", {
        "page_title": f"اطلبي الآن - {product.name}",
        "product": product,
        "variants": variants,
        "form": form,
        "shipping_home": settings_obj.shipping_home_fee_dzd,
        "shipping_office": settings_obj.shipping_office_fee_dzd,
    })

def order_success(request, code):
    order = get_object_or_404(Order.objects.select_related("product", "variant"), code=code)
    return render(request, "orders/order_success.html", {
        "page_title": "تم استلام الطلب",
        "order": order,
    })

def track_order(request):
    order = None
    history = None
    form = TrackOrderForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        order = Order.objects.filter(
            phone=form.cleaned_data["phone"],
            code=form.cleaned_data["code"]
        ).select_related("product", "variant").prefetch_related("history").first()

        if order:
            history = order.history.all()

    return render(request, "orders/track_order.html", {
        "page_title": "تتبع الطلب",
        "form": form,
        "order": order,
        "history": history,
    })