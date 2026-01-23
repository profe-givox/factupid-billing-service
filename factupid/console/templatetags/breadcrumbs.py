

from django import template
from django.template import Node, Variable
from django.template.defaulttags import url
from django.utils.encoding import smart_str  # Cambiado de smart_unicode a smart_str
from django.template import VariableDoesNotExist
from .breadcrumbs import *

register = template.Library()

@register.tag
def breadcrumb(parser, token):
    return BreadcrumbNode(token.split_contents()[1:])

@register.tag
def breadcrumb_url(parser, token):
    bits = token.split_contents()
    if len(bits) == 2:
        return breadcrumb(parser, token)
    title = bits.pop(1)
    token.contents = ' '.join(bits)
    url_node = url(parser, token)
    return UrlBreadcrumbNode(title, url_node)

class BreadcrumbNode(Node):
    def __init__(self, vars):
        self.vars = list(map(Variable, vars))

    def render(self, context):
        title = self.vars[0].var
        if title.find("'") == -1 and title.find('"') == -1:
            try:
                title = self.vars[0].resolve(context)
            except:
                title = ''
        else:
            title = title.strip("'").strip('"')
            title = smart_str(title)  # Cambiado de smart_unicode a smart_str

        url = None
        if len(self.vars) > 1:
            try:
                url = self.vars[1].resolve(context)
            except VariableDoesNotExist:
                url = None

        return create_crumb(title, url)

class UrlBreadcrumbNode(Node):
    def __init__(self, title, url_node):
        self.title = Variable(title)
        self.url_node = url_node

    def render(self, context):
        title = self.title.var
        if title.find("'") == -1 and title.find('"') == -1:
            try:
                title = self.title.resolve(context)
            except:
                title = ''
        else:
            title = title.strip("'").strip('"')
            title = smart_str(title)  # Cambiado de smart_unicode a smart_str

        url = self.url_node.render(context)
        return create_crumb(title, url)

def create_crumb(title, url=None):
    crumb = """<span class="breadcrumbs-arrow">🚩</span>"""
    if url:
        crumb += f"<a href='{url}'>{title}</a>"
    else:
        crumb += f"&nbsp;&nbsp;{title}"
    return crumb
