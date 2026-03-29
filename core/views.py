from django.shortcuts import render
from core.models import Review
from store.models import Category, Product

def home(request):
    categories = Category.objects.filter(is_active=True).order_by("name")[:8]
    new_products = Product.objects.filter(is_active=True).order_by("-created_at")[:8]
    best_sellers = Product.objects.filter(is_active=True).order_by("-sales_count", "-created_at")[:8]
    reviews = Review.objects.filter(is_active=True).order_by("-created_at")[:6]

    return render(request, "core/home.html", {
        "page_title": "الرئيسية",
        "categories": categories,
        "new_products": new_products,
        "best_sellers": best_sellers,
        "reviews": reviews,
        "meta_description": "ALMAS LUXRY — أزياء نسائية فاخرة في الجزائر. الدفع عند الاستلام فقط.",
    })

def contact(request):
    return render(request, "core/contact.html", {"page_title": "تواصل معنا"})

def shipping_policy(request):
    return render(request, "core/shipping_policy.html", {"page_title": "سياسة الشحن"})

def returns_policy(request):
    return render(request, "core/returns_policy.html", {"page_title": "سياسة الاسترجاع"})

def privacy_policy(request):
    return render(request, "core/privacy_policy.html", {"page_title": "سياسة الخصوصية"})