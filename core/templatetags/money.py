from django import template

register = template.Library()

@register.filter(name="dzd")
def dzd(value):
    try:
        n = int(round(float(value)))
    except Exception:
        return "0 دج"
    return f"{n:,} دج"