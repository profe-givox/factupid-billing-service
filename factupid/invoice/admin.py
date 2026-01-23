from django.contrib import admin

from .models import *


def create_admin_class(model):
    class GenerAdmin(admin.ModelAdmin):
        delete_confirmation_template = 'administrador django/delete_confirmation.html'
        delete_selected_confirmation_template = 'administrador django/delete_selected_confirmation.html'
        index_template = 'administrador django/index.html'
        change_form_template = 'administrador django/change_form.html'
        change_list_template = 'administrador django/change_list.html'
 
    return GenerAdmin



# Registro dinámico con create_admin_class
admin.site.register(InvoicePermissions, create_admin_class(InvoicePermissions))
admin.site.register(Cliente, create_admin_class(Cliente))
admin.site.register(User_Cliente, create_admin_class(User_Cliente))
admin.site.register(Tokens, create_admin_class(Tokens))
admin.site.register(PerfilFiscalUser, create_admin_class(PerfilFiscalUser))
admin.site.register(Timbre, create_admin_class(Timbre))
admin.site.register(Contratos, create_admin_class(Contratos))
admin.site.register(TimbreUserPerfil, create_admin_class(TimbreUserPerfil))
admin.site.register(LogStamp, create_admin_class(LogStamp))


# Register your models here.
# admin.site.register(InvoicePermissions)
# admin.site.register(Cliente)
# admin.site.register(User_Cliente)
# admin.site.register(Tokens)
# admin.site.register(PerfilFiscalUser)
# admin.site.register(Timbre)
# admin.site.register(Contratos)
# admin.site.register(TimbreUserPerfil)
# admin.site.register(LogStamp)
