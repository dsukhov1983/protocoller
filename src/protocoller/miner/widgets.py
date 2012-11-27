# coding: utf-8

from django import forms
from django.utils.safestring import mark_safe


class WysiHtml5Textarea(forms.Textarea):
    """
    Widget for wysihtml text area

    http://jhollingworth.github.com/bootstrap-wysihtml5/
    """
    def __init__(self, attrs=None):
        default_attrs = dict(style="width: 810px; height: 200px")
        if attrs:
            default_attrs = default_attrs.update(attrs)
        super(WysiHtml5Textarea, self).__init__(default_attrs)

    def _media(self):
        return forms.Media(
            css={'all': ('css/bootstrap-wysihtml5.css',)},
            js=('js/wysihtml5-0.3.0.js',
                'js/bootstrap-wysihtml5.js'))
    media = property(_media)

    def render(self, name, value, attrs=None):
        html = super(WysiHtml5Textarea, self).render(name, value, attrs)
        html += '<script type="text/javascript">$(".wysihtml5textarea").wysihtml5();</script>'
        return mark_safe(html)
