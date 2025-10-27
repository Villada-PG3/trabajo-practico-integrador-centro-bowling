from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permite acceder a un diccionario con una clave dinámica."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
