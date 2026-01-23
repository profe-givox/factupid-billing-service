from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from console.models import User_Service  # Asegúrate de ajustar esto al nombre correcto de tu app
from invoice.models import PerfilFiscalUser

class PlanAndGroupRequiredMixin(LoginRequiredMixin):
    group_required = 'invoice'  # Nombre del grupo requerido

    def dispatch(self, request, *args, **kwargs):
        # Verifica que el usuario esté autenticado
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Verifica si el usuario pertenece al grupo requerido
        if self.group_required and not request.user.groups.filter(name=self.group_required).exists():
            raise PermissionDenied("No tienes permiso para acceder a esta página.")

        # Verifica si el usuario tiene un plan activo asociado en User_Service
        if not self.user_has_plan():
            return redirect('api')  # Redirige a la página de selección de planes

        return super().dispatch(request, *args, **kwargs)

    def user_has_plan(self):
        # Verifica si existe un User_Service asociado al usuario con un plan válido
        return User_Service.objects.filter(idUser=self.request.user, idPlan__isnull=False).exists()

class PerfilFiscalRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        # Verifica que el usuario esté autenticado
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Verifica si el usuario tiene un perfil fiscal registrado
        if not self.user_has_perfil_fiscal():
            return redirect('invoice:perfilpreferencias')  # Redirige a la página de registro de perfil fiscal

        return super().dispatch(request, *args, **kwargs)

    def user_has_perfil_fiscal(self):
        # Verifica si existe un PerfilFiscalUser asociado al usuario
        return PerfilFiscalUser.objects.filter(user=self.request.user).exists()