from django import template

register = template.Library()
@register.filter
# @register.filter
def currency(value):
    try:
        return "{:,.0f}".format(value)
    except (ValueError, TypeError):
        return value


from django.utils.http import urlencode

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)