from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Divide un string en una lista usando el delimitador especificado (por defecto: ',')."""
    if isinstance(value, str):
        return value.split(delimiter)
    return []
