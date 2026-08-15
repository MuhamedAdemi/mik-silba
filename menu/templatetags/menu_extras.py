from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def eur(value):
    """Format a number as '3,50 €' (comma decimal, Euro sign) like the paper menu."""
    try:
        value = Decimal(value)
    except (InvalidOperation, TypeError):
        return value
    return f"{value:.2f}".replace(".", ",") + " €"
