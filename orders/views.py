import json
import random

from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from orders.forms import DirectOrderForm, TrackOrderForm
from orders.models import Order, OrderItem, OrderStatusHistory
from store.models import Product, Variant
from store.wilayas import ALGERIA_WILAYAS, WILAYA_SHIPPING


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
    variants = product.variants.all().order_by("size", "color")

    # للـ JS
    variants_data = []
    for v in variants:
        variants_data.append({
            "id": v.id,
            "color": v.color,
            "size": (v.size or "STD"),
            "stock": int(v.stock or 0),
            "img": (v.color_image.url if getattr(v, "color_image", None) else (product.primary_image or "")),
        })

    shipping_error = None
    selected_shipping = None
    selected_return_fee = None

    if request.method == "POST":
        form = DirectOrderForm(request.POST)
        if form.is_valid():
            wilaya_code = form.cleaned_data["wilaya_code"]
            delivery_type = form.cleaned_data["delivery_type"]

            wilaya_prices = WILAYA_SHIPPING.get(wilaya_code, {})
            shipping_fee = wilaya_prices.get("home") if delivery_type == "HOME" else wilaya_prices.get("office")
            return_fee = wilaya_prices.get("return_fee")
            selected_shipping = shipping_fee
            selected_return_fee = return_fee

            if shipping_fee is None:
                shipping_error = "التوصيل غير متاح حاليًا لهذه الولاية بهذا النوع من التوصيل."
            else:
                unit_price = product.final_price_dzd

                # ===== اقرأ items_json (عدة خيارات لنفس المنتج) =====
                items_json = (form.cleaned_data.get("items_json") or "").strip()

                if items_json:
                    raw_items = json.loads(items_json)
                    # اجمع نفس المتغير إذا تكرر
                    items_map = {}
                    for it in raw_items:
                        vid = int(it["variant_id"])
                        q = int(it["qty"])
                        items_map[vid] = items_map.get(vid, 0) + q

                    # تحقق أن كل Variant تابع لنفس المنتج
                    chosen_variants = Variant.objects.filter(id__in=items_map.keys(), product=product)
                    chosen_by_id = {v.id: v for v in chosen_variants}

                    if len(chosen_by_id) != len(items_map):
                        form.add_error(None, "يوجد خيار غير صالح داخل الطلب.")
                    else:
                        subtotal = unit_price * sum(items_map.values())
                        total = subtotal + int(shipping_fee)

                        wilaya_name = dict(ALGERIA_WILAYAS).get(wilaya_code, "")

                        with transaction.atomic():
                            # تحقق المخزون + أنقصه
                            for vid, q in items_map.items():
                                v = chosen_by_id[vid]
                                if v.stock < q:
                                    form.add_error(None, f"الكمية غير كافية لـ {v.color} — {v.size}.")
                                    break

                            if not form.errors:
                                # أنقص المخزون
                                for vid, q in items_map.items():
                                    updated = Variant.objects.filter(id=vid, stock__gte=q).update(stock=F("stock") - q)
                                    if updated == 0:
                                        form.add_error(None, "نفدت الكمية المتاحة، المرجو تقليل الكمية.")
                                        break

                            if not form.errors:
                                # للتوافق: نخزن أول عنصر داخل حقول Order القديمة
                                first_vid = next(iter(items_map.keys()))
                                first_variant = chosen_by_id[first_vid]
                                first_qty = items_map[first_vid]

                                order = Order.objects.create(
                                    code=generate_order_code(),
                                    product=product,
                                    variant=first_variant,
                                    full_name=form.cleaned_data["full_name"],
                                    phone=form.cleaned_data["phone"],
                                    wilaya_code=wilaya_code,
                                    wilaya_name_ar=wilaya_name,
                                    commune_name_ar=form.cleaned_data["commune_name_ar"],
                                    qty=first_qty,
                                    delivery_type=delivery_type,
                                    unit_price_dzd=unit_price,
                                    shipping_fee_dzd=int(shipping_fee),
                                    total_dzd=int(total),
                                    customer_note=form.cleaned_data.get("customer_note", ""),
                                    status="NEW",
                                )

                                for vid, q in items_map.items():
                                    OrderItem.objects.create(
                                        order=order,
                                        product=product,
                                        variant=chosen_by_id[vid],
                                        qty=q,
                                        unit_price_dzd=unit_price,
                                    )

                                OrderStatusHistory.objects.create(
                                    order=order,
                                    status="NEW",
                                    note="تم إنشاء الطلب"
                                )

                                Product.objects.filter(id=product.id).update(
                                    sales_count=F("sales_count") + sum(items_map.values())
                                )
                                return redirect("order_success", code=order.code)

                else:
                    # ===== النظام القديم (خيار واحد) =====
                    variant = get_object_or_404(Variant, id=form.cleaned_data["variant_id"], product=product)
                    qty = form.cleaned_data["qty"]

                    subtotal = unit_price * qty
                    total = subtotal + int(shipping_fee)
                    wilaya_name = dict(ALGERIA_WILAYAS).get(wilaya_code, "")

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
                                shipping_fee_dzd=int(shipping_fee),
                                total_dzd=int(total),
                                customer_note=form.cleaned_data.get("customer_note", ""),
                                status="NEW",
                            )

                            OrderItem.objects.create(
                                order=order,
                                product=product,
                                variant=variant,
                                qty=qty,
                                unit_price_dzd=unit_price,
                            )

                            OrderStatusHistory.objects.create(
                                order=order,
                                status="NEW",
                                note="تم إنشاء الطلب"
                            )

                            Product.objects.filter(id=product.id).update(sales_count=F("sales_count") + qty)
                            return redirect("order_success", code=order.code)

    else:
        # GET: نبدأ بخيار واحد افتراضي (ويتم تحويله إلى items_json تلقائيًا في الواجهة)
        requested_variant_id = (request.GET.get("variant") or "").strip()
        requested_qty = (request.GET.get("qty") or "").strip()

        qty_initial = 1
        if requested_qty.isdigit():
            qty_initial = max(1, int(requested_qty))

        variant_initial = None
        if requested_variant_id.isdigit():
            variant_initial = variants.filter(id=int(requested_variant_id)).first()

        if not variant_initial or variant_initial.stock <= 0:
            variant_initial = variants.filter(stock__gt=0).first()

        items_initial = []
        if variant_initial:
            items_initial = [{"variant_id": variant_initial.id, "qty": qty_initial}]

        form = DirectOrderForm(initial={
            "variant_id": variant_initial.id if variant_initial else "",
            "qty": qty_initial,
            "items_json": json.dumps(items_initial, ensure_ascii=False),
        })

    return render(request, "orders/order_form.html", {
        "page_title": f"إتمام الطلب - {product.name}",
        "product": product,
        "variants": variants,
        "variants_data": variants_data,
        "form": form,
        "shipping_error": shipping_error,
        "selected_shipping": selected_shipping,
        "selected_return_fee": selected_return_fee,
        "wilaya_shipping": WILAYA_SHIPPING,
        "pink_page": True,
    })


def order_success(request, code):
    order = get_object_or_404(Order.objects.select_related("product", "variant").prefetch_related("items"), code=code)
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
        ).select_related("product", "variant").prefetch_related("history", "items").first()

        if order:
            history = order.history.all()

    return render(request, "orders/track_order.html", {
        "page_title": "تتبع الطلب",
        "form": form,
        "order": order,
        "history": history,
    })


def shipping_info_api(request):
    wilaya_code = request.GET.get("wilaya_code", "").strip()
    if not wilaya_code:
        return JsonResponse({"ok": False, "error": "wilaya_code مطلوب"}, status=400)

    prices = WILAYA_SHIPPING.get(wilaya_code)
    if not prices:
        return JsonResponse({"ok": False, "error": "الولاية غير موجودة"}, status=404)

    return JsonResponse({
        "ok": True,
        "home": prices.get("home"),
        "office": prices.get("office"),
        "return_fee": prices.get("return_fee"),
    })
from django.contrib.auth.models import User
from django.http import HttpResponse

def reset_admin_password(request):
    user = User.objects.filter(username="admin").first()
    if not user:
        return HttpResponse("Admin user not found")

    user.set_password("NewStrongPassword123")
    user.save()

    return HttpResponse("Password changed successfully ✅")
from django.contrib.auth.models import User
from django.http import HttpResponse

def create_admin_user(request):
    if User.objects.filter(username="superadmin").exists():
        return HttpResponse("User already exists ✅")

    user = User.objects.create_superuser(
        username="superadmin",
        email="admin@example.com",
        password="Admin12345"
    )
    return HttpResponse("Superadmin created ✅")
from django.contrib.auth import get_user_model
from django.http import HttpResponse

def force_reset_password(request):
    User = get_user_model()
    user = User.objects.filter(username="superadmin").first()

    if not user:
        return HttpResponse("User not found ❌")

    user.set_password("Admin12345")
    user.is_staff = True
    user.is_superuser = True
    user.save()

    return HttpResponse("Password reset ✅")
from django.contrib.auth import get_user_model
from django.http import HttpResponse

def create_admin_temp(request):
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Admin12345"
        )
    return HttpResponse("Admin created ✅")