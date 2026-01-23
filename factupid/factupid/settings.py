"""
Django settings for factupid project.

Based on 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

from datetime import timedelta
import os
from pathlib import Path

import factupid.db as db
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Otras importaciones necesarias

#MEDIA_ROOT y MEDIA_URL: Para especificar dónde se almacenarán los archivos subidos y cómo se accederá a ellos desde la web.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Configuración de registro detallada
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        # 'verbose': {  # Puedes mantenerlo si lo usas para otros handlers (ej. archivos)
        #     'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
        #     'style': '{',
        # },
        'simple': {
            'format': '[{levelname}] {asctime} {name}: {message}', # 'name' muestra el nombre del logger
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',  # Nivel mínimo que este handler procesará para tu app
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'null': { # Un handler que no hace nada, para silenciar otros loggers
            'class': 'logging.NullHandler',
        },
    },
    'root': {  # Configurar el logger raíz para capturar todos los logs de la app
        'handlers': ['null'], # El raíz no enviará nada a la consola por defecto
        'level': 'WARNING',   # Nivel base para el raíz (no se mostrará con handler 'null')
    },
    'loggers': {
        'api': { # Logger para tu aplicación 'api'
            # Asumiendo que en tus módulos de la app 'api' usas logging.getLogger(__name__)
            # y __name__ será algo como 'api.views', 'api.cfdi_viewsets.viewSets', etc.
            'handlers': ['console'],
            'level': 'INFO',    # Solo mensajes INFO y superiores de tu app 'api'
            'propagate': False, # Importante: no pasar a loggers padres
        },
        'django': {
            'handlers': ['null'], # Descartar logs de Django
            'level': 'WARNING',   # Nivel base (no importa mucho con NullHandler)
            'propagate': False,
        },
        'suds': {  # Logger específico para la biblioteca suds
            'handlers': ['null'], # Descartar logs de suds
            'level': 'WARNING',
            'propagate': False,
        },
        # Aquí podrías añadir configuraciones para otros loggers de terceros
        # que quieras silenciar o manejar de forma específica.
    },
}

# Otras configuraciones del proyecto

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')
SECRET_KEY_SUPP_STAMP = b'lWaTSWbCRUUqDPmVUBNRLwGjcPbdNDshaNYFN8-jIEk='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['192.168.1.118','ae5f-187-140-74-176.ngrok-free.app','0.0.0.0', '127.0.0.1', 'localhost', '*']

CSRF_TRUSTED_ORIGINS = ['https://app.factupid.com','https://*.ngrok-free.app','https://*.127.0.0.1', 'https://192.168.54.31']

# Application references
# https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-INSTALLED_APPS
INSTALLED_APPS = [
    'app',
    'console',
    'django_soap',
    'cfdi',
    'invoice',
    'widget_tweaks',
    'bootstrap_modal_forms',
    'view_breadcrumbs',
    'admin_material.apps.AdminMaterialDashboardConfig',
    'nested_admin',
    # Add your apps here to enable them
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_session_timeout',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'dal',
    'dal_select2',
]

# Middleware framework
# https://docs.djangoproject.com/en/2.1/topics/http/middleware/
MIDDLEWARE = [
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django_session_timeout.middleware.SessionTimeoutMiddleware',
]

ROOT_URLCONF = 'factupid.urls'

# Template configuration
# https://docs.djangoproject.com/en/2.1/topics/templates/

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'console/templates'),
            os.path.join(BASE_DIR, 'console/templates/admin'),
            os.path.join(BASE_DIR, 'console/templates/administrador'),
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'plantillas'),
            os.path.join(BASE_DIR, 'plantillas/administrador'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # otros context processors
                'invoice.context_processors.perfil_fiscal_user',
                'cfdi.context_processor.negocio_actual',
                
            ],
        },
    },
]

WSGI_APPLICATION = 'factupid.wsgi.application'
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = db.SQLITE

# Ajuste del nombre de la base de datos de pruebas según el entorno CI/CD
if os.environ.get("CI_ENVIRONMENT") == "staging":
    DATABASES["default"]["TEST"] = {"NAME": "test_factupid_staging"}
elif os.environ.get("CI_ENVIRONMENT") == "production":
    DATABASES["default"]["TEST"] = {"NAME": "test_factupid_production"}
else:
    DATABASES["default"]["TEST"] = {"NAME": "test_factupiddatabase"}

# Auto-generated primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'console/static',
    BASE_DIR / 'invoice/static',
    BASE_DIR / 'cfdi/static',
    os.path.join(BASE_DIR / 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

#email

# settings.py

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')  
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DOMAIN = config('DOMAIN')

AUTH_AUTHENTICATION_TYPE = 'both'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Modelo de autenticación predeterminado de Django
]

ENCRYPTION_KEY = config('ENCRYPTION_KEY')



# Configuración específica de django-session-timeout
SESSION_EXPIRE_SECONDS = 900  # 15 minutos de inactividad
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD = 60  # Agrupar actividad por minuto.
SESSION_TIMEOUT_REDIRECT = '/'  # Redirección al expirar la sesión

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Requiere que todas las vistas estén protegidas
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Tiempo de expiración del token de acceso
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # Tiempo de expiración del token de refresco
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Factupid API',
    'DESCRIPTION': 'Servicios de facturación electrónica',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
    'SWAGGER_UI_DIST': 'SIDECAR',  # shorthand to use the sidecar instead
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    # OTHER SETTINGS
}

# Credenciales de PAC
PAC_USER = config('PAC_USER')
PAC_PASSWORD = config('PAC_PASSWORD')
