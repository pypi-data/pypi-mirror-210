from io import BytesIO

from django import template
from django.utils.safestring import mark_safe

import barcode

register = template.Library()


# Adapted by https://stackoverflow.com/questions/62244670/print-barcode-in-pdf-with-django
@register.simple_tag
def generate_barcode(uid):
    rv = BytesIO()
    writer = barcode.writer.SVGWriter()
    code = barcode.get("code128", uid, writer=writer)
    code.write(
        rv, options={"module_height": 5, "module_width": 0.3, "text_distance": 2, "font_size": 6}
    )

    rv.seek(0)
    # get rid of the first bit of boilerplate
    rv.readline()
    rv.readline()
    rv.readline()
    rv.readline()
    # read the svg tag into a string
    svg = rv.read()
    return mark_safe(svg.decode("utf-8"))  # noqa
