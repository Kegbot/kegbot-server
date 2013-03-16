from django import template
from socialregistration.templatetags import button

register = template.Library()

register.tag('untappd_button', button('untappd/untappd_button.html'))
