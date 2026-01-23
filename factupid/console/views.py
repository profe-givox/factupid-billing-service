"""
Definition of views.
"""

from datetime import datetime
import os
import re
from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from spyne.decorator import rpc
from spyne.model.complex import Array, ComplexModel, XmlAttribute
from spyne.model.primitive import Unicode, Integer, AnyXml, Ltree, String, Boolean, AnyDict
from spyne.service import ServiceBase
from django.contrib.auth import authenticate, login, logout
from django_soap.utils.client import SOAPClient
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from factupid import settings
from adapter.console.django_user_repository import CustomAuthAdapter
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, get_object_or_404
from django.template.context_processors import csrf
from console.forms import * 
from .models import *
from cfdi.models import UsersCFDI 
from django.core.mail import send_mail
import hashlib, datetime, random    
from django.utils import timezone
import datetime
import lxml.etree as ET
from suds.client import Client
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from adapter.console.django_user_repository import CustomAuthAdapter
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str as force_text
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from .forms import ResetPasswordForm2
#importa el orce_str
from django.utils.encoding import force_str
from django.contrib.auth.models import Group
from datetime import timedelta
from invoice.models import TimbreUserPerfil, PerfilFiscalUser
from invoice.vistas.user import register as registro
from django.templatetags.static import static

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.decorators import login_required
import os
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission








def servicios_app(request):
    if request.user.is_authenticated:
        # Inicializar el diccionario para almacenar los servicios y sus planes
        servicios_con_planes = {}

        # Obtener todos los Service_Plan donde el tipo es 'app' y están activos
        service_plans = Service_Plan.objects.filter(service__tipo='app', isActive=True)

        # Obtener los servicios contratados por el usuario
        user_services = User_Service.objects.filter(idUser=request.user)
        for user_service in user_services:
            service = user_service.idService
            # Verificar que idServicePlan no sea None antes de acceder a isActive
            if service.tipo == 'app' and user_service.idServicePlan and user_service.idServicePlan.isActive:
                if service not in servicios_con_planes:
                    # Incluir plan del usuario si está activo
                    servicios_con_planes[service] = {
                        'plan': user_service.idPlan,  # Plan seleccionado por el usuario
                        'url_servicio': service.url_servicio
                    }

        # Para cada service_plan, añadir los servicios que no tienen planes aún
        for sp in service_plans:
            if sp.service not in servicios_con_planes:
                # Si el usuario no ha contratado un plan para este servicio
                servicios_con_planes[sp.service] = {
                    'plan': None,  # Sin plan seleccionado
                    'url_servicio': 'no activado'  # Sin URL activada
                }

        # Obtener todos los planes disponibles
        todos_los_planes = Plan.objects.all()
    else:
        servicios_con_planes = {}
        todos_los_planes = []

    # --- PATCH: Asignar permisos CFDI si corresponde ---
    for user_service in user_services:
        service = user_service.idService
        if service.nombre.upper() == 'CFDI':
            usuario = request.user
            if not usuario.is_staff:
                usuario.is_staff = True
                usuario.save()
            try:
                cfdi_user, created = UsersCFDI.objects.get_or_create(
                    idUserCFDI=usuario,
                    defaults={'idUserServicePlan_id': user_service}
                )
                if not created:
                    cfdi_user.idUserServicePlan_id = user_service
                    cfdi_user.save()
                else:
                    #Para generar el token inicial y asignar el grupo cfdi
                    cfdi_user.generar_token_inicial()
                    #group = Group.objects.get(name='cfdi')
                    group = Group.objects.filter(name__in=['cfdi', 'CFDI'])
                    usuario.groups.add(*group)
            except Exception:
                pass

            cfdi_models = apps.get_app_config('cfdi').get_models()
            for model in cfdi_models:
                content_type = ContentType.objects.get_for_model(model)
                permissions = [
                    f'add_{model._meta.model_name}',
                    f'change_{model._meta.model_name}',
                    f'delete_{model._meta.model_name}',
                    f'view_{model._meta.model_name}',
                ]
                for perm in permissions:
                    try:
                        permission = Permission.objects.get(
                            codename=perm, content_type=content_type
                        )
                        usuario.user_permissions.add(permission)
                    except Permission.DoesNotExist:
                        continue

    return render(request, 'console/servicios.html', {
        'servicios_con_planes': servicios_con_planes,
        'planes': todos_los_planes
    })



def servicios_api(request):
    if request.user.is_authenticated:
        # Inicializar el diccionario para almacenar los servicios y sus planes
        servicios_con_planes = {}

        # Obtener todos los Service_Plan donde el tipo es 'api' y están activos
        service_plans = Service_Plan.objects.filter(service__tipo='api', isActive=True)

        # Obtener los servicios contratados por el usuario
        user_services = User_Service.objects.filter(idUser=request.user)
        for user_service in user_services:
            service = user_service.idService
            if service.tipo == 'api' and user_service.idServicePlan.isActive:
                if service not in servicios_con_planes:
                    # Incluir plan del usuario si está activo
                    servicios_con_planes[service] = {
                        'plan': user_service.idPlan,  # Plan seleccionado por el usuario
                        'url_servicio': service.url_servicio
                    }

        # Para cada service_plan, añadir los servicios que no tienen planes aún
        for sp in service_plans:
            if sp.service not in servicios_con_planes:
                # Si el usuario no ha contratado un plan para este servicio
                servicios_con_planes[sp.service] = {
                    'plan': None,  # Sin plan seleccionado
                    'url_servicio': 'no activado'  # Sin URL activada
                }

        # Obtener todos los planes disponibles
        todos_los_planes = Plan.objects.all()
    else:
        servicios_con_planes = {}
        todos_los_planes = []

    return render(request, 'console/servicios.html', {'servicios_con_planes': servicios_con_planes, 'planes': todos_los_planes})





def obtener_url_servicio(user_service):
    # Esta función obtiene la URL del servicio desde un objeto User_Service
    return user_service.url_servicio if user_service.idService else ''

def consultar_servicios_api(request):
    if request.user.is_authenticated:
        # Filtrar todos los servicios asociados al usuario actual
        user_services = User_Service.objects.filter(idUser=request.user)

        # Obtener las URLs de servicio para todos los servicios del usuario
        servicios = [
            {
                'user_service': user_service,
                'url_servicio': obtener_url_servicio(user_service)
            }
            for user_service in user_services
        ]
    else:
        servicios = []

    planes = Plan.objects.all()  # Obtener todos los planes
    
    return render(request, 'console/serviciosActivados.html', {'servicios': servicios, 'planes': planes})

###########


def SerActivos(request):
    """Renderiza la página de inicio."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'console/serviciosActivados.html',
        {
            'title': 'ACTIVADOS',
            'year': datetime.datetime.now().year,
        }
    )





##################

def home(request):
    """Renderiza la página de inicio."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'console/index.html',
        {
            'title': 'Página de inicio',
            'year': datetime.datetime.now().year,
        }
    )


    

def activacionBien(request):
    """Renderiza la página de activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'console/activation_success.html',
        {
            'title': 'Página de confirmacion',
            'year': datetime.datetime.now().year,
        }
    )


def activacionMal(request):
    """Renderiza la página de error en la activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'console/activation_failure.html',
        {
            'title': 'Página de error en la activacion',
            'year': datetime.datetime.now().year,
        }
    )

def activacionMalCorreo(request):
    """Renderiza la página de error en el correo."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'console/activation_failure_correo.html',
        {
            'title': 'Página de error en el correo',
            'year': datetime.datetime.now().year,
        }
    )


def activacionMalContrasena(request):
    """Renderiza la página de error en la contrasena."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'console/activation_failure_password.html',
        {
            'title': 'Página de error en la contrasena',
            'year': datetime.datetime.now().year,
        }
    )

def activacionMalUsuarionoregistrado(request):
    """Renderiza la página de error usuario no registrado."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'correo/activation_failure_usuarioRegistrado.html',
        {
            'title': 'Página de error usuario no registrado',
            'year': datetime.datetime.now().year,
        }
    )

def activacionenviada(request):
    """Renderiza la página de error en la activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'console/activation_sent.html',
        {
            'title': 'Página de envio de activacion',
            'year': datetime.datetime.now().year,
        }
    )

def errorLinkreutilizado(request):
    """Renderiza la página de error en la activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'console/link_reutilizado.html',
        {
            'title': 'Página de envio de activacion',
            'year': datetime.datetime.now().year,
        }
    )


def resteoMal(request):
    """Renderiza la página de error en la activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'console/reseteomal.html',
        {
            'title': 'Página de error en restear contraseña',
            'year': datetime.datetime.now().year,
        }
    )


def reseteoBien(request):
    """Renderiza la página de error en la activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'console/reseteobien.html',
        {
            'title': 'Página de restear contraseña',
            'year': datetime.datetime.now().year,
        }
    )

def reseteoEnviado(request):
    """Renderiza la página de error en la activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'console/reseteoEnviado.html',
        {
            'title': 'Página de envio de correo para resetar contraseña',
            'year': datetime.datetime.now().year,
        }
    )









# DDD Y REPOSITORY VINCULADO CON EL DE sesioniniciada(request)
# views.py


def iniciarsesionpartial(request):
    """Renderiza la página de inicio de sesión."""
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        identifier = request.POST['identifier']  # Puede ser username o email
        password = request.POST['password']

        auth_adapter = CustomAuthAdapter()
        user = auth_adapter.authenticate(identifier, password)  # Autenticar al usuario

        if user:
            # Verificar si el usuario está activo
            if user.is_active:
                # Si el usuario es autenticado con éxito y está activo, crea una sesión de usuario en Django.
                request.session['user_id'] = user.username
                return redirect('iniciarsesionpartial')  # Redirige al usuario a la página de inicio de sesión después del inicio de sesión exitoso
            else:
                return redirect('activacionmal')  # Redirige al usuario a la página de activación incorrecta si no está activo
        else:
            # Verificar si el correo es incorrecto
            if not auth_adapter.email_exists(identifier):
                return redirect('activacionmalcorreo')  # Redirige al usuario a la página de correo incorrecto
            else:
                # Usuario no encontrado o contraseña incorrecta
                return redirect('activacionmalcontrasena')  # Redirige al usuario a la página de contraseña incorrecta

    # Si no es un método POST o si la autenticación falla, renderiza la plantilla de inicio de sesión.
    return render(
        request,
        'console/index.html',  # Se debe cambiar el nombre del template a 'iniciarsesionpartial.html' si es necesario
        {
            'title': 'Iniciar Sesión',
            'year': timezone.now().year,
        }
    )


def sesioniniciada(request):
    if request.method == 'POST':
        identifier = request.POST['identifier']  # Puede ser username o email
        password = request.POST['password']
        auth_adapter = CustomAuthAdapter()
        user = auth_adapter.authenticate(identifier, password)
        if user is not None:
            if user.is_active:
                # Verifica si el usuario está activo
                login(request, user)
                return redirect('iniciarsesionpartial')  # Redirige al usuario a la página de inicio de sesión después del inicio de sesión exitoso
            else:
                return redirect('activacionmal')  # Redirige al usuario a la página de activación incorrecta si no está activo
        else:
            # Verificar si el correo es incorrecto
            if not auth_adapter.email_exists(identifier):
                return redirect('activacionmalcorreo')  # Redirige al usuario a la página de correo incorrecto
            else:
                # Usuario no encontrado o contraseña incorrecta
                return redirect('activacionmalcontrasena')  # Redirige al usuario a la página de contraseña incorrecta

    return render(request, 'iniciarsesion.html')





def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        # Verificar si los campos de contraseña están vacíos
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        
        # Expresión regular para verificar que la contraseña tenga al menos 8 caracteres y al menos un número o símbolo
        password_regex = re.compile(r'^(?=.*[0-9!@#$%^&*])(?=.{8,})')

        
        # Inicializar la variable de error en sesión
        request.session['password_error'] = False
    
        if not password1 or not password2:
            form.add_error('password1', 'Los campos de contraseña no pueden estar vacíos.')
            request.session['password_error'] = True
        elif not email:
            form.add_error('email', 'El campo de correo electrónico no puede estar vacío.')
        elif not password_regex.match(password1):
            form.add_error('password1', 'La contraseña debe tener al menos 8 caracteres y contener al menos un número o símbolo.')
            request.session['password_error'] = True
        elif form.is_valid() and not request.session.get('password_error', False):
            if User.objects.filter(email=email).exists():  # Verificar si el correo electrónico ya existe
                form.add_error('email', 'Este correo electrónico ya está registrado.')  # Agregar error al formulario
            else:
                user = form.save(commit=False)
                user.is_active = False  # Desactivar al usuario hasta que haga clic en el enlace de activación
                
                # Asignar el correo electrónico completo como nombre de usuario
                user.username = email
                
                # Guardar el usuario
                user.save()

                # Enviar correo electrónico de activación
                send_activation_email(request, user)

                # Eliminar indicador de error de sesión
                request.session.pop('password_error', None)

                return redirect('activacionenviada')  # Redirigir a una página de éxito después de registrar al usuario
    else:
        form = CustomUserCreationForm()
        # Limpiar la variable de error al cargar la página nuevamente
        request.session.pop('password_error', None)

    return render(request, 'console/register.html', {'form': form})

def generate_unique_username(email):
    base_username = email.split('@')[0]
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            free_plan = Plan.objects.get(nombre='FREE')
            invoice_service = Service.objects.get(nombre='Invoice stamping') 


         
            # Activar la cuenta del usuario
            invoice_group, created = Group.objects.get_or_create(name='invoice')
            if not user.groups.filter(name='invoice').exists():
                user.groups.add(invoice_group)
            user.is_active = True
            user.save()

            return redirect('activacionbien')  # Redirigir a la página de activación exitosa
        else:
            return redirect('activacionmal')  # El usuario ya está activado
    else:
        return redirect('errorLinkreutilizado')  # Token inválido o usuario no encontrado

def send_activation_email(request,user):
    
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = reverse('activate_account', kwargs={'uidb64': uidb64, 'token': token})
    current_host = request.get_host()
    activation_link = f"http://{current_host}{activation_link}"
    email_subject = 'Activa tu cuenta'
    email_body = f'Hola {user.email}, Por favor, utiliza el siguiente enlace para activar tu cuenta: {activation_link}'
    send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)





#############################################################


from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect

from django.urls import reverse

def generate_unique_token_for_user(user):
    # Genera un token único para el usuario
    return hashlib.sha256(f'{user.pk}{user.email}{random.random()}{timezone.now()}'.encode()).hexdigest()


def send_resetPassword_email(request,user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    resetPassword_link = reverse('resetPassword_account', kwargs={'uidb64': uidb64, 'token': token})
    current_host = request.get_host()
    resetPassword_link = f"http://{current_host}{resetPassword_link}"
    email_subject = 'Restablece tu cuenta'
    email_body = f'Hola {user.email}, Por favor, utiliza el siguiente enlace para restablece la clave tu cuenta: {resetPassword_link}'
    send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)




def restablecer_password(request):
    form = SendEmailResetPasswordForm()  # Movido fuera del bloque 'else'
    if request.method == 'POST':
        form = SendEmailResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            if user is not None:
                # Generar token
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                
                # Enviar correo con el enlace para restablecer contraseña
                resetPassword_link = reverse('resetPassword_account', kwargs={'uidb64': uidb64, 'token': token})
                current_host = request.get_host()
                resetPassword_link = f"http://{current_host}{resetPassword_link}"
                email_subject = 'Restablece tu contraseña'
                email_body = f'Hola {user.email}, Por favor, utiliza el siguiente enlace para restablecer tu contraseña: {resetPassword_link}'
                send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

                return redirect('reseteo_enviada')
            else:
                form.add_error('email', 'Este correo electrónico no está registrado.')
    return render(request, 'console/reseteo_password.html', {'form': form})



def resetPassword_account(request, uidb64, token):
    if request.method == 'POST':
        form = ResetPasswordForm2(request.POST)
        
        if form.is_valid():
            password = form.cleaned_data.get('password')
            password2 = form.cleaned_data.get('password2')
            
            # Expresión regular para validar que la contraseña tenga al menos 8 caracteres y contenga al menos un número o símbolo
            password_regex = re.compile(r'^(?=.*[0-9!@#$%^&*])(?=.{8,})')

            # Verificar si los campos de contraseña están vacíos
            if not password or not password2:
                form.add_error('password', 'Los campos de contraseña no pueden estar vacíos.')
            # Verificar si las contraseñas coinciden
            elif password != password2:
                form.add_error('password2', 'Las contraseñas no coinciden.')
            # Verificar si la contraseña cumple con los requisitos
            elif not password_regex.match(password):
                form.add_error('password', 'La contraseña debe tener al menos 8 caracteres y contener al menos un número o símbolo.')
            else:
                # Si la validación es correcta, proceder con la validación del usuario y token
                try:
                    uid = force_text(urlsafe_base64_decode(uidb64))
                    user = User.objects.get(pk=uid)
                except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                    user = None

                if user is not None and default_token_generator.check_token(user, token):
                    # Cambiar la contraseña del usuario
                    user.set_password(password)
                    user.save()
                    update_session_auth_hash(request, user)
                    return redirect('reseteobien')
                else:
                    return redirect('reseteomal')
        
        # Si hay errores en el formulario, se vuelven a mostrar en el template
        return render(request, 'console/form_reset_password.html', {'form': form})
    
    else:
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = ResetPasswordForm2()
            return render(request, 'console/form_reset_password.html', {'form': form})
        else:
            return redirect('reseteomal')

    return render(request, 'console/form_reset_password.html', {'form': form})

#############################################################################333333




def cerrarsesion(request):
    """Cierra la sesión del usuario y redirige a la página de inicio."""
    assert isinstance(request, HttpRequest)
    logout(request)  # Cierra la sesión del usuario
    return redirect('inicio')  # Redirige al usuario a la página de inicio de la app console






def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'console/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year': datetime.datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'console/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year': datetime.datetime.now().year,
        }
    )


#######################################################################

# @login_required
# def seleccion_servicio(request):
#     if request.method == 'POST':
#         # Obtener parámetros del formulario y datos relacionados
#         id_servicio = request.POST.get('service_id')
#         plan_id = request.POST.get('plan_id')
#         usuario = request.user

#         servicio = get_object_or_404(Service, id=id_servicio)
#         plan = get_object_or_404(Plan, id=plan_id) if plan_id else None

#         # Verificar si el usuario ya tiene un servicio activo
#         user_service = User_Service.objects.filter(idUser=usuario, idService=servicio).first()

#         if user_service:
#             # Actualizar servicio y plan del usuario
#             current_plan = user_service.idPlan
#             user_service.idPlan = plan
#             user_service.idServicePlan = Service_Plan.objects.filter(
#                 service=servicio, plan=plan, isActive=True
#             ).first()
#             user_service.date_cutoff = timezone.now().date() + timedelta(days=30)
#             user_service.aceptarTerminos = True
#             user_service.save()
#         else:
#             # Crear un nuevo servicio para el usuario
#             user_service = User_Service.objects.create(
#                 idService=servicio,
#                 idPlan=plan,
#                 aceptarTerminos=True,
#                 idServicePlan=Service_Plan.objects.filter(service=servicio, plan=plan, isActive=True).first(),
#                 idUser=usuario,
#                 date_cutoff=timezone.now().date() + timedelta(days=30)
#             )

#         # Verificar si el perfil fiscal del usuario existe y tiene RFC
#         perfil_fiscal = PerfilFiscalUser.objects.filter(user=usuario).first()
#         if not perfil_fiscal or not perfil_fiscal.rfc:
#             # Si el plan seleccionado requiere RFC, detener el proceso y enviar un correo
#             if plan.nombre in ['PRO', 'Enterprise']:
#                 pdf_path = os.path.join(settings.BASE_DIR, 'console/static/console/pdf/pasosContrato.pdf')                                                      
#                 perfil_url = reverse('invoice:perfilpreferencias')
#                 current_host = request.get_host()
#                 perfil_link = f"http://{current_host}{perfil_url}"

#                 # Renderizar la plantilla de correo electrónico HTML
#                 context = {
#                     'title': 'Actualización de tu servicio',
#                     'message': f'Hola {usuario.email}, por favor accede a tus preferencias de perfil a través del siguiente enlace: {perfil_link}',
#                 }
               

#                 # Crear el correo con adjunto usando EmailMultiAlternatives
#                 email_subject = 'Actualización de tu servicio'
#                 email_body = f'Hola {usuario.email}, por favor accede a tus preferencias de perfil a través del siguiente enlace: {perfil_link}'

#                 email = EmailMultiAlternatives(
#                     email_subject,
#                     email_body,  # Texto en formato plano
#                     settings.DEFAULT_FROM_EMAIL,
#                     [usuario.email],
#                 )
                
#                 # Adjuntar el contenido HTML renderizado
              
                
#                 # Adjuntar el archivo PDF
#                 with open(pdf_path, 'rb') as f:
#                     email.attach('pasosContrato.pdf', f.read(), 'application/pdf')

#                 email.send(fail_silently=False)

#                 return JsonResponse({
#                     'success': True, 
#                     'message': 'Plan seleccionado correctamente. Consulta el servicio que adquiriste en el boton de -Consultar servicios contratados-', 
#                     'service_url': servicio.url_servicio
#                 })
#         else:
#             # Procesar el perfil fiscal si existe
#             rfc = perfil_fiscal.rfc    
#             if plan.tipo == 'bajo consumo':
#                 perfil_fiscal.tipoCliente = 'O'  # On-Demand
#             else:
#                 perfil_fiscal.tipoCliente = 'P'  # Prepagado
#             perfil_fiscal.save()

#             # Manejar el perfil de timbre si el usuario tiene RFC
#             timbre_anterior = TimbreUserPerfil.objects.filter(
#                 userInvoice=usuario, estatus='A'
#             ).first()
#             if timbre_anterior:
#                 timbre_anterior.estatus = 'S'
#                 timbre_anterior.save()

#             # Asignar nuevos créditos y crear nuevo TimbreUserPerfil
#             nuevo_stamp = plan.limite_operaciones_plan
#             TimbreUserPerfil.objects.create(
#                 userInvoice=usuario,
#                 idUser_ServicePlan=user_service,
#                 stamp=nuevo_stamp,
#                 estatus='A',
#                 isOnDemmand=(plan.tipo == 'Bajo consumo' or plan.tipo == 'bajo consumo')
#             )
#          # Agregar usuario a un grupo con el nombre del servicio
#         nombre_grupo = servicio.nombre  # Suponiendo que 'nombre' es un atributo del modelo Service
#         grupo, created = Group.objects.get_or_create(name=nombre_grupo)
#         usuario.groups.add(grupo)

#         servicio_url = obtener_url_servicio(user_service)


#         if servicio == "Invoice stamping":
       
#             pdf_path = os.path.join(settings.BASE_DIR, 'console/static/console/pdf/pasosContrato.pdf')
#             perfil_url = reverse('invoice:perfilpreferencias')
#             current_host = request.get_host()
#             perfil_link = f"http://{current_host}{perfil_url}"

    

#             email_subject = 'Actualización de tu servicio'
#             email_body = f'Hola {usuario.email}, por favor accede a tus preferencias de perfil a través del siguiente enlace: {perfil_link}'

#             email = EmailMultiAlternatives(
#                 email_subject,
#                 email_body,  # Texto en formato plano
#                 settings.DEFAULT_FROM_EMAIL,
#                 [usuario.email],
#             )

#             # Adjuntar el archivo PDF
#             with open(pdf_path, 'rb') as f:
#                 email.attach('pasosContrato.pdf', f.read(), 'application/pdf')

#         else:
#     # Enviar correo sin archivo adjunto y con la URL del servicio en lugar del perfil link
#                 current_host = request.get_host()
#                 servicio_link = f"http://{current_host}{servicio_url}"
#                 email_subject = 'Actualización de tu servicio'
#                 email_body = f'Hola {usuario.email}, puedes acceder al servicio que adquiriste en el siguiente enlace: {servicio_link}'

#                 email = EmailMultiAlternatives(
#                     email_subject,
#                     email_body,  # Texto en formato plano
#                     settings.DEFAULT_FROM_EMAIL,
#                     [usuario.email],
#                 )

#                 email.send(fail_silently=False)
#         return JsonResponse({
#             'success': True, 
#             'message': 'Plan seleccionado correctamente. Consulta el servicio que adquiriste en el boton de -Consultar servicios contratados-', 
#             'service_url': servicio.url_servicio
#         })

#     # Obtener y renderizar los servicios disponibles
#     servicios = Service.objects.all()
#     return render(request, 'servicios.html', {'servicios': servicios})




def obtener_url_servicio(user_service):
    servicio = user_service.idService
    return servicio.url_servicio if servicio.url_servicio else "/"


# @login_required
# def seleccion_servicio(request):
#     if request.method == 'POST':
#         id_servicio = request.POST.get('service_id')
#         plan_id = request.POST.get('plan_id')
#         usuario = request.user

#         servicio = get_object_or_404(Service, id=id_servicio)
#         plan = get_object_or_404(Plan, id=plan_id) if plan_id else None

#         user_service = User_Service.objects.filter(idUser=usuario, idService=servicio).first()

#         if user_service:
#             current_plan = user_service.idPlan
#             user_service.idPlan = plan
#             user_service.idServicePlan = Service_Plan.objects.filter(
#                 service=servicio, plan=plan, isActive=True
#             ).first()
#             user_service.date_cutoff = timezone.now().date() + timedelta(days=30)
#             user_service.aceptarTerminos = True
#             user_service.save()
#         else:
#             user_service = User_Service.objects.create(
#                 idService=servicio,
#                 idPlan=plan,
#                 aceptarTerminos=True,
#                 idServicePlan=Service_Plan.objects.filter(service=servicio, plan=plan, isActive=True).first(),
#                 idUser=usuario,
#                 date_cutoff=timezone.now().date() + timedelta(days=30)
#             )

#         perfil_fiscal = PerfilFiscalUser.objects.filter(user=usuario).first()
#         if not perfil_fiscal or not perfil_fiscal.rfc:
#          if plan.nombre in ['PRO', 'Enterprise']:
#             current_host = request.get_host()
#             servicio_nombre = servicio.nombre.lower()

#             # URL personalizada por nombre del servicio
#             if servicio_nombre == "cfdi":
#                 perfil_link = f"http://{current_host}/cfdi"
#             elif servicio_nombre == "invoice stamping":
#                 perfil_link = f"http://{current_host}/invoice/perfil_pref/"
#             else:
#                 perfil_link = f"http://{current_host}/"

#             email_subject = 'Actualización de tu servicio'
#             email_body = f'Hola {usuario.email}, por favor accede a tu servicio a través del siguiente enlace: {perfil_link}'

#             email = EmailMultiAlternatives(
#                 email_subject,
#                 email_body,
#                 settings.DEFAULT_FROM_EMAIL,
#                 [usuario.email],
#             )

#             # ✅ Solo se adjunta el PDF si el servicio es Invoice Stamping
#             if servicio_nombre == "invoice stamping":
#                 pdf_path = os.path.join(settings.BASE_DIR, 'console/static/console/pdf/pasosContrato.pdf')
#                 with open(pdf_path, 'rb') as f:
#                     email.attach('pasosContrato.pdf', f.read(), 'application/pdf')

#             email.send(fail_silently=False)

#             return JsonResponse({
#                 'success': True,
#                 'message': 'Plan seleccionado correctamente. Consulta el servicio que adquiriste en el botón de -Consultar servicios contratados-',
#                 'service_url': perfil_link
#             })



#         else:
#             rfc = perfil_fiscal.rfc    
#             if plan.tipo == 'bajo consumo':
#                 perfil_fiscal.tipoCliente = 'O'
#             else:
#                 perfil_fiscal.tipoCliente = 'P'
#             perfil_fiscal.save()

#             timbre_anterior = TimbreUserPerfil.objects.filter(
#                 userInvoice=usuario, estatus='A'
#             ).first()
#             if timbre_anterior:
#                 timbre_anterior.estatus = 'S'
#                 timbre_anterior.save()

#             nuevo_stamp = plan.limite_operaciones_plan
#             TimbreUserPerfil.objects.create(
#                 userInvoice=usuario,
#                 idUser_ServicePlan=user_service,
#                 stamp=nuevo_stamp,
#                 estatus='A',
#                 isOnDemmand=(plan.tipo == 'Bajo consumo' or plan.tipo == 'bajo consumo')
#             )

#         nombre_grupo = servicio.nombre
#         grupo, created = Group.objects.get_or_create(name=nombre_grupo)
#         usuario.groups.add(grupo)

#         # ✅ URL del servicio correcta
#         servicio_url = obtener_url_servicio(user_service)
#         current_host = request.get_host()
#         servicio_link = f"http://{current_host}{servicio_url}"

#         # Enviar correo con link al servicio
#         email_subject = 'Actualización de tu servicio'
#         email_body = f'Hola {usuario.email}, puedes acceder al servicio que adquiriste en el siguiente enlace: {servicio_link}'

#         email = EmailMultiAlternatives(
#             email_subject,
#             email_body,
#             settings.DEFAULT_FROM_EMAIL,
#             [usuario.email],
#         )

#         email.send(fail_silently=False)

#         return JsonResponse({
#             'success': True, 
#             'message': 'Plan seleccionado correctamente. Consulta el servicio que adquiriste en el botón de -Consultar servicios contratados-', 
#             'service_url': servicio_url
#         })

#     servicios = Service.objects.all()
#     return render(request, 'servicios.html', {'servicios': servicios})


@login_required
def seleccion_servicio(request):
    if request.method == 'POST':
        id_servicio = request.POST.get('service_id')
        plan_id = request.POST.get('plan_id')
        usuario = request.user

        servicio = get_object_or_404(Service, id=id_servicio)
        plan = get_object_or_404(Plan, id=plan_id) if plan_id else None

        user_service = User_Service.objects.filter(idUser=usuario, idService=servicio).first()

        if user_service:
            user_service.idPlan = plan
            user_service.idServicePlan = Service_Plan.objects.filter(
                service=servicio, plan=plan, isActive=True
            ).first()
            user_service.date_cutoff = timezone.now().date() + timedelta(days=30)
            user_service.aceptarTerminos = True
            user_service.save()
        else:
            user_service = User_Service.objects.create(
                idService=servicio,
                idPlan=plan,
                aceptarTerminos=True,
                idServicePlan=Service_Plan.objects.filter(service=servicio, plan=plan, isActive=True).first(),
                idUser=usuario,
                date_cutoff=timezone.now().date() + timedelta(days=30)
            )

        perfil_fiscal = PerfilFiscalUser.objects.filter(user=usuario).first()

        # ✅ Si no hay RFC y el plan requiere uno
        if not perfil_fiscal or not perfil_fiscal.rfc:
            if plan.nombre in ['PRO', 'Enterprise']:
                current_host = request.get_host()
                servicio_link = servicio.get_full_url(current_host)

                email_subject = 'Actualización de tu servicio'
                email_body = f'Hola {usuario.email}, por favor accede a tu servicio a través del siguiente enlace: {servicio_link}'

                email = EmailMultiAlternatives(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [usuario.email],
                )

                # ✅ Solo adjuntar PDF si el servicio lo permite
                if servicio.enviar_pdf:
                    pdf_path = os.path.join(settings.BASE_DIR, 'console/static/console/pdf/pasosContrato.pdf')
                    with open(pdf_path, 'rb') as f:
                        email.attach('pasosContrato.pdf', f.read(), 'application/pdf')

                email.send(fail_silently=False)

                return JsonResponse({
                    'success': True,
                    'message': 'Plan seleccionado correctamente. Consulta el servicio que adquiriste en el botón de -Consultar servicios contratados-',
                    'service_url': servicio_link
                })

        else:
            # ✅ Procesar perfil fiscal y asignar timbres
            if plan.tipo == 'bajo consumo':
                perfil_fiscal.tipoCliente = 'O'
            else:
                perfil_fiscal.tipoCliente = 'P'
            perfil_fiscal.save()

            timbre_anterior = TimbreUserPerfil.objects.filter(userInvoice=usuario, estatus='A').first()
            if timbre_anterior:
                timbre_anterior.estatus = 'S'
                timbre_anterior.save()

            TimbreUserPerfil.objects.create(
                userInvoice=usuario,
                idUser_ServicePlan=user_service,
                stamp=plan.limite_operaciones_plan,
                estatus='A',
                isOnDemmand=(plan.tipo.lower() == 'bajo consumo')
            )

        # ✅ Asignar grupo según nombre del servicio
        grupo, _ = Group.objects.get_or_create(name=servicio.nombre)
        usuario.groups.add(grupo)

        # ✅ Enviar correo final con link del servicio
        servicio_link = servicio.get_full_url(request.get_host())

        email_subject = 'Actualización de tu servicio'
        email_body = f'Hola {usuario.email}, puedes acceder al servicio que adquiriste en el siguiente enlace: {servicio_link}'

        email = EmailMultiAlternatives(
            email_subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email],
        )

        # ✅ Adjuntar PDF si aplica en este correo final también
        if servicio.enviar_pdf:
            pdf_path = os.path.join(settings.BASE_DIR, 'console/static/console/pdf/pasosContrato.pdf')
            with open(pdf_path, 'rb') as f:
                email.attach('pasosContrato.pdf', f.read(), 'application/pdf')

        email.send(fail_silently=False)

        return JsonResponse({
            'success': True,
            'message': 'Plan seleccionado correctamente. Consulta el servicio que adquiriste en el botón de -Consultar servicios contratados-',
            'service_url': servicio_link
        })

    servicios = Service.objects.all()
    return render(request, 'servicios.html', {'servicios': servicios})









#eliminar

@login_required
def eliminar_servicio(request):
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        usuario = request.user
        password = request.POST.get('password')

        # Buscar y eliminar la asociación del usuario con el servicio especificado
        try:
            # Primero eliminar los objetos relacionados en TimbreUserPerfil
            TimbreUserPerfil.objects.filter(userInvoice=usuario).delete()

            # Eliminar el perfil fiscal del usuario
            PerfilFiscalUser.objects.filter(user=usuario).delete()

            # Luego eliminar la asociación entre el usuario y el servicio
            user_service = User_Service.objects.get(idUser=usuario, idService_id=service_id)
            servicio = user_service.idService

            user = authenticate(username=request.user.username, password=password)
            if user is None:
                return JsonResponse({'error': 'Contraseña incorrecta'}, status=400)




            user_service.delete()

            # Verificar si el servicio eliminado es 'Invoice stamping' para eliminar al usuario del grupo 'invoice'
            if servicio.nombre == 'Invoice stamping':
                try:
                    group = Group.objects.get(name='invoice')
                    usuario.groups.remove(group)
                except Group.DoesNotExist:
                    return JsonResponse({'error': 'El grupo "invoice" no existe.'}, status=404)
                
            if servicio.nombre == 'CFDI':
                try:
                    group = Group.objects.get(name='cfdi')
                    usuario.groups.remove(group)
                except Group.DoesNotExist:
                    return JsonResponse({'error': 'El grupo "cfdi" no existe.'}, status=404)

            ####################################################################################################

            return JsonResponse({'success': True})
        except User_Service.DoesNotExist:
            return JsonResponse({'error': 'No se encontró el servicio asociado al usuario.'}, status=404)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)
######################################################################

def some_view(request):
    # The variables needed are URL and HEADERS everything 
    # else is extra that you might need for your request
    client = SOAPClient(
        url='http://www.dneonline.com/calculator.asmx?wsdl',
        headers = {'content-type': 'application/soap+xml'}
    )

    # Load up your crafted XML template from your /templates folder
    # with the values it expects
    response = client.send_request('soap_request/test.xml', {'intA': 2, 'intB': 2})

    # The response is of SoapResult and you can get your items like
    value = (
        response
            .get('soap:Envelope')
            .get('soap:Body')
            .get('AddResponse')
            .get_value('AddResult')
    )
    return render(request,
                  'console/test_soap_client.html',
                  {'value': value}
                  )





class Incidencia(ComplexModel):
    _type_info = [
        ('IdIncidencia', String),
        ('RfcEmisor', String),
        ('Uuid', String),
        ('CodigoError', String),
        ('WorkProcessId', String),
        ('MensajeIncidencia', String),
        ('ExtraInfo', String),
        ('NoCertificadoPac', String),
        ('FechaRegistro', String),
    ]
    


class AcuseRecepcionCFDI(ComplexModel):
    _type_info = [
        ('xml', String),
        ('UUID', String),
        ('faultstring', String),
        ('Fecha', String),
        ('CodEstatus', String),
        ('faultcode', String),
        ('SatSeal', String),
        ('Incidencias', Array(Incidencia)),
        ('NoCertificadoSAT', String),
     
    ]
    
