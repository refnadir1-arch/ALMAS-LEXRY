from django.urls import path
from core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),
    path("policies/shipping/", views.shipping_policy, name="shipping_policy"),
    path("policies/returns/", views.returns_policy, name="returns_policy"),
    path("policies/privacy/", views.privacy_policy, name="privacy_policy"),
]