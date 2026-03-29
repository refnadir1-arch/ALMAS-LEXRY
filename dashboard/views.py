import csv

from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.models import Review, StoreSettings
from dashboard.forms import (
    DashboardLoginForm,
    CategoryForm,
    ProductForm,
    VariantForm,
    ReviewForm,
    StoreSettingsForm,
    OrderStatusUpdateForm,
)
from dashboard.utils import dashboard_required, admin_only
from orders.models import Order, OrderStatusHistory
from store.models import Category, Product, ProductImage, Variant


def dashboard_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard_home")

    form = DashboardLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect("dashboard_home")

    return render(request, "dashboard/login.html", {
        "form": form,
        "page_title": "دخول لوحة التحكم",
    })


def dashboard_logout(request):
    logout(request)
    return redirect("dashboard_login")


@dashboard_required
def dashboard_home(request):
    total_orders = Order.objects.count()
    revenue = Order.objects.filter(status="DELIVERED").aggregate(total=Sum("total_dzd"))["total"] or 0
    pending = Order.objects.exclude(status__in=["DELIVERED", "CANCELED"]).count()
    delivered = Order.objects.filter(status="DELIVERED").count()
    canceled = Order.objects.filter(status="CANCELED").count()

    top_products = Product.objects.order_by("-sales_count", "-created_at")[:8]
    low_stock_variants = Variant.objects.select_related("product").filter(stock__lte=2).order_by("stock")[:12]
    latest_orders = Order.objects.select_related("product", "variant").order_by("-created_at")[:10]

    return render(request, "dashboard/dashboard.html", {
        "page_title": "لوحة التحكم",
        "total_orders": total_orders,
        "revenue": revenue,
        "pending": pending,
        "delivered": delivered,
        "canceled": canceled,
        "top_products": top_products,
        "low_stock_variants": low_stock_variants,
        "latest_orders": latest_orders,
    })


@dashboard_required
def categories_list(request):
    categories = Category.objects.order_by("name")
    return render(request, "dashboard/categories_list.html", {
        "page_title": "الأقسام",
        "categories": categories,
    })


@dashboard_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم إنشاء القسم بنجاح.")
        return redirect("dashboard_categories")
    return render(request, "dashboard/category_form.html", {
        "page_title": "إضافة قسم",
        "form": form,
    })


@dashboard_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم تحديث القسم.")
        return redirect("dashboard_categories")
    return render(request, "dashboard/category_form.html", {
        "page_title": "تعديل القسم",
        "form": form,
    })


@dashboard_required
def products_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = Product.objects.select_related("category").order_by("-created_at")

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__name__icontains=q))

    paginator = Paginator(qs, 20)
    products = paginator.get_page(request.GET.get("page"))

    return render(request, "dashboard/products_list.html", {
        "page_title": "المنتجات",
        "products": products,
        "q": q,
    })


@dashboard_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        product = form.save()

        image = form.cleaned_data.get("image")
        if image:
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=True
            )

        extra_image = request.FILES.get("extra_images")
        if extra_image:
            ProductImage.objects.create(
                product=product,
                image=extra_image,
                is_primary=False
            )

        messages.success(request, "تم إنشاء المنتج بنجاح.")
        return redirect("dashboard_products")

    return render(request, "dashboard/product_form.html", {
        "page_title": "إضافة منتج",
        "form": form,
        "product": None,
    })


@dashboard_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)

    if request.method == "POST" and form.is_valid():
        product = form.save()

        image = form.cleaned_data.get("image")
        if image:
            ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=True
            )

        extra_image = request.FILES.get("extra_images")
        if extra_image:
            ProductImage.objects.create(
                product=product,
                image=extra_image,
                is_primary=False
            )

        messages.success(request, "تم تحديث المنتج.")
        return redirect("dashboard_products")

    return render(request, "dashboard/product_form.html", {
        "page_title": "تعديل المنتج",
        "form": form,
        "product": product,
    })


@admin_only
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "تم حذف المنتج.")
    return redirect("dashboard_products")


@dashboard_required
def variants_manage(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = VariantForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        variant = form.save(commit=False)
        variant.product = product
        variant.save()
        messages.success(request, "تمت إضافة المتغير بنجاح.")
        return redirect("dashboard_variants", product_id=product.id)

    variants = product.variants.all().order_by("size", "color")
    return render(request, "dashboard/variants_manage.html", {
        "page_title": f"متغيرات {product.name}",
        "product": product,
        "form": form,
        "variants": variants,
    })


@dashboard_required
def orders_list(request):
    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()

    qs = Order.objects.select_related("product", "variant").order_by("-created_at")

    if q:
        qs = qs.filter(
            Q(code__icontains=q) |
            Q(phone__icontains=q) |
            Q(full_name__icontains=q)
        )

    if status:
        qs = qs.filter(status=status)

    paginator = Paginator(qs, 30)
    orders = paginator.get_page(request.GET.get("page"))

    return render(request, "dashboard/orders_list.html", {
        "page_title": "الطلبات",
        "orders": orders,
        "q": q,
        "status": status,
    })


@dashboard_required
def order_detail(request, code):
    order = get_object_or_404(
        Order.objects.select_related("product", "variant").prefetch_related("history"),
        code=code
    )

    form = OrderStatusUpdateForm(
        request.POST or None,
        initial={
            "status": order.status,
            "admin_note": order.admin_note,
        }
    )

    if request.method == "POST" and form.is_valid():
        new_status = form.cleaned_data["status"]
        note = form.cleaned_data.get("note", "")
        admin_note = form.cleaned_data.get("admin_note", "")

        order.status = new_status
        order.admin_note = admin_note

        if new_status == "SHIPPED" and not order.shipped_at:
            order.shipped_at = timezone.now()

        order.save()

        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            note=note,
            changed_by=request.user
        )

        messages.success(request, "تم تحديث الطلب.")
        return redirect("dashboard_order_detail", code=order.code)

    return render(request, "dashboard/order_detail.html", {
        "page_title": f"طلب {order.code}",
        "order": order,
        "form": form,
        "history": order.history.all(),
    })


@dashboard_required
def orders_export_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="orders.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow([
        "رمز الطلب",
        "الاسم",
        "الهاتف",
        "المنتج",
        "المقاس",
        "اللون",
        "الكمية",
        "الولاية",
        "البلدية",
        "نوع التوصيل",
        "الحالة",
        "الإجمالي",
        "التاريخ",
    ])

    for o in Order.objects.select_related("product", "variant").order_by("-created_at"):
        writer.writerow([
            o.code,
            o.full_name,
            o.phone,
            o.product.name,
            o.variant.size,
            o.variant.color,
            o.qty,
            o.wilaya_name_ar,
            o.commune_name_ar,
            o.get_delivery_type_display(),
            o.get_status_display(),
            o.total_dzd,
            o.created_at.strftime("%Y-%m-%d %H:%M"),
        ])

    return response


@dashboard_required
def reviews_list(request):
    reviews = Review.objects.order_by("-created_at")
    return render(request, "dashboard/reviews_list.html", {
        "page_title": "آراء الزبونات",
        "reviews": reviews,
    })


@dashboard_required
def review_create(request):
    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تمت إضافة الرأي.")
        return redirect("dashboard_reviews")
    return render(request, "dashboard/review_form.html", {
        "page_title": "إضافة رأي",
        "form": form,
    })


@dashboard_required
def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk)
    form = ReviewForm(request.POST or None, instance=review)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم تحديث الرأي.")
        return redirect("dashboard_reviews")
    return render(request, "dashboard/review_form.html", {
        "page_title": "تعديل الرأي",
        "form": form,
    })


@admin_only
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.delete()
    messages.success(request, "تم حذف الرأي.")
    return redirect("dashboard_reviews")


@admin_only
def settings_form(request):
    settings_obj = StoreSettings.get_solo()
    form = StoreSettingsForm(request.POST or None, instance=settings_obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم حفظ الإعدادات.")
        return redirect("dashboard_settings")
    return render(request, "dashboard/settings_form.html", {
        "page_title": "إعدادات المتجر",
        "form": form,
    })


@dashboard_required
def customers_list(request):
    customers = (
        Order.objects.values("phone", "full_name")
        .annotate(orders_count=Count("id"), total_spent=Sum("total_dzd"))
        .order_by("-orders_count", "-total_spent")
    )
    return render(request, "dashboard/customers_list.html", {
        "page_title": "الزبونات",
        "customers": customers,
    })