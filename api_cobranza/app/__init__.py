"""
Compatibilidad de imports para distintos entrypoints.

Permite que imports como ``from app...`` funcionen cuando el módulo se
carga como ``api_cobranza.app...`` (por ejemplo desde la raíz del repo).
"""

import sys


# Si se importó como "api_cobranza.app", exponer alias "app".
if __name__ != "app":
    sys.modules.setdefault("app", sys.modules[__name__])
