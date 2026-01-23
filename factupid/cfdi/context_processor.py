
from .models import *

# def negocio_actual(request):
#     if request.user.is_authenticated:
#         try:
#             usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
#             usuario_raiz = usuario_cfdi.get_raiz()
#             negocios = InformacionFiscal.objects.filter(idUserCFDI=usuario_raiz, activo=True)
#             negocio = negocios.filter(es_principal=True).first()
#             return {
#                 'negocio_actual': negocio,
#                 'negocios_usuario': negocios
#             }
#         except UsersCFDI.DoesNotExist:
#             return {}
#     return {}

def negocio_actual(request):
    if request.user.is_authenticated:
        try:
            usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
            usuario_raiz = usuario_cfdi.get_raiz()
            negocios = InformacionFiscal.objects.filter(idUserCFDI=usuario_raiz, activo=True)

            negocio = usuario_cfdi.negocio_activo
            
            conteo = usuario_cfdi.get_conteo_timbres_actual()

            # Fallback si no hay negocio activo
            if not negocio or not negocio.activo:
                negocio = negocios.filter(es_principal=True).first()
                if negocio:
                    usuario_cfdi.negocio_activo = negocio
                    usuario_cfdi.save()

            return {
                'negocio_actual': negocio,
                'negocios_usuario': negocios,
                'coneo_timbres': conteo
            }

        except UsersCFDI.DoesNotExist:
            return {}
    return {}


def obtener_negocio_activo_para(request):
    if not request.user.is_authenticated:
        return None
    try:
        usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=request.user)
        negocio = usuario_cfdi.negocio_activo
        if negocio and negocio.activo:
            return negocio
        return None
    except UsersCFDI.DoesNotExist:
        return None

