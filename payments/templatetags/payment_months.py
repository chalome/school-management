from django import template

from payments.months import month_label

register = template.Library()


@register.filter
def display_month(value):
    return month_label(value)
