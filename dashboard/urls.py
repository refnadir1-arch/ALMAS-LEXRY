from django.urls import path
from dashboard import views

urlpatterns = [
    path("login/", views.dashboard_login, name="dashboard_login"),
    path("logout/", views.dashboard_logout, name="dashboard_logout"),
    path("", views.dashboard_home, name="dashboard_home"),

    path("categories/", views.categories_list, name="dashboard_categories"),
    path("categories/new/", views.category_create, name="dashboard_category_create"),
    path("categories/<int:pk>/edit/", views.category_edit, name="dashboard_category_edit"),

    path("products/", views.products_list, name="dashboard_products"),
    path("products/new/", views.product_create, name="dashboard_product_create"),
    path("products/<int:pk>/edit/", views.product_edit, name="dashboard_product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="dashboard_product_delete"),
    path("products/<int:product_id>/variants/", views.variants_manage, name="dashboard_variants"),

    path("orders/", views.orders_list, name="dashboard_orders"),
    path("orders/<str:code>/delete/", views.order_delete, name="dashboard_order_delete"),
    path("orders/<str:code>/", views.order_detail, name="dashboard_order_detail"),
    path("orders/export/csv/", views.orders_export_csv, name="dashboard_orders_export_csv"),

    path("reviews/", views.reviews_list, name="dashboard_reviews"),
    path("reviews/new/", views.review_create, name="dashboard_review_create"),
    path("reviews/<int:pk>/edit/", views.review_edit, name="dashboard_review_edit"),
    path("reviews/<int:pk>/delete/", views.review_delete, name="dashboard_review_delete"),


    path("settings/", views.settings_form, name="dashboard_settings"),
    path("customers/", views.customers_list, name="dashboard_customers"),
]