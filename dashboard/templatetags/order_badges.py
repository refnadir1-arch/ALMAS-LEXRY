from django import template

register = template.Library()

@register.filter
def order_status_class(value):
    mapping = {
        "NEW": "status-new",
        "PENDING_CONFIRMATION": "status-pending",
        "CONFIRMED": "status-confirmed",
        "PREPARING": "status-preparing",
        "SHIPPED": "status-shipped",
        "OUT_FOR_DELIVERY": "status-out",
        "DELIVERED": "status-delivered",
        "CANCELED": "status-canceled",
    }
    return mapping.get(value, "status-default")