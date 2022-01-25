"""Extra template filters for the dash app."""
from django import template

register = template.Library()


def _num_arg(val):
    """Try to cast the given value to an integer of float if it is a string."""
    if isinstance(val, (int, float)):
        return val

    if isinstance(val, str):
        if val.isdecimal():
            return int(val)
        return float(val)

    raise ValueError("can't coerce value to a number")


@register.filter(is_safe=True)
def div(val, other):
    """Integer division filter function."""
    val = _num_arg(val)
    other = _num_arg(other)

    # Divide by zero?
    if other == 0:
        return 0

    return val // other


@register.filter(is_safe=True)
def mul(val, other):
    """Multiply filter function."""
    val = _num_arg(val)
    other = _num_arg(other)

    return val * other


@register.filter("round", is_safe=True)
def _round(val, ndigits=None):
    """Round filter function."""
    val = _num_arg(val)
    return round(val, ndigits)
