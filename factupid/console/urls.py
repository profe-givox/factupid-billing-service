"""
Definition of urls for factupid.
"""
from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from console import forms
from django.conf import settings
from django.conf.urls.static import static
from console import views
from django.urls import include, path
from django.core.mail import send_mail
from django.contrib import admin
from django.contrib.auth import views as auth_views
admin.autodiscover()



urlpatterns = [
    path('', views.home, name='inicio'),
    path('contact/', views.contact, name='contacto'),
    path('about/', views.about, name='mas'),
    
    path('register/', views.register, name='register'),
    path('iniciarsesion/',
         LoginView.as_view
         (
             template_name='console/iniciarsesion.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'iniciar sesion',
                 'year' : datetime.now().year,
             }
         ),
         name='iniciarsesion'),
    path('cerrarsesion/', views.cerrarsesion, name='cerrarsesion'),
    #path('administrador/', admin.site.urls),
    path('Bienvenido/', views.sesioniniciada, name='iniciosesion'),
    path('iniciarsesionpartial/', views.iniciarsesionpartial, name='iniciarsesionpartial'),
    path('activacionbien/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    path('activacionEnviada/', views.activacionenviada, name='activacionenviada'),
    path('activacionmal/', views.activacionMal, name='activacionmal'),
    path('malcorreo/', views.activacionMalCorreo, name='activacionmalcorreo'),
    path('malcontrasena/', views.activacionMalContrasena, name='activacionmalcontrasena'),
    path('noregistrado/', views.activacionMalUsuarionoregistrado, name='activacionmalusuarionoregistrado'),
    path('error/', views.errorLinkreutilizado, name='errorLinkreutilizado'),
    path('activacionExitosa/', views.activacionBien, name='activacionbien'),
    path('app/', views.servicios_app, name='app'),
    path('api/', views.servicios_api, name='api'),
    path('seleccion_servicio/', views.seleccion_servicio, name='seleccion_servicio'),
    path('eliminar-servicio/', views.eliminar_servicio, name='eliminar_servicio'),
    path('servContr/', views.consultar_servicios_api, name='consultar_servicios_api'),
    path('serviciosActivados/', views.SerActivos, name='seleccion_servicioContr'),

    path('reset_password/',views.restablecer_password, name="reset_password"),
    path('reset_password_send/',views.reseteoEnviado, name="reseteo_enviada"),
    path('reset_password_form/<uidb64>/<token>/',views.resetPassword_account, name="resetPassword_account"),
    path('reset_password_done/',views.reseteoBien, name="reseteobien"),
    path('reset_password_bad/',views.resteoMal, name="reseteomal"),


    
    
    
    
    
]