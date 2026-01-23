"""
Definition of urls for factupid.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth.decorators import login_required, permission_required
from cfdi import views
from django.contrib.auth.views import LoginView
from cfdi import forms
from datetime import datetime
from django.urls import path

app_name = "cfdi"
urlpatterns = [
    path('', views.home, name='inicio'),
    path('get_datos_codigo_postal/', views.get_datos_codigo_postal, name='get_datos_codigo_postal'),
    # path('ajax/delete_otro_pago/', views.ajax_delete_otro_pago, name='ajax_delete_otro_pago'),
    # path('ajax/delete_subcontratacion/', views.ajax_delete_subcontratacion, name='ajax_delete_subcontratacion'),
    # path('ajax/delete_deduccion/', views.ajax_delete_deduccion, name='ajax_delete_deduccion'),
    # path('ajax/delete_percepcion/', views.ajax_delete_percepcion, name='ajax_delete_percepcion'),
    path('verificar_comprobante/', views.verificar_comprobante, name='verificar_comprobante'),
    path('mi-admin/get_claveprodserv/', views.get_claveprodserv, name='get_claveprodserv'),
    path('get_claveunidad/', views.get_claveunidad, name='get_claveunidad'),
   # path('guardar-como-borrador/<int:factura_id>/', views.guardar_como_borrador, name='guardar_como_borrador'),
    path('contact/', views.contact, name='contacto'),
    path('about/', views.about, name='mas'),
    path('register/', views.register, name='registrarse'),
    path('cerrarsesion/', views.cerrarsesion, name='cerrarsesion'),
    path('activacionbien/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    path('activacionmal/', views.activacionMal, name='activacionmal'),
    path('malcorreo/', views.activacionMalCorreo, name='activacionmalcorreo'),
    path('malcontrasena/', views.activacionMalContrasena, name='activacionmalcontrasena'),
    path('noregistrado/', views.activacionMalUsuarionoregistrado, name='activacionmalusuarionoregistrado'),
    path('error/', views.errorLinkreutilizado, name='errorLinkreutilizado'),
    path('activacionEnviada/', views.activacionenviada, name='activacionenviada'),
    path('activacionExitosa/', views.activacionBien, name='activacionbien'),
#######################################################################################################    
     path('iniciarsesion/', 
         LoginView.as_view(
             template_name='cfdi/iniciarsesion.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context={
                 'title': 'Iniciar Sesión',
                 'year': datetime.now().year,
             }
         ), 
         name='iniciarsesion'),
    path('iniciarsesionpartial/', views.iniciarsesionpartial, name='iniciarsesionpartial'),
    path('Bienvenido/', views.sesioniniciada, name='iniciosesion'),

#########################################################################
    path('reset_password/',views.restablecer_password, name="reset_password"),
    path('reset_password_send/',views.reseteoEnviado, name="reseteo_enviada"),
    path('reset_password_form/<uidb64>/<token>/',views.resetPassword_account, name="resetPassword_account"),
    path('reset_password_done/',views.reseteoBien, name="reseteobien"),
    path('reset_password_bad/',views.resteoMal, name="reseteomal"),


##############################################################################

    path('informacion_fiscal/activar/<int:pk>/', views.activar_informacion_fiscal, name='activar_informacion_fiscal'),
    path('informacion_fiscal/subir_imagen/<int:pk>/', views.subir_imagen_informacion_fiscal, name='subir_imagen_informacion_fiscal'),
    path ('logout/', views.custom_logout, name='logout'),
    path('ajax/addenda-form/', views.get_addenda_form, name='ajax_addenda_form'),
    path("concepto/obtener_formulario_complemento_concepto/", views.get_complemento_form, name="obtener_formulario_complemento_concepto"),
    path('claveprodserv-autocomplete/', views.ClaveProdServAutocomplete.as_view(), name='claveprodserv-autocomplete'),
    path('informacionaduanera-autocomplete/', views.InformacionAduaneraAutocomplete.as_view(), name='informacionaduanera-autocomplete'),
    path('activar-negocio/<int:negocio_id>/', views.activar_negocio, name='activar_negocio'),
    # Ejemplo típico en urls.py
    path('ajax/percepcion-extra-form/', views.get_percepcion_extra_form, name='percepcion-extra-form'),
    path('cancelar/', views.cancelar_comprobante, name='cancelar_comprobante'),
    path('obtener_cancelacion/<int:id>/', views.obtener_cancelacion, name='obtener_cancelacion'),
    path('obtener_datos_cancelacion/<int:id>/', views.obtener_datos_cancelacion_modal, name='obtener_datos_cancelacion'),
    path('actualizar_estatus_cancelaciones/', views.actualizar_estatus_cancelaciones, name='actualizar_estatus_cancelaciones'),

    path('ajax/percepcion-indemnizacion-form/', views.get_separacion_indemnizacion_form, name='percepcion-indemnizacion-form'),
    path('ajax/percepcion-jubilacion-form/', views.get_jubilacion_pension_retiro_form, name='percepcion-jubilacion-form'),  
    path('bitacora/pdf/<int:pk>/', views.ver_pdf_comprobante, name='ver_pdf_comprobante'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

