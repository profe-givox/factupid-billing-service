"""
Definition of urls for factupid.
"""
from django.urls import path
from django.contrib.auth.decorators import login_required, permission_required

from invoice import views
from django.contrib.auth.views import LoginView
from invoice import forms
from datetime import datetime
from invoice.vistas.cliente.views import *
from django.urls import path
from invoice.vistas.cliente.views import SendContractEmailView

app_name = "invoice"
urlpatterns = [
    path('', views.home, name='inicio'),
    path('terminos', views.terminos, name='Terminos'),
    path('politicas', views.politicas, name='Politicas'),
    path('soap_service/stamp', views.my_soap_application, name='soap_service'),
    path('soap_service/register', views.my_register_application, name='register_service'),
    path('soap_service/cancel', views.my_soap_application_cancel, name='soap_service_cancel'),
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
             template_name='invoice/iniciarsesion.html',
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

    # path('catalogoClientesinv/', views.catalogo_clientes, name='catalogoClientesinv'),

    
    path('clientes/lista/', ClientListView.as_view(), name='client_list'),
    path('clientes/add/', MultiFormView.as_view(), name='multi_form_view'),
    path('clientes/edit/<int:pk>/', ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/delete/<int:pk>/', ClienteDeleteView.as_view(), name='cliente_delete'),
    path('clientes/estatus/<int:pk>/', ClienteEstatusView.as_view(), name='cliente_estatus'),

    path('clientes/timbres/<int:cliente_id>/', timbres_cliente, name='timbres_clientes'), 
    path('clientes/timbres_Add/', add_timbre, name='add_timbre'),


    path('clientes/tokens/', TokenCreateView.as_view(), name='client_token'), 
    path('clientes/listTokens/', TokensListView.as_view(), name='list_token'),  
    path('clientes/token_reset/<int:pk>/', TokenResetView.as_view(), name='reset_token'),
    path('clientes/token_update/<int:pk>/', TokenUpdateView.as_view(), name='update_token'),

    
    path('clientes/listaFirma/', ContratoListView.as_view(), name='lista_contrato'),
    path('perfiles/listaFirma/', ContratosListViewPerfil, name='lista_contratoPerfil'),


    # Otras rutas
    path('contrato/<int:contrato_id>/descargar_pdf/', descargar_contrato_pdf, name='descargar_contrato_pdf'),
    path('contrato/<int:contrato_id>/descargar_xml/', descargar_contrato_xml, name='descargar_contrato_xml'),
    path('contrato/<int:contrato_id>/descargar_pdfPerfil/', descargar_contrato_pdfPerfil, name='descargar_contrato_pdfPerfil'),
    path('contrato/<int:contrato_id>/descargar_xmlPerfil/', descargar_contrato_xmlPerfil, name='descargar_contrato_xmlPerfil'),
    path('send-email/<int:contrato_id>/', SendContractEmailView, name='send_contract_email'),
    path('send-email-archivos/<int:contrato_id>/', SendContractFirmadoEmailView, name='send_contractArchivos_email'),


     
    
    path('perfil_pref/', MultiFormPerfilView.as_view(), name='perfilpreferencias'),
    #path('perfil_pref/edit/<int:pk>/', PerfilUpdateView.as_view(), name='perfil_update'),
    path('perfil_pref/delete/<int:pk>/', PerfilDeleteView.as_view(), name='perfil_delete'),  

    path('perfil_pref/historial-creditos/', facturas_por_fecha, name='perfil_historial'),  
    
]