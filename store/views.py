from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from store.models import Category, Product

def store_view(request):
    qs = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images", "variants")

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(name__icontains=q)

    category_slug = (request.GET.get("category") or "").strip()
    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    size = (request.GET.get("size") or "").strip()
    if size:
        qs = qs.filter(variants__size=size)

    color = (request.GET.get("color") or "").strip()
    if color:
        qs = qs.filter(variants__color__icontains=color)

    available = (request.GET.get("available") or "").strip()
    if available == "1":
        qs = qs.filter(variants__stock__gt=0)

    sort = (request.GET.get("sort") or "new").strip()
    if sort == "price_asc":
        qs = qs.order_by("price_dzd", "-created_at")
    elif sort == "price_desc":
        qs = qs.order_by("-price_dzd", "-created_at")
    elif sort == "best":
        qs = qs.order_by("-sales_count", "-created_at")
    elif sort == "discount":
        qs = qs.order_by("-discount_percent", "-created_at")
    else:
        qs = qs.order_by("-created_at")

    qs = qs.distinct()

    paginator = Paginator(qs, 12)
    products = paginator.get_page(request.GET.get("page"))

    categories = Category.objects.filter(is_active=True).order_by("name")

    return render(request, "store/store.html", {
        "page_title": "المنتجات",
        "products": products,
        "categories": categories,
        "filters": {
            "q": q,
            "category": category_slug,
            "size": size,
            "color": color,
            "available": available,
            "sort": sort,
        }
    })

def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("images", "variants"),
        slug=slug,
        is_active=True
    )
    related = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=product.pk).order_by("-created_at")[:8]

    return render(request, "store/product_detail.html", {
        "page_title": product.name,
        "product": product,
        "variants": product.variants.all().order_by("size", "color"),
        "related": related,
    })