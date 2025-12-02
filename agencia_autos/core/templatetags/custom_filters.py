from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def currency(value):
    """Formato de moneda con comas y símbolo de peso"""
    try:
        # Convertir a float si es string
        if isinstance(value, str):
            value = float(value)
        
        # Formatear con comas
        formatted = intcomma(int(value))
        return f"${formatted}"
    except (ValueError, TypeError):
        return value

@register.filter
def percentage(value):
    """Formato de porcentaje"""
    try:
        if isinstance(value, str):
            value = float(value)
        return f"{value}%"
    except (ValueError, TypeError):
        return value
