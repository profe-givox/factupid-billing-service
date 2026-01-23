from sre_constants import IN
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django_soap.utils.SOAPHandlerBase import SoapResult
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
import lxml.etree as ET
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str as force_text
from django.urls import reverse, reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
#from zeep import Transport
from django.contrib.auth import authenticate, login
from suds.client import Client
import logging

from django.conf import settings 
from adapter.console.django_user_repository import CustomAuthAdapter
import logging
from decouple import config

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
        url = config('URL_UTILITIES')
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
        url = config('URL_UTILITIES')
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
    
class SignContractSOAP(ServiceBase):
    #######################################METODOS DE GESTION DE TOKENS,
    
   
    @rpc(String(nillable=False), String(nillable=False),String(nillable=False))
    def get_documents(ctx, snid, taxpayer_id, type):
        # Llamar al método de registro de usuario
        url = config('URL_SIGNCONTRACT')
        client = Client(url, cache=None)
        # Preparar la solicitud SOAP con los parámetros correctos
        response = client.service.get_documents(
            snid=snid,
            taxpayer_id=taxpayer_id,
            type=type
        )
        
        return response
    
    
    
    # @rpc(String(nillable=False), String(nillable=False),String(nillable=False))
    # def reset_token(ctx, username, password, token):
    #     url = "https://manifiesto.cfdiquadrum.com.mx:8008/servicios/soap/firmar.wsdl"
    #     client = Client(url, cache=None)

    #     # Preparar la solicitud SOAP con los parámetros correctos
    #     response = client.service.reset_token(
    #         username=username,
    #         password=password,
    #         token=token
    #     )
    #     # Devolver la respuesta en el formato esperado
    #     return response
        
    
    
    
    
    # @rpc(String(nillable=False), String(nillable=False),String(nillable=False), String(nillable=False))
    # def update_token(ctx, username, password, token, status):
    #     # Llamar al método de registro de usuario
    #     url = "https://manifiesto.cfdiquadrum.com.mx:8008/servicios/soap/firmar.wsdl"
    #     client = Client(url, cache=None)

    #     # Preparar la solicitud SOAP con los parámetros correctos
    #     response = client.service.update_token(
    #         username=username,
    #         password=password,
    #         token=token,
    #         status=status
    #     )
    #     print(response)
    #     # Devolver la respuesta en el formato esperado
    #     return response