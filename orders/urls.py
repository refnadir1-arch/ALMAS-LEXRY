from django.urls import path
from orders import views

urlpatterns = [
    path("order/product/<int:product_id>/", views.direct_order, name="direct_order"),
    path("order/success/<str:code>/", views.order_success, name="order_success"),
    path("track-order/", views.track_order, name="track_order"),
]