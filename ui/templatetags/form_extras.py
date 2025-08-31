from django import template
register = template.Library()

@register.filter
def addclass(field, css):
    """Uso: {{ form.campo|addclass:'input' }}"""
    existing = field.field.widget.attrs.get('class', '')
    field.field.widget.attrs['class'] = (existing + ' ' + css).strip()
    return field
