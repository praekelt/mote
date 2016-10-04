from django import template


register = template.Library()

# hedley: this is the wrong file!

@register.filter
def index(List, i):
    return List[int(i)]
