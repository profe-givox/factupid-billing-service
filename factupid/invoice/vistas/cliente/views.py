from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from invoice.views import ResellerUser, customersResponse
from invoice.vistas.user.register import ResellerUserArray
from invoice.models import Cliente, User_Cliente, Tokens, Timbre,TimbreUserPerfil, Contratos
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings 
from console.models import SupplierStamp
from invoice.forms import ClientForm, ClientMoralForm, ClientFisicoForm, ClientExtranjeroForm, PerfilMoralForm,PerfilFisicoForm,RegimenFiscalForm, TokensForm, TokensResetForm, TokensUPdateForm
from invoice.models import  PerfilFiscalUser
from console.models import User_Service, Service_Plan

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.models import User, Group
from django.http import JsonResponse, HttpResponse
import json
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.views.generic import DetailView

import base64
from invoice.vistas.user import register
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from datetime import datetime
import xml.etree.ElementTree as ET

from django.db.models import OuterRef, Subquery
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Prefetch
from django.db import transaction
import concurrent.futures
from django.db import transaction
from datetime import datetime # Importa timezone para obtener la fecha actual
from invoice.mixins import PlanAndGroupRequiredMixin, PerfilFiscalRequiredMixin
from decouple import config


@require_POST
def add_timbre(request):
    try:
        data = json.loads(request.body)
        user_cliente_id = data.get('user_cliente')
        stamp = data.get('facturas')

        if not user_cliente_id or stamp is None:
            return JsonResponse({'error': 'Datos inválidos'}, status=400)

        try:
            user_cliente = User_Cliente.objects.get(id=user_cliente_id)
        except User_Cliente.DoesNotExist:
            return JsonResponse({'error': 'Usuario cliente no encontrado'}, status=404)

        try:
            # Iniciar transacción atómica
            with transaction.atomic():
                # Convertir facturas a entero
                stamp = int(stamp)
                # Timbres de usuario
                # Obtener la instancia de Usuario asociada al usuario logueado
                print('stamp',request.user.id)
                usuario =  PerfilFiscalUser.objects.get(user=request.user)

                print('usuario',usuario)
                # Obtener el último registro de TimbreUserPerfil para el usuario
                ultimo_registro = TimbreUserPerfil.objects.get(userInvoice=request.user, estatus='A')
                print('timbre user---', ultimo_registro)

                #obtener el user_service
                # asegurar que el servicio invoice este y su id para que diferencie los servicios
                user_services = User_Service.objects.get(idUser=request.user, idService__nombre="Invoice stamping")
                print('service:',user_services)
                # Obtén los Service_Plan relacionados con el usuario logueado
                service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()
                print('service plan:',service_plans.id)

                
                # if usuario.tipoCliente == 'O':
                #     timbreUser = TimbreUserPerfil(userInvoice=request.user, idUser_ServicePlan=user_services, stamp=ultimo_registro.stamp, isOnDemmand=True)
                if usuario.tipoCliente == 'P':
                    # Calcular la nueva cantidad de facturas para el nuevo registro
                    nueva_cantidad_facturas = ultimo_registro.stamp if ultimo_registro else 0

                    if stamp > 0:
                        nueva_cantidad_facturas -= stamp
                    else:
                        nueva_cantidad_facturas += abs(stamp)  # Sumar la cantidad de facturas si es negativa

                    print ('tipo de usuario',usuario.tipoCliente)
                    print('nueva cantidad',nueva_cantidad_facturas)

                    timbreUser = TimbreUserPerfil(userInvoice=request.user, idUser_ServicePlan=user_services, stamp=nueva_cantidad_facturas)

                    print('tipouser isondemand',timbreUser.isOnDemmand)
                else:
                    timbreUser = TimbreUserPerfil.objects.filter(userInvoice=request.user, estatus='A').first()

                print('prueba')
                #Si el timbre es ondemant no se llama el clean el modelo para realizar la validacion y asignacion en el web service
                if not timbreUser.isOnDemmand:
                    print('validaciones timbre user')
                    timbreUser.full_clean()  # Ejecuta todas las validaciones
                
                    print('timbre user creado', timbreUser)
                    #Se guarda el nuevo timbre
                    # Guardar el nuevo TimbreUserPerfil
                    try:
                        timbreUser.save()
                        print('TimbreUserPerfil creado y guardado con éxito:', timbreUser)
                        #Cambiar la bitacaro actual a suspendida
                        ultimo_registro.estatus = 'S'
                        #Guardar la bitacora suspendida
                        ultimo_registro.save()
                    except Exception as e:
                        print("Error al guardar TimbreUserPerfil:", e)

                print('timbre cliente')
                # Timbres de cliente
                print('cliente',user_cliente.idCliente)
                # Obtener el cliente
                cliente = Cliente.objects.get(id=user_cliente.idCliente.id)
                print(cliente)
                #Obatener la bitacora Timbre actuamente activa
                actualTimbre = Timbre.objects.get(user_cliente=user_cliente, estatus = 'A')
                print('timbre', actualTimbre)

                print (cliente.tipoCliente)
                # if cliente.tipoCliente == 'O':
                #     timbre = Timbre(user_cliente=user_cliente, stamp=int(actualTimbre.stamp) + int(stamp), isOnDemmand=True)
                if cliente.tipoCliente == 'P':
                    timbre = Timbre(user_cliente=user_cliente, stamp=int(actualTimbre.stamp) + int(stamp), cont_stamped_cliente=actualTimbre.cont_stamped_cliente)
                    print('nueva cantidad',timbre.stamp)
                    #Si el timbre es ondemant no se llama el clean el modelo para realizar la validacion y asignacion en el web service
                    print(timbre.isOnDemmand)
                    if timbre.isOnDemmand == False:
                        timbre.full_clean()  # Ejecuta todas las validaciones
                    
                        #Se guarda el nuevo timbre
                        timbre.save()

                        #Cambiar la bitacaro actual a suspendida
                        actualTimbre.estatus = 'S'
                        #Guardar la bitacora suspendida
                        actualTimbre.save()


                return JsonResponse({'message': 'Timbre creado con éxito'})
        except ValidationError as e:
            return JsonResponse({'error': e.message_dict}, status=400)


    except ValidationError as e:
        return JsonResponse({'error': e.message_dict}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error en el formato de datos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



    
    
def timbres_cliente(request, cliente_id):
    try:
        # Obtener el User_Cliente correspondiente
        user_cliente = User_Cliente.objects.get(idCliente_id=cliente_id, idUser=request.user)
    except User_Cliente.DoesNotExist:
        return HttpResponse(f"No se encontró User_Cliente para cliente_id={cliente_id} y user_id={request.user.id}", status=404)
    
    # Obtener los Timbres relacionados con este User_Cliente
    timbres = Timbre.objects.filter(user_cliente=user_cliente)
    
    # Si no hay timbres asociados, devolver una respuesta vacía
    if not timbres.exists():
        return JsonResponse({'timbres': []})

    # Preparar los datos para el JSON
    timbres_data = [{
        'fecha': timbre.fecha.strftime('%Y-%m-%d %H:%M:%S'),
        'StampsDisponibles': timbre.stamp,
        'StampsUsadosTotales': timbre.cont_stamped_cliente,
        'StampsUsadosHoy': timbre.cont_stamped_day
    } for timbre in timbres]

    return JsonResponse({'timbres': timbres_data})

class MultiFormView(PlanAndGroupRequiredMixin, PerfilFiscalRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'clientes/crear.html'
    success_url = reverse_lazy('invoice:client_list')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['moral_form'] = ClientMoralForm(user=self.request.user)
        context['fisica_form'] = ClientFisicoForm(user=self.request.user)
        context['extranjero_form'] = ClientExtranjeroForm(user=self.request.user)
        context['title'] = 'Creación de Clientes'
        context['list_url'] = reverse_lazy('invoice:client_list')
        context['action'] = 'add'
        context['submit_type'] = ''
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action', None)
            if action != 'add':
                data['error'] = 'Acción no reconocida'
                return JsonResponse(data)
                
            submit = request.POST.get('submit_type', None)
            if not submit:
                data['error'] = 'No se ha especificado el tipo de formulario enviado'
                return JsonResponse(data)
                
            moral_form = ClientMoralForm(request.POST, request.FILES)
            fisica_form = ClientFisicoForm(request.POST, request.FILES)
            extranjero_form = ClientExtranjeroForm(request.POST, request.FILES)
            
            with transaction.atomic():
                Cliente.usuario_logueado=request.user
                if submit == 'moral_submit':
                    if moral_form.is_valid():
                        cliente = moral_form.save()
                        try:
                            user_cliente = User_Cliente(idCliente=cliente, idUser=request.user)
                            user_cliente.full_clean()
                            user_cliente.save()
                            if cliente.tipoCliente == 'P':
                                Timbre.objects.create(user_cliente=user_cliente)
                            else:
                                Timbre.objects.create(user_cliente=user_cliente, isOnDemmand=True)
                            Contratos.objects.create(Cliente=cliente)
                            return JsonResponse({'success': True})
                        except ValidationError as e:
                            cliente.delete()
                            data['error'] = e.message_dict  # Capturar errores de validación del modelo
                            return JsonResponse(data)
                    else:
                        data['error'] = moral_form.errors
                elif submit == 'fisica_submit':
                    if fisica_form.is_valid():
                        cliente = fisica_form.save()
                        try:
                            user_cliente = User_Cliente(idCliente=cliente, idUser=request.user)
                            user_cliente.full_clean()
                            user_cliente.save()
                            if cliente.tipoCliente == 'P':
                                Timbre.objects.create(user_cliente=user_cliente)
                            else:
                                Timbre.objects.create(user_cliente=user_cliente, isOnDemmand=True)
                            Contratos.objects.create(Cliente=cliente)
                            return JsonResponse({'success': True})
                        except ValidationError as e:
                            cliente.delete()
                            data['error'] = e.message_dict  # Capturar errores de validación del modelo
                            return JsonResponse(data)
                    else:
                        data['error'] = fisica_form.errors
                elif submit == 'extranjero_submit':
                    if extranjero_form.is_valid():
                        cliente = extranjero_form.save()
                        try:
                            user_cliente = User_Cliente(idCliente=cliente, idUser=request.user)
                            user_cliente.full_clean()
                            user_cliente.save()
                            if cliente.tipoCliente == 'P':
                                Timbre.objects.create(user_cliente=user_cliente, isOnDemmand=True)
                            else:
                                Timbre.objects.create(user_cliente=user_cliente)
                                
                            Contratos.objects.create(Cliente=cliente)
                            return JsonResponse({'success': True})
                        except ValidationError as e:
                            cliente.delete()
                            data['error'] = e.message_dict  # Capturar errores de validación del modelo
                            return JsonResponse(data)
                    else:
                        data['error'] = extranjero_form.errors
                else:
                    data['error'] = 'Tipo de formulario no reconocido'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)


       
        # return self.render_to_response(self.get_context_data(
        #     moral_form=moral_form,
        #     fisica_form=fisica_form,
        #     extranjero_form=extranjero_form
        # ))

# vistas basadas en clases
class ClientListView(PlanAndGroupRequiredMixin, PerfilFiscalRequiredMixin, LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/lista.html'
    login_url = '/login/'  # Redirigir a esta URL si no está autenticado

    def get_queryset(self):
        # Prefetch para obtener solo timbres activos relacionados con cada User_Cliente
        timbres_activos = Timbre.objects.filter(estatus='A')  # Filtra los timbres activos
        user_clientes = User_Cliente.objects.filter(idUser=self.request.user).prefetch_related(
            Prefetch('timbres_de_cliente', queryset=timbres_activos, to_attr='timbres_activos')
        ).select_related('idCliente')
        
        return user_clientes

    # def post(self, request, *args, **kwargs):
    #     data = {}
    #     try:
    #         data = Cliente.objects.get(pk=request.POST['id']).toJSON()
    #     except Exception as e:
    #         data['error'] = str(e)
    #     return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Clientes'
        context['client_list'] = self.get_queryset()
        context['create_url'] = reverse_lazy('invoice:multi_form_view')
        return context
    
    
class ClienteUpdateView(PlanAndGroupRequiredMixin, PerfilFiscalRequiredMixin, LoginRequiredMixin,UpdateView):
    model = Cliente
    template_name = 'clientes/actualizar.html'
    success_url = reverse_lazy('invoice:client_list')
    login_url = '/login/'  # Redirigir a esta URL si no está autenticado

    def get_form_class(self):
        cliente = self.get_object()
        if cliente.tipoReceptor == 'moral':
            return ClientMoralForm
        elif cliente.tipoReceptor == 'fisica':
            return ClientFisicoForm
        else:
            return ClientExtranjeroForm
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pasa el usuario logueado al formulario
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.objects = self.get_object()
        return super().dispatch(request, *args, **kwargs) 
    
    def post(self, request, *args, **kwargs):
        cliente = self.get_object()
        print(cliente.Cer, cliente.Key, cliente.passphrase)

        data = {}
        try:
            submit = request.POST['submit_type']
            cliente = self.get_object()  # Obtén la instancia actual del cliente
            Cliente.usuario_logueado=request.user
            if submit == 'moral_submit':
                form = ClientMoralForm(request.POST, request.FILES, instance=cliente)
            elif submit == 'fisica_submit':
                form = ClientFisicoForm(request.POST, request.FILES, instance=cliente)
            elif submit == 'extranjero_submit':
                form = ClientExtranjeroForm(request.POST, request.FILES, instance=cliente)
            else:
                data['error'] = 'Tipo de formulario no válido.'
                return JsonResponse(data)

            print(request.FILES)
            print(request.POST)
            print(form.errors)

            if form.is_valid():
                cliente = form.save()  # Guarda la instancia actualizada
                # No es necesario crear un nuevo User_Cliente, ya que el cliente ya existe
                return JsonResponse({'success': True})
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['title'] = 'Actualizacion de Cliente'
            context['tipoReceptor'] = self.get_object().tipoReceptor
            context['list_url'] = reverse_lazy('invoice:client_list')
            return context

    def form_valid(self, form):
        form.instance.user_cliente = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return str(self.success_url) 
    
class ClienteDeleteView(PlanAndGroupRequiredMixin, PerfilFiscalRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'clientes/delete.html'
    success_url = reverse_lazy('invoice:client_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminacion del Cliente'
        context['entity'] = 'Clientes'
        context['list_url'] = reverse_lazy('invoice:client_list')
        return context

class ClienteEstatusView(PlanAndGroupRequiredMixin, PerfilFiscalRequiredMixin, DetailView):
    model = User_Cliente
    template_name = 'clientes/estatus.html'  # Ruta al template
    context_object_name = 'cliente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Estatus del Cliente'
        context['entity'] = 'Clientes'
        context['list_url'] = reverse_lazy('invoice:client_list')
        return context
    
    def post(self, request, *args, **kwargs):
        data = {}
        try:
            # Obtener la instancia actual del objeto
            cliente_instance = self.get_object()

            # Cambiar el estatus del cliente
            if cliente_instance.estatus == 'A':
                cliente_instance.estatus = 'S'
            else:
                cliente_instance.estatus = 'A'
            
            print(cliente_instance.idCliente.rfc)

            # Guardar la instancia solo si la validación es exitosa
            cliente_instance.save()

            # Incluir el nuevo estatus en la respuesta
            data = {'success': True, 'estatus': cliente_instance.estatus}
            
        except Exception as e:
            # Manejar errores y devolverlos como parte de la respuesta JSON
            data['error'] = str(e)

        # Devuelve la respuesta JSON
        return JsonResponse(data)

    
class TokenCreateView(PlanAndGroupRequiredMixin, PerfilFiscalRequiredMixin, LoginRequiredMixin, TemplateView):
    model = Tokens
    template_name = 'clientes/tokens.html'
    success_url = reverse_lazy('invoice:list_token')
    login_url = '/login/'  # Redirigir a esta URL si no está autenticado

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token_form'] = TokensForm()
        context['title'] = 'Creación de Token'
        context['list_url'] = reverse_lazy('invoice:list_token')
        context['action'] = 'add'
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                Tokens.usuario_logueado = request.user
                
                token_form = TokensForm(request.POST, request.FILES)

                print(request.FILES)
                print(request.POST)
                print(token_form.errors)
                
                if token_form.is_valid():
                    # Crea una instancia del modelo pero no la guarda en la base de datos todavía
                    token_instance = token_form.save(commit=False)
                    # Crea un nuevo usuario utilizando los datos del formulario
                    new_user = User.objects.create_user(
                        username=token_instance.userName,
                        first_name=token_instance.nombre,
                        password=token_instance.token 
                    )

                    # Asigna el grupo al usuario recién creado
                    grupo = Group.objects.get(name='invoice')  # Reemplaza 'nombre_del_grupo' por el nombre del grupo que deseas asignar
                    new_user.groups.add(grupo)

                    # Asigna el usuario creado al campo idUserToken
                    token_instance.idUserToken = new_user

                    # Asigna el usuario logueado al campo idUserParent
                    token_instance.idUserParent = request.user
                    
                    # variable temporal para que el usuario copie el token
                    getToken = token_instance.token
                    
                    # eliminar token para que no se almacene
                    token_instance.token = 'token creado'

                    # Guarda la instancia en la base de datos
                    token_instance.save()
                    
                    print('token creado', token_instance)

                    # Incluye el token en la respuesta
                    print('token prueba:', getToken)
                    data = {'success': True, 'token': getToken}
                else:
                    data['error'] = token_form.errors
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        
        # Devuelve la respuesta JSON
        return JsonResponse(data)
    
class TokensListView(PlanAndGroupRequiredMixin, PerfilFiscalRequiredMixin, LoginRequiredMixin, ListView):
    model = Tokens
    template_name = 'clientes/lista_tokens.html'
    login_url = '/login/'  # Redirigir a esta URL si no está autenticado

    def get_queryset(self):
        # Filtra los clientes que están asociados con el usuario logueado
        return Tokens.objects.filter(idUserParent=self.request.user)

    # def post(self, request, *args, **kwargs):
    #     data = {}
    #     try:
    #         data = Cliente.objects.get(pk=request.POST['id']).toJSON()
    #     except Exception as e:
    #         data['error'] = str(e)
    #     return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Tokens'
        context['token_list'] = self.get_queryset()
        context['create_url'] = reverse_lazy('invoice:client_token')
        return context

class ReadOnlyTokensForm(PlanAndGroupRequiredMixin, PerfilFiscalRequiredMixin, TokensUPdateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['readonly'] = True

class TokenResetView(PlanAndGroupRequiredMixin, PerfilFiscalRequiredMixin, LoginRequiredMixin,UpdateView):
    model = Tokens
    form_class = TokensResetForm
    template_name = 'clientes/reset_token.html'
    success_url = reverse_lazy('invoice:list_token')
    login_url = '/login/'  # Redirigir a esta URL si no está autenticado

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reset Token'
        context['token_form'] = self.get_form()
        context['list_url'] = self.success_url
        context['action'] = 'edit'

        # Deshabilitar campos en el formulario
        form = context['token_form']
        for field in form.fields.values():
            field.widget.attrs['readonly'] = True  # Establecer el atributo readonly para los campos

        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
             # Obtener la instancia actual del token
            token_instance = self.get_object()

            # Llenar el formulario con los datos existentes del token
            token_form = self.form_class(request.POST, instance=token_instance)

            if token_form.is_valid():
                # Guarda la instancia del token y actualiza los datos
                token_instance = token_form.save()

                # Actualizar la contraseña del usuario asociado
                new_password = token_instance.token
                
                token_instance.token = 'update token'
                token_instance.save()
                
                user = token_instance.idUserToken
                user.set_password(new_password)
                user.save()

                # Incluye el nuevo token en la respuesta
                data = {'success': True, 'token': new_password}
            else:
                data['error'] = token_form.errors
        except Exception as e:
            data['error'] = str(e)
        
        # Devuelve la respuesta JSON
        return JsonResponse(data)   
    
class TokenUpdateView(PlanAndGroupRequiredMixin, PerfilFiscalRequiredMixin, LoginRequiredMixin,UpdateView):
    model = Tokens
    form_class = ReadOnlyTokensForm  # Usar el formulario de solo lectura
    template_name = 'clientes/update_token.html'
    success_url = reverse_lazy('invoice:list_token')
    login_url = '/login/'  # Redirigir a esta URL si no está autenticado

    def get_context_data(self, **kwargs):
        token = self.object  # Obtén el objeto que se está editando
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update estatus Token'
        context['token_form'] = self.get_form()
        context['list_url'] = self.success_url
        context['estatus'] = token.estatus  # Agrega el valor de estatus al contexto
        context['action'] = 'edit'
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            # Obtener la instancia actual del token
            token_instance = self.get_object()

            # Llenar el formulario con los datos existentes del token
            token_form = self.form_class(request.POST, instance=token_instance)

            if token_form.is_valid():
                # Guarda la instancia del token y actualiza los datos
                token_instance = token_form.save()

                # Activar o desactivar al usuario basado en el estatus del token
                user = token_instance.idUserToken
                if token_instance.estatus == 'true':
                    user.is_active = True
                else:
                    user.is_active = False
                user.save()

                # Incluye un mensaje de éxito en la respuesta
                data = {'success': True}
            else:
                data['error'] = token_form.errors
        except Exception as e:
            data['error'] = str(e)
        
        # Devuelve la respuesta JSON
        return JsonResponse(data)   
    
    ##############################
    



# Vista para eliminar perfil
class PerfilDeleteView(PlanAndGroupRequiredMixin, DeleteView):
    model =  PerfilFiscalUser
    template_name = 'perfiles/delete.html'
    success_url = reverse_lazy('invoice:perfilpreferencias')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación del Perfil'
        context['entity'] = 'Perfil'
        return context

#importa el reverse
from django.urls import reverse


# Vista para manejar formularios múltiples de perfil
# views.py

from suds.client import Client


def get_user_info(ctx, reseller_username, reseller_password, taxpayer_id):
    # URL del servicio SOAP
    url = config('URL_REGISTRO_CLIENTES')
    client = Client(url, cache=None)

    # Llamar al método get del servicio SOAP
    contenido = client.service.get(
        reseller_username=reseller_username,
        reseller_password=reseller_password,
        taxpayer_id=taxpayer_id
    )

    # Crear instancia de la respuesta personalizada
    response = customersResponse()
    incids = []

    # Procesar los datos recibidos y mapearlos a los modelos
    for key, value in client.dict(contenido).items():
        print(key, "->", value)  # Quitar los prints si no son necesarios para depuración
        if key == 'message':
            response.message = contenido.message
        elif key == 'users':
            user_data = contenido.users
            if user_data:
                for user_value in user_data:
                    reseller_user = ResellerUser()
                    reseller_user_array = ResellerUserArray()

                    reseller_user.status = user_value[1][0].status
                    print(user_value[1][0].status)
                    reseller_user.counter = str(user_value[1][0].counter)
                    print(user_value[1][0].counter)
                    reseller_user.taxpayer_id = user_value[1][0].taxpayer_id
                    print(user_value[1][0].taxpayer_id)
                    reseller_user.credit = str(user_value[1][0].credit)
                    print(user_value[1][0].credit)
                    
                    incids.append(reseller_user)
        
    response.users = incids

    return response




class MultiFormPerfilView(PlanAndGroupRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'perfiles/actualizar.html'
    success_url = reverse_lazy('invoice:perfilpreferencias')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_perfil = PerfilFiscalUser.objects.filter(user=self.request.user).first()
        
        usuario = self.request.user
        user_services = User_Service.objects.filter(idUser=usuario).first()
        print('service:',user_services)
        service_plans = Service_Plan.objects.filter(
            service=user_services.idService, 
            plan=user_services.idPlan
        ).first()
        if service_plans and service_plans.supplierStamp:
            url_sign_manifest = service_plans.supplierStamp.urlSignManifest
            print('URL:', url_sign_manifest)
        # Siempre mostrar ambos formularios
        context['moral_form'] = PerfilMoralForm(instance=user_perfil, user=self.request.user)
        context['fisico_form'] = PerfilFisicoForm(instance=user_perfil, user=self.request.user)
        context['regimen_form'] = RegimenFiscalForm(instance=user_perfil)
        context['action'] = 'update' if user_perfil else 'add'
        context['title'] = 'Actualización de Perfil Fiscal'
        context['perfil_registrado'] = user_perfil is not None
        context['tipoReceptor'] = user_perfil.tipoReceptor if user_perfil else 'moral'
        context['url_sign_manifest'] = url_sign_manifest
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        
        try:
            PerfilFiscalUser.usuario_logueado = request.user
            submit_type = request.POST.get('submit_type')
            user_perfil = PerfilFiscalUser.objects.filter(user=request.user).first()
            
            if not user_perfil:
                # Crea un nuevo perfil si no existe
                user_perfil = PerfilFiscalUser(user=request.user)
                user_perfil.save()

            if submit_type == 'moral_submit':
                moral_form = PerfilMoralForm(request.POST, request.FILES, instance=user_perfil, user=request.user)
                if moral_form.is_valid():
                    moral_form.clean()
                    moral_form.save()
                    user_perfil.tipoReceptor = 'moral'
                    user_perfil.save()
                    return JsonResponse({'success': True})
                else:
                    data['error'] = moral_form.errors
            elif submit_type == 'fisica_submit':
                fisico_form = PerfilFisicoForm(request.POST, request.FILES, instance=user_perfil, user=request.user)
                if fisico_form.is_valid():
                    fisico_form.clean()
                    fisico_form.save()
                    user_perfil.tipoReceptor = 'fisica'
                    user_perfil.save()
                    return JsonResponse({'success': True})
                else:
                    data['error'] = fisico_form.errors
            elif submit_type == 'regimen_submit':
                regimen_form = RegimenFiscalForm(request.POST, request.FILES, instance=user_perfil)
                if regimen_form.is_valid():
                    regimen_form.save()
                    return JsonResponse({'success': True})
                else:
                    data['error'] = regimen_form.errors
            else:
                data['error'] = 'Formulario no válido o tipo de envío no reconocido'
        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data)



# Firma de contrato
class ContratoListView(PlanAndGroupRequiredMixin, PerfilFiscalRequiredMixin, LoginRequiredMixin, ListView):
    model = Contratos
    template_name = 'clientes/lista_firma.html'
    login_url = '/login/'  # Redirigir a esta URL si no está autenticado

    def get_queryset(self):
        # Filtra los clientes que están asociados con el usuario logueado
        return Contratos.objects.filter(Cliente__user_cliente__idUser=self.request.user)

    # def post(self, request, *args, **kwargs):
    #     data = {}
    #     try:
    #         data = Cliente.objects.get(pk=request.POST['id']).toJSON()
    #     except Exception as e:
    #         data['error'] = str(e)
    #     return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtén los servicios relacionados con el usuario logueado
        usuario = self.request.user
        user_services = User_Service.objects.filter(idUser=usuario).first()
        print('service:',user_services)
        # Obtén los Service_Plan relacionados con el usuario logueado
        service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()
        print('service plan:',service_plans)
        contratos = self.get_queryset()

        # Actualiza el estatus de cada contrato llamando al servicio web
        for contrato in contratos:
            print('Contratos:', contrato.Cliente)
            actualizar_estatus_contrato(contrato, service_plans.supplierStamp)

        context['title'] = 'Listado de Contratos'
        context['contrato_list'] = contratos
        return context
    



def ContratosListViewPerfil(request):
    # Obtener el perfil fiscal del usuario logueado
    perfil_fiscal = PerfilFiscalUser.objects.filter(user=request.user).first()

    # Obtener los servicios del usuario logueado
    user_services = User_Service.objects.filter(idUser=request.user).first()
    
    if user_services:
        # Obtén los Service_Plan relacionados con el usuario logueado
        service_plans = Service_Plan.objects.filter(
            service=user_services.idService, 
            plan=user_services.idPlan
        ).first()
        if service_plans and service_plans.supplierStamp:
            url_sign_manifest = service_plans.supplierStamp.urlSignManifest
            print('URL:', url_sign_manifest)
            
            # Actualiza el estatus de cada contrato llamando al servicio web
            for contrato in PerfilFiscalUser.objects.filter(user=request.user):
                print('PerfilFiscalUser:', contrato.nombre)
                actualizar_estatus_contratoPerfil(contrato, service_plans.supplierStamp)
        else:
            url_sign_manifest = None
    else:
        service_plans = None
        url_sign_manifest = None

    if perfil_fiscal:
        context = {
            'perfil_fiscal': perfil_fiscal,  # Asegúrate de pasar el objeto completo al contexto
            'nombre': perfil_fiscal.nombre,
            'rfc': perfil_fiscal.rfc,
            'estado_firma': perfil_fiscal.estado_firma,
            'contratoXML': perfil_fiscal.contratoXML,
            'contratoPDF': perfil_fiscal.contratoPDF,
            'user_services': user_services,  # Añadir los servicios al contexto si es necesario
            'service_plans': service_plans,  # Añadir los planes de servicio al contexto si es necesario
            'url_sign_manifest': url_sign_manifest  # Añadir la URL al contexto
        }
    else:
        context = {
            'user_services': user_services,
            'service_plans': service_plans,
            'url_sign_manifest': url_sign_manifest
        }

    return render(request, 'perfiles/lista_firma.html', context)



    










# def obtener_url_sign_manifest(request, id):
#     try:
#         service_plan = Service_Plan.objects.filter(usuario=request.user, isActive=True).first()
#         if service_plan and service_plan.supplierStamp:
#             url_sign_manifest = service_plan.supplierStamp.urlSignManifest
#             return HttpResponse(url_sign_manifest, status=200)
#         else:
#             return HttpResponse('No se encontró una URL de firma válida.', status=404)
#     except Exception as e:
#         return HttpResponse(f'Error: {str(e)}', status=500)



# def obtener_url_sign_manifest(request, id):
#     try:
#         service_plan = Service_Plan.objects.filter(usuario=request.user, isActive=True).first()
#         if service_plan and service_plan.supplierStamp:
#             url_sign_manifest = service_plan.supplierStamp.urlSignManifest
#             return redirect(url_sign_manifest)
#         else:
#             return HttpResponseNotFound('No se encontró una URL de firma válida.')
#     except Exception as e:
#         return HttpResponseNotFound(f'Error: {str(e)}')





def facturas_por_fecha(request):
    context = {}

    try:
        # Obtener el usuario autenticado
        usuario = get_object_or_404(User, email=request.user.email)

        # Consultar las facturas asociadas a este usuario sin sumar, solo por fecha
        timbres = TimbreUserPerfil.objects.filter(userInvoice=usuario).order_by('fecha')

        context['fecha_actual'] = datetime.now().strftime('%d-%m-%Y')
        context['timbres'] = timbres

        # Renderizar la plantilla con los datos de facturas
        return render(request, 'perfiles/facturas_modal.html', context)

    except User.DoesNotExist:
        context['error'] = "No se encontró el perfil de usuario."
        return render(request, 'perfiles/facturas_modal.html', context)

    except Exception as e:
        context['error'] = "Ocurrió un error al procesar la solicitud."
        return render(request, 'perfiles/facturas_modal.html', context)

    
    #Para obtener las facturas (creditos) por el correo del usuario (este codigo es de la vista de arriba pero con el correo del usuario)
    # context = {}

    # try:
    #     # Obtener el usuario autenticado
    #     usuario = get_object_or_404(Usuario, user=request.user)

    #     # Consultar las facturas asociadas a este usuario sin sumar, solo por fecha
    #     timbres = TimbreUserPerfil.objects.filter(usuario=usuario).order_by('fecha')

    #     context['fecha_actual'] = datetime.now().strftime('%d-%m-%Y')
    #     context['timbres'] = timbres

    #     # Renderizar la plantilla con los datos de facturas
    #     return render(request, 'perfiles/facturas_modal.html', context)

    # except Usuario.DoesNotExist:
    #     context['error'] = "No se encontró el perfil de usuario."
    #     return render(request, 'perfiles/facturas_modal.html', context)

    # except Exception as e:
    #     context['error'] = "Ocurrió un error al procesar la solicitud."
    #     return render(request, 'perfiles/facturas_modal.html', context)



    
def actualizar_estatus_contrato(contrato, service_plans):
    # Verifica si el contrato ya tiene el estatus True
    if contrato.estado_firma == 'true':
        print(f"El contrato {contrato.id} ya está activo. No es necesario actualizarlo.")
        return
    
    errors = {}
    try:
        # Llamada al servicio web para obtener el nuevo estatus
        print(f"Cliente: {contrato.Cliente}")
        print(f"RFC: {contrato.Cliente.rfc}")
        print('Llamada al servicio get_documents')
        
        def obtener_pdf():
            return register.SignContractSOAP.get_documents(
                '',
                service_plans.idSocio,
                contrato.Cliente.rfc,
                'PDF'
            )

        # Ejecutar las siguientes dos tareas en paralelo: XML y add_tokens
        def obtener_xml():
            return register.SignContractSOAP.get_documents(
                '',
                service_plans.idSocio,
                contrato.Cliente.rfc,
                'XML'
            )
        
        # Ejecutar en paralelo usando ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_pdf = executor.submit(obtener_pdf)
            future_xml = executor.submit(obtener_xml)

            # Obtener los resultados
            resultadoPDF = future_pdf.result()
            resultadoXML = future_xml.result()

        # Verificamos los resultados
        print("Debug: Resultado del servicio SOAP - PDF", resultadoPDF.success)
        print("Debug: Resultado del servicio SOAP - XML", resultadoXML.success)
        
        if resultadoPDF.success or resultadoXML.success:
            
            if resultadoXML.success:
                xml_response = resultadoXML.contract 
                # Parsear el XML
                root = ET.fromstring(xml_response)

                # Encontrar el elemento <contrato> y obtener el valor del atributo "fecha"
                fecha_contrato = root.find(".//contrato").attrib['fecha']
                    
                # Guarda el XML devuelto por el servicio web
                contrato.contratoXML = resultadoXML.contract 
            else:
                # Parsear el XML
                fecha_contrato = datetime.now()



            # Si el servicio web indica éxito, actualiza el contrato
            contrato.estado_firma = 'true'  # Cambia el estatus a True
            contrato.fecha = fecha_contrato # Guarda la fecha de actualización

            # Guarda el PDF devuelto por el servicio web
            contrato.contratoPDF = resultadoPDF.contract 

            # Guarda los cambios en la base de datos
            contrato.save()
            print(f"El contrato {contrato.id} ha sido actualizado correctamente.")

        else:
            print(f"Error al actualizar el contrato {contrato.id}: {resultadoPDF.error}")
            # Manejo de errores o incidencias en caso de fallo
            errors['error'] = resultadoPDF.error
    except Exception as e:
        print(f"Excepción al actualizar el contrato {contrato.id}: {str(e)}")
        errors['exception'] = str(e)

def descargar_contrato_pdf(request, contrato_id):
    contrato = get_object_or_404(Contratos, id=contrato_id)
    pdf_data = base64.b64decode(contrato.contratoPDF)
    
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Contrato_{contrato.Cliente}_RFC_{contrato.Cliente.rfc}.pdf"'
    return response

def descargar_contrato_xml(request, contrato_id):
    contrato = get_object_or_404(Contratos, id=contrato_id)
    xml_data = contrato.contratoXML 
    
    response = HttpResponse(xml_data, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="Contrato_{contrato.Cliente}_RFC_{contrato.Cliente.rfc}.xml"'
    return response




########################################################################################################################

def actualizar_estatus_contratoPerfil(contrato, service_plans):
    # Verifica si el contrato ya tiene el estatus True
    if contrato.estado_firma == 'true':
        print(f"El contrato {contrato.id} ya está activo. No es necesario actualizarlo.")
        return
    
    errors = {}
    try:
        # Llamada al servicio web para obtener el nuevo estatus
        print(f"Cliente: {contrato.nombre}")
        print(f"RFC: {contrato.rfc}")
        print('Llamada al servicio get_documents')

        def obtener_pdf():
            return register.SignContractSOAP.get_documents(
                '',
                service_plans.idSocio,
                contrato.rfc,
                'PDF'
            )


        # Ejecutar las siguientes dos tareas en paralelo: XML y add_tokens
        def obtener_xml():
            return register.SignContractSOAP.get_documents(
                '',
                service_plans.idSocio,
                contrato.rfc,
                'XML'
            )

        def agregar_tokens():
            user_service = User_Service.objects.filter(idUser=contrato.user).first()
            service_plans = Service_Plan.objects.filter(service=user_service.idService, plan=user_service.idPlan).first()
            userperfil = User.objects.get(id=contrato.user.id)
                
            resultado = register.UtilitiesSOAP.add_tokens(
                '',
                service_plans.supplierStamp.user,
                service_plans.supplierStamp.decrypt_password(),
                contrato.nombre,
                userperfil.username,
                '',
                'true'
            )
                # Suponiendo que 'resultado' es un objeto con 'message' y 'token'
            if hasattr(resultado, 'message'):
                reset = register.UtilitiesSOAP.reset_token(
                    '',
                    service_plans.supplierStamp.user,
                    service_plans.supplierStamp.decrypt_password(),
                    userperfil.username
                )
                print('reset token', reset)
                return reset
            elif hasattr(resultado, 'token'):
                return resultado
                    
        # Ejecutar en paralelo usando ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_pdf = executor.submit(obtener_pdf)
            future_xml = executor.submit(obtener_xml)
            future_tokens = executor.submit(agregar_tokens)

            # Obtener los resultados
            resultadoPDF = future_pdf.result()
            resultadoXML = future_xml.result()
            resultado_tokens = future_tokens.result()

        # Verificamos los resultados
        print("Debug: Resultado del servicio SOAP - PDF", resultadoPDF.success)
        print("Debug: Resultado del servicio SOAP - XML", resultadoXML.success)
        print("Debug: Resultado del servicio SOAP - TOKEN", resultado_tokens)

        if resultadoXML.success or resultadoPDF.success:
                
            if resultadoXML.success:
                xml_response = resultadoXML.contract 
                # Parsear el XML
                root = ET.fromstring(xml_response)

                # Encontrar el elemento <contrato> y obtener el valor del atributo "fecha"
                fecha_contrato = root.find(".//contrato").attrib['fecha']
                    
                # Guarda el XML devuelto por el servicio web
                contrato.contratoXML = resultadoXML.contract 
            else:
                # Parsear el XML
                fecha_contrato = datetime.now()

            # Si el servicio web indica éxito, actualiza el contrato
            contrato.estado_firma = 'true'  # Cambia el estatus a True
            contrato.fecha = fecha_contrato # Guarda la fecha de actualización

            # Guarda el PDF devuelto por el servicio web
            contrato.contratoPDF = resultadoPDF.contract 
                
            # Guarda el Token devuelto por el servicio web
            contrato.token = resultado_tokens.token
                
            # Cambiar el estatus del usuario a activo
            contrato.estatus = 'A'
                
            # Guarda los cambios en la base de datos
            contrato.save()
                
            print(f"El contrato {contrato.id} ha sido actualizado correctamente.")

    except Exception as e:
        print(f"Excepción al actualizar el contrato {contrato.id}: {str(e)}")
        errors['exception'] = str(e)




# def descargar_contrato_pdfPerfil(request, contrato_id):
#     contrato = get_object_or_404(PerfilFiscalUser, id=contrato_id)
#     pdf_data = base64.b64decode(contrato.contratoPDF)
    
#     response = HttpResponse(pdf_data, content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="Contrato_{contrato.PerfilFiscalUser}_RFC_{contrato.PerfilFiscalUser.rfc}.pdf"'
#     return response

# def descargar_contrato_xmlPerfil(request, contrato_id):
#     contrato = get_object_or_404(PerfilFiscalUser, id=contrato_id)
#     xml_data = contrato.contratoXML 
    
#     response = HttpResponse(xml_data, content_type='application/xml')
#     response['Content-Disposition'] = f'attachment; filename="Contrato_{contrato.PerfilFiscalUser}_RFC_{contrato.PerfilFiscalUser.rfc}.xml"'
#     return response


def descargar_contrato_pdfPerfil(request, contrato_id):
    contrato = get_object_or_404(PerfilFiscalUser, id=contrato_id)
    pdf_data = base64.b64decode(contrato.contratoPDF)

    # Ajustamos el acceso al nombre del perfil y RFC
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Contrato_{contrato.nombre}_RFC_{contrato.rfc}.pdf"'
    return response

def descargar_contrato_xmlPerfil(request, contrato_id):
    contrato = get_object_or_404(PerfilFiscalUser, id=contrato_id)
    xml_data = contrato.contratoXML

    response = HttpResponse(xml_data, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="Contrato_{contrato.nombre}_RFC_{contrato.rfc}.xml"'
    return response




########################################################################################################################



from django.core.mail import EmailMessage

def SendContractEmailView(request, contrato_id):
    contrato = get_object_or_404(Contratos, id=contrato_id)
    cliente_email = contrato.Cliente.email
    cliente_nombre = contrato.Cliente.nombre


    user_services = User_Service.objects.filter(idUser=request.user).first()
    
    if user_services:
        # Obtén los Service_Plan relacionados con el usuario logueado
        service_plans = Service_Plan.objects.filter(
            service=user_services.idService, 
            plan=user_services.idPlan
        ).first()
        if service_plans and service_plans.supplierStamp:
            url_sign_manifest = service_plans.supplierStamp.urlSignManifest
            print('URL:', url_sign_manifest)


    # URL que quieres usar en el asunto
    url = url_sign_manifest
    
    # Obtener el correo del usuario autenticado
    if request.user.is_authenticated:
        from_email = request.user.email
    else:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    # Configura el correo electrónico
    subject = f'Contrato XML disponible en: {url}'
    body = f'Hola {cliente_nombre},\n\nEl contrato está disponible para su consulta en el siguiente enlace: {url}.\n\nSaludos cordiales.'
    to_email = [cliente_email]

    # Crear el correo electrónico sin archivos adjuntos
    email = EmailMessage(
        subject,
        body,
        from_email,
        to_email
    )
    
    try:
        email.send()
        # Redirigir a una página de éxito o a la vista anterior
        return redirect('invoice:lista_contrato')  # Cambia esto a la URL deseada
    except Exception as e:
        # Manejo de errores: redirigir a una página de error o mostrar un mensaje
        return redirect('invoice:lista_contrato')  # Cambia esto a la URL deseada
    
    
    
    
    


def SendContractFirmadoEmailView(request, contrato_id):
    contrato = get_object_or_404(Contratos, id=contrato_id)
    cliente_email = contrato.Cliente.email
    cliente_nombre = contrato.Cliente.nombre

    # Obtener el correo del usuario autenticado
    if request.user.is_authenticated:
        from_email = request.user.email
    else:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    # Configura el correo electrónico
    subject = f'Contrato firmado disponible para su descarga'
    body = f'Hola {cliente_nombre},\n\nAdjunto encontrarás el contrato firmado en formato PDF y XML.\n\nSaludos cordiales.'
    to_email = [cliente_email]

    # Crear el correo electrónico
    email = EmailMessage(
        subject,
        body,
        from_email,
        to_email
    )

    # Adjuntar el archivo PDF
    pdf_data = base64.b64decode(contrato.contratoPDF)
    pdf_filename = f"Contrato_{contrato.Cliente}_RFC_{contrato.Cliente.rfc}.pdf"
    email.attach(pdf_filename, pdf_data, 'application/pdf')

    # Adjuntar el archivo XML
    xml_data = contrato.contratoXML
    xml_filename = f"Contrato_{contrato.Cliente}_RFC_{contrato.Cliente.rfc}.xml"
    email.attach(xml_filename, xml_data, 'application/xml')
    
    try:
        email.send()
        # Redirigir a una página de éxito o a la vista anterior
        return redirect('invoice:lista_contrato')  # Cambia esto a la URL deseada
    except Exception as e:
        # Manejo de errores: redirigir a una página de error o mostrar un mensaje
        return redirect('invoice:lista_contrato')  # Cambia esto a la URL deseada



