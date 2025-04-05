from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='calculate_percentage')
def calculate_percentage(value, max_value=1000):
    try:
        if value is None:
            return 0
        value = float(value)
        max_value = float(max_value)
        percentage = (value / max_value) * 100
        return min(100, max(0, percentage))
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter(name='div')
def div(value, arg):
    try:
        if isinstance(value, (int, float, Decimal)):
            return float(value) / float(arg)
        return 0
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter(name='mul')
def mul(value, arg):
    try:
        if isinstance(value, (int, float, Decimal)):
            return float(value) * float(arg)
        return 0
    except (ValueError, TypeError):
        return 0 