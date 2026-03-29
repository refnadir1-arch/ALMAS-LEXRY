from django.urls import path
from store import views

urlpatterns = [
    path("store/", views.store_view, name="store"),
    path("p/<str:slug>/", views.product_detail, name="product_detail"),
]