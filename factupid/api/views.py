from rest_framework import viewsets
from console.models import Customer, SelectedService, Service, Service_Plan, SupplierStamp, Plan, Post, User_Service
from .serializers import *
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from console.models import Service, Plan, User_Service, Service_Plan
from console.views import obtener_url_servicio
from invoice.models import PerfilFiscalUser, TimbreUserPerfil
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
import os

# ViewSets app Console
class UserServiceViewSet(viewsets.ModelViewSet):
    serializer_class = UserServiceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = User_Service.objects.all()

    def get_queryset(self):
        """ Filtrar User_Service para devolver solo los registros del usuario autenticado. """
        return User_Service.objects.filter(idUser=self.request.user)

class ServicePlanViewSet(viewsets.ModelViewSet):
    serializer_class = ServicePlanSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Service_Plan.objects.all()
    
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    

class SeleccionServicioAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Obtener parámetros del formulario y datos relacionados
        id_servicio = request.data.get('service_id')
        plan_id = request.data.get('plan_id')
        usuario = request.user

        servicio = get_object_or_404(Service, id=id_servicio)
        plan = get_object_or_404(Plan, id=plan_id) if plan_id else None

        # Verificar si el usuario ya tiene un servicio activo
        user_service = User_Service.objects.filter(idUser=usuario, idService=servicio).first()

        if user_service:
            # Actualizar servicio y plan del usuario
            current_plan = user_service.idPlan
            user_service.idPlan = plan
            user_service.idServicePlan = Service_Plan.objects.filter(
                service=servicio, plan=plan, isActive=True
            ).first()
            user_service.date_cutoff = timezone.now().date() + timedelta(days=30)
            user_service.aceptarTerminos = True
            user_service.save()
        else:
            # Crear un nuevo servicio para el usuario
            user_service = User_Service.objects.create(
                idService=servicio,
                idPlan=plan,
                aceptarTerminos=True,
                idServicePlan=Service_Plan.objects.filter(service=servicio, plan=plan, isActive=True).first(),
                idUser=usuario,
                date_cutoff=timezone.now().date() + timedelta(days=30)
            )

        # Verificar si el perfil fiscal del usuario existe y tiene RFC
        perfil_fiscal = PerfilFiscalUser.objects.filter(user=usuario).first()
        if not perfil_fiscal or not perfil_fiscal.rfc:
            # Si el plan seleccionado requiere RFC, detener el proceso y enviar un correo
            if plan.nombre in ['PRO', 'Enterprise']:
                pdf_path = os.path.join(settings.BASE_DIR, 'console/static/console/pdf/pasosContrato.pdf')                                                      
                perfil_url = reverse('invoice:perfilpreferencias')
                current_host = request.get_host()
                perfil_link = f"http://{current_host}{perfil_url}"

                # Renderizar la plantilla de correo electrónico HTML
                context = {
                    'title': 'Actualización de tu servicio',
                    'message': f'Hola {usuario.email}, por favor accede a tus preferencias de perfil a través del siguiente enlace: {perfil_link}',
                }

                # Crear el correo con adjunto usando EmailMultiAlternatives
                email_subject = 'Actualización de tu servicio'
                email_body = f'Hola {usuario.email}, por favor accede a tus preferencias de perfil a través del siguiente enlace: {perfil_link}'

                email = EmailMultiAlternatives(
                    email_subject,
                    email_body,  # Texto en formato plano
                    settings.DEFAULT_FROM_EMAIL,
                    [usuario.email],
                )
                
                # Adjuntar el contenido HTML renderizado
                
                # Adjuntar el archivo PDF
                with open(pdf_path, 'rb') as f:
                    email.attach('pasosContrato.pdf', f.read(), 'application/pdf')

                email.send(fail_silently=False)

                return Response({
                    'success': True, 
                    'message': 'Plan seleccionado correctamente. Consulta el servicio que adquiriste en el boton de -Consultar servicios contratados-', 
                    'service_url': servicio.url_servicio
                }, status=status.HTTP_200_OK)
        else:
            # Procesar el perfil fiscal si existe
            rfc = perfil_fiscal.rfc    
            if plan.tipo == 'bajo consumo':
                perfil_fiscal.tipoCliente = 'O'  # On-Demand
            else:
                perfil_fiscal.tipoCliente = 'P'  # Prepagado
            perfil_fiscal.save()

            # Manejar el perfil de timbre si el usuario tiene RFC
            timbre_anterior = TimbreUserPerfil.objects.filter(
                userInvoice=usuario, estatus='A'
            ).first()
            if timbre_anterior:
                timbre_anterior.estatus = 'S'
                timbre_anterior.save()

            # Asignar nuevos créditos y crear nuevo TimbreUserPerfil
            nuevo_stamp = plan.limite_operaciones_plan
            TimbreUserPerfil.objects.create(
                userInvoice=usuario,
                idUser_ServicePlan=user_service,
                stamp=nuevo_stamp,
                estatus='A',
                isOnDemmand=(plan.tipo == 'Bajo consumo' or plan.tipo == 'bajo consumo')
            )

        # Agregar usuario a un grupo con el nombre del servicio
        nombre_grupo = servicio.nombre  # Suponiendo que 'nombre' es un atributo del modelo Service
        grupo, created = Group.objects.get_or_create(name=nombre_grupo)
        usuario.groups.add(grupo)

        servicio_url = obtener_url_servicio(user_service)

        if servicio.nombre == "Invoice stamping":
            pdf_path = os.path.join(settings.BASE_DIR, 'console/static/console/pdf/pasosContrato.pdf')
            perfil_url = reverse('invoice:perfilpreferencias')
            current_host = request.get_host()
            perfil_link = f"http://{current_host}{perfil_url}"

            email_subject = 'Actualización de tu servicio'
            email_body = f'Hola {usuario.email}, por favor accede a tus preferencias de perfil a través del siguiente enlace: {perfil_link}'

            email = EmailMultiAlternatives(
                email_subject,
                email_body,  # Texto en formato plano
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
            )

            # Adjuntar el archivo PDF
            with open(pdf_path, 'rb') as f:
                email.attach('pasosContrato.pdf', f.read(), 'application/pdf')

        else:
            # Enviar correo sin archivo adjunto y con la URL del servicio en lugar del perfil link
            current_host = request.get_host()
            servicio_link = f"http://{current_host}{servicio_url}"
            email_subject = 'Actualización de tu servicio'
            email_body = f'Hola {usuario.email}, puedes acceder al servicio que adquiriste en el siguiente enlace: {servicio_link}'

            email = EmailMultiAlternatives(
                email_subject,
                email_body,  # Texto en formato plano
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
            )

        email.send(fail_silently=False)
        return Response({
            'success': True, 
            'message': 'Plan seleccionado correctamente. Consulta el servicio que adquiriste en el boton de -Consultar servicios contratados-', 
            'service_url': servicio.url_servicio
        }, status=status.HTTP_200_OK)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated,DjangoModelPermissions]

class SelectedServiceViewSet(viewsets.ModelViewSet):
    queryset = SelectedService.objects.all()
    serializer_class = SelectedServiceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
class SupplierStampViewSet(viewsets.ModelViewSet):
    queryset = SupplierStamp.objects.all()
    serializer_class = SupplierStampSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


# viewsets para los modelos de permisos y grupos de Django
class UserPermissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def list(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)