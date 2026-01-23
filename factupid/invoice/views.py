from datetime import datetime, timezone
import re

from django.utils import timezone

from sre_constants import IN
from django.shortcuts import redirect, render
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django_soap.utils.SOAPHandlerBase import SoapResult
from spyne import Iterable, Uuid
from spyne.application import Application
from spyne.decorator import rpc
from spyne.model.complex import Array, ComplexModel, XmlAttribute
from spyne.model.primitive import Unicode, Integer, AnyXml, Ltree, String, Boolean, AnyDict
from spyne.protocol.soap import Soap11, Soap12
from spyne.protocol.xml import etree
from spyne.server.django import DjangoApplication
from spyne.service import ServiceBase
import datetime
from django_soap.utils.client import SOAPClient
# importa los templates
from django.shortcuts import render
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
import xml.etree.ElementTree as ET
import base64
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str as force_text
from django.urls import reverse, reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
#from zeep import Transport
from console.models import Plan, Service, Service_Plan,User_Service
from django.contrib.auth import authenticate, login
from suds.client import Client
import logging
from django.contrib.auth.models import User

from django.conf import settings 
from invoice.forms import CustomUserCreationForm, LoginForm , Tokens
from django.contrib.auth.models import Group
from .models import LogStamp, Cliente, User_Cliente, TimbreUserPerfil, PerfilFiscalUser, Timbre
from adapter.console.django_user_repository import CustomAuthAdapter
import logging
import time
from decouple import config



#importaciones necesarias para la arquitectura repository y dominio


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import HttpResponse
from adapter.invoice.django_customer_repository import DjangoCustomerRepository

# Creamos una instancia del repositorio de clientes
customer_repository = DjangoCustomerRepository()
from adapter.invoice.django_customer_repository import DjangoCustomerRepository
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group


# Create your views here.
def _sync_cfdi_enterprise_counter(user, cantidad=1):
    if not user or cantidad == 0:
        return
    try:
        from cfdi.models import UsersCFDI
    except Exception as exc:
        logging.getLogger(__name__).warning(
            "No se pudo importar UsersCFDI para sincronizar: %s", exc
        )
        return

    try:
        usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=user)
    except UsersCFDI.DoesNotExist:
        return

    raiz = usuario_cfdi.get_raiz()
    plan = getattr(getattr(raiz, 'idUserServicePlan_id', None), 'idPlan', None)
    if not plan or not getattr(plan, 'nombre', None):
        return
    if plan.nombre.strip().lower() != 'enterprise':
        return

    try:
        raiz.registrar_timbre(cantidad=cantidad, sync_invoice=False)
    except ValueError as exc:
        logging.getLogger(__name__).warning(
            "No se pudo sincronizar timbres en CFDI: %s", exc
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
        ('incidencia', String),

    ]

#vista de query_pending
class AcuseRecepcionCFDIQuery(ComplexModel):
    _type_info = [
        ('status', String),
        ('xml', String),
        ('uuid', String),
        ('uuid_status', String),
        ('next_attempt', String),
        ('attempts', String),
        ('error', String),
        ('date', String),
     
    ]
#crea una clase Tadd para la vista de add



# class customers(ComplexModel):
#     _type_info = [
#         ('reseller_username', String),
#         ('reseller_password', String),
#         ('page', String),
#     ]

# class customersQuery(ComplexModel):
#      _type_info = [
#         ('status', String),
#         ('counter', Integer),
#         ('taxpayer_id', String),
#         ('credit', Integer),
        
        
#      ]
    





#vista de quick_stamp, stamped, sign_stamp
class AcuseRecepcionCFDIQuickStamp(ComplexModel):
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
        ('incidencia', String),
    ]


    

#@user_passes_test(is_valid_user)
class SoapService(ServiceBase):
    # Obtener todos los usuarios
    

    @rpc(Unicode(nillable=False), _returns=Unicode)
    def hello(ctx, name):
        return 'Hello, {}'.format(name)

    @rpc(Integer(nillable=False), Integer(nillable=False), _returns=Integer)
    def sum(ctx, a, b):
        return int(a + b)
    
    @rpc(Unicode(nillable=False), Unicode(nillable=False), Unicode(nillable=False), _returns=AcuseRecepcionCFDI)
    def stamp(ctx, xml, username, password):
        # Verifica si hay un usuario activo que pertenesca al grupo Customers
        # Verifica si hay un usuario activo que pertenece al grupo Customers
        try:
            if DjangoCustomerRepository.validate_user(username, xml, password):
                print("El usuario cumple las condiciones")
        except PermissionDenied as e:
            arCFDI = AcuseRecepcionCFDI()
            arCFDI.incidencia = str(e)
            return arCFDI
        # xml = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPGNmZGk6Q29tcHJvYmFudGUgeG1sbnM6Y2ZkaT0iaHR0cDovL3d3dy5zYXQuZ29iLm14L2NmZC80IiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6c2NoZW1hTG9jYXRpb249Imh0dHA6Ly93d3cuc2F0LmdvYi5teC9jZmQvNCBodHRwOi8vd3d3LnNhdC5nb2IubXgvc2l0aW9faW50ZXJuZXQvY2ZkLzQvY2ZkdjQwLnhzZCIgVmVyc2lvbj0iNC4wIiBTZXJpZT0iQSIgRm9saW89IjE2N0FCQyIgRmVjaGE9IjIwMjMtMDktMjdUMjE6MTI6MjIiIFNlbGxvPSJMQXIrYUdBSzZURXM2MG5PZnVXNWxkZS8zb0hXTkdwcWRoQWRhSCtzUjArUDNnZURBalVab0lNaHBsRkVQeWpuWEg4K01Pbnc0a21hTVp2MWwrQThsVkNZb3hpN3FkQStJQUhUNWNobVppTXBubVBIV05pQTlQOGxNSFRSclJaenc0aGVqTG9lNnYyeWJwOTJPU3hjUHpWR1ZLTE8yMTJLbFlKc0dJZnJ6anNyWC8zQm8wM0VHTGFFcGdtYzBLVTJBczBvcUJuZHFlUmNidVRubjIveFVSQ1VDWk05QUJIV3Q2UTZmeXd0dGI5clh1OTB4ajZIUEFJMUM5Y1p2d3dFRWVFdFhKckl6ZzZoVWRIQ2Zib0dWeTBjeU9VWjA1ejVkMmtYRFFZVjlVUWc5MERsdmlhaU45MnNXLzFxZ2NZTm83Q3llckRhNXNjVlNOZkx6elJiZkE9PSIgRm9ybWFQYWdvPSIwMiIgTm9DZXJ0aWZpY2Fkbz0iMzAwMDEwMDAwMDA1MDAwMDM0MTYiIENlcnRpZmljYWRvPSJNSUlGc0RDQ0E1aWdBd0lCQWdJVU16QXdNREV3TURBd01EQTFNREF3TURNME1UWXdEUVlKS29aSWh2Y05BUUVMQlFBd2dnRXJNUTh3RFFZRFZRUUREQVpCUXlCVlFWUXhMakFzQmdOVkJBb01KVk5GVWxaSlEwbFBJRVJGSUVGRVRVbE9TVk5VVWtGRFNVOU9JRlJTU1VKVlZFRlNTVUV4R2pBWUJnTlZCQXNNRVZOQlZDMUpSVk1nUVhWMGFHOXlhWFI1TVNnd0pnWUpLb1pJaHZjTkFRa0JGaGx2YzJOaGNpNXRZWEowYVc1bGVrQnpZWFF1WjI5aUxtMTRNUjB3R3dZRFZRUUpEQlF6Y21FZ1kyVnljbUZrWVNCa1pTQmpZV3hwZWpFT01Bd0dBMVVFRVF3Rk1EWXpOekF4Q3pBSkJnTlZCQVlUQWsxWU1Sa3dGd1lEVlFRSURCQkRTVlZFUVVRZ1JFVWdUVVZZU1VOUE1SRXdEd1lEVlFRSERBaERUMWxQUVVOQlRqRVJNQThHQTFVRUxSTUlNaTQxTGpRdU5EVXhKVEFqQmdrcWhraUc5dzBCQ1FJVEZuSmxjM0J2Ym5OaFlteGxPaUJCUTBSTlFTMVRRVlF3SGhjTk1qTXdOVEU0TVRFME16VXhXaGNOTWpjd05URTRNVEUwTXpVeFdqQ0IxekVuTUNVR0ExVUVBeE1lUlZORFZVVk1RU0JMUlUxUVJWSWdWVkpIUVZSRklGTkJJRVJGSUVOV01TY3dKUVlEVlFRcEV4NUZVME5WUlV4QklFdEZUVkJGVWlCVlVrZEJWRVVnVTBFZ1JFVWdRMVl4SnpBbEJnTlZCQW9USGtWVFExVkZURUVnUzBWTlVFVlNJRlZTUjBGVVJTQlRRU0JFUlNCRFZqRWxNQ01HQTFVRUxSTWNSVXRWT1RBd016RTNNME01SUM4Z1ZrRkVRVGd3TURreU4wUktNekVlTUJ3R0ExVUVCUk1WSUM4Z1ZrRkVRVGd3TURreU4waFRVbE5TVERBMU1STXdFUVlEVlFRTEV3cFRkV04xY25OaGJDQXhNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXRtZWNPNm4yR1MwekwwMjVnYkhHUVZ4em5QRElDb1h6UjJ1VW5nejREcXhWVUMvdzljRTZGeFNpWG0yYXA4R2NqZzd3bWNaZm04NUVCYXhDeC8wSjJ1NUNxbmh6SW9HQ2RoQlB1aFdRbkloNVRMZ2ovWDZ1TnF1d1prS0NoYk5lOWFlRmlyVS9KYnlON0VnaWE5b0tIOUtaVXNvZGlNL3BXQUgwMFBDdG9LSjlPQmNTSE1xOFJxYTNLS29CY2ZrZzFacmd1ZWZmd1JMd3M5eU9jUldMYjAyc0RPUHpHSW0vakVGaWNWWXQySHcxcWRSRTV4bVRaN0FHRzBVSHMrdW5rR2pwQ1ZlSitCRUJuMEpQTFdWdkRLSFpBUU1qNnM1Qmt1MzUrZC9NeUFUa3BPUHNHVC9WVG5zb3V4ZWtEZmlrSkQxZjdBMVpwSmJxRHBrSm5zczN2UUlEQVFBQm94MHdHekFNQmdOVkhSTUJBZjhFQWpBQU1Bc0dBMVVkRHdRRUF3SUd3REFOQmdrcWhraUc5dzBCQVFzRkFBT0NBZ0VBRmFVZ2o1UHFndkppZ05NZ3RyZFhabmJQZlZCYnVrQWJXNE9HblVoTnJBN1NSQUFmdjJCU0drMTZQSTBuQk9yN3FGMm1JdG1CbmpnRXdrK0RUdjhacjd3NXFwN3ZsZUM2ZElzWkZOSm9hNlpuZHJFL2Y3S08xQ1lydUxYcjVnd0VrSXlHZko5Tnd5SWFndkhITXN6enlIaVNaSUE4NTBmV3RicXR5dGhwQWxpSjJqRjM1TTVwTlMrWVRrUkIrVDZML2M2bTAweW1OM3E5bFQxckIwM1l5d3hyTHJlUlNGWk9TcmJ3V2ZnMzRFSmJIZmJGWHBDU1ZZZEpSZmlWZHZIbmV3TjByNWZVbFB0UjlzdFFIeXVxZXd6ZGt5YjVqVFR3MDJEMmNVZkw1N3ZsUFN0Qmo3U0VpM3VPV3ZMcnNpRG5uQ0l4Uk1ZSjJVQTJrdERLSGsrelduc0RtYWVsZVN6b252MkNIVzQyeVhZUEN2V2k4OG9FMURKTllMTmtJanVhN014QW5rTlpiU2NOdzAxQTZ6YkxzWjN5OEc2ZUVZbnhTVFJmd2pkOEVQNGtkaUhOSmZ0bTdaNGlSVTdIT1ZoNzkvbFJXQitnZDE3MXMzZC9tSTlrdGUzTVJ5NlY4TU1FTUNBbk1ib0dwYW9vWXdnQW13Y2xJMlhaQ2N6TldYZmhhV2UwWlM1UG15dEQvR0RwWHprWDBvRWdZOUsvdVlvNVY3N05kWmJHQWpteWk4Y0UyQjJvZ3Z5YU4yWGZJSW5yWlBnRWZmSjRBQjdrRkEybXdlc2RMT0NoMEJMRDlpdG1DdmUzQTFGR1I0K3N0TzJBTlVvaUkzdzNUdjJ5UVNnNGJqZURsSjA4bFhhYUZDTFcycGVFWE1YalFVazdmbXBiNU1OdU9VVFc2QkU9IiBTdWJUb3RhbD0iNjQ3NC44MSIgTW9uZWRhPSJNWE4iIFRpcG9DYW1iaW89IjEiIFRvdGFsPSI3NTEwLjc3IiBUaXBvRGVDb21wcm9iYW50ZT0iSSIgRXhwb3J0YWNpb249IjAxIiBNZXRvZG9QYWdvPSJQVUUiIEx1Z2FyRXhwZWRpY2lvbj0iNTgwMDAiPgogIDxjZmRpOkNmZGlSZWxhY2lvbmFkb3MgVGlwb1JlbGFjaW9uPSIwMSI+CiAgICA8Y2ZkaTpDZmRpUmVsYWNpb25hZG8gVVVJRD0iQTM5REE2NkItNTJDQS00OUUzLTg3OUItNUMwNTE4NUIwRUY3Ii8+CiAgPC9jZmRpOkNmZGlSZWxhY2lvbmFkb3M+CiAgPGNmZGk6RW1pc29yIFJmYz0iRUtVOTAwMzE3M0M5IiBOb21icmU9IkVTQ1VFTEEgS0VNUEVSIFVSR0FURSIgUmVnaW1lbkZpc2NhbD0iNjAxIi8+CiAgPGNmZGk6UmVjZXB0b3IgUmZjPSJBQUJGODAwNjE0SEkwIiBOb21icmU9IkZFTElYIE1BTlVFTCBBTkRSQURFIEJBTExBRE8iIFVzb0NGREk9IlMwMSIgUmVnaW1lbkZpc2NhbFJlY2VwdG9yPSI2MTYiIERvbWljaWxpb0Zpc2NhbFJlY2VwdG9yPSI4NjQwMCIvPgogIDxjZmRpOkNvbmNlcHRvcz4KICAgIDxjZmRpOkNvbmNlcHRvIENsYXZlUHJvZFNlcnY9IjgwMTMxNTAwIiBDYW50aWRhZD0iMS4wMCIgQ2xhdmVVbmlkYWQ9IkNFIiBOb0lkZW50aWZpY2FjaW9uPSIwMDAwMSIgVW5pZGFkPSJDRSIgRGVzY3JpcGNpb249IkFSUkVOREFNSUVOVE8gREUgSlVBUkVaIFBURSAxMDgtQSIgVmFsb3JVbml0YXJpbz0iNjQ3NC44MSIgSW1wb3J0ZT0iNjQ3NC44MSIgT2JqZXRvSW1wPSIwMiI+CiAgICAgIDxjZmRpOkltcHVlc3Rvcz4KICAgICAgICA8Y2ZkaTpUcmFzbGFkb3M+CiAgICAgICAgICA8Y2ZkaTpUcmFzbGFkbyBCYXNlPSI2NDc0LjgxIiBJbXB1ZXN0bz0iMDAyIiBUaXBvRmFjdG9yPSJUYXNhIiBUYXNhT0N1b3RhPSIwLjE2MDAwMCIgSW1wb3J0ZT0iMTAzNS45NiIvPgogICAgICAgIDwvY2ZkaTpUcmFzbGFkb3M+CiAgICAgIDwvY2ZkaTpJbXB1ZXN0b3M+CiAgICA8L2NmZGk6Q29uY2VwdG8+CiAgPC9jZmRpOkNvbmNlcHRvcz4KICA8Y2ZkaTpJbXB1ZXN0b3MgVG90YWxJbXB1ZXN0b3NUcmFzbGFkYWRvcz0iMTAzNS45NiI+CiAgICA8Y2ZkaTpUcmFzbGFkb3M+CiAgICAgIDxjZmRpOlRyYXNsYWRvIEJhc2U9IjY0NzQuODEiIEltcG9ydGU9IjEwMzUuOTYiIEltcHVlc3RvPSIwMDIiIFRhc2FPQ3VvdGE9IjAuMTYwMDAwIiBUaXBvRmFjdG9yPSJUYXNhIi8+CiAgICA8L2NmZGk6VHJhc2xhZG9zPgogIDwvY2ZkaTpJbXB1ZXN0b3M+CjwvY2ZkaTpDb21wcm9iYW50ZT4K"
        # username = "antojitossol13@gmail.com"
        # password = ""
        # Autenticar al usuario utilizando el método de Django
        usuarioInvo = User.objects.filter(username=username).first()
        #Generar un token para el usuario invoice
        #if Tokens.objects.filter(userName=username, token=password).exists():
        # if Tokens.objects.filter(userName=username).exists():
        #     print('El usuario está en la tabla Tokens.')
        #     # Consuming the stamp service
        #     url = config('URL_TIMBRADO')
        #     client = Client(url,cache=None)
        #     contenido = client.service.stamp(xml,username,password)   
        # else:
        #     print('El usuario NO está en la tabla Tokens views.')
        #     print('add')
        #     user_service = User_Service.objects.filter(idUser=usuarioInvo).first()
        #     print('user_service:', user_service) 

        #     # Obtener la instancia de Service_Plan relacionada con el User_Service
        #     service_plans = Service_Plan.objects.filter(service=user_service.idService, plan=user_service.idPlan).first()
        #     print('service_plans:', service_plans)
        #     perfil = PerfilFiscalUser.objects.get(user=usuarioInvo)

        #     # Consuming the stamp service
        #     url = config('URL_TIMBRADO')
        #     client = Client(url,cache=None)
        #     contenido = client.service.stamp(xml,usuarioInvo.username,perfil.decrypt_token())        

        # Consuming the stamp service
        url = config('URL_TIMBRADO')
        client = Client(url,cache=None)
        contenido = client.service.stamp(xml,username,password)   
        
        #arCFDI = client.factory.create('tns:stampResult')
        arCFDI = AcuseRecepcionCFDI()
        incids = []
        
        #print(str(contenido.UUID))
        
        for key, value in Client.dict(contenido).items():   
            print(key, "->", value)
            if key=='xml':
                arCFDI.xml = contenido.xml
            elif key=='UUID' :     
                arCFDI.UUID = contenido.UUID
            elif key == 'Fecha' :
                arCFDI.Fecha = contenido.Fecha
            elif key == 'CodEstatus' :
                arCFDI.CodEstatus = contenido.CodEstatus
            elif key == 'SatSeal' :
                arCFDI.SatSeal = contenido.SatSeal
            elif key == 'NoCertificadoSAT' :
                arCFDI.NoCertificadoSAT = contenido.NoCertificadoSAT
            elif (key=='Incidencias'):
                incit = contenido.Incidencias
                if not(incit is None) :
                    print(incit)
                    for value in incit:
                        incid = Incidencia()
                        print(value[1][0])
                        incid.IdIncidencia = value[1][0].IdIncidencia
                        incid.RfcEmisor = value[1][0].RfcEmisor
                        incid.Uuid = value[1][0].Uuid
                        incid.CodigoError = value[1][0].CodigoError
                        incid.WorkProcessId = value[1][0].WorkProcessId if  hasattr( value[1][0], "WorkProcessId") else None
                        #incid.WorkProcessId = value[1][0].WorkProcessId
                        incid.MensajeIncidencia = value[1][0].MensajeIncidencia
                        incid.ExtraInfo = value[1][0].ExtraInfo
                        incid.NoCertificadoPac = value[1][0].NoCertificadoPac
                        incid.FechaRegistro = value[1][0].FechaRegistro
            
                        incids.append(incid)

        arCFDI.Incidencias = incids 
                
        if contenido:
            print('respuesta exitosa') 
           # Decodificar la cadena Base64
            decoded_bytes = base64.b64decode(xml)
            decoded_string = decoded_bytes.decode('utf-8')

            # Parsear el XML para extraer el RFC
            root = ET.fromstring(decoded_string)
            emisor = root.find('.//cfdi:Emisor', {'cfdi': 'http://www.sat.gob.mx/cfd/4'}).attrib['Rfc'] 
            print('RFC emisor:', emisor)

            # Usuario autenticado con éxito, ahora verificar si está en la tabla Tokens
            usuario = Tokens.objects.filter(userName=username).first()
            #if Tokens.objects.filter(userName=usuarioInvo, token=password).exists():
            if usuario is not None:
                print('El usuario está en la tabla Tokens.')
                # Buscar el usuario por nombre de usuario
                #usuario = Tokens.objects.get(userName=username, token=password)
                
                print(usuario)
                if PerfilFiscalUser.objects.filter(user=usuario.idUserParent, rfc =emisor).exists():
                    user_service = User_Service.objects.filter(idUser=usuario.idUserParent).first()
                    print('user_service:', user_service)

                    # Obtener la instancia de Service_Plan relacionada con el User_Service
                    service_plans = Service_Plan.objects.filter(service=user_service.idService, plan=user_service.idPlan).first()
                    print('service_plans:', service_plans)

                    #aumentar contador y definir el estatus
                    estatus='sin_timbrar'
                    if not arCFDI.Incidencias:
                        estatus='timbrada'

                        actualTimbre = TimbreUserPerfil.objects.get(userInvoice=usuario.idUserParent, estatus = 'A')

                        if actualTimbre.isOnDemmand == False:
                            actualTimbre.stamp=actualTimbre.stamp-1
                        actualTimbre.cont_stamped_user = actualTimbre.cont_stamped_user+1
                        actualTimbre.cont_stamped_day=  actualTimbre.cont_stamped_day+1
                        actualTimbre.save()
                        _sync_cfdi_enterprise_counter(usuario.idUserParent)

                        print('aumentar contador')

                        if actualTimbre.stamp == 0:
                            perfil = PerfilFiscalUser.objects.get(user=usuario.idUserParent)
                            perfil.estatus = 'S'
                            perfil.save()

                    # # Crear el registro de LogStamp
                    log_stamp = LogStamp.objects.create(
                        UUID=arCFDI.UUID,
                        Fecha=arCFDI.Fecha,
                        Emisor=emisor,
                        CodEstatus=arCFDI.CodEstatus,
                        SatSeal=arCFDI.SatSeal,
                        NoCertificadoSAT=arCFDI.NoCertificadoSAT,
                        idUser_ServicePlan=service_plans,
                        idUser=usuario.idUserParent,
                        status=estatus,
                        typeOperation='stamp'
                    )
                else:
                    user_service = User_Service.objects.filter(idUser=usuario.idUserParent).first()
                    print('user_service:', user_service)

                    # Obtener la instancia de Service_Plan relacionada con el User_Service
                    service_plans = Service_Plan.objects.filter(service=user_service.idService, plan=user_service.idPlan).first()
                    print('service_plans:', service_plans)

                    #aumentar contador y definir el estatus
                    estatus='sin_timbrar'
                    if not arCFDI.Incidencias:
                        estatus='timbrada'

                        cliente = Cliente.objects.get(user_cliente__idUser=usuario.idUserParent, rfc=emisor)
                        user_cliente = User_Cliente.objects.get(idCliente=cliente, idUser=usuario.idUserParent)
                        print(user_cliente.countStamp)

                        user_cliente.countStamp=user_cliente.countStamp+1
                        user_cliente.save()

                        actualTimbre = Timbre.objects.get(user_cliente=user_cliente, estatus = 'A')

                        if actualTimbre.isOnDemmand == False:
                            actualTimbre.stamp=actualTimbre.stamp-1
                        actualTimbre.cont_stamped_cliente= actualTimbre.cont_stamped_cliente+1
                        actualTimbre.cont_stamped_day=  actualTimbre.cont_stamped_day+1
                        actualTimbre.save()
                        _sync_cfdi_enterprise_counter(usuario.idUserParent)

                        print('aumentar contador')
                        print(user_cliente.countStamp)
                        if actualTimbre.stamp == 0:
                            user_cliente.estatus = 'S'
                            user_cliente.save()


                    # # Crear el registro de LogStamp
                    print('cliente token', usuario, usuario.id)
                    log_stamp = LogStamp.objects.create(
                        UUID=arCFDI.UUID,
                        Fecha=arCFDI.Fecha,
                        Emisor=emisor,
                        CodEstatus=arCFDI.CodEstatus,
                        SatSeal=arCFDI.SatSeal,
                        NoCertificadoSAT=arCFDI.NoCertificadoSAT,
                        idUser_ServicePlan=service_plans,
                        idUser=usuarioInvo,
                        status=estatus,
                        typeOperation='stamp'
                    )           
                    
                
            else:
                print('El usuario NO está en la tabla Tokens.')
                # Buscar el usuario por nombre de usuario
                print(usuarioInvo)  
                user_service = User_Service.objects.filter(idUser=usuarioInvo).first()
                print('user_service:', user_service) 

                # Obtener la instancia de Service_Plan relacionada con el User_Service
                service_plans = Service_Plan.objects.filter(service=user_service.idService).first()
                print('service_plans:', service_plans)

                #aumentar contador y definir el estatus
                estatus='sin_timbrar'
                if not arCFDI.Incidencias:
                    estatus='timbrada'

                    actualTimbre = TimbreUserPerfil.objects.get(userInvoice=usuarioInvo, estatus = 'A')
                    
                    if actualTimbre.isOnDemmand == False:
                        actualTimbre.stamp=actualTimbre.stamp-1
                    actualTimbre.cont_stamped_user= actualTimbre.cont_stamped_user+1
                    actualTimbre.cont_stamped_day=  actualTimbre.cont_stamped_day+1
                    actualTimbre.save()
                    _sync_cfdi_enterprise_counter(usuarioInvo)
                    
                    if actualTimbre.stamp == 0:
                            perfil = PerfilFiscalUser.objects.get(user=usuario.idUserParent)
                            perfil.estatus = 'S'
                            perfil.save()

                # # Crear el registro de LogStamp
                log_stamp = LogStamp.objects.create(
                    UUID=arCFDI.UUID,
                    Fecha=arCFDI.Fecha,
                    Emisor=emisor,
                    CodEstatus=arCFDI.CodEstatus,
                    SatSeal=arCFDI.SatSeal,
                    NoCertificadoSAT=arCFDI.NoCertificadoSAT,
                    idUser_ServicePlan=service_plans,
                    idUser=usuarioInvo,
                    status=estatus,
                    typeOperation='stamp'
                )       
                
            
        # arCFDI.xml = contenido.xml                
        # arCFDI.UUID = contenido.UUID
        # arCFDI.Fecha =  contenido.Fecha
        # arCFDI.CodEstatus =  contenido.CodEstatus
        # arCFDI.SatSeal =   contenido.SatSeal
        # arCFDI.NoCertificadoSAT =  contenido.NoCertificadoSAT
        
        # incit = contenido.Incidencias
        # if not(incit is None) :
        #     print(incit)
        #     for value in incit:
        #         incid = Incidencia()
        #         print(value[1][0])
        #         incid.IdIncidencia = value[1][0].IdIncidencia
        #         incid.RfcEmisor = value[1][0].RfcEmisor
        #         incid.Uuid = value[1][0].Uuid
        #         incid.CodigoError = value[1][0].CodigoError
        #         incid.WorkProcessId = value[1][0].WorkProcessId
        #         incid.MensajeIncidencia = value[1][0].MensajeIncidencia
        #         incid.ExtraInfo = value[1][0].ExtraInfo
        #         incid.NoCertificadoPac = value[1][0].NoCertificadoPac
        #         incid.FechaRegistro = value[1][0].FechaRegistro
            
        #         incids.append(incid)
                
        

        # # # dictresp = result.value.items()
        # # # for key, value in dictresp :
        # # #     if (isinstance( value, dict)):
        # # #         incid = Incidencia()
        # # #         for key, value in value:
        # # #             incid[key.split(':')[1]] = value
        # # #         incids.append(incid)
        # # #     else:
        # # #         eval('arCFDI.' + key.split(':')[1] + ' = value')
                                
        return arCFDI


   
    @rpc(Unicode(nillable=False), Unicode(nillable=False), Unicode(nillable=False), _returns=AcuseRecepcionCFDIQuery)
    def status_stamp(ctx, username, password, uuid):
        # Verifica si hay un usuario activo que pertenesca al grupo Customers
        if DjangoCustomerRepository.validate() == True:
            print("Al menos un usuario cumple las condiciones")
        else:
            return "Error: No tienes permisos para acceder a esta página."
        # xml = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPGNmZGk6Q29tcHJvYmFudGUgeG1sbnM6Y2ZkaT0iaHR0cDovL3d3dy5zYXQuZ29iLm14L2NmZC80IiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6c2NoZW1hTG9jYXRpb249Imh0dHA6Ly93d3cuc2F0LmdvYi5teC9jZmQvNCBodHRwOi8vd3d3LnNhdC5nb2IubXgvc2l0aW9faW50ZXJuZXQvY2ZkLzQvY2ZkdjQwLnhzZCIgVmVyc2lvbj0iNC4wIiBTZXJpZT0iQSIgRm9saW89IjE2N0FCQyIgRmVjaGE9IjIwMjMtMDktMjdUMjE6MTI6MjIiIFNlbGxvPSJMQXIrYUdBSzZURXM2MG5PZnVXNWxkZS8zb0hXTkdwcWRoQWRhSCtzUjArUDNnZURBalVab0lNaHBsRkVQeWpuWEg4K01Pbnc0a21hTVp2MWwrQThsVkNZb3hpN3FkQStJQUhUNWNobVppTXBubVBIV05pQTlQOGxNSFRSclJaenc0aGVqTG9lNnYyeWJwOTJPU3hjUHpWR1ZLTE8yMTJLbFlKc0dJZnJ6anNyWC8zQm8wM0VHTGFFcGdtYzBLVTJBczBvcUJuZHFlUmNidVRubjIveFVSQ1VDWk05QUJIV3Q2UTZmeXd0dGI5clh1OTB4ajZIUEFJMUM5Y1p2d3dFRWVFdFhKckl6ZzZoVWRIQ2Zib0dWeTBjeU9VWjA1ejVkMmtYRFFZVjlVUWc5MERsdmlhaU45MnNXLzFxZ2NZTm83Q3llckRhNXNjVlNOZkx6elJiZkE9PSIgRm9ybWFQYWdvPSIwMiIgTm9DZXJ0aWZpY2Fkbz0iMzAwMDEwMDAwMDA1MDAwMDM0MTYiIENlcnRpZmljYWRvPSJNSUlGc0RDQ0E1aWdBd0lCQWdJVU16QXdNREV3TURBd01EQTFNREF3TURNME1UWXdEUVlKS29aSWh2Y05BUUVMQlFBd2dnRXJNUTh3RFFZRFZRUUREQVpCUXlCVlFWUXhMakFzQmdOVkJBb01KVk5GVWxaSlEwbFBJRVJGSUVGRVRVbE9TVk5VVWtGRFNVOU9JRlJTU1VKVlZFRlNTVUV4R2pBWUJnTlZCQXNNRVZOQlZDMUpSVk1nUVhWMGFHOXlhWFI1TVNnd0pnWUpLb1pJaHZjTkFRa0JGaGx2YzJOaGNpNXRZWEowYVc1bGVrQnpZWFF1WjI5aUxtMTRNUjB3R3dZRFZRUUpEQlF6Y21FZ1kyVnljbUZrWVNCa1pTQmpZV3hwZWpFT01Bd0dBMVVFRVF3Rk1EWXpOekF4Q3pBSkJnTlZCQVlUQWsxWU1Sa3dGd1lEVlFRSURCQkRTVlZFUVVRZ1JFVWdUVVZZU1VOUE1SRXdEd1lEVlFRSERBaERUMWxQUVVOQlRqRVJNQThHQTFVRUxSTUlNaTQxTGpRdU5EVXhKVEFqQmdrcWhraUc5dzBCQ1FJVEZuSmxjM0J2Ym5OaFlteGxPaUJCUTBSTlFTMVRRVlF3SGhjTk1qTXdOVEU0TVRFME16VXhXaGNOTWpjd05URTRNVEUwTXpVeFdqQ0IxekVuTUNVR0ExVUVBeE1lUlZORFZVVk1RU0JMUlUxUVJWSWdWVkpIUVZSRklGTkJJRVJGSUVOV01TY3dKUVlEVlFRcEV4NUZVME5WUlV4QklFdEZUVkJGVWlCVlVrZEJWRVVnVTBFZ1JFVWdRMVl4SnpBbEJnTlZCQW9USGtWVFExVkZURUVnUzBWTlVFVlNJRlZTUjBGVVJTQlRRU0JFUlNCRFZqRWxNQ01HQTFVRUxSTWNSVXRWT1RBd016RTNNME01SUM4Z1ZrRkVRVGd3TURreU4wUktNekVlTUJ3R0ExVUVCUk1WSUM4Z1ZrRkVRVGd3TURreU4waFRVbE5TVERBMU1STXdFUVlEVlFRTEV3cFRkV04xY25OaGJDQXhNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXRtZWNPNm4yR1MwekwwMjVnYkhHUVZ4em5QRElDb1h6UjJ1VW5nejREcXhWVUMvdzljRTZGeFNpWG0yYXA4R2NqZzd3bWNaZm04NUVCYXhDeC8wSjJ1NUNxbmh6SW9HQ2RoQlB1aFdRbkloNVRMZ2ovWDZ1TnF1d1prS0NoYk5lOWFlRmlyVS9KYnlON0VnaWE5b0tIOUtaVXNvZGlNL3BXQUgwMFBDdG9LSjlPQmNTSE1xOFJxYTNLS29CY2ZrZzFacmd1ZWZmd1JMd3M5eU9jUldMYjAyc0RPUHpHSW0vakVGaWNWWXQySHcxcWRSRTV4bVRaN0FHRzBVSHMrdW5rR2pwQ1ZlSitCRUJuMEpQTFdWdkRLSFpBUU1qNnM1Qmt1MzUrZC9NeUFUa3BPUHNHVC9WVG5zb3V4ZWtEZmlrSkQxZjdBMVpwSmJxRHBrSm5zczN2UUlEQVFBQm94MHdHekFNQmdOVkhSTUJBZjhFQWpBQU1Bc0dBMVVkRHdRRUF3SUd3REFOQmdrcWhraUc5dzBCQVFzRkFBT0NBZ0VBRmFVZ2o1UHFndkppZ05NZ3RyZFhabmJQZlZCYnVrQWJXNE9HblVoTnJBN1NSQUFmdjJCU0drMTZQSTBuQk9yN3FGMm1JdG1CbmpnRXdrK0RUdjhacjd3NXFwN3ZsZUM2ZElzWkZOSm9hNlpuZHJFL2Y3S08xQ1lydUxYcjVnd0VrSXlHZko5Tnd5SWFndkhITXN6enlIaVNaSUE4NTBmV3RicXR5dGhwQWxpSjJqRjM1TTVwTlMrWVRrUkIrVDZML2M2bTAweW1OM3E5bFQxckIwM1l5d3hyTHJlUlNGWk9TcmJ3V2ZnMzRFSmJIZmJGWHBDU1ZZZEpSZmlWZHZIbmV3TjByNWZVbFB0UjlzdFFIeXVxZXd6ZGt5YjVqVFR3MDJEMmNVZkw1N3ZsUFN0Qmo3U0VpM3VPV3ZMcnNpRG5uQ0l4Uk1ZSjJVQTJrdERLSGsrelduc0RtYWVsZVN6b252MkNIVzQyeVhZUEN2V2k4OG9FMURKTllMTmtJanVhN014QW5rTlpiU2NOdzAxQTZ6YkxzWjN5OEc2ZUVZbnhTVFJmd2pkOEVQNGtkaUhOSmZ0bTdaNGlSVTdIT1ZoNzkvbFJXQitnZDE3MXMzZC9tSTlrdGUzTVJ5NlY4TU1FTUNBbk1ib0dwYW9vWXdnQW13Y2xJMlhaQ2N6TldYZmhhV2UwWlM1UG15dEQvR0RwWHprWDBvRWdZOUsvdVlvNVY3N05kWmJHQWpteWk4Y0UyQjJvZ3Z5YU4yWGZJSW5yWlBnRWZmSjRBQjdrRkEybXdlc2RMT0NoMEJMRDlpdG1DdmUzQTFGR1I0K3N0TzJBTlVvaUkzdzNUdjJ5UVNnNGJqZURsSjA4bFhhYUZDTFcycGVFWE1YalFVazdmbXBiNU1OdU9VVFc2QkU9IiBTdWJUb3RhbD0iNjQ3NC44MSIgTW9uZWRhPSJNWE4iIFRpcG9DYW1iaW89IjEiIFRvdGFsPSI3NTEwLjc3IiBUaXBvRGVDb21wcm9iYW50ZT0iSSIgRXhwb3J0YWNpb249IjAxIiBNZXRvZG9QYWdvPSJQVUUiIEx1Z2FyRXhwZWRpY2lvbj0iNTgwMDAiPgogIDxjZmRpOkNmZGlSZWxhY2lvbmFkb3MgVGlwb1JlbGFjaW9uPSIwMSI+CiAgICA8Y2ZkaTpDZmRpUmVsYWNpb25hZG8gVVVJRD0iQTM5REE2NkItNTJDQS00OUUzLTg3OUItNUMwNTE4NUIwRUY3Ii8+CiAgPC9jZmRpOkNmZGlSZWxhY2lvbmFkb3M+CiAgPGNmZGk6RW1pc29yIFJmYz0iRUtVOTAwMzE3M0M5IiBOb21icmU9IkVTQ1VFTEEgS0VNUEVSIFVSR0FURSIgUmVnaW1lbkZpc2NhbD0iNjAxIi8+CiAgPGNmZGk6UmVjZXB0b3IgUmZjPSJBQUJGODAwNjE0SEkwIiBOb21icmU9IkZFTElYIE1BTlVFTCBBTkRSQURFIEJBTExBRE8iIFVzb0NGREk9IlMwMSIgUmVnaW1lbkZpc2NhbFJlY2VwdG9yPSI2MTYiIERvbWljaWxpb0Zpc2NhbFJlY2VwdG9yPSI4NjQwMCIvPgogIDxjZmRpOkNvbmNlcHRvcz4KICAgIDxjZmRpOkNvbmNlcHRvIENsYXZlUHJvZFNlcnY9IjgwMTMxNTAwIiBDYW50aWRhZD0iMS4wMCIgQ2xhdmVVbmlkYWQ9IkNFIiBOb0lkZW50aWZpY2FjaW9uPSIwMDAwMSIgVW5pZGFkPSJDRSIgRGVzY3JpcGNpb249IkFSUkVOREFNSUVOVE8gREUgSlVBUkVaIFBURSAxMDgtQSIgVmFsb3JVbml0YXJpbz0iNjQ3NC44MSIgSW1wb3J0ZT0iNjQ3NC44MSIgT2JqZXRvSW1wPSIwMiI+CiAgICAgIDxjZmRpOkltcHVlc3Rvcz4KICAgICAgICA8Y2ZkaTpUcmFzbGFkb3M+CiAgICAgICAgICA8Y2ZkaTpUcmFzbGFkbyBCYXNlPSI2NDc0LjgxIiBJbXB1ZXN0bz0iMDAyIiBUaXBvRmFjdG9yPSJUYXNhIiBUYXNhT0N1b3RhPSIwLjE2MDAwMCIgSW1wb3J0ZT0iMTAzNS45NiIvPgogICAgICAgIDwvY2ZkaTpUcmFzbGFkb3M+CiAgICAgIDwvY2ZkaTpJbXB1ZXN0b3M+CiAgICA8L2NmZGk6Q29uY2VwdG8+CiAgPC9jZmRpOkNvbmNlcHRvcz4KICA8Y2ZkaTpJbXB1ZXN0b3MgVG90YWxJbXB1ZXN0b3NUcmFzbGFkYWRvcz0iMTAzNS45NiI+CiAgICA8Y2ZkaTpUcmFzbGFkb3M+CiAgICAgIDxjZmRpOlRyYXNsYWRvIEJhc2U9IjY0NzQuODEiIEltcG9ydGU9IjEwMzUuOTYiIEltcHVlc3RvPSIwMDIiIFRhc2FPQ3VvdGE9IjAuMTYwMDAwIiBUaXBvRmFjdG9yPSJUYXNhIi8+CiAgICA8L2NmZGk6VHJhc2xhZG9zPgogIDwvY2ZkaTpJbXB1ZXN0b3M+CjwvY2ZkaTpDb21wcm9iYW50ZT4K"
        # username = "antojitossol13@gmail.com"
        # password = "1nT36R4c!0N"
        # uuid = 7FCD44E2-6884-53AF-ABA2-2A5660E571FE

        # Consuming the stamp service
        url = config('URL_TIMBRADO')
        client = Client(url,cache=None)
        contenido = client.service.query_pending(username,password,uuid)        

         # Crear instancia de AcuseRecepcionCFDIQuery
        response = AcuseRecepcionCFDIQuery()

        # Configurar los atributos del response según el formato deseado
        for key, value in Client.dict(contenido).items():   
            print(key, "->", value)
            if key=='status':
                response.status = value
            elif key=='xml' :     
                response.xml = value
            elif key == 'uuid' :
                response.uuid = value
            elif key == 'uuid_status' :
                response.uuid_status = value
            elif key == 'next_attempt' :
                response.next_attempt = value
            elif key == 'attempts' :
                response.attempts = value
            elif key == 'date' :
                response.date = value
            elif key == 'error' :
                response.error = value

        return response

    @rpc(Unicode(nillable=False), Unicode(nillable=False), Unicode(nillable=False), _returns=AcuseRecepcionCFDIQuickStamp)
    def fast_stamp(ctx, xml, username, password):
        # Verifica si hay un usuario activo que pertenesca al grupo Customers
        if DjangoCustomerRepository.validate_user(username, xml, ) == True:
            print("El usuario cumple las condiciones")
        else:
            arCFDI = AcuseRecepcionCFDI()
            arCFDI.incidencia = 'Créditos para timbrado/cancelación agotados'
            return arCFDI
        # xml = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPGNmZGk6Q29tcHJvYmFudGUgeG1sbnM6Y2ZkaT0iaHR0cDovL3d3dy5zYXQuZ29iLm14L2NmZC80IiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6c2NoZW1hTG9jYXRpb249Imh0dHA6Ly93d3cuc2F0LmdvYi5teC9jZmQvNCBodHRwOi8vd3d3LnNhdC5nb2IubXgvc2l0aW9faW50ZXJuZXQvY2ZkLzQvY2ZkdjQwLnhzZCIgVmVyc2lvbj0iNC4wIiBTZXJpZT0iQSIgRm9saW89IjE2N0FCQyIgRmVjaGE9IjIwMjMtMDktMjdUMjE6MTI6MjIiIFNlbGxvPSJMQXIrYUdBSzZURXM2MG5PZnVXNWxkZS8zb0hXTkdwcWRoQWRhSCtzUjArUDNnZURBalVab0lNaHBsRkVQeWpuWEg4K01Pbnc0a21hTVp2MWwrQThsVkNZb3hpN3FkQStJQUhUNWNobVppTXBubVBIV05pQTlQOGxNSFRSclJaenc0aGVqTG9lNnYyeWJwOTJPU3hjUHpWR1ZLTE8yMTJLbFlKc0dJZnJ6anNyWC8zQm8wM0VHTGFFcGdtYzBLVTJBczBvcUJuZHFlUmNidVRubjIveFVSQ1VDWk05QUJIV3Q2UTZmeXd0dGI5clh1OTB4ajZIUEFJMUM5Y1p2d3dFRWVFdFhKckl6ZzZoVWRIQ2Zib0dWeTBjeU9VWjA1ejVkMmtYRFFZVjlVUWc5MERsdmlhaU45MnNXLzFxZ2NZTm83Q3llckRhNXNjVlNOZkx6elJiZkE9PSIgRm9ybWFQYWdvPSIwMiIgTm9DZXJ0aWZpY2Fkbz0iMzAwMDEwMDAwMDA1MDAwMDM0MTYiIENlcnRpZmljYWRvPSJNSUlGc0RDQ0E1aWdBd0lCQWdJVU16QXdNREV3TURBd01EQTFNREF3TURNME1UWXdEUVlKS29aSWh2Y05BUUVMQlFBd2dnRXJNUTh3RFFZRFZRUUREQVpCUXlCVlFWUXhMakFzQmdOVkJBb01KVk5GVWxaSlEwbFBJRVJGSUVGRVRVbE9TVk5VVWtGRFNVOU9JRlJTU1VKVlZFRlNTVUV4R2pBWUJnTlZCQXNNRVZOQlZDMUpSVk1nUVhWMGFHOXlhWFI1TVNnd0pnWUpLb1pJaHZjTkFRa0JGaGx2YzJOaGNpNXRZWEowYVc1bGVrQnpZWFF1WjI5aUxtMTRNUjB3R3dZRFZRUUpEQlF6Y21FZ1kyVnljbUZrWVNCa1pTQmpZV3hwZWpFT01Bd0dBMVVFRVF3Rk1EWXpOekF4Q3pBSkJnTlZCQVlUQWsxWU1Sa3dGd1lEVlFRSURCQkRTVlZFUVVRZ1JFVWdUVVZZU1VOUE1SRXdEd1lEVlFRSERBaERUMWxQUVVOQlRqRVJNQThHQTFVRUxSTUlNaTQxTGpRdU5EVXhKVEFqQmdrcWhraUc5dzBCQ1FJVEZuSmxjM0J2Ym5OaFlteGxPaUJCUTBSTlFTMVRRVlF3SGhjTk1qTXdOVEU0TVRFME16VXhXaGNOTWpjd05URTRNVEUwTXpVeFdqQ0IxekVuTUNVR0ExVUVBeE1lUlZORFZVVk1RU0JMUlUxUVJWSWdWVkpIUVZSRklGTkJJRVJGSUVOV01TY3dKUVlEVlFRcEV4NUZVME5WUlV4QklFdEZUVkJGVWlCVlVrZEJWRVVnVTBFZ1JFVWdRMVl4SnpBbEJnTlZCQW9USGtWVFExVkZURUVnUzBWTlVFVlNJRlZTUjBGVVJTQlRRU0JFUlNCRFZqRWxNQ01HQTFVRUxSTWNSVXRWT1RBd016RTNNME01SUM4Z1ZrRkVRVGd3TURreU4wUktNekVlTUJ3R0ExVUVCUk1WSUM4Z1ZrRkVRVGd3TURreU4waFRVbE5TVERBMU1STXdFUVlEVlFRTEV3cFRkV04xY25OaGJDQXhNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXRtZWNPNm4yR1MwekwwMjVnYkhHUVZ4em5QRElDb1h6UjJ1VW5nejREcXhWVUMvdzljRTZGeFNpWG0yYXA4R2NqZzd3bWNaZm04NUVCYXhDeC8wSjJ1NUNxbmh6SW9HQ2RoQlB1aFdRbkloNVRMZ2ovWDZ1TnF1d1prS0NoYk5lOWFlRmlyVS9KYnlON0VnaWE5b0tIOUtaVXNvZGlNL3BXQUgwMFBDdG9LSjlPQmNTSE1xOFJxYTNLS29CY2ZrZzFacmd1ZWZmd1JMd3M5eU9jUldMYjAyc0RPUHpHSW0vakVGaWNWWXQySHcxcWRSRTV4bVRaN0FHRzBVSHMrdW5rR2pwQ1ZlSitCRUJuMEpQTFdWdkRLSFpBUU1qNnM1Qmt1MzUrZC9NeUFUa3BPUHNHVC9WVG5zb3V4ZWtEZmlrSkQxZjdBMVpwSmJxRHBrSm5zczN2UUlEQVFBQm94MHdHekFNQmdOVkhSTUJBZjhFQWpBQU1Bc0dBMVVkRHdRRUF3SUd3REFOQmdrcWhraUc5dzBCQVFzRkFBT0NBZ0VBRmFVZ2o1UHFndkppZ05NZ3RyZFhabmJQZlZCYnVrQWJXNE9HblVoTnJBN1NSQUFmdjJCU0drMTZQSTBuQk9yN3FGMm1JdG1CbmpnRXdrK0RUdjhacjd3NXFwN3ZsZUM2ZElzWkZOSm9hNlpuZHJFL2Y3S08xQ1lydUxYcjVnd0VrSXlHZko5Tnd5SWFndkhITXN6enlIaVNaSUE4NTBmV3RicXR5dGhwQWxpSjJqRjM1TTVwTlMrWVRrUkIrVDZML2M2bTAweW1OM3E5bFQxckIwM1l5d3hyTHJlUlNGWk9TcmJ3V2ZnMzRFSmJIZmJGWHBDU1ZZZEpSZmlWZHZIbmV3TjByNWZVbFB0UjlzdFFIeXVxZXd6ZGt5YjVqVFR3MDJEMmNVZkw1N3ZsUFN0Qmo3U0VpM3VPV3ZMcnNpRG5uQ0l4Uk1ZSjJVQTJrdERLSGsrelduc0RtYWVsZVN6b252MkNIVzQyeVhZUEN2V2k4OG9FMURKTllMTmtJanVhN014QW5rTlpiU2NOdzAxQTZ6YkxzWjN5OEc2ZUVZbnhTVFJmd2pkOEVQNGtkaUhOSmZ0bTdaNGlSVTdIT1ZoNzkvbFJXQitnZDE3MXMzZC9tSTlrdGUzTVJ5NlY4TU1FTUNBbk1ib0dwYW9vWXdnQW13Y2xJMlhaQ2N6TldYZmhhV2UwWlM1UG15dEQvR0RwWHprWDBvRWdZOUsvdVlvNVY3N05kWmJHQWpteWk4Y0UyQjJvZ3Z5YU4yWGZJSW5yWlBnRWZmSjRBQjdrRkEybXdlc2RMT0NoMEJMRDlpdG1DdmUzQTFGR1I0K3N0TzJBTlVvaUkzdzNUdjJ5UVNnNGJqZURsSjA4bFhhYUZDTFcycGVFWE1YalFVazdmbXBiNU1OdU9VVFc2QkU9IiBTdWJUb3RhbD0iNjQ3NC44MSIgTW9uZWRhPSJNWE4iIFRpcG9DYW1iaW89IjEiIFRvdGFsPSI3NTEwLjc3IiBUaXBvRGVDb21wcm9iYW50ZT0iSSIgRXhwb3J0YWNpb249IjAxIiBNZXRvZG9QYWdvPSJQVUUiIEx1Z2FyRXhwZWRpY2lvbj0iNTgwMDAiPgogIDxjZmRpOkNmZGlSZWxhY2lvbmFkb3MgVGlwb1JlbGFjaW9uPSIwMSI+CiAgICA8Y2ZkaTpDZmRpUmVsYWNpb25hZG8gVVVJRD0iQTM5REE2NkItNTJDQS00OUUzLTg3OUItNUMwNTE4NUIwRUY3Ii8+CiAgPC9jZmRpOkNmZGlSZWxhY2lvbmFkb3M+CiAgPGNmZGk6RW1pc29yIFJmYz0iRUtVOTAwMzE3M0M5IiBOb21icmU9IkVTQ1VFTEEgS0VNUEVSIFVSR0FURSIgUmVnaW1lbkZpc2NhbD0iNjAxIi8+CiAgPGNmZGk6UmVjZXB0b3IgUmZjPSJBQUJGODAwNjE0SEkwIiBOb21icmU9IkZFTElYIE1BTlVFTCBBTkRSQURFIEJBTExBRE8iIFVzb0NGREk9IlMwMSIgUmVnaW1lbkZpc2NhbFJlY2VwdG9yPSI2MTYiIERvbWljaWxpb0Zpc2NhbFJlY2VwdG9yPSI4NjQwMCIvPgogIDxjZmRpOkNvbmNlcHRvcz4KICAgIDxjZmRpOkNvbmNlcHRvIENsYXZlUHJvZFNlcnY9IjgwMTMxNTAwIiBDYW50aWRhZD0iMS4wMCIgQ2xhdmVVbmlkYWQ9IkNFIiBOb0lkZW50aWZpY2FjaW9uPSIwMDAwMSIgVW5pZGFkPSJDRSIgRGVzY3JpcGNpb249IkFSUkVOREFNSUVOVE8gREUgSlVBUkVaIFBURSAxMDgtQSIgVmFsb3JVbml0YXJpbz0iNjQ3NC44MSIgSW1wb3J0ZT0iNjQ3NC44MSIgT2JqZXRvSW1wPSIwMiI+CiAgICAgIDxjZmRpOkltcHVlc3Rvcz4KICAgICAgICA8Y2ZkaTpUcmFzbGFkb3M+CiAgICAgICAgICA8Y2ZkaTpUcmFzbGFkbyBCYXNlPSI2NDc0LjgxIiBJbXB1ZXN0bz0iMDAyIiBUaXBvRmFjdG9yPSJUYXNhIiBUYXNhT0N1b3RhPSIwLjE2MDAwMCIgSW1wb3J0ZT0iMTAzNS45NiIvPgogICAgICAgIDwvY2ZkaTpUcmFzbGFkb3M+CiAgICAgIDwvY2ZkaTpJbXB1ZXN0b3M+CiAgICA8L2NmZGk6Q29uY2VwdG8+CiAgPC9jZmRpOkNvbmNlcHRvcz4KICA8Y2ZkaTpJbXB1ZXN0b3MgVG90YWxJbXB1ZXN0b3NUcmFzbGFkYWRvcz0iMTAzNS45NiI+CiAgICA8Y2ZkaTpUcmFzbGFkb3M+CiAgICAgIDxjZmRpOlRyYXNsYWRvIEJhc2U9IjY0NzQuODEiIEltcG9ydGU9IjEwMzUuOTYiIEltcHVlc3RvPSIwMDIiIFRhc2FPQ3VvdGE9IjAuMTYwMDAwIiBUaXBvRmFjdG9yPSJUYXNhIi8+CiAgICA8L2NmZGk6VHJhc2xhZG9zPgogIDwvY2ZkaTpJbXB1ZXN0b3M+CjwvY2ZkaTpDb21wcm9iYW50ZT4K"
        # username = "antojitossol13@gmail.com"
        # password = "1nT36R4c!0N"
        # uuid = 7FCD44E2-6884-53AF-ABA2-2A5660E571FE

        # Consuming the stamp service
        url = config('URL_TIMBRADO')
        client = Client(url,cache=None)
        contenido = client.service.quick_stamp(xml,username,password)      
        contenido2 = client.service.stamped(xml,username,password)    

         # Crear instancia de AcuseRecepcionCFDIQuery
        response = AcuseRecepcionCFDIQuickStamp()
        incids = []

        for key, value in Client.dict(contenido2).items():   
            print(key, "->", value)
            if key=='xml':
                response.xml = contenido2.xml
            elif key == 'SatSeal' :
                response.SatSeal = contenido2.SatSeal
        # Configurar los atributos del response según el formato deseado
        for key, value in Client.dict(contenido).items():   
            print(key, "->", value)
            if key=='UUID' :     
                response.UUID = contenido.UUID
            elif key == 'faultstring' :
                response.faultstring = contenido.faultstring
            elif key == 'Fecha' :
                response.Fecha = contenido.Fecha
            elif key == 'CodEstatus' :
                response.CodEstatus = contenido.CodEstatus
            elif key == 'faultcode' :
                response.faultcode = contenido.faultcode
            elif key == 'NoCertificadoSAT' :
                response.NoCertificadoSAT = contenido.NoCertificadoSAT
            elif (key=='Incidencias'):
                incit = contenido.Incidencias
                if not(incit is None) :
                    for value in incit:
                        incid = Incidencia()
                        incid.IdIncidencia = value[1][0].IdIncidencia
                        incid.Uuid = value[1][0].Uuid
                        incid.CodigoError = value[1][0].CodigoError
                        #incid.WorkProcessId = value[1][0].WorkProcessId
                        incid.WorkProcessId = value[1][0].WorkProcessId if  hasattr( value[1][0], "WorkProcessId") else None
                        incid.MensajeIncidencia = value[1][0].MensajeIncidencia
                        incid.RfcEmisor = value[1][0].RfcEmisor
                        incid.ExtraInfo = value[1][0].ExtraInfo
                        incid.NoCertificadoPac = value[1][0].NoCertificadoPac
                        incid.FechaRegistro = value[1][0].FechaRegistro
            
                        incids.append(incid)
        
        response.Incidencias = incids 

        return response
    @rpc(Unicode(nillable=False), Unicode(nillable=False), Unicode(nillable=False), _returns=AcuseRecepcionCFDIQuickStamp)
    def stamped(ctx, xml, username, password):
        # Verifica si hay un usuario activo que pertenesca al grupo Customers
        if DjangoCustomerRepository.validate_user(username, xml) == True:
            print("El usuario cumple las condiciones")
        else:
            arCFDI = AcuseRecepcionCFDI()
            arCFDI.incidencia = 'Créditos para timbrado/cancelación agotados'
            return arCFDI
        # xml = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPGNmZGk6Q29tcHJvYmFudGUgeG1sbnM6Y2ZkaT0iaHR0cDovL3d3dy5zYXQuZ29iLm14L2NmZC80IiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6c2NoZW1hTG9jYXRpb249Imh0dHA6Ly93d3cuc2F0LmdvYi5teC9jZmQvNCBodHRwOi8vd3d3LnNhdC5nb2IubXgvc2l0aW9faW50ZXJuZXQvY2ZkLzQvY2ZkdjQwLnhzZCIgVmVyc2lvbj0iNC4wIiBTZXJpZT0iQSIgRm9saW89IjE2N0FCQyIgRmVjaGE9IjIwMjMtMDktMjdUMjE6MTI6MjIiIFNlbGxvPSJMQXIrYUdBSzZURXM2MG5PZnVXNWxkZS8zb0hXTkdwcWRoQWRhSCtzUjArUDNnZURBalVab0lNaHBsRkVQeWpuWEg4K01Pbnc0a21hTVp2MWwrQThsVkNZb3hpN3FkQStJQUhUNWNobVppTXBubVBIV05pQTlQOGxNSFRSclJaenc0aGVqTG9lNnYyeWJwOTJPU3hjUHpWR1ZLTE8yMTJLbFlKc0dJZnJ6anNyWC8zQm8wM0VHTGFFcGdtYzBLVTJBczBvcUJuZHFlUmNidVRubjIveFVSQ1VDWk05QUJIV3Q2UTZmeXd0dGI5clh1OTB4ajZIUEFJMUM5Y1p2d3dFRWVFdFhKckl6ZzZoVWRIQ2Zib0dWeTBjeU9VWjA1ejVkMmtYRFFZVjlVUWc5MERsdmlhaU45MnNXLzFxZ2NZTm83Q3llckRhNXNjVlNOZkx6elJiZkE9PSIgRm9ybWFQYWdvPSIwMiIgTm9DZXJ0aWZpY2Fkbz0iMzAwMDEwMDAwMDA1MDAwMDM0MTYiIENlcnRpZmljYWRvPSJNSUlGc0RDQ0E1aWdBd0lCQWdJVU16QXdNREV3TURBd01EQTFNREF3TURNME1UWXdEUVlKS29aSWh2Y05BUUVMQlFBd2dnRXJNUTh3RFFZRFZRUUREQVpCUXlCVlFWUXhMakFzQmdOVkJBb01KVk5GVWxaSlEwbFBJRVJGSUVGRVRVbE9TVk5VVWtGRFNVOU9JRlJTU1VKVlZFRlNTVUV4R2pBWUJnTlZCQXNNRVZOQlZDMUpSVk1nUVhWMGFHOXlhWFI1TVNnd0pnWUpLb1pJaHZjTkFRa0JGaGx2YzJOaGNpNXRZWEowYVc1bGVrQnpZWFF1WjI5aUxtMTRNUjB3R3dZRFZRUUpEQlF6Y21FZ1kyVnljbUZrWVNCa1pTQmpZV3hwZWpFT01Bd0dBMVVFRVF3Rk1EWXpOekF4Q3pBSkJnTlZCQVlUQWsxWU1Sa3dGd1lEVlFRSURCQkRTVlZFUVVRZ1JFVWdUVVZZU1VOUE1SRXdEd1lEVlFRSERBaERUMWxQUVVOQlRqRVJNQThHQTFVRUxSTUlNaTQxTGpRdU5EVXhKVEFqQmdrcWhraUc5dzBCQ1FJVEZuSmxjM0J2Ym5OaFlteGxPaUJCUTBSTlFTMVRRVlF3SGhjTk1qTXdOVEU0TVRFME16VXhXaGNOTWpjd05URTRNVEUwTXpVeFdqQ0IxekVuTUNVR0ExVUVBeE1lUlZORFZVVk1RU0JMUlUxUVJWSWdWVkpIUVZSRklGTkJJRVJGSUVOV01TY3dKUVlEVlFRcEV4NUZVME5WUlV4QklFdEZUVkJGVWlCVlVrZEJWRVVnVTBFZ1JFVWdRMVl4SnpBbEJnTlZCQW9USGtWVFExVkZURUVnUzBWTlVFVlNJRlZTUjBGVVJTQlRRU0JFUlNCRFZqRWxNQ01HQTFVRUxSTWNSVXRWT1RBd016RTNNME01SUM4Z1ZrRkVRVGd3TURreU4wUktNekVlTUJ3R0ExVUVCUk1WSUM4Z1ZrRkVRVGd3TURreU4waFRVbE5TVERBMU1STXdFUVlEVlFRTEV3cFRkV04xY25OaGJDQXhNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXRtZWNPNm4yR1MwekwwMjVnYkhHUVZ4em5QRElDb1h6UjJ1VW5nejREcXhWVUMvdzljRTZGeFNpWG0yYXA4R2NqZzd3bWNaZm04NUVCYXhDeC8wSjJ1NUNxbmh6SW9HQ2RoQlB1aFdRbkloNVRMZ2ovWDZ1TnF1d1prS0NoYk5lOWFlRmlyVS9KYnlON0VnaWE5b0tIOUtaVXNvZGlNL3BXQUgwMFBDdG9LSjlPQmNTSE1xOFJxYTNLS29CY2ZrZzFacmd1ZWZmd1JMd3M5eU9jUldMYjAyc0RPUHpHSW0vakVGaWNWWXQySHcxcWRSRTV4bVRaN0FHRzBVSHMrdW5rR2pwQ1ZlSitCRUJuMEpQTFdWdkRLSFpBUU1qNnM1Qmt1MzUrZC9NeUFUa3BPUHNHVC9WVG5zb3V4ZWtEZmlrSkQxZjdBMVpwSmJxRHBrSm5zczN2UUlEQVFBQm94MHdHekFNQmdOVkhSTUJBZjhFQWpBQU1Bc0dBMVVkRHdRRUF3SUd3REFOQmdrcWhraUc5dzBCQVFzRkFBT0NBZ0VBRmFVZ2o1UHFndkppZ05NZ3RyZFhabmJQZlZCYnVrQWJXNE9HblVoTnJBN1NSQUFmdjJCU0drMTZQSTBuQk9yN3FGMm1JdG1CbmpnRXdrK0RUdjhacjd3NXFwN3ZsZUM2ZElzWkZOSm9hNlpuZHJFL2Y3S08xQ1lydUxYcjVnd0VrSXlHZko5Tnd5SWFndkhITXN6enlIaVNaSUE4NTBmV3RicXR5dGhwQWxpSjJqRjM1TTVwTlMrWVRrUkIrVDZML2M2bTAweW1OM3E5bFQxckIwM1l5d3hyTHJlUlNGWk9TcmJ3V2ZnMzRFSmJIZmJGWHBDU1ZZZEpSZmlWZHZIbmV3TjByNWZVbFB0UjlzdFFIeXVxZXd6ZGt5YjVqVFR3MDJEMmNVZkw1N3ZsUFN0Qmo3U0VpM3VPV3ZMcnNpRG5uQ0l4Uk1ZSjJVQTJrdERLSGsrelduc0RtYWVsZVN6b252MkNIVzQyeVhZUEN2V2k4OG9FMURKTllMTmtJanVhN014QW5rTlpiU2NOdzAxQTZ6YkxzWjN5OEc2ZUVZbnhTVFJmd2pkOEVQNGtkaUhOSmZ0bTdaNGlSVTdIT1ZoNzkvbFJXQitnZDE3MXMzZC9tSTlrdGUzTVJ5NlY4TU1FTUNBbk1ib0dwYW9vWXdnQW13Y2xJMlhaQ2N6TldYZmhhV2UwWlM1UG15dEQvR0RwWHprWDBvRWdZOUsvdVlvNVY3N05kWmJHQWpteWk4Y0UyQjJvZ3Z5YU4yWGZJSW5yWlBnRWZmSjRBQjdrRkEybXdlc2RMT0NoMEJMRDlpdG1DdmUzQTFGR1I0K3N0TzJBTlVvaUkzdzNUdjJ5UVNnNGJqZURsSjA4bFhhYUZDTFcycGVFWE1YalFVazdmbXBiNU1OdU9VVFc2QkU9IiBTdWJUb3RhbD0iNjQ3NC44MSIgTW9uZWRhPSJNWE4iIFRpcG9DYW1iaW89IjEiIFRvdGFsPSI3NTEwLjc3IiBUaXBvRGVDb21wcm9iYW50ZT0iSSIgRXhwb3J0YWNpb249IjAxIiBNZXRvZG9QYWdvPSJQVUUiIEx1Z2FyRXhwZWRpY2lvbj0iNTgwMDAiPgogIDxjZmRpOkNmZGlSZWxhY2lvbmFkb3MgVGlwb1JlbGFjaW9uPSIwMSI+CiAgICA8Y2ZkaTpDZmRpUmVsYWNpb25hZG8gVVVJRD0iQTM5REE2NkItNTJDQS00OUUzLTg3OUItNUMwNTE4NUIwRUY3Ii8+CiAgPC9jZmRpOkNmZGlSZWxhY2lvbmFkb3M+CiAgPGNmZGk6RW1pc29yIFJmYz0iRUtVOTAwMzE3M0M5IiBOb21icmU9IkVTQ1VFTEEgS0VNUEVSIFVSR0FURSIgUmVnaW1lbkZpc2NhbD0iNjAxIi8+CiAgPGNmZGk6UmVjZXB0b3IgUmZjPSJBQUJGODAwNjE0SEkwIiBOb21icmU9IkZFTElYIE1BTlVFTCBBTkRSQURFIEJBTExBRE8iIFVzb0NGREk9IlMwMSIgUmVnaW1lbkZpc2NhbFJlY2VwdG9yPSI2MTYiIERvbWljaWxpb0Zpc2NhbFJlY2VwdG9yPSI4NjQwMCIvPgogIDxjZmRpOkNvbmNlcHRvcz4KICAgIDxjZmRpOkNvbmNlcHRvIENsYXZlUHJvZFNlcnY9IjgwMTMxNTAwIiBDYW50aWRhZD0iMS4wMCIgQ2xhdmVVbmlkYWQ9IkNFIiBOb0lkZW50aWZpY2FjaW9uPSIwMDAwMSIgVW5pZGFkPSJDRSIgRGVzY3JpcGNpb249IkFSUkVOREFNSUVOVE8gREUgSlVBUkVaIFBURSAxMDgtQSIgVmFsb3JVbml0YXJpbz0iNjQ3NC44MSIgSW1wb3J0ZT0iNjQ3NC44MSIgT2JqZXRvSW1wPSIwMiI+CiAgICAgIDxjZmRpOkltcHVlc3Rvcz4KICAgICAgICA8Y2ZkaTpUcmFzbGFkb3M+CiAgICAgICAgICA8Y2ZkaTpUcmFzbGFkbyBCYXNlPSI2NDc0LjgxIiBJbXB1ZXN0bz0iMDAyIiBUaXBvRmFjdG9yPSJUYXNhIiBUYXNhT0N1b3RhPSIwLjE2MDAwMCIgSW1wb3J0ZT0iMTAzNS45NiIvPgogICAgICAgIDwvY2ZkaTpUcmFzbGFkb3M+CiAgICAgIDwvY2ZkaTpJbXB1ZXN0b3M+CiAgICA8L2NmZGk6Q29uY2VwdG8+CiAgPC9jZmRpOkNvbmNlcHRvcz4KICA8Y2ZkaTpJbXB1ZXN0b3MgVG90YWxJbXB1ZXN0b3NUcmFzbGFkYWRvcz0iMTAzNS45NiI+CiAgICA8Y2ZkaTpUcmFzbGFkb3M+CiAgICAgIDxjZmRpOlRyYXNsYWRvIEJhc2U9IjY0NzQuODEiIEltcG9ydGU9IjEwMzUuOTYiIEltcHVlc3RvPSIwMDIiIFRhc2FPQ3VvdGE9IjAuMTYwMDAwIiBUaXBvRmFjdG9yPSJUYXNhIi8+CiAgICA8L2NmZGk6VHJhc2xhZG9zPgogIDwvY2ZkaTpJbXB1ZXN0b3M+CjwvY2ZkaTpDb21wcm9iYW50ZT4K"
        # username = "antojitossol13@gmail.com"
        # password = "1nT36R4c!0N"
        # uuid = 7FCD44E2-6884-53AF-ABA2-2A5660E571FE

        # Consuming the stamp service
        url = config('URL_TIMBRADO')
        client = Client(url,cache=None)    
        contenido = client.service.stamped(xml,username,password)    

         # Crear instancia de AcuseRecepcionCFDIQuery
        response = AcuseRecepcionCFDIQuickStamp()
        incids = []

        # Configurar los atributos del response según el formato deseado
        for key, value in Client.dict(contenido).items():   
            print(key, "->", value)
            if key=='xml':
                response.xml = contenido.xml
            elif key=='UUID' :     
                response.UUID = contenido.UUID
            elif key == 'faultstring' :
                response.faultstring = contenido.faultstring
            elif key == 'Fecha' :
                response.Fecha = contenido.Fecha
            elif key == 'CodEstatus' :
                response.CodEstatus = contenido.CodEstatus
            elif key == 'faultcode' :
                response.faultcode = contenido.faultcode
            elif key == 'SatSeal' :
                response.SatSeal = contenido.SatSeal
            elif key == 'NoCertificadoSAT' :
                response.NoCertificadoSAT = contenido.NoCertificadoSAT
            elif (key=='Incidencias'):
                incit = contenido.Incidencias
                if not(incit is None) :
                    for value in incit:
                        incid = Incidencia()
                        incid.IdIncidencia = value[1][0].IdIncidencia
                        incid.Uuid = value[1][0].Uuid
                        incid.CodigoError = value[1][0].CodigoError
                        incid.WorkProcessId = value[1][0].WorkProcessId if  hasattr( value[1][0], "WorkProcessId") else None
                        #incid.WorkProcessId = value[1][0].WorkProcessId
                        incid.MensajeIncidencia = value[1][0].MensajeIncidencia
                        incid.RfcEmisor = value[1][0].RfcEmisor
                        incid.ExtraInfo = value[1][0].ExtraInfo
                        incid.NoCertificadoPac = value[1][0].NoCertificadoPac
                        incid.FechaRegistro = value[1][0].FechaRegistro
            
                        incids.append(incid)
        
        response.Incidencias = incids 

        return response
    
    @rpc(Unicode(nillable=False), Unicode(nillable=False), Unicode(nillable=False), _returns=AcuseRecepcionCFDIQuickStamp)
    def sign_stamp(ctx, xml, username, password):
        # Verifica si hay un usuario activo que pertenece al grupo Customers
        try:
            if DjangoCustomerRepository.validate_user(username, xml, password):
                print("El usuario cumple las condiciones")
        except PermissionDenied as e:
            arCFDI = AcuseRecepcionCFDI()
            arCFDI.incidencia = str(e)
            return arCFDI
        # xml = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPGNmZGk6Q29tcHJvYmFudGUgeG1sbnM6Y2ZkaT0iaHR0cDovL3d3dy5zYXQuZ29iLm14L2NmZC80IiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6c2NoZW1hTG9jYXRpb249Imh0dHA6Ly93d3cuc2F0LmdvYi5teC9jZmQvNCBodHRwOi8vd3d3LnNhdC5nb2IubXgvc2l0aW9faW50ZXJuZXQvY2ZkLzQvY2ZkdjQwLnhzZCIgVmVyc2lvbj0iNC4wIiBTZXJpZT0iQSIgRm9saW89IjE2N0FCQyIgRmVjaGE9IjIwMjMtMDktMjdUMjE6MTI6MjIiIFNlbGxvPSJMQXIrYUdBSzZURXM2MG5PZnVXNWxkZS8zb0hXTkdwcWRoQWRhSCtzUjArUDNnZURBalVab0lNaHBsRkVQeWpuWEg4K01Pbnc0a21hTVp2MWwrQThsVkNZb3hpN3FkQStJQUhUNWNobVppTXBubVBIV05pQTlQOGxNSFRSclJaenc0aGVqTG9lNnYyeWJwOTJPU3hjUHpWR1ZLTE8yMTJLbFlKc0dJZnJ6anNyWC8zQm8wM0VHTGFFcGdtYzBLVTJBczBvcUJuZHFlUmNidVRubjIveFVSQ1VDWk05QUJIV3Q2UTZmeXd0dGI5clh1OTB4ajZIUEFJMUM5Y1p2d3dFRWVFdFhKckl6ZzZoVWRIQ2Zib0dWeTBjeU9VWjA1ejVkMmtYRFFZVjlVUWc5MERsdmlhaU45MnNXLzFxZ2NZTm83Q3llckRhNXNjVlNOZkx6elJiZkE9PSIgRm9ybWFQYWdvPSIwMiIgTm9DZXJ0aWZpY2Fkbz0iMzAwMDEwMDAwMDA1MDAwMDM0MTYiIENlcnRpZmljYWRvPSJNSUlGc0RDQ0E1aWdBd0lCQWdJVU16QXdNREV3TURBd01EQTFNREF3TURNME1UWXdEUVlKS29aSWh2Y05BUUVMQlFBd2dnRXJNUTh3RFFZRFZRUUREQVpCUXlCVlFWUXhMakFzQmdOVkJBb01KVk5GVWxaSlEwbFBJRVJGSUVGRVRVbE9TVk5VVWtGRFNVOU9JRlJTU1VKVlZFRlNTVUV4R2pBWUJnTlZCQXNNRVZOQlZDMUpSVk1nUVhWMGFHOXlhWFI1TVNnd0pnWUpLb1pJaHZjTkFRa0JGaGx2YzJOaGNpNXRZWEowYVc1bGVrQnpZWFF1WjI5aUxtMTRNUjB3R3dZRFZRUUpEQlF6Y21FZ1kyVnljbUZrWVNCa1pTQmpZV3hwZWpFT01Bd0dBMVVFRVF3Rk1EWXpOekF4Q3pBSkJnTlZCQVlUQWsxWU1Sa3dGd1lEVlFRSURCQkRTVlZFUVVRZ1JFVWdUVVZZU1VOUE1SRXdEd1lEVlFRSERBaERUMWxQUVVOQlRqRVJNQThHQTFVRUxSTUlNaTQxTGpRdU5EVXhKVEFqQmdrcWhraUc5dzBCQ1FJVEZuSmxjM0J2Ym5OaFlteGxPaUJCUTBSTlFTMVRRVlF3SGhjTk1qTXdOVEU0TVRFME16VXhXaGNOTWpjd05URTRNVEUwTXpVeFdqQ0IxekVuTUNVR0ExVUVBeE1lUlZORFZVVk1RU0JMUlUxUVJWSWdWVkpIUVZSRklGTkJJRVJGSUVOV01TY3dKUVlEVlFRcEV4NUZVME5WUlV4QklFdEZUVkJGVWlCVlVrZEJWRVVnVTBFZ1JFVWdRMVl4SnpBbEJnTlZCQW9USGtWVFExVkZURUVnUzBWTlVFVlNJRlZTUjBGVVJTQlRRU0JFUlNCRFZqRWxNQ01HQTFVRUxSTWNSVXRWT1RBd016RTNNME01SUM4Z1ZrRkVRVGd3TURreU4wUktNekVlTUJ3R0ExVUVCUk1WSUM4Z1ZrRkVRVGd3TURreU4waFRVbE5TVERBMU1STXdFUVlEVlFRTEV3cFRkV04xY25OaGJDQXhNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXRtZWNPNm4yR1MwekwwMjVnYkhHUVZ4em5QRElDb1h6UjJ1VW5nejREcXhWVUMvdzljRTZGeFNpWG0yYXA4R2NqZzd3bWNaZm04NUVCYXhDeC8wSjJ1NUNxbmh6SW9HQ2RoQlB1aFdRbkloNVRMZ2ovWDZ1TnF1d1prS0NoYk5lOWFlRmlyVS9KYnlON0VnaWE5b0tIOUtaVXNvZGlNL3BXQUgwMFBDdG9LSjlPQmNTSE1xOFJxYTNLS29CY2ZrZzFacmd1ZWZmd1JMd3M5eU9jUldMYjAyc0RPUHpHSW0vakVGaWNWWXQySHcxcWRSRTV4bVRaN0FHRzBVSHMrdW5rR2pwQ1ZlSitCRUJuMEpQTFdWdkRLSFpBUU1qNnM1Qmt1MzUrZC9NeUFUa3BPUHNHVC9WVG5zb3V4ZWtEZmlrSkQxZjdBMVpwSmJxRHBrSm5zczN2UUlEQVFBQm94MHdHekFNQmdOVkhSTUJBZjhFQWpBQU1Bc0dBMVVkRHdRRUF3SUd3REFOQmdrcWhraUc5dzBCQVFzRkFBT0NBZ0VBRmFVZ2o1UHFndkppZ05NZ3RyZFhabmJQZlZCYnVrQWJXNE9HblVoTnJBN1NSQUFmdjJCU0drMTZQSTBuQk9yN3FGMm1JdG1CbmpnRXdrK0RUdjhacjd3NXFwN3ZsZUM2ZElzWkZOSm9hNlpuZHJFL2Y3S08xQ1lydUxYcjVnd0VrSXlHZko5Tnd5SWFndkhITXN6enlIaVNaSUE4NTBmV3RicXR5dGhwQWxpSjJqRjM1TTVwTlMrWVRrUkIrVDZML2M2bTAweW1OM3E5bFQxckIwM1l5d3hyTHJlUlNGWk9TcmJ3V2ZnMzRFSmJIZmJGWHBDU1ZZZEpSZmlWZHZIbmV3TjByNWZVbFB0UjlzdFFIeXVxZXd6ZGt5YjVqVFR3MDJEMmNVZkw1N3ZsUFN0Qmo3U0VpM3VPV3ZMcnNpRG5uQ0l4Uk1ZSjJVQTJrdERLSGsrelduc0RtYWVsZVN6b252MkNIVzQyeVhZUEN2V2k4OG9FMURKTllMTmtJanVhN014QW5rTlpiU2NOdzAxQTZ6YkxzWjN5OEc2ZUVZbnhTVFJmd2pkOEVQNGtkaUhOSmZ0bTdaNGlSVTdIT1ZoNzkvbFJXQitnZDE3MXMzZC9tSTlrdGUzTVJ5NlY4TU1FTUNBbk1ib0dwYW9vWXdnQW13Y2xJMlhaQ2N6TldYZmhhV2UwWlM1UG15dEQvR0RwWHprWDBvRWdZOUsvdVlvNVY3N05kWmJHQWpteWk4Y0UyQjJvZ3Z5YU4yWGZJSW5yWlBnRWZmSjRBQjdrRkEybXdlc2RMT0NoMEJMRDlpdG1DdmUzQTFGR1I0K3N0TzJBTlVvaUkzdzNUdjJ5UVNnNGJqZURsSjA4bFhhYUZDTFcycGVFWE1YalFVazdmbXBiNU1OdU9VVFc2QkU9IiBTdWJUb3RhbD0iNjQ3NC44MSIgTW9uZWRhPSJNWE4iIFRpcG9DYW1iaW89IjEiIFRvdGFsPSI3NTEwLjc3IiBUaXBvRGVDb21wcm9iYW50ZT0iSSIgRXhwb3J0YWNpb249IjAxIiBNZXRvZG9QYWdvPSJQVUUiIEx1Z2FyRXhwZWRpY2lvbj0iNTgwMDAiPgogIDxjZmRpOkNmZGlSZWxhY2lvbmFkb3MgVGlwb1JlbGFjaW9uPSIwMSI+CiAgICA8Y2ZkaTpDZmRpUmVsYWNpb25hZG8gVVVJRD0iQTM5REE2NkItNTJDQS00OUUzLTg3OUItNUMwNTE4NUIwRUY3Ii8+CiAgPC9jZmRpOkNmZGlSZWxhY2lvbmFkb3M+CiAgPGNmZGk6RW1pc29yIFJmYz0iRUtVOTAwMzE3M0M5IiBOb21icmU9IkVTQ1VFTEEgS0VNUEVSIFVSR0FURSIgUmVnaW1lbkZpc2NhbD0iNjAxIi8+CiAgPGNmZGk6UmVjZXB0b3IgUmZjPSJBQUJGODAwNjE0SEkwIiBOb21icmU9IkZFTElYIE1BTlVFTCBBTkRSQURFIEJBTExBRE8iIFVzb0NGREk9IlMwMSIgUmVnaW1lbkZpc2NhbFJlY2VwdG9yPSI2MTYiIERvbWljaWxpb0Zpc2NhbFJlY2VwdG9yPSI4NjQwMCIvPgogIDxjZmRpOkNvbmNlcHRvcz4KICAgIDxjZmRpOkNvbmNlcHRvIENsYXZlUHJvZFNlcnY9IjgwMTMxNTAwIiBDYW50aWRhZD0iMS4wMCIgQ2xhdmVVbmlkYWQ9IkNFIiBOb0lkZW50aWZpY2FjaW9uPSIwMDAwMSIgVW5pZGFkPSJDRSIgRGVzY3JpcGNpb249IkFSUkVOREFNSUVOVE8gREUgSlVBUkVaIFBURSAxMDgtQSIgVmFsb3JVbml0YXJpbz0iNjQ3NC44MSIgSW1wb3J0ZT0iNjQ3NC44MSIgT2JqZXRvSW1wPSIwMiI+CiAgICAgIDxjZmRpOkltcHVlc3Rvcz4KICAgICAgICA8Y2ZkaTpUcmFzbGFkb3M+CiAgICAgICAgICA8Y2ZkaTpUcmFzbGFkbyBCYXNlPSI2NDc0LjgxIiBJbXB1ZXN0bz0iMDAyIiBUaXBvRmFjdG9yPSJUYXNhIiBUYXNhT0N1b3RhPSIwLjE2MDAwMCIgSW1wb3J0ZT0iMTAzNS45NiIvPgogICAgICAgIDwvY2ZkaTpUcmFzbGFkb3M+CiAgICAgIDwvY2ZkaTpJbXB1ZXN0b3M+CiAgICA8L2NmZGk6Q29uY2VwdG8+CiAgPC9jZmRpOkNvbmNlcHRvcz4KICA8Y2ZkaTpJbXB1ZXN0b3MgVG90YWxJbXB1ZXN0b3NUcmFzbGFkYWRvcz0iMTAzNS45NiI+CiAgICA8Y2ZkaTpUcmFzbGFkb3M+CiAgICAgIDxjZmRpOlRyYXNsYWRvIEJhc2U9IjY0NzQuODEiIEltcG9ydGU9IjEwMzUuOTYiIEltcHVlc3RvPSIwMDIiIFRhc2FPQ3VvdGE9IjAuMTYwMDAwIiBUaXBvRmFjdG9yPSJUYXNhIi8+CiAgICA8L2NmZGk6VHJhc2xhZG9zPgogIDwvY2ZkaTpJbXB1ZXN0b3M+CjwvY2ZkaTpDb21wcm9iYW50ZT4K"
        # username = "antojitossol13@gmail.com"
        # password = "1nT36R4c!0N"
        # uuid = 7FCD44E2-6884-53AF-ABA2-2A5660E571FE
        
        # Autenticar al usuario utilizando el método de Django
        usuarioInvo = authenticate(username=username, password=password)
        #Generar un token para el usuario invoice
        #if Tokens.objects.filter(userName=username, token=password).exists():
        if Tokens.objects.filter(userName=username).exists():
            # Cronometrar el tiempo de respuesta de la llamada al servicio SOAP
            inicio = time.time()  # Marca el tiempo de inicio
            # Consuming the stamp service
            url = config('URL_TIMBRADO')
            client = Client(url,cache=None)    
            contenido = client.service.sign_stamp(xml,username,password)    
            
            fin = time.time()  # Marca el tiempo de finalización
            tiempo_transcurrido = fin - inicio
            print(f"Tiempo de respuesta del servicio SOAP (sign_stamp con token): {tiempo_transcurrido:.4f} segundos")

        else:
            print('El usuario NO está en la tabla Tokens.')
            print('add')
            user_service = User_Service.objects.filter(idUser=usuarioInvo).first()
            print('user_service:', user_service) 

            # Obtener la instancia de Service_Plan relacionada con el User_Service
            service_plans = Service_Plan.objects.filter(service=user_service.idService).first()
            print('service_plans:', service_plans)
            perfil = PerfilFiscalUser.objects.get(user=usuarioInvo)

            # Cronometrar el tiempo de respuesta de la llamada al servicio SOAP
            inicio = time.time()  # Marca el tiempo de inicio
            
            # Consuming the stamp service
            url = config('URL_TIMBRADO')
            client = Client(url,cache=None)
            contenido = client.service.sign_stamp(xml,usuarioInvo.username,perfil.decrypt_token())  

            fin = time.time()  # Marca el tiempo de finalización
            tiempo_transcurrido = fin - inicio
            print(f"Tiempo de respuesta del servicio SOAP (sign_stamp con token): {tiempo_transcurrido:.4f} segundos")
         # Crear instancia de AcuseRecepcionCFDIQuery
        response = AcuseRecepcionCFDIQuickStamp()
        incids = []

        # Configurar los atributos del response según el formato deseado
        for key, value in Client.dict(contenido).items():   
            print(key, "->", value)
            if key=='xml':
                response.xml = contenido.xml
            elif key=='UUID' :     
                response.UUID = contenido.UUID
            elif key == 'faultstring' :
                response.faultstring = contenido.faultstring
            elif key == 'Fecha' :
                response.Fecha = contenido.Fecha
            elif key == 'CodEstatus' :
                response.CodEstatus = contenido.CodEstatus
            elif key == 'faultcode' :
                response.faultcode = contenido.faultcode
            elif key == 'SatSeal' :
                response.SatSeal = contenido.SatSeal
            elif key == 'NoCertificadoSAT' :
                response.NoCertificadoSAT = contenido.NoCertificadoSAT
            elif (key=='Incidencias'):
                incit = contenido.Incidencias
                if not(incit is None) :
                    for value in incit:
                        incid = Incidencia()
                        incid.IdIncidencia = value[1][0].IdIncidencia
                        incid.Uuid = value[1][0].Uuid
                        incid.CodigoError = value[1][0].CodigoError
                        incid.WorkProcessId = value[1][0].WorkProcessId if  hasattr( value[1][0], "WorkProcessId") else None
                        #incid.WorkProcessId = value[1][0].WorkProcessId
                        incid.MensajeIncidencia = value[1][0].MensajeIncidencia
                        incid.RfcEmisor = value[1][0].RfcEmisor
                        incid.ExtraInfo = value[1][0].ExtraInfo
                        incid.NoCertificadoPac = value[1][0].NoCertificadoPac
                        incid.FechaRegistro = value[1][0].FechaRegistro
            
                        incids.append(incid)
        
        response.Incidencias = incids 
        
        if contenido:
            print('respuesta exitosa') 
           # Decodificar la cadena Base64
            decoded_bytes = base64.b64decode(xml)
            decoded_string = decoded_bytes.decode('utf-8')

            # Parsear el XML para extraer el RFC
            root = ET.fromstring(decoded_string)
            emisor = root.find('.//cfdi:Emisor', {'cfdi': 'http://www.sat.gob.mx/cfd/4'}).attrib['Rfc'] 
            print('RFC emisor:', emisor)

            # Usuario autenticado con éxito, ahora verificar si está en la tabla Tokens
            #if Tokens.objects.filter(userName=usuarioInvo, token=password).exists():
            if Tokens.objects.filter(userName=usuarioInvo).exists():
                print('El usuario está en la tabla Tokens.')
                # Buscar el usuario por nombre de usuario
                #usuario = Tokens.objects.get(userName=username, token=password)
                usuario = Tokens.objects.get(userName=username)
                print(usuario)
                if PerfilFiscalUser.objects.filter(user=usuario.idUserParent, rfc =emisor).exists():  
                    user_service = User_Service.objects.filter(idUser=usuario.idUserParent).first()
                    print('user_service:', user_service) 

                    # Obtener la instancia de Service_Plan relacionada con el User_Service
                    service_plans = Service_Plan.objects.filter(service=user_service.idService, plan=user_service.idPlan).first()
                    print('service_plans:', service_plans)

                    #aumentar contador y definir el estatus
                    estatus='sin_timbrar'
                    if not response.Incidencias:
                        estatus='firmada_timbrada'

                        
                        actualTimbre = TimbreUserPerfil.objects.get(userInvoice=usuario.idUserParent, estatus = 'A')
                        
                        if actualTimbre.isOnDemmand == False:
                            actualTimbre.stamp=actualTimbre.stamp-1
                        actualTimbre.cont_stamped_user= actualTimbre.cont_stamped_user+1
                        actualTimbre.cont_stamped_day=  actualTimbre.cont_stamped_day+1
                        actualTimbre.save()
                        _sync_cfdi_enterprise_counter(usuario.idUserParent)
                        
                        print('aumentar contador')
                        
                        if actualTimbre.stamp == 0:
                            perfil = PerfilFiscalUser.objects.get(user=usuario.idUserParent)
                            perfil.estatus = 'S'
                            perfil.save()
                    
                    # # Crear el registro de LogStamp
                    log_stamp = LogStamp.objects.create(
                        UUID=response.UUID,
                        Fecha=response.Fecha,
                        Emisor=emisor,
                        CodEstatus=response.CodEstatus,
                        SatSeal=response.SatSeal,
                        NoCertificadoSAT=response.NoCertificadoSAT,
                        idUser_ServicePlan=service_plans,
                        idUser=usuario.idUserParent,
                        status=estatus,
                        typeOperation='sign_stamp'
                    )        
                else:    
                    user_service = User_Service.objects.filter(idUser=usuario.idUserParent).first()
                    print('user_service:', user_service) 

                    # Obtener la instancia de Service_Plan relacionada con el User_Service
                    service_plans = Service_Plan.objects.filter(service=user_service.idService).first()
                    print('service_plans:', service_plans)

                    #aumentar contador y definir el estatus
                    print('incidencias', response.Incidencias)
                    estatus='sin_timbrar'
                    if not response.Incidencias:
                        estatus='firmada_timbrada'
                        
                        cliente = Cliente.objects.get(user_cliente__idUser=usuario.idUserParent ,rfc=emisor)
                        user_cliente = User_Cliente.objects.get(idCliente=cliente, idUser=usuario.idUserParent)

                        print(user_cliente.countStamp)
                        user_cliente.countStamp=user_cliente.countStamp+1
                        user_cliente.save()
                        print('aumentar contador')
                        print(user_cliente.countStamp)

                        actualTimbre = Timbre.objects.get(user_cliente=user_cliente, estatus = 'A')
                        
                        if actualTimbre.isOnDemmand == False:
                            actualTimbre.stamp=actualTimbre.stamp-1
                        actualTimbre.cont_stamped_cliente= actualTimbre.cont_stamped_cliente+1
                        actualTimbre.cont_stamped_day=  actualTimbre.cont_stamped_day+1
                        actualTimbre.save()
                        _sync_cfdi_enterprise_counter(usuario.idUserParent)
                        
                        if actualTimbre.stamp == 0:
                            user_cliente.estatus = 'S'
                            user_cliente.save()

                    # # Crear el registro de LogStamp
                    log_stamp = LogStamp.objects.create(
                        UUID=response.UUID,
                        Fecha=response.Fecha,
                        Emisor=emisor,
                        CodEstatus=response.CodEstatus,
                        SatSeal=response.SatSeal,
                        NoCertificadoSAT=response.NoCertificadoSAT,
                        idUser_ServicePlan=service_plans,
                        idUser=usuarioInvo,
                        status=estatus,
                        typeOperation='sign_stamp'
                    )  
            else:
                print('El usuario NO está en la tabla Tokens.')
                # Buscar el usuario por nombre de usuario
                print(usuarioInvo)  
                user_service = User_Service.objects.filter(idUser=usuarioInvo).first()
                print('user_service:', user_service) 

                # Obtener la instancia de Service_Plan relacionada con el User_Service
                service_plans = Service_Plan.objects.filter(service=user_service.idService, plan=user_service.idPlan).first()
                print('service_plans:', service_plans)

                #aumentar contador y definir el estatus
                estatus='sin_timbrar'
                if not response.Incidencias:
                    estatus='firmada_timbrada'

                    
                    actualTimbre = TimbreUserPerfil.objects.get(userInvoice=usuarioInvo, estatus = 'A')
                    
                    if actualTimbre.isOnDemmand == False:
                        actualTimbre.stamp=actualTimbre.stamp-1
                    actualTimbre.cont_stamped_user= actualTimbre.cont_stamped_user+1
                    actualTimbre.cont_stamped_day=  actualTimbre.cont_stamped_day+1
                    actualTimbre.save()
                    _sync_cfdi_enterprise_counter(usuarioInvo)
                    
                    print('aumentar contador')
                    
                    if actualTimbre.stamp == 0:
                        perfil = PerfilFiscalUser.objects.get(user=usuarioInvo)
                        perfil.estatus = 'S'
                        perfil.save()
                   
                # # Crear el registro de LogStamp
                log_stamp = LogStamp.objects.create(
                    UUID=response.UUID,
                    Fecha=response.Fecha,
                    Emisor=emisor,
                    CodEstatus=response.CodEstatus,
                    SatSeal=response.SatSeal,
                    NoCertificadoSAT=response.NoCertificadoSAT,
                    idUser_ServicePlan=service_plans,
                    idUser=usuarioInvo,
                    status=estatus,
                    typeOperation='sign_stamp'
                )        


        return response

class UUID(ComplexModel):
    UUID = XmlAttribute(String)
    FolioSustitucion= XmlAttribute(String)
    Motivo= XmlAttribute(String)
    
class Folio(ComplexModel):
    _type_info = [
        ('UUID', String),
        ('EstatusUUID', String),
        ('EstatusCancelacion', String),
    ]
    
class CancelaCFDIResult(ComplexModel):
    _type_info = [
        ('Folios', Array(Folio)),
        ('Acuse', String),
        ('Fecha', String),
        ('RfcEmisor', String),
        ('CodEstatus', String),
        ('incidencia', String),
    ]
    

class SoapServiceCancel(ServiceBase):
    
    @rpc(String(nillable=False), String(nillable=False), String(nillable=False), Unicode(nillable=False), Unicode(nillable=False), Boolean(nillable=False), Array(UUID), _returns=CancelaCFDIResult)
    def cancel(ctx, username, password, taxpayer_id, cer, key, store_pending, uuids=[]):
        # Verifica si hay un usuario activo que pertenesca al grupo Customers
        if DjangoCustomerRepository.validate_cancel_user(username, taxpayer_id) == True:
            print("El usuario cumple las condiciones")
        else:
            arCFDI = CancelaCFDIResult()
            arCFDI.incidencia = 'Créditos para timbrado/cancelación agotados'
            return arCFDI
        
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('suds.client').setLevel(logging.DEBUG)
        
        usuarioInvo = authenticate(username=username, password=password)
        #Generar un token para el usuario invoice
        #if Tokens.objects.filter(userName=username, token=password).exists():
        if Tokens.objects.filter(userName=username).exists():
            url = config('URL_CANCELACION')
            client = Client(url,cache=None)
            print(uuids)
            UUIDS_list = client.factory.create("ns0:UUIDArray")
            for uuid in uuids:
                invoices_obj = client.factory.create("ns0:UUID")
                invoices_obj._UUID=uuid.UUID
                invoices_obj._FolioSustitucion=uuid.FolioSustitucion
                invoices_obj._Motivo=uuid.Motivo
                UUIDS_list.UUID.append(invoices_obj)
            
            result = client.service.cancel(UUIDS_list, username, password, taxpayer_id, cer, key, store_pending)
        
            print(result)
        else:
            print('El usuario NO está en la tabla Tokens views.')
            print('add')
            user_service = User_Service.objects.filter(idUser=usuarioInvo).first()
            print('user_service:', user_service) 

            # Obtener la instancia de Service_Plan relacionada con el User_Service
            service_plans = Service_Plan.objects.filter(service=user_service.idService, plan=user_service.idPlan).first()
            print('service_plans:', service_plans)
            perfil = PerfilFiscalUser.objects.get(user=usuarioInvo)
            
            url = config('URL_CANCELACION')
            client = Client(url,cache=None)
            print(uuids)
            UUIDS_list = client.factory.create("ns0:UUIDArray")
            for uuid in uuids:
                invoices_obj = client.factory.create("ns0:UUID")
                invoices_obj._UUID=uuid.UUID
                invoices_obj._FolioSustitucion=uuid.FolioSustitucion
                invoices_obj._Motivo=uuid.Motivo
                UUIDS_list.UUID.append(invoices_obj)
            
            result = client.service.cancel(UUIDS_list, username, perfil.token, taxpayer_id, cer, key, store_pending)
        
            print(result)
            
        cancellCFDI = CancelaCFDIResult()
        _folios = []
        UUIDS=''
        EstatusCancelacion=''
        
        for k, v in Client.dict(result).items():
            if k=='Acuse' or k=='s0:Acuse':
                cancellCFDI.Acuse =  v 
            elif k=='Fecha' or k=='s0:Fecha':
                cancellCFDI.Fecha =  v  
            elif k=='RfcEmisor' or k=='s0:RfcEmisor':
                cancellCFDI.RfcEmisor =  v
            elif k=='CodEstatus' or k=='s0:CodEstatus':
                cancellCFDI.CodEstatus =  v        
            elif k=='Folios' or k=='s0:Folios':
                folios = v
                # print(v)
                if not(folios is None) :
                    for value in folios:
                        print(value)
                        print(value[1][0])
                        folio = Folio()
                        folio.UUID = value[1][0].UUID
                        UUIDS = value[1][0].UUID
                        folio.EstatusUUID = value[1][0].EstatusUUID
                        folio.EstatusCancelacion = value[1][0].EstatusCancelacion
                        EstatusCancelacion=value[1][0].EstatusCancelacion
                   
                        _folios.append(folio)
                
        
        cancellCFDI.Folios = _folios

        if cancellCFDI:
            print('respuesta exitosa') 

            print('RFC emisor:', taxpayer_id)
            emisor=taxpayer_id

            # Usuario autenticado con éxito, ahora verificar si está en la tabla Tokens
            #if Tokens.objects.filter(userName=usuarioInvo, token=password).exists():
            if Tokens.objects.filter(userName=usuarioInvo).exists():
                # Buscar el usuario por nombre de usuario
                #usuario = Tokens.objects.get(userName=username, token=password)
                usuario = Tokens.objects.get(userName=username)
                print(usuario)  
               
                if PerfilFiscalUser.objects.filter(user=usuario.idUserParent, rfc =emisor).exists(): 
                    user_service = User_Service.objects.filter(idUser=usuario.idUserParent).first()
                    print('user_service:', user_service) 

                    # Obtener la instancia de Service_Plan relacionada con el User_Service
                    service_plans = Service_Plan.objects.filter(service=user_service.idService).first()
                    print('service_plans:', service_plans)

                    #aumentar contador y definir el estatus
                    print('acuse', cancellCFDI.Folios)
                    estatus='sin_timbrar'
                    if cancellCFDI.Acuse:
                        
                        actualTimbre = TimbreUserPerfil.objects.get(userInvoice=usuario.idUserParent, estatus = 'A')

                        if actualTimbre.isOnDemmand == False:
                            actualTimbre.stamp=actualTimbre.stamp-1
                        actualTimbre.cont_stamped_user = actualTimbre.cont_stamped_user+1
                        actualTimbre.cont_stamped_day=  actualTimbre.cont_stamped_day+1
                        actualTimbre.save()
                        _sync_cfdi_enterprise_counter(usuario.idUserParent)

                        print('aumentar contador')

                        if actualTimbre.stamp == 0:
                            perfil = PerfilFiscalUser.objects.get(user=usuario.idUserParent)
                            perfil.estatus = 'S'
                            perfil.save()

                    # # Crear el registro de LogStamp
                    log_stamp = LogStamp.objects.create(
                        UUID= UUIDS,
                        Fecha=cancellCFDI.Fecha ,
                        Emisor=emisor,
                        CodEstatus=EstatusCancelacion,
                        idUser_ServicePlan=service_plans,
                        idUser=usuario.idUserParent,
                        status=estatus,
                        typeOperation='cancel'
                    )  
                    
                else:
                    user_service = User_Service.objects.filter(idUser=usuario.idUserParent).first()
                    print('user_service:', user_service) 

                    # Obtener la instancia de Service_Plan relacionada con el User_Service
                    service_plans = Service_Plan.objects.filter(service=user_service.idService).first()
                    print('service_plans:', service_plans)

                    #aumentar contador y definir el estatus
                    print('acuse', cancellCFDI.Folios)
                    estatus='sin_timbrar'
                    if cancellCFDI.Acuse:
                        cliente = Cliente.objects.get(user_cliente__idUser=usuario.idUserParent, rfc=emisor)
                        user_cliente = User_Cliente.objects.get(idCliente=cliente, idUser=usuario.idUserParent)
                        
                        print(user_cliente.countStamp)
                        
                        user_cliente.countStamp=user_cliente.countStamp+1
                        user_cliente.save()

                        actualTimbre = Timbre.objects.get(user_cliente=user_cliente, estatus = 'A')

                        if actualTimbre.isOnDemmand == False:
                            actualTimbre.stamp=actualTimbre.stamp-1
                        actualTimbre.cont_stamped_cliente= actualTimbre.cont_stamped_cliente+1
                        actualTimbre.cont_stamped_day=  actualTimbre.cont_stamped_day+1
                        actualTimbre.save()
                        _sync_cfdi_enterprise_counter(usuario.idUserParent)

                        print('aumentar contador')
                        print(user_cliente.countStamp)

                    # # Crear el registro de LogStamp
                    log_stamp = LogStamp.objects.create(
                        UUID= UUIDS,
                        Fecha=cancellCFDI.Fecha ,
                        Emisor=emisor,
                        CodEstatus=EstatusCancelacion,
                        idUser_ServicePlan=service_plans,
                        idUser=usuario.id,
                        status=estatus,
                        typeOperation='cancel'
                    )  
            
            else:
                user_service = User_Service.objects.filter(idUser=usuario.idUserParent).first()
                print('user_service:', user_service) 

                # Obtener la instancia de Service_Plan relacionada con el User_Service
                service_plans = Service_Plan.objects.filter(service=user_service.idService).first()
                print('service_plans:', service_plans)

                #aumentar contador y definir el estatus
                print('acuse', cancellCFDI.Folios)
                estatus='sin_timbrar'
                if cancellCFDI.Acuse:
                    
                    actualTimbre = TimbreUserPerfil.objects.get(userInvoice=usuarioInvo, estatus = 'A')
                    
                    if actualTimbre.isOnDemmand == False:
                        actualTimbre.stamp=actualTimbre.stamp-1
                    actualTimbre.cont_stamped_user= actualTimbre.cont_stamped_user+1
                    actualTimbre.cont_stamped_day=  actualTimbre.cont_stamped_day+1
                    actualTimbre.save()
                    _sync_cfdi_enterprise_counter(usuarioInvo)

                # # Crear el registro de LogStamp
                log_stamp = LogStamp.objects.create(
                    UUID= UUIDS,
                    Fecha=cancellCFDI.Fecha ,
                    Emisor=emisor,
                    CodEstatus=EstatusCancelacion,
                    idUser_ServicePlan=service_plans,
                    idUser=usuarioInvo,
                    status=estatus,
                    typeOperation='cancel'
                )  
                                
                                
        return cancellCFDI


        # # The variables needed are URL and HEADERS everything 
        # # else is extra that you might need for your request
        # client = SOAPClient(
        #     url='https://demo-facturacion.finkok.com/servicios/soap/cancel.wsdl',
        #     headers = {'content-type': 'application/soap+xml'}
        # )
        # # # Load up your crafted XML template from your /templates folder
        # # # with the values it expects
        # # # xml = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPGNmZGk6Q29tcHJvYmFudGUgeG1sbnM6Y2ZkaT0iaHR0cDovL3d3dy5zYXQuZ29iLm14L2NmZC80IiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6c2NoZW1hTG9jYXRpb249Imh0dHA6Ly93d3cuc2F0LmdvYi5teC9jZmQvNCBodHRwOi8vd3d3LnNhdC5nb2IubXgvc2l0aW9faW50ZXJuZXQvY2ZkLzQvY2ZkdjQwLnhzZCIgVmVyc2lvbj0iNC4wIiBTZXJpZT0iQSIgRm9saW89IjE2N0FCQyIgRmVjaGE9IjIwMjMtMDktMjdUMjE6MTI6MjIiIFNlbGxvPSJMQXIrYUdBSzZURXM2MG5PZnVXNWxkZS8zb0hXTkdwcWRoQWRhSCtzUjArUDNnZURBalVab0lNaHBsRkVQeWpuWEg4K01Pbnc0a21hTVp2MWwrQThsVkNZb3hpN3FkQStJQUhUNWNobVppTXBubVBIV05pQTlQOGxNSFRSclJaenc0aGVqTG9lNnYyeWJwOTJPU3hjUHpWR1ZLTE8yMTJLbFlKc0dJZnJ6anNyWC8zQm8wM0VHTGFFcGdtYzBLVTJBczBvcUJuZHFlUmNidVRubjIveFVSQ1VDWk05QUJIV3Q2UTZmeXd0dGI5clh1OTB4ajZIUEFJMUM5Y1p2d3dFRWVFdFhKckl6ZzZoVWRIQ2Zib0dWeTBjeU9VWjA1ejVkMmtYRFFZVjlVUWc5MERsdmlhaU45MnNXLzFxZ2NZTm83Q3llckRhNXNjVlNOZkx6elJiZkE9PSIgRm9ybWFQYWdvPSIwMiIgTm9DZXJ0aWZpY2Fkbz0iMzAwMDEwMDAwMDA1MDAwMDM0MTYiIENlcnRpZmljYWRvPSJNSUlGc0RDQ0E1aWdBd0lCQWdJVU16QXdNREV3TURBd01EQTFNREF3TURNME1UWXdEUVlKS29aSWh2Y05BUUVMQlFBd2dnRXJNUTh3RFFZRFZRUUREQVpCUXlCVlFWUXhMakFzQmdOVkJBb01KVk5GVWxaSlEwbFBJRVJGSUVGRVRVbE9TVk5VVWtGRFNVOU9JRlJTU1VKVlZFRlNTVUV4R2pBWUJnTlZCQXNNRVZOQlZDMUpSVk1nUVhWMGFHOXlhWFI1TVNnd0pnWUpLb1pJaHZjTkFRa0JGaGx2YzJOaGNpNXRZWEowYVc1bGVrQnpZWFF1WjI5aUxtMTRNUjB3R3dZRFZRUUpEQlF6Y21FZ1kyVnljbUZrWVNCa1pTQmpZV3hwZWpFT01Bd0dBMVVFRVF3Rk1EWXpOekF4Q3pBSkJnTlZCQVlUQWsxWU1Sa3dGd1lEVlFRSURCQkRTVlZFUVVRZ1JFVWdUVVZZU1VOUE1SRXdEd1lEVlFRSERBaERUMWxQUVVOQlRqRVJNQThHQTFVRUxSTUlNaTQxTGpRdU5EVXhKVEFqQmdrcWhraUc5dzBCQ1FJVEZuSmxjM0J2Ym5OaFlteGxPaUJCUTBSTlFTMVRRVlF3SGhjTk1qTXdOVEU0TVRFME16VXhXaGNOTWpjd05URTRNVEUwTXpVeFdqQ0IxekVuTUNVR0ExVUVBeE1lUlZORFZVVk1RU0JMUlUxUVJWSWdWVkpIUVZSRklGTkJJRVJGSUVOV01TY3dKUVlEVlFRcEV4NUZVME5WUlV4QklFdEZUVkJGVWlCVlVrZEJWRVVnVTBFZ1JFVWdRMVl4SnpBbEJnTlZCQW9USGtWVFExVkZURUVnUzBWTlVFVlNJRlZTUjBGVVJTQlRRU0JFUlNCRFZqRWxNQ01HQTFVRUxSTWNSVXRWT1RBd016RTNNME01SUM4Z1ZrRkVRVGd3TURreU4wUktNekVlTUJ3R0ExVUVCUk1WSUM4Z1ZrRkVRVGd3TURreU4waFRVbE5TVERBMU1STXdFUVlEVlFRTEV3cFRkV04xY25OaGJDQXhNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXRtZWNPNm4yR1MwekwwMjVnYkhHUVZ4em5QRElDb1h6UjJ1VW5nejREcXhWVUMvdzljRTZGeFNpWG0yYXA4R2NqZzd3bWNaZm04NUVCYXhDeC8wSjJ1NUNxbmh6SW9HQ2RoQlB1aFdRbkloNVRMZ2ovWDZ1TnF1d1prS0NoYk5lOWFlRmlyVS9KYnlON0VnaWE5b0tIOUtaVXNvZGlNL3BXQUgwMFBDdG9LSjlPQmNTSE1xOFJxYTNLS29CY2ZrZzFacmd1ZWZmd1JMd3M5eU9jUldMYjAyc0RPUHpHSW0vakVGaWNWWXQySHcxcWRSRTV4bVRaN0FHRzBVSHMrdW5rR2pwQ1ZlSitCRUJuMEpQTFdWdkRLSFpBUU1qNnM1Qmt1MzUrZC9NeUFUa3BPUHNHVC9WVG5zb3V4ZWtEZmlrSkQxZjdBMVpwSmJxRHBrSm5zczN2UUlEQVFBQm94MHdHekFNQmdOVkhSTUJBZjhFQWpBQU1Bc0dBMVVkRHdRRUF3SUd3REFOQmdrcWhraUc5dzBCQVFzRkFBT0NBZ0VBRmFVZ2o1UHFndkppZ05NZ3RyZFhabmJQZlZCYnVrQWJXNE9HblVoTnJBN1NSQUFmdjJCU0drMTZQSTBuQk9yN3FGMm1JdG1CbmpnRXdrK0RUdjhacjd3NXFwN3ZsZUM2ZElzWkZOSm9hNlpuZHJFL2Y3S08xQ1lydUxYcjVnd0VrSXlHZko5Tnd5SWFndkhITXN6enlIaVNaSUE4NTBmV3RicXR5dGhwQWxpSjJqRjM1TTVwTlMrWVRrUkIrVDZML2M2bTAweW1OM3E5bFQxckIwM1l5d3hyTHJlUlNGWk9TcmJ3V2ZnMzRFSmJIZmJGWHBDU1ZZZEpSZmlWZHZIbmV3TjByNWZVbFB0UjlzdFFIeXVxZXd6ZGt5YjVqVFR3MDJEMmNVZkw1N3ZsUFN0Qmo3U0VpM3VPV3ZMcnNpRG5uQ0l4Uk1ZSjJVQTJrdERLSGsrelduc0RtYWVsZVN6b252MkNIVzQyeVhZUEN2V2k4OG9FMURKTllMTmtJanVhN014QW5rTlpiU2NOdzAxQTZ6YkxzWjN5OEc2ZUVZbnhTVFJmd2pkOEVQNGtkaUhOSmZ0bTdaNGlSVTdIT1ZoNzkvbFJXQitnZDE3MXMzZC9tSTlrdGUzTVJ5NlY4TU1FTUNBbk1ib0dwYW9vWXdnQW13Y2xJMlhaQ2N6TldYZmhhV2UwWlM1UG15dEQvR0RwWHprWDBvRWdZOUsvdVlvNVY3N05kWmJHQWpteWk4Y0UyQjJvZ3Z5YU4yWGZJSW5yWlBnRWZmSjRBQjdrRkEybXdlc2RMT0NoMEJMRDlpdG1DdmUzQTFGR1I0K3N0TzJBTlVvaUkzdzNUdjJ5UVNnNGJqZURsSjA4bFhhYUZDTFcycGVFWE1YalFVazdmbXBiNU1OdU9VVFc2QkU9IiBTdWJUb3RhbD0iNjQ3NC44MSIgTW9uZWRhPSJNWE4iIFRpcG9DYW1iaW89IjEiIFRvdGFsPSI3NTEwLjc3IiBUaXBvRGVDb21wcm9iYW50ZT0iSSIgRXhwb3J0YWNpb249IjAxIiBNZXRvZG9QYWdvPSJQVUUiIEx1Z2FyRXhwZWRpY2lvbj0iNTgwMDAiPgogIDxjZmRpOkNmZGlSZWxhY2lvbmFkb3MgVGlwb1JlbGFjaW9uPSIwMSI+CiAgICA8Y2ZkaTpDZmRpUmVsYWNpb25hZG8gVVVJRD0iQTM5REE2NkItNTJDQS00OUUzLTg3OUItNUMwNTE4NUIwRUY3Ii8+CiAgPC9jZmRpOkNmZGlSZWxhY2lvbmFkb3M+CiAgPGNmZGk6RW1pc29yIFJmYz0iRUtVOTAwMzE3M0M5IiBOb21icmU9IkVTQ1VFTEEgS0VNUEVSIFVSR0FURSIgUmVnaW1lbkZpc2NhbD0iNjAxIi8+CiAgPGNmZGk6UmVjZXB0b3IgUmZjPSJBQUJGODAwNjE0SEkwIiBOb21icmU9IkZFTElYIE1BTlVFTCBBTkRSQURFIEJBTExBRE8iIFVzb0NGREk9IlMwMSIgUmVnaW1lbkZpc2NhbFJlY2VwdG9yPSI2MTYiIERvbWljaWxpb0Zpc2NhbFJlY2VwdG9yPSI4NjQwMCIvPgogIDxjZmRpOkNvbmNlcHRvcz4KICAgIDxjZmRpOkNvbmNlcHRvIENsYXZlUHJvZFNlcnY9IjgwMTMxNTAwIiBDYW50aWRhZD0iMS4wMCIgQ2xhdmVVbmlkYWQ9IkNFIiBOb0lkZW50aWZpY2FjaW9uPSIwMDAwMSIgVW5pZGFkPSJDRSIgRGVzY3JpcGNpb249IkFSUkVOREFNSUVOVE8gREUgSlVBUkVaIFBURSAxMDgtQSIgVmFsb3JVbml0YXJpbz0iNjQ3NC44MSIgSW1wb3J0ZT0iNjQ3NC44MSIgT2JqZXRvSW1wPSIwMiI+CiAgICAgIDxjZmRpOkltcHVlc3Rvcz4KICAgICAgICA8Y2ZkaTpUcmFzbGFkb3M+CiAgICAgICAgICA8Y2ZkaTpUcmFzbGFkbyBCYXNlPSI2NDc0LjgxIiBJbXB1ZXN0bz0iMDAyIiBUaXBvRmFjdG9yPSJUYXNhIiBUYXNhT0N1b3RhPSIwLjE2MDAwMCIgSW1wb3J0ZT0iMTAzNS45NiIvPgogICAgICAgIDwvY2ZkaTpUcmFzbGFkb3M+CiAgICAgIDwvY2ZkaTpJbXB1ZXN0b3M+CiAgICA8L2NmZGk6Q29uY2VwdG8+CiAgPC9jZmRpOkNvbmNlcHRvcz4KICA8Y2ZkaTpJbXB1ZXN0b3MgVG90YWxJbXB1ZXN0b3NUcmFzbGFkYWRvcz0iMTAzNS45NiI+CiAgICA8Y2ZkaTpUcmFzbGFkb3M+CiAgICAgIDxjZmRpOlRyYXNsYWRvIEJhc2U9IjY0NzQuODEiIEltcG9ydGU9IjEwMzUuOTYiIEltcHVlc3RvPSIwMDIiIFRhc2FPQ3VvdGE9IjAuMTYwMDAwIiBUaXBvRmFjdG9yPSJUYXNhIi8+CiAgICA8L2NmZGk6VHJhc2xhZG9zPgogIDwvY2ZkaTpJbXB1ZXN0b3M+CjwvY2ZkaTpDb21wcm9iYW50ZT4K"
        # # username = "antojitossol13@gmail.com"
        # # password = "1nT36R4c!0N"
        # # taxpayer_id="EKU9003173C9"
        # # cer="LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tDQpNSUlGc0RDQ0E1aWdBd0lCQWdJVU16QXdNREV3TURBd01EQTFNREF3TURNME1UWXdEUVlKS29aSWh2Y05BUUVMDQpCUUF3Z2dFck1ROHdEUVlEVlFRRERBWkJReUJWUVZReExqQXNCZ05WQkFvTUpWTkZVbFpKUTBsUElFUkZJRUZFDQpUVWxPU1ZOVVVrRkRTVTlPSUZSU1NVSlZWRUZTU1VFeEdqQVlCZ05WQkFzTUVWTkJWQzFKUlZNZ1FYVjBhRzl5DQphWFI1TVNnd0pnWUpLb1pJaHZjTkFRa0JGaGx2YzJOaGNpNXRZWEowYVc1bGVrQnpZWFF1WjI5aUxtMTRNUjB3DQpHd1lEVlFRSkRCUXpjbUVnWTJWeWNtRmtZU0JrWlNCallXeHBlakVPTUF3R0ExVUVFUXdGTURZek56QXhDekFKDQpCZ05WQkFZVEFrMVlNUmt3RndZRFZRUUlEQkJEU1ZWRVFVUWdSRVVnVFVWWVNVTlBNUkV3RHdZRFZRUUhEQWhEDQpUMWxQUVVOQlRqRVJNQThHQTFVRUxSTUlNaTQxTGpRdU5EVXhKVEFqQmdrcWhraUc5dzBCQ1FJVEZuSmxjM0J2DQpibk5oWW14bE9pQkJRMFJOUVMxVFFWUXdIaGNOTWpNd05URTRNVEUwTXpVeFdoY05NamN3TlRFNE1URTBNelV4DQpXakNCMXpFbk1DVUdBMVVFQXhNZVJWTkRWVVZNUVNCTFJVMVFSVklnVlZKSFFWUkZJRk5CSUVSRklFTldNU2N3DQpKUVlEVlFRcEV4NUZVME5WUlV4QklFdEZUVkJGVWlCVlVrZEJWRVVnVTBFZ1JFVWdRMVl4SnpBbEJnTlZCQW9UDQpIa1ZUUTFWRlRFRWdTMFZOVUVWU0lGVlNSMEZVUlNCVFFTQkVSU0JEVmpFbE1DTUdBMVVFTFJNY1JVdFZPVEF3DQpNekUzTTBNNUlDOGdWa0ZFUVRnd01Ea3lOMFJLTXpFZU1Cd0dBMVVFQlJNVklDOGdWa0ZFUVRnd01Ea3lOMGhUDQpVbE5TVERBMU1STXdFUVlEVlFRTEV3cFRkV04xY25OaGJDQXhNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DDQpBUThBTUlJQkNnS0NBUUVBdG1lY082bjJHUzB6TDAyNWdiSEdRVnh6blBESUNvWHpSMnVVbmd6NERxeFZVQy93DQo5Y0U2RnhTaVhtMmFwOEdjamc3d21jWmZtODVFQmF4Q3gvMEoydTVDcW5oeklvR0NkaEJQdWhXUW5JaDVUTGdqDQovWDZ1TnF1d1prS0NoYk5lOWFlRmlyVS9KYnlON0VnaWE5b0tIOUtaVXNvZGlNL3BXQUgwMFBDdG9LSjlPQmNTDQpITXE4UnFhM0tLb0JjZmtnMVpyZ3VlZmZ3Ukx3czl5T2NSV0xiMDJzRE9QekdJbS9qRUZpY1ZZdDJIdzFxZFJFDQo1eG1UWjdBR0cwVUhzK3Vua0dqcENWZUorQkVCbjBKUExXVnZES0haQVFNajZzNUJrdTM1K2QvTXlBVGtwT1BzDQpHVC9WVG5zb3V4ZWtEZmlrSkQxZjdBMVpwSmJxRHBrSm5zczN2UUlEQVFBQm94MHdHekFNQmdOVkhSTUJBZjhFDQpBakFBTUFzR0ExVWREd1FFQXdJR3dEQU5CZ2txaGtpRzl3MEJBUXNGQUFPQ0FnRUFGYVVnajVQcWd2SmlnTk1nDQp0cmRYWm5iUGZWQmJ1a0FiVzRPR25VaE5yQTdTUkFBZnYyQlNHazE2UEkwbkJPcjdxRjJtSXRtQm5qZ0V3aytEDQpUdjhacjd3NXFwN3ZsZUM2ZElzWkZOSm9hNlpuZHJFL2Y3S08xQ1lydUxYcjVnd0VrSXlHZko5Tnd5SWFndkhIDQpNc3p6eUhpU1pJQTg1MGZXdGJxdHl0aHBBbGlKMmpGMzVNNXBOUytZVGtSQitUNkwvYzZtMDB5bU4zcTlsVDFyDQpCMDNZeXd4ckxyZVJTRlpPU3Jid1dmZzM0RUpiSGZiRlhwQ1NWWWRKUmZpVmR2SG5ld04wcjVmVWxQdFI5c3RRDQpIeXVxZXd6ZGt5YjVqVFR3MDJEMmNVZkw1N3ZsUFN0Qmo3U0VpM3VPV3ZMcnNpRG5uQ0l4Uk1ZSjJVQTJrdERLDQpIayt6V25zRG1hZWxlU3pvbnYyQ0hXNDJ5WFlQQ3ZXaTg4b0UxREpOWUxOa0lqdWE3TXhBbmtOWmJTY053MDFBDQo2emJMc1ozeThHNmVFWW54U1RSZndqZDhFUDRrZGlITkpmdG03WjRpUlU3SE9WaDc5L2xSV0IrZ2QxNzFzM2QvDQptSTlrdGUzTVJ5NlY4TU1FTUNBbk1ib0dwYW9vWXdnQW13Y2xJMlhaQ2N6TldYZmhhV2UwWlM1UG15dEQvR0RwDQpYemtYMG9FZ1k5Sy91WW81Vjc3TmRaYkdBam15aThjRTJCMm9ndnlhTjJYZklJbnJaUGdFZmZKNEFCN2tGQTJtDQp3ZXNkTE9DaDBCTEQ5aXRtQ3ZlM0ExRkdSNCtzdE8yQU5Vb2lJM3czVHYyeVFTZzRiamVEbEowOGxYYWFGQ0xXDQoycGVFWE1YalFVazdmbXBiNU1OdU9VVFc2QkU9DQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tDQo="
        # # key="LS0tLS1CRUdJTiBFTkNSWVBURUQgUFJJVkFURSBLRVktLS0tLQpNSUlGSERCT0Jna3Foa2lHOXcwQkJRMHdRVEFwQmdrcWhraUc5dzBCQlF3d0hBUUlCMERVampGMjBzb0NBZ2dBCk1Bd0dDQ3FHU0liM0RRSUpCUUF3RkFZSUtvWklodmNOQXdjRUNIN0UyRDI5NjErSUJJSUV5Qmc2MjJ0Tk1DeDAKOXZKRDNKT0FkWU1MYU5PZCtTWHNQQ0dnVHVXcjFqSU90WUFhT1VMTmVnb2paSE5jMkY2RkROeUlJSXdJV0d0QwozaHczNnJaUTRWL1lEY1l4a3N1QTZoZUZEMUVFQXRmbkMvWU5wVkZ2Um5MUVFXRHhSQitBSjA5OEJibGZyNlB1ClRPZVhCYXRyMzRNbkQ1NnBZVVB3cTFjeUVPbW5XOXY0N1JPTlRSdlNKeDY2a21ZSlU4V2hHZ1Bmc3ZYWktJVFEKM3FtRXZOc0FrVm9LaEhiV0VCZ3UrZFpDTXRHbnZ6bUtmVnh6R0xnMEFiRHBmYW1QalRhaUlBYlpaMHh4ckVYSQphbnhNMHE1R1ZNZCt0eG00SVozbndpYmRmS1o2SHR1UDhZUk9DRldlVnVQOEpLMTJndC9vMXNBNFFCZnliaEc1CkRlQ3o5OXFhZjE2OWZjWlErZisyZm1oS1M4elozUDV6WkpTYXkxMFR6dno5b2pYeERsRDU1dWNFcXVVY0lZanEKSXducUFucVJZSVk1VC8zeDBHQ1pQL1NjbnN3Y040dkRBZjJRb3VPb28zUDBWYjBoT3JaS2JkL0VGSUM2ZXNsTgp0U2pBODQwTTdtNXRpcklaQ0FOZDA2V1QxelhVczc3YzZGd0t5RDJQR3V3V1B0TnZPaFVxT1lQV015K3FxeitnCmJ5YVg3OTlIWjhaM2tkbkhWcG42ZXl1Q25udzFMN3hVd1lyZElyY2UrNUhlbm1aMjh1TndpTUdCWlNqS21xMDIKeFlYSDN6UUJGYitnYi9XLzZqK3o1U2RPOHNzUE16a3BOSkZxSFIwNWpDNlpobmJqY1M1ejF3NnBydDRmcnpjbgpES0xqNG5nODAxRlBDNVRHQTNXYTZQOGFRRDZWTkxSRFU0UDFsV3RHSFgrTXloNmxTK25kdDdsZ2JqQXlpQy9tCm5mVlMyZ3NkQmZieUpTK0lURzBOMTN4NWYyOEVsYWJnTUtENUFYNFNlVHZSRjIrQWtZYTIxZUJ5NmtUaFF5SVoKZG15Skt5WlNycGhCYXhWNmwzUnpNQnNWY1RnTC82YnYxQ0tSYVliV0NRK2lrSlZWMWpraTE3YUEwQ21VRUJoagprM2loclN3cVNTVHZ0UllxYU53UDJkUEpuaHBHQzhtdFV5cjVycHNkSlBPTTd1UUNmaWpqcDA0dEN0d1BGeHJSCmZrRDRGMG1ieVFFRmhHWW01TGEwVlRmME1FKy82cWxjdU11NFZnWTREMjZrM1QyTE53VTlMTU9TYkNtaXkrRHIKaDJVcmVTcTJEdHprak90ek1RYXBrS3pjMVFmNHB6Zkh6ejhqemJrL0oraDUzVmd2VWFaZzhyRXMrZXZkVEJicgo2NkthdWwvQSt5YS9yYmtMMEtQMWNkN09pVk5OZjAzRGtIMmVIS0ZuMzRkVjdkcWdkMFl4UExQNXFnMHB1dTVvCjEvc3dsRXFtWnBxc09RNGI5bVJHNnBZOFc3NUJyMnI3clQ5ODBBbDlweFhxVld0OUZscEZmOWZ5SjhFN09SN3MKMnI4M0NkRmNBSjBDM2tLbkxZRDBvWHlPOTllQ0llR3ZuT2JJcEo4b2FrSGl2SU1lSVpIVk5MbjhjUmxRYTdLaApkMHRGZ1p0NUo0MWtWVmlBVnQ1S1dSakJvVFhQc2hLaFg3dGh5ZHdUSlJ1SGNjRDRnMlhaQisxOFRMSUZTczFHClZLVFNUK3hwbEt6VXdNSUxpWWY3N3ZIN2FrUTBWVUxZZGxDVDMyQ2N3MGgzMGFoMTVoaFRoKzFTU3c2em9JVWMKb0dHYW1tS0NKRWlNZHZjSk5kV3oxa2llUWdUOUNibmlKQmxWUTRrTzV4eWpVbVRIeWhveWtnbjdnWXovaGpwUgpFUlczdDFGUWtXMyttNkhOY2s2VC9TcUEzRFEwakVqamxDRDdjaVNWSE4wcmRxWUxLTGVrTjBiRlV6SDNQR2N4CmtRdWkzbVQ1c3FpcXB5dkhGRnB6c0tLay9LQk9uMjVXcmtTR1lmdFZyWFVSbm9tdllLMUdpeDVEbVVNajFtaU4KTHpKZlZYTFM4MUwvQWF3TTUyRVlrNGhLZHhrOTFaN1Q3S2hQVHJ6R01WMERrdDNXRTc4MXhmSU5HOUQ0eDVUVwpBVFJFYnllL1RGaS9IeG9Xd0xiVk9RPT0KLS0tLS1FTkQgRU5DUllQVEVEIFBSSVZBVEUgS0VZLS0tLS0K"
        # # store_pending = 0
        # # uuids = [
        # #                         {'uuid': "0D0C5D40-F15C-5BCF-85AA-50BE8AAD81CE", 
        # #                          'folioSustitucion': "", 
        # #                          'motivo': "02" }
        # #                     ]

        # response = client.send_request('soap_request/cancel.xml', {
        #             'uuids': uuids ,
        #             'username': username, 
        #             'password': password,
        #             'taxpayer_id': taxpayer_id ,
        #             'cer': cer,
        #             'key': key,
        #             'store_pending': store_pending
        #         }          
        #         )
    
        # result = (response.get('senv:Envelope').get('senv:Body')
        #     .get('tns:cancelResponse')
        #     .get('tns:cancelResult')
        #     )

        # cancellCFDI = CancelaCFDIResult()
        # _folios = []
        
        # #arCFDI.xml =  ("", result.get_value('s0:xml'))[not(result.get_value('s0:xml')  is  None )]
        # cancellCFDI.Acuse =  result.get_value('s0:Acuse') if result.get_value('s0:Acuse')  else  ""
        # cancellCFDI.UUID =  result.get_value('s0:Fecha') if result.get_value('s0:Fecha') else "" 
        # cancellCFDI.RfcEmisor =  result.get_value('s0:RfcEmisor') if result.get_value('s0:RfcEmisor') else ""
        # cancellCFDI.CodEstatus =  result.get_value('s0:CodEstatus') if result.get_value('s0:CodEstatus') else ""        
        
        # folios = result.get('s0:Folios')
        # if not(folios is None) :
        #     for key, value in folios.value.items():
        #         folio = Folio()
        #         folio.UUID = value['s0:UUID']
        #         folio.EstatusUUID = value['s0:EstatusUUID']
        #         folio.EstatusCancelacion = value['s0:EstatusCancelacion']
                   
        #         _folios.append(folio)
                
        # #cancellCFDI.Incidencias = incids if bool(incids) else None
        # cancellCFDI.Folios = _folios
                                
        # return cancellCFDI


    
soap_app = Application(
    [SoapService],
    tns='soap.example.factupid',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
)

soap_app_cancel = Application(
    [ SoapServiceCancel],
    tns='soap.example.factupid',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
)

django_soap_application = DjangoApplication(soap_app)
django_soap_application_cancel = DjangoApplication(soap_app_cancel)
my_soap_application = csrf_exempt(django_soap_application)
my_soap_application_cancel = csrf_exempt(django_soap_application_cancel)



def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'invoice/contact.html',
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
        'invoice/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year': datetime.datetime.now().year,
        }
    )

# def home(request):
#     """Renderiza la página de inicio."""
#     assert isinstance(request, HttpRequest)
    
#      # Obtener el perfil fiscal del usuario logueado
#     perfil_fiscal = PerfilFiscalUser.objects.filter(user=request.user).first()

#     # Obtener los servicios del usuario logueado
#     user_services = User_Service.objects.filter(idUser=request.user).first()
    
#     if user_services:
#         # Obtén los Service_Plan relacionados con el usuario logueado
#         service_plans = Service_Plan.objects.filter(
#             service=user_services.idService, 
#             plan=user_services.idPlan
#         ).first()
#         if service_plans and service_plans.supplierStamp:
#             url_sign_manifest = service_plans.supplierStamp.urlSignManifest
#             print('URL:', url_sign_manifest)
#         else:
#             url_sign_manifest = None
#     else:
#         service_plans = None
#         url_sign_manifest = None
    
#     return render(
#         request,
#         'invoice/index.html',
#         {
#             'title': 'Página de inicio',
#             'year': datetime.datetime.now().year,
#             'url_sign_manifest': url_sign_manifest
#         }
#     )

from django.http import HttpRequest
from django.shortcuts import render
import datetime

def home(request):
    """Renderiza la página de inicio."""
    assert isinstance(request, HttpRequest)

    if request.user.is_authenticated:
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
            else:
                url_sign_manifest = None
        else:
            service_plans = None
            url_sign_manifest = None
    else:
        url_sign_manifest = None

    # Renderiza la página de inicio con el contexto adecuado
    return render(
        request,
        'invoice/index.html',
        {
            'title': 'Página de inicio',
            'year': datetime.datetime.now().year,
            'url_sign_manifest': url_sign_manifest
        }
    )


def errorLinkreutilizado(request):
    """Renderiza la página de error en la activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'invoice/link_reutilizado.html',
        {
            'title': 'Página de envio de activacion',
            'year': datetime.datetime.now().year,
        }
    )

# partes para el registro *************************************************************************************************************************************


# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
        
#         # Verificar si los campos de contraseña están vacíos
#         password1 = request.POST.get('password1')
#         password2 = request.POST.get('password2')
#         email = request.POST.get('email')
        
#         # Expresión regular para verificar que la contraseña tenga al menos 8 caracteres y al menos un número o símbolo
#         password_regex = re.compile(r'^(?=.*[0-9!@#$%^&*])(?=.{8,})')

#         if not password1 or not password2:
#             form.add_error('password1', 'Los campos de contraseña no pueden estar vacíos.')
#         elif not email:
#             form.add_error('email', 'El campo de correo electrónico no puede estar vacío.')
#         elif not password_regex.match(password1):
#             form.add_error('password1', 'La contraseña debe tener al menos 8 caracteres y contener al menos un número o símbolo.')
#         elif form.is_valid():
#             if User.objects.filter(email=email).exists():  # Verificar si el correo electrónico ya existe
#                 form.add_error('email', 'Este correo electrónico ya está registrado.')  # Agregar error al formulario
#             else:
#                 user = form.save(commit=False)
#                 user.is_active = False  # Desactivar al usuario hasta que haga clic en el enlace de activación
                
#                 # Generar un username único basado en el email
#                 user.username = generate_unique_username(email)

#                 # Guardar el usuario
#                 user.save()
                
#                 # Agregar el usuario al grupo 'invoice'
#                 group = Group.objects.get(name='invoice')
#                 user.groups.add(group)

#                 # Enviar correo electrónico de activación
#                 send_activation_email(request, user)

#                 return redirect(reverse_lazy('invoice:activacionenviada'))  # Redirigir a una página de éxito después de registrar al usuario
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'invoice/register.html', {'form': form})



# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
        
#         # Verificar si los campos de contraseña están vacíos
#         password1 = request.POST.get('password1')
#         password2 = request.POST.get('password2')
#         email = request.POST.get('email')
        
#         # Expresión regular para verificar que la contraseña tenga al menos 8 caracteres y al menos un número o símbolo
#         password_regex = re.compile(r'^(?=.*[0-9!@#$%^&*])(?=.{8,})')

#         if not password1 or not password2:
#             form.add_error('password1', 'Los campos de contraseña no pueden estar vacíos.')
#         elif not email:
#             form.add_error('email', 'El campo de correo electrónico no puede estar vacío.')
#         elif not password_regex.match(password1):
#             form.add_error('password1', 'La contraseña debe tener al menos 8 caracteres y contener al menos un número o símbolo.')
#         elif form.is_valid():
#             if User.objects.filter(email=email).exists():  # Verificar si el correo electrónico ya existe
#                 form.add_error('email', 'Este correo electrónico ya está registrado.')  # Agregar error al formulario
#             else:
#                 user = form.save(commit=False)
#                 user.is_active = False  # Desactivar al usuario hasta que haga clic en el enlace de activación
                
#                 # Asignar el correo electrónico completo como nombre de usuario
#                 user.username = email

#                 # Guardar el usuario
#                 user.save()
                
#                 # Agregar el usuario al grupo 'invoice'
#                 group = Group.objects.get(name='invoice')
#                 user.groups.add(group)

#                 # Enviar correo electrónico de activación
#                 send_activation_email(request, user)

#                 return redirect(reverse_lazy('invoice:activacionenviada'))  # Redirigir a una página de éxito después de registrar al usuario
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'invoice/register.html', {'form': form})


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
                
                # Agregar el usuario al grupo 'invoice'
                # group = Group.objects.get(name='invoice')
                group = Group.objects.get(name__in=['invoice', 'Invoice stamping'])

                user.groups.add(group)

                # Enviar correo electrónico de activación
                send_activation_email(request, user)

                # Eliminar indicador de error de sesión
                request.session.pop('password_error', None)

                return redirect(reverse_lazy('invoice:activacionenviada'))  # Redirigir a una página de éxito después de registrar al usuario
    else:
        form = CustomUserCreationForm()
        # Limpiar la variable de error al cargar la página nuevamente
        request.session.pop('password_error', None)

    return render(request, 'invoice/register.html', {'form': form})




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
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:  # Verificar si el usuario ya está activo
            # Activar la cuenta del usuario
            user.is_active = True
            user.save()

            free_plan = Plan.objects.get(nombre='FREE')
            invoice_service = Service.objects.get(nombre='Invoice stamping') 

            idServiceP = Service_Plan.objects.get(
                service=invoice_service,
                plan=free_plan,
                isActive=True
            )
  

            User_Service.objects.create(
                idUser=user,
                idPlan=free_plan,
                idService=invoice_service,
                date_cutoff=datetime.date.today() + datetime.timedelta(days=30),
                idServicePlan=idServiceP,
                aceptarTerminos=True
                
            )

            return redirect(reverse_lazy('invoice:activacionbien'))
        else:
            # Usuario ya activado, redirigir a página de activación inválida
            return redirect(reverse_lazy('invoice:activacionmal'))
    else:
        # Token inválido o usuario no encontrado, redirigir a página de activación inválida
        return redirect(reverse_lazy('invoice:errorLinkreutilizado'))
    

    
def send_activation_email(request, user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # Usar el nombre de la aplicación 'invoice' en el reverse
    activation_link = reverse('invoice:activate_account', kwargs={'uidb64': uidb64, 'token': token})
    terminos_link = reverse('invoice:Terminos')

    # Construir los enlaces completos
    current_host = request.get_host()
    activation_link = f"http://{current_host}{activation_link}"
    terminos_link = f"http://{current_host}{terminos_link}"

    email_subject = 'Activa tu cuenta'
    email_body = (
        f'Hola {user.email},\n\n'
        f'Por favor, utiliza el siguiente enlace para activar tu cuenta:\n{activation_link}\n\n'
        f'Si deseas visualizar los términos y condiciones, haz clic aquí:\n{terminos_link}'
    )

    send_mail(
        subject=email_subject,
        message=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )

def activacionBien(request):
    """Renderiza la página de activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'invoice/activation_success.html',
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
        'invoice/activation_failure.html',
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
        'invoice/activation_failure_correo.html',
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
        'invoice/activation_failure_password.html',
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
        'invoice/activation_failure_usuarioRegistrado.html',
        {
            'title': 'Página de error usuario no registrado',
            'year': datetime.datetime.now().year,
        }
    )

def activacionenviada(request):
    """Renderiza la página de envío de activación."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'invoice/activation_sent.html',
        {
            'title': 'Página de envío de activación',
            'year': datetime.datetime.now().year,
        }
    )


def terminos(request):
    """Renderiza la página de inicio."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'invoice/TerminosCondiciones.html',
        {
            'title': 'Página de Términos y Condiciones',
            'year': datetime.datetime.now().year,
        }
    )
    
def politicas(request):
    """Renderiza la página de inicio."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'invoice/PoliticasPrivacidad.html',
        {
            'title': 'Página de POLÍTICAS DE PRIVACIDAD',
            'year': datetime.datetime.now().year,
        }
    )
#************************************************************************************************************************************

#para inicar sesion*****************************************************************************************************

#METODO UTILIZANDO LAS FORMAS ABSTRASCTAS
# DDD Y REPOSITORY VINCULADO CON EL DE sesioniniciada(request)
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
                # Crear sesión de usuario en Django.
                login(request, user)
                
                # Verificar si el usuario pertenece al grupo "invoice"
                if user.groups.filter(name__in=['invoice', 'Invoice stamping']).exists():
                    return redirect(reverse_lazy('invoice:iniciarsesionpartial'))  # Redirige a la página de inicio
                else:
                    return redirect(reverse_lazy('invoice:activacionmalusuarionoregistrado'))  # Redirige si no pertenece al grupo "invoice"
            else:
                return redirect(reverse_lazy('invoice:activacionmal'))  # Redirige si no está activo
        else:
            # Verificar si el correo es incorrecto
            if not auth_adapter.email_exists(identifier):
                return redirect(reverse_lazy('invoice:activacionmalcorreo'))  # Redirige si el correo es incorrecto
            else:
                # Usuario no encontrado o contraseña incorrecta
                return redirect(reverse_lazy('invoice:activacionmalcontrasena'))  # Redirige si la contraseña es incorrecta

    # Si no es un método POST o si la autenticación falla, renderiza la plantilla de inicio de sesión.
    return render(
        request,
        'invoice/index.html',  # Cambia a 'iniciarsesionpartial.html' si es necesario
        {
            'title': 'Iniciar Sesión',
            'year': datetime.datetime.now(),
        }
    )


def sesioniniciada(request):
    if request.method == 'POST':
        identifier = request.POST['identifier']  # Puede ser username o email
        password = request.POST['password']
        auth_adapter = CustomAuthAdapter()
        user = auth_adapter.authenticate(identifier, password)
        
        if user:
            # Verificar si el usuario está activo
            if user.is_active:
                # Iniciar sesión y verificar el grupo
                login(request, user)
                
                # Verificar si el usuario pertenece al grupo "invoice"
                if user.groups.filter(name__in=['invoice', 'Invoice stamping']).exists():
                    return redirect(reverse_lazy('invoice:iniciarsesionpartial'))  # Redirige a la página de inicio
        
            else:
                return redirect(reverse_lazy('invoice:activacionmal'))  # Redirige si no está activo
        else:
            # Verificar si el identificador (email o username) es incorrecto
            if not auth_adapter.email_exists(identifier):
                return redirect(reverse_lazy('invoice:activacionmalcorreo'))  # Redirige si el correo es incorrecto
            else:
                # Usuario no encontrado o contraseña incorrecta
                return redirect(reverse_lazy('invoice:activacionmalcontrasena'))  # Redirige si la contraseña es incorrecta

    return render(
        request,
        'invoice/index.html',  # Cambia a 'iniciarsesionpartial.html' si es necesario
        {
            'title': 'Iniciar Sesión',
            'year': timezone.now().year,
        }
    )

def cerrarsesion(request):
    """Cierra la sesión del usuario y redirige a la página de inicio."""
    assert isinstance(request, HttpRequest)
    logout(request)  # Cierra la sesión del usuario
    return redirect(reverse_lazy('invoice:inicio'))


#################################################################################
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from invoice.forms import SendEmailResetPasswordForm, ResetPasswordForm2
import hashlib
import random
from django.contrib.auth import update_session_auth_hash
#el httpresponse
from django.http import HttpResponse


def generate_unique_token_for_user(user):
    # Genera un token único para el usuario
    return hashlib.sha256(f'{user.pk}{user.email}{random.random()}{timezone.now()}'.encode()).hexdigest()


def send_resetPassword_email(request,user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    resetPassword_link = reverse('invoice:resetPassword_account', kwargs={'uidb64': uidb64, 'token': token})
    current_host = request.get_host()
    resetPassword_link = f"http://{current_host}{resetPassword_link}"
    email_subject = 'Restablece tu cuenta'
    email_body = f'Hola {user.username}, Por favor, utiliza el siguiente enlace para restablece la clave tu cuenta: {resetPassword_link}'
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
                resetPassword_link = reverse('invoice:resetPassword_account', kwargs={'uidb64': uidb64, 'token': token})
                current_host = request.get_host()
                resetPassword_link = f"http://{current_host}{resetPassword_link}"
                email_subject = 'Restablece tu contraseña'
                email_body = f'Hola {user.email}, Por favor, utiliza el siguiente enlace para restablecer tu contraseña: {resetPassword_link}'
                send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                return redirect(reverse_lazy('invoice:reseteo_enviada'))

                
            else:
                form.add_error('email', 'Este correo electrónico no está registrado.')
    return render(request, 'invoice/reseteo_password.html', {'form': form})



def resetPassword_account(request, uidb64, token):
    if request.method == 'POST':
        form = ResetPasswordForm2(request.POST)

        # Verificar si los campos son válidos primero
        password = form.cleaned_data.get('password') if form.is_valid() else ''
        password2 = form.cleaned_data.get('password2') if form.is_valid() else ''

        # Expresión regular para verificar que la contraseña tenga al menos 8 caracteres y contenga al menos un número o símbolo
        password_regex = re.compile(r'^(?=.*[0-9!@#$%^&*])(?=.{8,})')

        # Verificar si las contraseñas están vacías
        if not password or not password2:
            form.add_error('password', 'Los campos de contraseña no pueden estar vacíos.')
        # Verificar si las contraseñas coinciden
        elif password != password2:
            form.add_error('password2', 'Las contraseñas no coinciden.')
        # Verificar si la contraseña cumple con el formato
        elif not password_regex.match(password):
            form.add_error('password', 'La contraseña debe tener al menos 8 caracteres y contener al menos un número o símbolo.')
        else:
            try:
                uid = force_text(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                # Resetear la contraseña del usuario
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)
                return redirect(reverse_lazy('invoice:reseteobien'))

            return redirect(reverse_lazy('invoice:reseteomal'))

    else:
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = ResetPasswordForm2()
            return render(request, 'invoice/form_reset_password.html', {'form': form})
        else:
            return redirect(reverse_lazy('invoice:reseteomal'))

    return render(request, 'invoice/form_reset_password.html', {'form': form})




def resteoMal(request):
    """Renderiza la página de error en la activacion."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'invoice/reseteomal.html',
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
        'invoice/reseteobien.html',
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
        'invoice/reseteoEnviado.html',
        {
            'title': 'Página de envio de correo para resetar contraseña',
            'year': datetime.datetime.now().year,
        }
    )


######################## crud catalogo de clientes


# @login_required
# def catalogo_clientes(request):
#     """Renderiza una página con los clientes registrados."""
#     # Obtener todos los clientes registrados
#     clientes = Customer.objects.all()

#     return render(
#         request,
#         'invoice/catalogoClientes.html',
#         {
#             'title': 'Catálogo de Clientes',
#             'clientes': clientes,
#         }
#     )

######################################################################METODOS SOAP




class ResellerUserArray(ComplexModel):
    _type_info = [
        ('status', String),
        ('counter', String),
        ('taxpayer_id', String),
        ('credit', String),
    ]

class ResellerUser(ComplexModel):
    _type_info = [
        ('status', String),
        ('counter', String),
        ('taxpayer_id', String),
        ('credit', String),
    ]

class customersResponse(ComplexModel):
    _type_info = [
        ('message', String),
        ('users', Array(ResellerUser)),
    ]

class GetResponse(ComplexModel):
    _type_info = [
        ('message', String),
        ('users', Array(ResellerUser)),
    ]



class TaddResponse(ComplexModel):
    message = String
    success = Boolean
    

class TeditResponse(ComplexModel):
    message = String
    success = Boolean
    
    

class TswitchResponse(ComplexModel):
    message = String
    success = Boolean

class TassignResponse(ComplexModel):
    success = Boolean
    credit = Integer
    message = String
    
class TgetResponse(ComplexModel):
    message = String
    users = Array(ResellerUser)

     # # username = "antojitossol13@gmail.com"
        # # password = "1nT36R4c!0N"
        # # taxpayer_id="EKU9003173C9"
        # # cer="LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tDQpNSUlGc0RDQ0E1aWdBd0lCQWdJVU16QXdNREV3TURBd01EQTFNREF3TURNME1UWXdEUVlKS29aSWh2Y05BUUVMDQpCUUF3Z2dFck1ROHdEUVlEVlFRRERBWkJReUJWUVZReExqQXNCZ05WQkFvTUpWTkZVbFpKUTBsUElFUkZJRUZFDQpUVWxPU1ZOVVVrRkRTVTlPSUZSU1NVSlZWRUZTU1VFeEdqQVlCZ05WQkFzTUVWTkJWQzFKUlZNZ1FYVjBhRzl5DQphWFI1TVNnd0pnWUpLb1pJaHZjTkFRa0JGaGx2YzJOaGNpNXRZWEowYVc1bGVrQnpZWFF1WjI5aUxtMTRNUjB3DQpHd1lEVlFRSkRCUXpjbUVnWTJWeWNtRmtZU0JrWlNCallXeHBlakVPTUF3R0ExVUVFUXdGTURZek56QXhDekFKDQpCZ05WQkFZVEFrMVlNUmt3RndZRFZRUUlEQkJEU1ZWRVFVUWdSRVVnVFVWWVNVTlBNUkV3RHdZRFZRUUhEQWhEDQpUMWxQUVVOQlRqRVJNQThHQTFVRUxSTUlNaTQxTGpRdU5EVXhKVEFqQmdrcWhraUc5dzBCQ1FJVEZuSmxjM0J2DQpibk5oWW14bE9pQkJRMFJOUVMxVFFWUXdIaGNOTWpNd05URTRNVEUwTXpVeFdoY05NamN3TlRFNE1URTBNelV4DQpXakNCMXpFbk1DVUdBMVVFQXhNZVJWTkRWVVZNUVNCTFJVMVFSVklnVlZKSFFWUkZJRk5CSUVSRklFTldNU2N3DQpKUVlEVlFRcEV4NUZVME5WUlV4QklFdEZUVkJGVWlCVlVrZEJWRVVnVTBFZ1JFVWdRMVl4SnpBbEJnTlZCQW9UDQpIa1ZUUTFWRlRFRWdTMFZOVUVWU0lGVlNSMEZVUlNCVFFTQkVSU0JEVmpFbE1DTUdBMVVFTFJNY1JVdFZPVEF3DQpNekUzTTBNNUlDOGdWa0ZFUVRnd01Ea3lOMFJLTXpFZU1Cd0dBMVVFQlJNVklDOGdWa0ZFUVRnd01Ea3lOMGhUDQpVbE5TVERBMU1STXdFUVlEVlFRTEV3cFRkV04xY25OaGJDQXhNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DDQpBUThBTUlJQkNnS0NBUUVBdG1lY082bjJHUzB6TDAyNWdiSEdRVnh6blBESUNvWHpSMnVVbmd6NERxeFZVQy93DQo5Y0U2RnhTaVhtMmFwOEdjamc3d21jWmZtODVFQmF4Q3gvMEoydTVDcW5oeklvR0NkaEJQdWhXUW5JaDVUTGdqDQovWDZ1TnF1d1prS0NoYk5lOWFlRmlyVS9KYnlON0VnaWE5b0tIOUtaVXNvZGlNL3BXQUgwMFBDdG9LSjlPQmNTDQpITXE4UnFhM0tLb0JjZmtnMVpyZ3VlZmZ3Ukx3czl5T2NSV0xiMDJzRE9QekdJbS9qRUZpY1ZZdDJIdzFxZFJFDQo1eG1UWjdBR0cwVUhzK3Vua0dqcENWZUorQkVCbjBKUExXVnZES0haQVFNajZzNUJrdTM1K2QvTXlBVGtwT1BzDQpHVC9WVG5zb3V4ZWtEZmlrSkQxZjdBMVpwSmJxRHBrSm5zczN2UUlEQVFBQm94MHdHekFNQmdOVkhSTUJBZjhFDQpBakFBTUFzR0ExVWREd1FFQXdJR3dEQU5CZ2txaGtpRzl3MEJBUXNGQUFPQ0FnRUFGYVVnajVQcWd2SmlnTk1nDQp0cmRYWm5iUGZWQmJ1a0FiVzRPR25VaE5yQTdTUkFBZnYyQlNHazE2UEkwbkJPcjdxRjJtSXRtQm5qZ0V3aytEDQpUdjhacjd3NXFwN3ZsZUM2ZElzWkZOSm9hNlpuZHJFL2Y3S08xQ1lydUxYcjVnd0VrSXlHZko5Tnd5SWFndkhIDQpNc3p6eUhpU1pJQTg1MGZXdGJxdHl0aHBBbGlKMmpGMzVNNXBOUytZVGtSQitUNkwvYzZtMDB5bU4zcTlsVDFyDQpCMDNZeXd4ckxyZVJTRlpPU3Jid1dmZzM0RUpiSGZiRlhwQ1NWWWRKUmZpVmR2SG5ld04wcjVmVWxQdFI5c3RRDQpIeXVxZXd6ZGt5YjVqVFR3MDJEMmNVZkw1N3ZsUFN0Qmo3U0VpM3VPV3ZMcnNpRG5uQ0l4Uk1ZSjJVQTJrdERLDQpIayt6V25zRG1hZWxlU3pvbnYyQ0hXNDJ5WFlQQ3ZXaTg4b0UxREpOWUxOa0lqdWE3TXhBbmtOWmJTY053MDFBDQo2emJMc1ozeThHNmVFWW54U1RSZndqZDhFUDRrZGlITkpmdG03WjRpUlU3SE9WaDc5L2xSV0IrZ2QxNzFzM2QvDQptSTlrdGUzTVJ5NlY4TU1FTUNBbk1ib0dwYW9vWXdnQW13Y2xJMlhaQ2N6TldYZmhhV2UwWlM1UG15dEQvR0RwDQpYemtYMG9FZ1k5Sy91WW81Vjc3TmRaYkdBam15aThjRTJCMm9ndnlhTjJYZklJbnJaUGdFZmZKNEFCN2tGQTJtDQp3ZXNkTE9DaDBCTEQ5aXRtQ3ZlM0ExRkdSNCtzdE8yQU5Vb2lJM3czVHYyeVFTZzRiamVEbEowOGxYYWFGQ0xXDQoycGVFWE1YalFVazdmbXBiNU1OdU9VVFc2QkU9DQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tDQo="
        # # key="LS0tLS1CRUdJTiBFTkNSWVBURUQgUFJJVkFURSBLRVktLS0tLQpNSUlGSERCT0Jna3Foa2lHOXcwQkJRMHdRVEFwQmdrcWhraUc5dzBCQlF3d0hBUUlCMERVampGMjBzb0NBZ2dBCk1Bd0dDQ3FHU0liM0RRSUpCUUF3RkFZSUtvWklodmNOQXdjRUNIN0UyRDI5NjErSUJJSUV5Qmc2MjJ0Tk1DeDAKOXZKRDNKT0FkWU1MYU5PZCtTWHNQQ0dnVHVXcjFqSU90WUFhT1VMTmVnb2paSE5jMkY2RkROeUlJSXdJV0d0QwozaHczNnJaUTRWL1lEY1l4a3N1QTZoZUZEMUVFQXRmbkMvWU5wVkZ2Um5MUVFXRHhSQitBSjA5OEJibGZyNlB1ClRPZVhCYXRyMzRNbkQ1NnBZVVB3cTFjeUVPbW5XOXY0N1JPTlRSdlNKeDY2a21ZSlU4V2hHZ1Bmc3ZYWktJVFEKM3FtRXZOc0FrVm9LaEhiV0VCZ3UrZFpDTXRHbnZ6bUtmVnh6R0xnMEFiRHBmYW1QalRhaUlBYlpaMHh4ckVYSQphbnhNMHE1R1ZNZCt0eG00SVozbndpYmRmS1o2SHR1UDhZUk9DRldlVnVQOEpLMTJndC9vMXNBNFFCZnliaEc1CkRlQ3o5OXFhZjE2OWZjWlErZisyZm1oS1M4elozUDV6WkpTYXkxMFR6dno5b2pYeERsRDU1dWNFcXVVY0lZanEKSXducUFucVJZSVk1VC8zeDBHQ1pQL1NjbnN3Y040dkRBZjJRb3VPb28zUDBWYjBoT3JaS2JkL0VGSUM2ZXNsTgp0U2pBODQwTTdtNXRpcklaQ0FOZDA2V1QxelhVczc3YzZGd0t5RDJQR3V3V1B0TnZPaFVxT1lQV015K3FxeitnCmJ5YVg3OTlIWjhaM2tkbkhWcG42ZXl1Q25udzFMN3hVd1lyZElyY2UrNUhlbm1aMjh1TndpTUdCWlNqS21xMDIKeFlYSDN6UUJGYitnYi9XLzZqK3o1U2RPOHNzUE16a3BOSkZxSFIwNWpDNlpobmJqY1M1ejF3NnBydDRmcnpjbgpES0xqNG5nODAxRlBDNVRHQTNXYTZQOGFRRDZWTkxSRFU0UDFsV3RHSFgrTXloNmxTK25kdDdsZ2JqQXlpQy9tCm5mVlMyZ3NkQmZieUpTK0lURzBOMTN4NWYyOEVsYWJnTUtENUFYNFNlVHZSRjIrQWtZYTIxZUJ5NmtUaFF5SVoKZG15Skt5WlNycGhCYXhWNmwzUnpNQnNWY1RnTC82YnYxQ0tSYVliV0NRK2lrSlZWMWpraTE3YUEwQ21VRUJoagprM2loclN3cVNTVHZ0UllxYU53UDJkUEpuaHBHQzhtdFV5cjVycHNkSlBPTTd1UUNmaWpqcDA0dEN0d1BGeHJSCmZrRDRGMG1ieVFFRmhHWW01TGEwVlRmME1FKy82cWxjdU11NFZnWTREMjZrM1QyTE53VTlMTU9TYkNtaXkrRHIKaDJVcmVTcTJEdHprak90ek1RYXBrS3pjMVFmNHB6Zkh6ejhqemJrL0oraDUzVmd2VWFaZzhyRXMrZXZkVEJicgo2NkthdWwvQSt5YS9yYmtMMEtQMWNkN09pVk5OZjAzRGtIMmVIS0ZuMzRkVjdkcWdkMFl4UExQNXFnMHB1dTVvCjEvc3dsRXFtWnBxc09RNGI5bVJHNnBZOFc3NUJyMnI3clQ5ODBBbDlweFhxVld0OUZscEZmOWZ5SjhFN09SN3MKMnI4M0NkRmNBSjBDM2tLbkxZRDBvWHlPOTllQ0llR3ZuT2JJcEo4b2FrSGl2SU1lSVpIVk5MbjhjUmxRYTdLaApkMHRGZ1p0NUo0MWtWVmlBVnQ1S1dSakJvVFhQc2hLaFg3dGh5ZHdUSlJ1SGNjRDRnMlhaQisxOFRMSUZTczFHClZLVFNUK3hwbEt6VXdNSUxpWWY3N3ZIN2FrUTBWVUxZZGxDVDMyQ2N3MGgzMGFoMTVoaFRoKzFTU3c2em9JVWMKb0dHYW1tS0NKRWlNZHZjSk5kV3oxa2llUWdUOUNibmlKQmxWUTRrTzV4eWpVbVRIeWhveWtnbjdnWXovaGpwUgpFUlczdDFGUWtXMyttNkhOY2s2VC9TcUEzRFEwakVqamxDRDdjaVNWSE4wcmRxWUxLTGVrTjBiRlV6SDNQR2N4CmtRdWkzbVQ1c3FpcXB5dkhGRnB6c0tLay9LQk9uMjVXcmtTR1lmdFZyWFVSbm9tdllLMUdpeDVEbVVNajFtaU4KTHpKZlZYTFM4MUwvQWF3TTUyRVlrNGhLZHhrOTFaN1Q3S2hQVHJ6R01WMERrdDNXRTc4MXhmSU5HOUQ0eDVUVwpBVFJFYnllL1RGaS9IeG9Xd0xiVk9RPT0KLS0tLS1FTkQgRU5DUllQVEVEIFBSSVZBVEUgS0VZLS0tLS0K"
       


#CLASE PARA LA NUEVA APLICACION DE REGISTRO DE USUARIOS PARA LA EXTENSION WIZDLE

class RegisterService (ServiceBase):
    #######################################METODOS DE REGISTRO DE USUARIOS,
    
   
    @rpc(String(nillable=False), String(nillable=False),String(nillable=False), String(nillable=False), String(nillable=False), String(nillable=False),String(nillable=False), _returns=TaddResponse)
    def add(ctx, reseller_username, reseller_password, taxpayer_id, type_user,cer,key,passphrase):
        # Llamar al método de registro de usuario
        url = config('URL_REGISTRO_CLIENTES')
        client = Client(url, cache=None)
        print("entro al metodo add")
        # Preparar la solicitud SOAP con los parámetros correctos
        response = client.service.add(
            reseller_username=reseller_username,
            reseller_password=reseller_password,
            taxpayer_id=taxpayer_id,
            type_user=type_user,
            cer=cer,
            key=key,
            passphrase=passphrase
            
            
            
            
        )
        
        print(response)

        # Devolver la respuesta en el formato esperado
        return TaddResponse(message=response.message, success=response.success)
    
    
    
    @rpc(String(nillable=False), String(nillable=False),String(nillable=False), String(nillable=False), String(nillable=False), String(nillable=False),String(nillable=False), _returns=TeditResponse)
    def edit(ctx, reseller_username, reseller_password, taxpayer_id, status,cer,key,passphrase):
        url = config('URL_REGISTRO_CLIENTES')
        client = Client(url, cache=None)

        # Preparar la solicitud SOAP con los parámetros correctos
        response = client.service.edit(
            reseller_username=reseller_username,
            reseller_password=reseller_password,
            taxpayer_id=taxpayer_id,
            status=status,
            cer=cer,
            key=key,
            passphrase=passphrase
        )
        print(response)
        
        return TeditResponse(message=response.message, success=response.success)
        
    
    
    
    
    @rpc(String(nillable=False), String(nillable=False),String(nillable=False), String(nillable=False),  _returns=TswitchResponse)
    def switch(ctx, username, password, taxpayer_id, type_user,):
        # Llamar al método de registro de usuario
        url = config('URL_REGISTRO_CLIENTES')
        client = Client(url, cache=None)

        # Preparar la solicitud SOAP con los parámetros correctos
        response = client.service.switch(
            username=username,
            password=password,
            taxpayer_id=taxpayer_id,
            type_user=type_user,
        )

        # Devolver la respuesta en el formato esperado
        return TswitchResponse(message=response.message ,success=response.success)
    
    
    
    @rpc(String(nillable=False), String(nillable=False),String(nillable=False), Integer(nillable=False),  _returns=TassignResponse)
    def assign(ctx, username, password, taxpayer_id, credit,):
        # Llamar al método de registro de usuario
        url = config('URL_REGISTRO_CLIENTES')
        client = Client(url, cache=None)

        # Preparar la solicitud SOAP con los parámetros correctos
        response = client.service.assign(
            username=username,
            password=password,
            taxpayer_id=taxpayer_id,
            credit=credit,
        )

        # Devolver la respuesta en el formato esperado
        return TassignResponse(success=response.success, credit=response.credit,message=response.message)
    
    
    
    
    
    
    
    
##############################################METODO PARA CONSULTAR LOS CLIENTES
    
    
    @rpc(String(nillable=False), String(nillable=False), Unicode(nillable=False), _returns=customersResponse)
    def customers(ctx, reseller_username, reseller_password, page):
    # Llamar al método de registro de usuario
        url = config('URL_REGISTRO_CLIENTES')
        client = Client(url, cache=None)

        contenido = client.service.customers(reseller_username,reseller_password,page)    

         # Crear instancia de AcuseRecepcionCFDIQuery
        response = customersResponse()
        incids = []

        # Configurar los atributos del response según el formato deseado
        # EL siguiente for recorre los atributos que regresa el metodo soap para mostarlos en la pagina usa los modelos anteriores
        # El primer for recorre customersResponse y en user se encuentra que tiene como datos 2 array
        # El segundoo for es para recorrer los 2 array y mostrar sus datos con los modelos "ResellerUser" y "ResellerUserArray" respectivamente
        # (Quitar los print solo son para ver que datos se estan guardando en los modelos y mostrarlos en la pagina)
        for key, value in Client.dict(contenido).items():   
            print(key, "->", value)
            if key=='message':
                response.message = contenido.message
            elif (key=='users'):
                incit = contenido.users
                if not(incit is None) :
                    for value in incit:
                        incid = ResellerUser()
                        incidd = ResellerUserArray()
                        incid.status = value[1][0].status
                        print(value[1][0].status)
                        incid.counter = str(value[1][0].counter)
                        print(value[1][0].counter)
                        incid.taxpayer_id = value[1][0].taxpayer_id
                        print(value[1][0].taxpayer_id)
                        incid.credit = str(value[1][0].credit)
                        print(value[1][0].credit)

                        incidd.status = value[1][1].status
                        print(value[1][1].status)
                        incidd.counter = str(value[1][1].counter)
                        print(value[1][1].counter)
                        incidd.taxpayer_id = value[1][1].taxpayer_id
                        print(value[1][1].taxpayer_id)
                        incidd.credit = str(value[1][1].credit)
                        print(value[1][1].credit)
            
                        incids.append(incid)
                        incids.append(incidd)
        
        response.users = incids 

        return response
    
    
    
    @rpc(String(nillable=False), String(nillable=False), Unicode(nillable=False), _returns=customersResponse)
    def get(ctx, reseller_username, reseller_password, taxpayer_id):
    # Llamar al método de registro de usuario
        url = config('URL_REGISTRO_CLIENTES')
        client = Client(url, cache=None)

        contenido = client.service.get(reseller_username,reseller_password,taxpayer_id)    

         # Crear instancia de AcuseRecepcionCFDIQuery
        response = customersResponse()
        incids = []

        # Configurar los atributos del response según el formato deseado
        # EL siguiente for recorre los atributos que regresa el metodo soap para mostarlos en la pagina usa los modelos anteriores
        # El primer for recorre customersResponse y en user se encuentra que tiene como datos 2 array
        # El segundoo for es para recorrer los 2 array y mostrar sus datos con los modelos "ResellerUser" y "ResellerUserArray" respectivamente
        # (Quitar los print solo son para ver que datos se estan guardando en los modelos y mostrarlos en la pagina)
        for key, value in Client.dict(contenido).items():   
            print(key, "->", value)
            if key=='message':
                response.message = contenido.message
            elif (key=='users'):
                incit = contenido.users
                if not(incit is None) :
                    for value in incit:
                        incid = ResellerUser()
                        incidd = ResellerUserArray()
                        incid.status = value[1][0].status
                        print(value[1][0].status)
                        incid.counter = str(value[1][0].counter)
                        print(value[1][0].counter)
                        incid.taxpayer_id = value[1][0].taxpayer_id
                        print(value[1][0].taxpayer_id)
                        incid.credit = str(value[1][0].credit)
                        print(value[1][0].credit)
                        incids.append(incid)
        
        response.users = incids 

        return response
    
    
    
    
    
register_app = Application(
    [RegisterService],
    tns='soap.example.factupid',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
)

django_register_application = DjangoApplication(register_app)
my_register_application = csrf_exempt(django_register_application)



class UtilitiesSOAP(ServiceBase):
    #######################################METODOS DE GESTION DE TOKENS,
    
   
    @rpc(String(nillable=False), String(nillable=False),String(nillable=False), String(nillable=False), String(nillable=False), String(nillable=False))
    def add_tokens(ctx, username, password, name, token_username, taxpayer_id, status):
        # Llamar al método de registro de usuario
        url = config('URL_UTILITIES')
        client = Client(url, cache=None)
        print('add_token')
        # Preparar la solicitud SOAP con los parámetros correctos
        response = client.service.add_token(
            username=username,
            password=password,
            name=name,
            token_username=token_username,
            taxpayer_id=taxpayer_id,
            status=status
            
        )
        
        return response
    
    
    
    @rpc(String(nillable=False), String(nillable=False),String(nillable=False))
    def reset_token(ctx, username, password, token):
        url = url = config('URL_UTILITIES')
        client = Client(url, cache=None)

        # Preparar la solicitud SOAP con los parámetros correctos
        response = client.service.reset_token(
            username=username,
            password=password,
            token=token
        )
        # Devolver la respuesta en el formato esperado
        return response
        
    
    
    
    
    @rpc(String(nillable=False), String(nillable=False),String(nillable=False), String(nillable=False))
    def update_token(ctx, username, password, token, status):
        # Llamar al método de registro de usuario
        url = url = config('URL_UTILITIES')
        client = Client(url, cache=None)

        # Preparar la solicitud SOAP con los parámetros correctos
        response = client.service.update_token(
            username=username,
            password=password,
            token=token,
            status=status
        )
        print(response)
        # Devolver la respuesta en el formato esperado
        return response
