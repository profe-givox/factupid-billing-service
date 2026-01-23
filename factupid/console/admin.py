from django.contrib import admin
from .models import *
from invoice.models import *
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

def create_admin_class(model):
    class GenerAdmin(admin.ModelAdmin):
        delete_confirmation_template = 'administrador django/delete_confirmation.html'
        delete_selected_confirmation_template = 'administrador django/delete_selected_confirmation.html'
        index_template = 'administrador django/index.html'
        change_form_template = 'administrador django/change_form.html'
        change_list_template = 'administrador django/change_list.html'
 
    return GenerAdmin




# Desregistrar User y Group primero
admin.site.unregister(User)
admin.site.unregister(Group)

# Registrarlos nuevamente con create_admin_class
admin.site.register(User, create_admin_class(User))
admin.site.register(Group, create_admin_class(Group))
admin.site.register(SupplierStamp, create_admin_class(SupplierStamp))
admin.site.register(Service, create_admin_class(Service))
admin.site.register(Plan, create_admin_class(Plan))
admin.site.register(Service_Plan, create_admin_class(Service_Plan))
admin.site.register(Post, create_admin_class(Post))
admin.site.register(User_Service, create_admin_class(User_Service))
admin.site.register(SelectedService, create_admin_class(SelectedService))

################invoice
