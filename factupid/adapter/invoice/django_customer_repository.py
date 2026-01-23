from dominio.invoice.customer_repository import CustomerRepository
from django.contrib.auth.mixins import UserPassesTestMixin
from dominio.invoice.Customer import Customer
from django.http import HttpResponseForbidden

from dominio.invoice.customer_repository import CustomerRepository
from django.contrib.auth.models import User, Group
from invoice.models import Cliente, User_Cliente, PerfilFiscalUser,Timbre,Tokens, TimbreUserPerfil
from django.shortcuts import redirect

import base64
import xml.etree.ElementTree as ET

from django.core.exceptions import PermissionDenied    
        
from django.contrib.auth import authenticate

class DjangoCustomerRepository(CustomerRepository):
    def is_valid_user(username, grupo, xml, password):
        try:
            # Verificar si el XML está en formato base64 válido
            try:
                decoded_bytes = base64.b64decode(xml, validate=True)  # Valida si es Base64
                decoded_string = decoded_bytes.decode('utf-8')
            except (base64.binascii.Error, UnicodeDecodeError) as e:
                return False, "El XML no está en formato Base64 o es inválido."

            # Parsear el XML para extraer el RFC
            try:
                root = ET.fromstring(decoded_string)
                emisor = root.find('.//cfdi:Emisor', {'cfdi': 'http://www.sat.gob.mx/cfd/4'}).attrib['Rfc']
                print('RFC emisor:', emisor)
            except ET.ParseError:
                return False, "El XML tiene un formato incorrecto o no se pudo parsear."
            
            user = User.objects.get(username=username)
            if user is None:
                return False, "Usuario o contraseña incorrectos."
            usertk = Tokens.objects.filter(idUserToken=user).first()
            if usertk is None:
                userpf = PerfilFiscalUser.objects.filter(user=user, rfc=emisor).first()
                if userpf is None:
                    return False, "Usuario o contraseña incorrectos."
                elif  ( userpf.decrypt_token() == password) or ( user.check_password(password)):
                    pass
                else:       
                    return False, "Usuario o contraseña incorrectos."
            else:
                user = authenticate(username=username, password=password)
            
            usuario = user
            if usuario is None:
                return False, "Usuario o contraseña incorrectos."
        
            print('usuario timbrando',usuario)
            
            # Verificar si el usuario pertenece al grupo y está activo
            if not usuario.is_active:
                return False, "El usuario no está activo."

            if not usuario.groups.filter(name=grupo).exists():
                return False, "El usuario no pertenece al grupo invoice."
            
            # Verificar si el usuario pertenece al grupo y está activo
            pertenece_al_grupo = usuario.groups.filter(name=grupo).exists()
            print("Username:", usuario.username)
            print("Pertenece al Grupo:", pertenece_al_grupo)
            print("Está activo:", usuario.is_active)

            
            # Usuario autenticado con éxito, ahora verificar si está en la tabla Clientes
            #if Tokens.objects.filter(userName=usuario, token=password).exists():
            if usertk is not None:
                print('El usuario está en la tabla Tokens es un cliente.')
                # Si está en Tokens, es un cliente
                
                print(usertk)
                invoiseUser = PerfilFiscalUser.objects.get(user=usertk.idUserParent, rfc =emisor)
                if invoiseUser is not None:
                    print('el token pertenece al usuario invoice: ', invoiseUser)
                    timbreUser = TimbreUserPerfil.objects.get(userInvoice=invoiseUser.user, estatus = 'A')          
                    print('timbre relacionado',timbreUser)
                        
                    if timbreUser.estatus=='A' and (timbreUser.stamp > 0 or timbreUser.stamp == -1):
                        print('user',invoiseUser, 'timbres:',timbreUser.stamp)
                        return True, None  # Retorna True si todo es válido
                    
                    print('No tiene creditos suficientes', timbreUser.stamp )
                
                    return False, "No tiene creditos suficientes"
                
                else:
                    #clientee = Tokens.objects.get(userName=username, token=password)
                    #clientee = Tokens.objects.get(userName=username)
                    clientee = usertk
                    cliente = Cliente.objects.get(user_cliente__idUser=clientee.idUserParent, rfc=emisor)
                    user_cliente = User_Cliente.objects.get(idCliente=cliente)

                    timbre = Timbre.objects.get(user_cliente=user_cliente, estatus='A')
                    print('timbre relacionado',timbre)
                        
                    if user_cliente.estatus == 'A' and (timbre.stamp > 0 or timbre.stamp == -1):
                        print('cliente',cliente, 'estatus:', user_cliente.estatus, 'timbres:',timbre.stamp)
                        return True, None  # Retorna True si todo es válido
                    
                    print('No esta activo el usuario o no tiene creditos suficientes', timbre.stamp )
                
                    return False, "El cliente o no tiene creditos suficientes"
            
            else:
                print('El usuario NO está en la tabla tokens, no es un cliente.')
                # Si no está en Tokens, entonces es un usuario
                print(usuario, emisor)
                if   userpf is not None:
                    userInvoice = userpf
                    print(userpf)
                    
                    timbreUser = TimbreUserPerfil.objects.get(userInvoice=usuario, estatus = 'A')
                    print('timbre relacionado',timbreUser)
                        
                    if timbreUser.estatus=='A' and (timbreUser.stamp > 0 or timbreUser.stamp == -1):
                        print('user',userInvoice, 'timbres:',timbreUser.stamp)
                        return True, None  # Retorna True si todo es válido
                    
                    print('No tiene creditos suficientes', timbreUser.stamp )
                
                    return False, "No tiene créditos suficientes."
                else:
                    return  False, "El RFC no coincide con el usuario."
        
        except User.DoesNotExist:
            print("Usuario no encontrado")
            return False

    def validate_user(username, xml, password):
        grupo = Group.objects.get(name='invoice')
        is_valid, message = DjangoCustomerRepository.is_valid_user(username, grupo, xml, password)
        
        if not is_valid:
            print(f"Validación fallida: {message}")
            raise PermissionDenied(message)
        
        return True
    # validaciones para cancelar
    def is_valid_cancel_user(username, grupo, rfc):
        try:
            # Buscar el usuario por nombre de usuario
            usuario = User.objects.get(username=username)

            emisor = rfc
            print('RFC emisor:', emisor)
            # Verificar si el usuario pertenece al grupo y está activo
            pertenece_al_grupo = usuario.groups.filter(name=grupo).exists()

            
            if not usuario.is_active or not usuario.groups.filter(name=grupo).exists():
                return False
            print("Username:", usuario.username)
            print("Pertenece al Grupo:", pertenece_al_grupo)
            print("Está activo:", usuario.is_active)

            print('RFC EMISOR:', emisor)
            cliente = Cliente.objects.get(rfc=emisor)
            user_cliente = User_Cliente.objects.get(idCliente=cliente)
                
            if user_cliente.estatus == 'A' and user_cliente.timbres > 0 or  user_cliente.timbres == -1:
                print('cliente',cliente, 'estatus:', user_cliente.estatus, 'timbres:',user_cliente.timbres)
                return True
            print('No esta activo el usuario o no tiene creditos suficientes')
            return False
        except User.DoesNotExist:
            print("Usuario no encontrado")
            return False

    def validate_cancel_user(username, rfc):
        print('cancel')
        grupo = Group.objects.get(name='invoice')
        if DjangoCustomerRepository.is_valid_cancel_user(username, grupo, rfc) == False:
            print("No tienes permisos para acceder a esta página, el usuario no tiene permiso para acceder a la pagina")
            return PermissionDenied("No tienes permisos para acceder a esta página.")
        return True
    
    def is_valid(user, grupo):
        for usuario in user:
            print("Username: ",usuario.username)
            pertenece_al_grupo = grupo in usuario.groups.all()
            us = User.objects.get(username=usuario.username)
            print("Pertenece al Grupo:",pertenece_al_grupo)
            print("Esta activo:", usuario.is_active)
            if pertenece_al_grupo and usuario.is_active:
                print("Es superuser?",us.is_superuser)
                return True
        return False

    def validate():
        usuario = User.objects.all()
        grupo = Group.objects.get(name='invoice')
        if DjangoCustomerRepository.is_valid(usuario, grupo) == False:
            print("No tienes permisos para acceder a esta página, no se encontro un usuario activo perteneciente al grupo Customers")
            return PermissionDenied("No tienes permisos para acceder a esta página.")
        return True
    
    def get_customer_by_id(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            return user
        except User.DoesNotExist:
            return None

    def get_customer_by_username(self, username):
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return None


    def create_customer(self, customer):
        return Customer.objects.create(
            name=customer.name,
            email=customer.email,
            permissions=customer.permissions
        )

    def update_customer(self, customer):
        # Implementar la lógica de actualización según tus necesidades
        pass

    def delete_customer(self, customer_id):
        # Implementar la lógica de eliminación según tus necesidades
        pass

# class SuperuserValidator:
#     @staticmethod
#     def is_superuser_logged_in(user, grupo):
#         for usuario in user:
#             print(usuario.username)
#             pertenece_al_grupo = grupo in usuario.groups.all()
#             us = User.objects.get(username=usuario.username)
#             print("Grupo",pertenece_al_grupo)
#             if pertenece_al_grupo and usuario.is_active:
#                 print("es superuser?",us.is_superuser)
#                 return True
#         return False

#     @staticmethod
#     def validate_superuser():
#         usuario = User.objects.all()
#         grupo = Group.objects.get(name='Customers')
#         if SuperuserValidator.is_superuser_logged_in(usuario, grupo) == False:
#             print("no funciona meriweyn")
#             return PermissionDenied("No tienes permisos para acceder a esta página.")
#         return True
        
# class IsSuperuserMixin(UserPassesTestMixin):
#     def test_func(self):
#         user = self.request.user
#         print("Valor de user.is_superuser:", user.is_superuser)  # Imprimir el valor de is_superuser
#         return user.is_authenticated and user.is_superuser

#     def handle_no_permission(self):
#         return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

#from dominio.invoice.Customer import Customer
#from dominio.invoice.customer_repository import CustomerRepository


#class django_customer_repository(CustomerRepository):
#    """description of class"""
    
#    def __init__(self) -> None:
#        super().__init__()
        
#    def validate(self, customer: Customer) -> Customer:
#        return super().validate(customer)
    
#    def register(self, customer: Customer) -> Customer:
#        return super().register(customer)
    

