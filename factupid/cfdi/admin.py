from django import forms
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.models import Group,Permission
from .models import *






# Register your models here.



admin.site.index_template = 'administrador django/base.html'
admin.site.login_template = 'administrador django/login.html'



def create_admin_class(model):
    class GenerAdmin(admin.ModelAdmin):
        delete_confirmation_template = 'administrador django/delete_confirmation.html'
        delete_selected_confirmation_template = 'administrador django/delete_selected_confirmation.html'
        index_template = 'administrador django/index.html'
        change_form_template = 'administrador django/change_form.html'
        change_list_template = 'administrador django/change_list.html'
 
    return GenerAdmin


class ClaveProdServAdmin(admin.ModelAdmin):
    delete_confirmation_template = 'administrador django/delete_confirmation.html'
    delete_selected_confirmation_template = 'administrador django/delete_selected_confirmation.html'
    search_fields = ['c_ClaveProdServ', 'descripcion', 'palabras_similares']  # Permitir búsquedas
    index_template = 'administrador django/index.html'
    change_form_template = 'administrador django/change_form.html'
    change_list_template = 'administrador django/change_list.html'
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated


class CustomGroupAdminForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple("permisos", is_stacked=False),
        required=False,
    )

    class Meta:
        model = Group
        fields = "__all__"

    

class GroupAdmin(admin.ModelAdmin):
    delete_confirmation_template = 'administrador django/delete_confirmation.html'
    delete_selected_confirmation_template = 'administrador django/delete_selected_confirmation.html'
    index_template = 'administrador django/index.html'
    change_form_template = 'administrador django/change_form.html'
    change_list_template = 'administrador django/change_list.html'
    form = CustomGroupAdminForm

    def get_form(self, request, obj=None, **kwargs):
        """Asegurar que los permisos se pasen al contexto correctamente."""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['permissions'].queryset = Permission.objects.all()
        return form

    def get_context_data(self, request, obj=None):
        """Pasar los permisos disponibles y elegidos al contexto de la plantilla."""
        context = super().get_changeform_initial_data(request)
        context['available_permissions'] = Permission.objects.all()
        if obj:
            context['chosen_permissions'] = obj.permissions.all()
        else:
            context['chosen_permissions'] = []
        return context
    

class CustomUserAdminForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple("permisos", is_stacked=False),
        required=False,
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple("grupos", is_stacked=False),
        required=False,
    )

    class Meta:
        model = User
        fields = "__all__"

    # class Media:
    #     css = {
    #         'all': ('cfdi/administrador django/custom_admin.css',)  # Ruta a tu CSS
    #     }

class UserAdmin(admin.ModelAdmin):
    delete_confirmation_template = 'administrador django/delete_confirmation.html'
    delete_selected_confirmation_template = 'administrador django/delete_selected_confirmation.html'
    index_template = 'administrador django/index.html'
    change_form_template = 'administrador django/change_form.html'
    change_list_template = 'administrador django/change_list.html'
    form = CustomUserAdminForm

    def get_form(self, request, obj=None, **kwargs):
        """Asegurar que los permisos y grupos se pasen al contexto correctamente."""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['permissions'].queryset = Permission.objects.all()
        form.base_fields['groups'].queryset = Group.objects.all()
        return form

    def get_context_data(self, request, obj=None):
        """Pasar los permisos y grupos disponibles y elegidos al contexto de la plantilla."""
        context = super().get_changeform_initial_data(request)
        context['available_permissions'] = Permission.objects.all()
        context['available_groups'] = Group.objects.all()
        if obj:
            context['chosen_permissions'] = obj.permissions.all()
            context['chosen_groups'] = obj.groups.all()
        else:
            context['chosen_permissions'] = []
            context['chosen_groups'] = []
        return context
    
   
class codigopostal (admin.ModelAdmin):
    delete_confirmation_template = 'administrador django/delete_confirmation.html'
    delete_selected_confirmation_template = 'administrador django/delete_selected_confirmation.html'
    index_template = 'administrador django/index.html'
    change_form_template = 'administrador django/change_form.html'
    change_list_template = 'administrador django/change_list.html'
    search_fields = ['c_CodigoPostal', 'c_Municipio__descripcion', 'c_Localidad__descripcion']


class comprobante(admin.ModelAdmin):
        delete_confirmation_template = 'administrador django/delete_confirmation.html'
        delete_selected_confirmation_template = 'administrador django/delete_selected_confirmation.html'
        index_template = 'administrador django/index.html'
        change_form_template = 'administrador django/change_form.html'
        change_list_template = 'administrador django/change_list.html' 
        autocomplete_fields = ['c_LugarExpedicion']  # Campos de autocompletar

class comprobantejubilacion(admin.ModelAdmin):
        delete_confirmation_template = 'administrador django/delete_confirmation.html'
        delete_selected_confirmation_template = 'administrador django/delete_selected_confirmation.html'
        index_template = 'administrador django/index.html'
        list_display = ['total_una_exhibicion', 'ingreso_acumulable', 'ingreso_no_acumulable']
        change_form_template = 'administrador django/change_form.html'
        change_list_template = 'administrador django/change_list.html' 
        



class NominaAdmin(admin.ModelAdmin):
        delete_confirmation_template = 'administrador django/delete_confirmation.html'
        delete_selected_confirmation_template = 'administrador django/delete_selected_confirmation.html'
        index_template = 'administrador django/index.html'
        change_form_template = 'administrador django/change_form.html'
        change_list_template = 'administrador django/change_list.html' 
        autocomplete_fields = ['c_CodigoPostal']  # Campos de autocompletar


admin.site.register(CodigoPostal, codigopostal)
admin.site.register(Comprobante, comprobante)

# Desregistrar el admin original y registrar el personalizado
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


# Registros dinámicos en admin.site
admin.site.unregister(User)

admin.site.register(User, UserAdmin)


admin.site.register(VersionCFDI, create_admin_class(VersionCFDI))
# admin.site.register(Deduccion, create_admin_class(Deduccion))
# admin.site.register(TipoDeduccion, create_admin_class(TipoDeduccion))
admin.site.register(TipoComprobante, create_admin_class(TipoComprobante))
admin.site.register(FormaPago, create_admin_class(FormaPago))
admin.site.register(Moneda, create_admin_class(Moneda))
# admin.site.register(Exportaciones, create_admin_class(Exportaciones))
admin.site.register(MetodoPago, create_admin_class(MetodoPago))
admin.site.register(Periodicidad, create_admin_class(Periodicidad))
admin.site.register(Meses, create_admin_class(Meses))
admin.site.register(TipoRelacion, create_admin_class(TipoRelacion))
admin.site.register(RegimenFiscal, create_admin_class(RegimenFiscal))
admin.site.register(Pais, create_admin_class(Pais))
admin.site.register(UsoCFDI, create_admin_class(UsoCFDI))
admin.site.register(ClaveProdServ, ClaveProdServAdmin)
admin.site.register(ClaveUnidad, create_admin_class(ClaveUnidad))
admin.site.register(ObjetoImp, create_admin_class(ObjetoImp))
admin.site.register(Impuesto, create_admin_class(Impuesto))
admin.site.register(TipoFactor, create_admin_class(TipoFactor))
admin.site.register(Aduana, create_admin_class(Aduana))
# admin.site.register(numpedimentoaduana, create_admin_class(numpedimentoaduana))
admin.site.register(PatenteAduanal, create_admin_class(PatenteAduanal))
admin.site.register(TasaOCuota, create_admin_class(TasaOCuota))
admin.site.register(Estado, create_admin_class(Estado))
admin.site.register(Localidad, create_admin_class(Localidad))
admin.site.register(Municipio, create_admin_class(Municipio))

admin.site.register(Colonia, create_admin_class(Colonia))
admin.site.register(InformacionFiscal, create_admin_class(InformacionFiscal))
admin.site.register(FacturaElectronica, create_admin_class(FacturaElectronica))
admin.site.register(InformacionPago, create_admin_class(InformacionPago))
admin.site.register(Receptor, create_admin_class(Receptor))
admin.site.register(Conceptos, create_admin_class(Conceptos))
admin.site.register(InformacionGlobal, create_admin_class(InformacionGlobal))
admin.site.register(Emisor, create_admin_class(Emisor))
admin.site.register(ComprobantesRelacionados, create_admin_class(ComprobantesRelacionados))
admin.site.register(LeyendasFiscales, create_admin_class(LeyendasFiscales))
admin.site.register(FacturaElectronicaBorrador, create_admin_class(FacturaElectronicaBorrador))
admin.site.register(CertificadoSelloDigital, create_admin_class(CertificadoSelloDigital))
admin.site.register(ComprobanteEmitido, create_admin_class(ComprobanteEmitido))
admin.site.register(origenCFDI, create_admin_class(origenCFDI))
admin.site.register(Conceptosimpuesto, create_admin_class(Conceptosimpuesto))

admin.site.register(Exportacion, create_admin_class(Exportacion))
admin.site.register(Impuestos, create_admin_class(Impuestos))
admin.site.register(InformacionAduanera, create_admin_class(InformacionAduanera))
admin.site.register(UsersCFDI, create_admin_class(UsersCFDI))
admin.site.register(CfdiRelacionados, create_admin_class(CfdiRelacionados))
admin.site.register(TiposComplemento, create_admin_class(TiposComplemento))
admin.site.register(TimbreFiscalDigital, create_admin_class(TimbreFiscalDigital))
admin.site.register(Complemento, create_admin_class(Complemento))
admin.site.register(Addenda, create_admin_class(Addenda))
admin.site.register(AddendaSiemensGamesa, create_admin_class(AddendaSiemensGamesa))
admin.site.register(AddendaGrupoADO, create_admin_class(AddendaGrupoADO))
admin.site.register(AddendaWaldos, create_admin_class(AddendaWaldos))
admin.site.register(AddendaTerraMultitransportes, create_admin_class(AddendaTerraMultitransportes))
admin.site.register(ACuentaTerceros, create_admin_class(ACuentaTerceros))
admin.site.register(CuentaPredial, create_admin_class(CuentaPredial))
admin.site.register(Parte, create_admin_class(Parte))
admin.site.register(PedimentoCFDI, create_admin_class(PedimentoCFDI))
admin.site.register(Banco, create_admin_class(Banco))
admin.site.register(TipoNomina, create_admin_class(TipoNomina))
admin.site.register(CancelacionCFDI, create_admin_class(CancelacionCFDI))
admin.site.register(GroupMeta, create_admin_class(GroupMeta))
admin.site.register(BitacoraCFDI, create_admin_class(BitacoraCFDI))
admin.site.register(UserTimbreCount, create_admin_class(UserTimbreCount))

#sindicalizado
admin.site.register(Sindicalizado, create_admin_class(Sindicalizado))

#Nomina
admin.site.register(Nomina, NominaAdmin)

#horas extras
admin.site.register(HorasExtra, create_admin_class(HorasExtra))

#otropago
admin.site.register(OtroPago, create_admin_class(OtroPago))
#incapacidad
admin.site.register(Incapacidad, create_admin_class(Incapacidad))
#Deducciones
admin.site.register(Deduccion, create_admin_class(Deduccion))

#plantillas 
admin.site.register(Plantilla, create_admin_class(Plantilla))

#JubilacionPensionRetiro
admin.site.register(JubilacionPensionRetiro, create_admin_class(comprobantejubilacion))