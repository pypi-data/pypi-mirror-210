from datetime import datetime, date
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def is_expired(value):
    """
    Helper Function
    """
    return value < datetime.now().date()


def expires_next_year(value):
    """
    Helper Function
    """
    return value < date(date.today().year + 1, 12, 31)


@register.filter(is_safe=True)
def expiration_class(value):
    """
    Set CSS class for date fields
    """
    if not value:
        return mark_safe('class="danger"')

    if is_expired(value):
        return mark_safe('class="danger"')
    elif expires_next_year(value):
        return mark_safe('class="warning"')
    else:
        return


@register.filter(is_safe=True)
def coverage_class(value):
    """
    Set CSS class for text fields
    """
    if not value or value == "None":
        return mark_safe('class="danger"')


@register.filter(is_safe=True)
def boolian_class(value):
    """
    Set CSS class for boolian fields to display a green thick or a red cross
    """
    if value:
        return mark_safe('class="mdi mdi-check-bold text-success"')
    else:
        return mark_safe('class="mdi mdi-close-thick text-danger"')
