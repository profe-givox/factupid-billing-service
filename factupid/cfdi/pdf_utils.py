import os
from functools import lru_cache

from django.conf import settings
from satcfdi.render import pdf_bytes
from satcfdi.render.environment import CFDIEnvironment


@lru_cache(maxsize=1)
def get_comprobante_template():
    """Return the custom CFDI Jinja template for PDF generation."""
    template_dir = os.path.join(settings.BASE_DIR, "cfdi", "templates")
    env = CFDIEnvironment(templates_path=template_dir)
    return env.get_template("pdf/Comprobante_main.html")


def render_comprobante_pdf_bytes(cfdi):
    """Render CFDI to PDF bytes using the custom comprobante template."""
    return pdf_bytes(cfdi, template=get_comprobante_template())
