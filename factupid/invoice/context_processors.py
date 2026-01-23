from .models import PerfilFiscalUser

def perfil_fiscal_user(request):
    perfil = None
    if request.user.is_authenticated:
        try:
            perfil = PerfilFiscalUser.objects.get(user=request.user)
        except PerfilFiscalUser.DoesNotExist:
            perfil = None
    return {'perfil_fiscal_user': perfil}