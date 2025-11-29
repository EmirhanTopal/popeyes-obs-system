from django import template
register = template.Library()

@register.filter
def make_tuple(value, arg):
    """İki değerden tuple oluşturur."""
    return (int(value), int(arg))

@register.filter
def get_grade(grades_dict, key_tuple):
    """grades_dict içinden (enrollment_id, component_id) çiftine göre not döndürür"""
    return grades_dict.get(key_tuple, "")
