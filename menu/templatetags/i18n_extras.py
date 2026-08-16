from django import template

from config.translations import translate

register = template.Library()


@register.simple_tag(takes_context=True)
def t(context, key):
    lang = context.get("LANG", "hr")
    return translate(key, lang)
