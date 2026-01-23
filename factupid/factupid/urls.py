"""
Definition of urls for factupid.
"""

from datetime import datetime
from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views
from cfdi.Ladoclientes import mi_admin_site
from cfdi import views as cfdi_views


from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from cfdi import views as cfdi_views

urlpatterns = [
    path("api/", include('api.urls')),
    path('nested_admin/', include('nested_admin.urls')),
    path('invoice/', include('invoice.urls')),
    path('mi-admin/', mi_admin_site.urls),
    path('console/', include('console.urls')),
    path('cfdi/', include('cfdi.urls')),
    path('', cfdi_views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    # path('soap_service/stamp', views.my_soap_application, name='soap_service'),
    # path('soap_service/cancel', views.my_soap_application_cancel, name='soap_service_cancel'),
    # path('soap_client/', views.some_view, name='soap_client'),
    # path('login/',
    #         LoginView.as_view
    #         (
    #             template_name='app/login.html',
    #             authentication_form=forms.BootstrapAuthenticationForm,
    #             extra_context=
    #             {
    #                 'title': 'Log in',
    #                 'year' : datetime.now().year,
    #             }
    #         ),
    #         name='login'),
    # path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),   
    # YOUR PATTERNS
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]


from django.conf.urls.static import static


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
