from django.conf import settings
from django.db import models
from django.contrib.auth.models import Permission
from invoice.choices import tipo_Cliente, ESTADO_FIRMA, estatus, REGIMENES_FISCAL, estatus_token, STATUS_CHOICES, OPERATION_CHOICES, estatus_timbre
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from cryptography.fernet import Fernet
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_der_private_key

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os 
#############33
from cryptography.hazmat.primitives import hashes

from datetime import datetime
from OpenSSL import crypto
from django.db import models
from django.core.exceptions import ValidationError
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_der_private_key
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from django.db import models
from satcfdi.portal import SATFacturaElectronica
from satcfdi.models import Signer

import subprocess
import datetime
from datetime import datetime as dt
from datetime import timezone

from cryptography.x509.oid import NameOID
import os
import re
import datetime
import requests


import base64
from invoice.vistas.user import register
from suds.client import Client
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from console.models import User_Service, Service_Plan


class InvoicePermissions(models.Model):
    class Meta:
        permissions = (
            ("view_my_soap_application_cancel", "Can view SOAP application cancellation"),
            ("view_my_soap_application_stamp", "Can view SOAP application stamp"),
        )


# class Customer(models.Model):
#     nombre = models.CharField(max_length=100)
#     correoElectronico = models.EmailField()
#     rfc = models.CharField(max_length=100)
#     telefono = models.CharField(max_length=100)
#     tipoDeCliente = models.CharField(max_length=100)
#     certificado = models.FileField(upload_to='certificados/')
#     llave = models.FileField(upload_to='llaves/')
#     contrasena = models.CharField(max_length=100)
#     calle = models.CharField(max_length=100)
#     noExterior = models.CharField(max_length=100)
#     noInterior = models.CharField(max_length=100)
#     colonia = models.CharField(max_length=100)
#     localidad = models.CharField(max_length=100)
#     municipio = models.CharField(max_length=100)
#     estado = models.CharField(max_length=100)
#     codigoPostal = models.CharField(max_length=100)

#     def __str__(self):
#         return f"{self.id} - {self.nombre}"
    


class Cliente(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    apellidoP = models.CharField(max_length=150, verbose_name='Apellido Paterno', null=True, blank=True)
    apellidoM = models.CharField(max_length=150, verbose_name='Apellido Materno', null=True, blank=True)  
    email = models.EmailField(max_length=150, verbose_name='Correo Electronico')
    rfc = models.CharField(max_length=13, verbose_name='RFC', blank=True)
    curp = models.CharField(max_length=18, verbose_name='CURP', blank=True)
    telefono = models.CharField(max_length=10,verbose_name='Telefono', blank=True, null=True)
    tipoCliente = models.CharField(max_length=20, choices=tipo_Cliente, blank=True, default='P')
    Cer = models.FileField(upload_to='cers/', null=True, blank=True)
    Key = models.FileField(upload_to='keys/', null=True, blank=True)
    passphrase = models.CharField(max_length=150,verbose_name='Passphrase', blank=True)
    calle = models.CharField(max_length=150,verbose_name='Calle', blank=True)
    numeroExterior = models.PositiveIntegerField(verbose_name='Numero Exterior', blank=True, null=True)
    numeroInterior = models.PositiveIntegerField(verbose_name='Numero Interior', blank=True, null=True)
    colonia = models.CharField(max_length=150,verbose_name='Colonia', blank=True)
    localidad = models.CharField(max_length=150,verbose_name='Localidad', blank=True)
    municipio = models.CharField(max_length=150,verbose_name='Municipio', blank=True)
    estado = models.CharField(max_length=150,verbose_name='Estado', blank=True)
    pais = models.CharField(max_length=150,verbose_name='pais', null=True, blank=True)
    codigoPostal = models.CharField(max_length=150,verbose_name='Codigo Postal', blank=True)
    tipoReceptor = models.CharField(max_length=15, blank=True, default='moral')
    cer_base64 = models.TextField(null=True, blank=True, verbose_name='Certificado Base64')
    key_base64 = models.TextField(null=True, blank=True, verbose_name='Clave Privada Base64')

    # Variable adicional para almacenar el usuario logueado
    usuario_logueado = None  # Esta variable no es un campo de la base de datos

    def __str__(self):
        return self.nombre
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Guardar el estado inicial de cer y key para comparaciones posteriores
        self._cer_actual = self.Cer
        self._key_actual = self.Key
        self._tipoCliente_Actual = self.tipoCliente

    def clean(self):
        errors = {}
        # Leer archivos una vez y almacenar en variables
        key_data = self.Key.read() if self.Key else None
        cer_data = self.Cer.read() if self.Cer else None
        
        
        # Validación personalizada para el nombre
        if not re.match(r'^[a-zA-Z\s]+$', self.nombre):
            errors['nombre'] = 'El nombre solo puede contener letras y espacios.'

         # Validación personalizada para los apellidos
        if self.apellidoP and not re.match(r'^[a-zA-Z\s]+$', self.apellidoP):
            errors['apellidoP'] = 'El apellido paterno solo puede contener letras y espacios.'
        if self.apellidoM and not re.match(r'^[a-zA-Z\s]+$', self.apellidoM):
            errors['apellidoM'] = 'El apellido materno solo puede contener letras y espacios.'
        
        # Validación para el numero de telefono de que solo debe tener 10 numeros y no letras o simbolos
        if self.telefono and not re.match(r'^\d{10}$', str(self.telefono)):
            errors['telefono'] = 'Formato no valido, tiene que ser un numero de telefono correcto.'

        # Validación para el codigo postal de que solo debe tener 5 numeros y no letras o simbolos
        if self.codigoPostal and not re.match(r'^\d{5}$', self.codigoPostal):
            errors['codigoPostal'] = 'Formato no valido, tiene que ser un codigo postal correcto.'

        # Validación de la CURP
        if self.curp and not re.match(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]{2}$', self.curp):
            errors['curp'] = 'La CURP no tiene un formato válido.'

        # Validación de la dirección de correo electrónico
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', self.email):
            errors['email'] = 'El correo electrónico no tiene un formato válido.'

        # Validación personalizada para RFC
        if self.tipoReceptor in ['fisica', 'moral','extranjero'] and not self.rfc:
            errors['rfc'] = 'El campo RFC es obligatorio para el registro de clientes'
        elif self.tipoReceptor in ['fisica', 'moral'] and self.rfc:
            if not re.match(r'^[A-Z&Ñ]{3,4}\d{6}(?:[A-Z\d]{3})?$', self.rfc):
                errors['rfc'] = 'El RFC no tiene un formato válido.'
        # if self.tipoReceptor == 'extranjero' and self.rfc:
        #     errors['rfc'] = 'El campo RFC no debe estar presente para clientes extranjeros.'

       # Validación de archivo .key
        if self.Key:
            if not self.Key.name.lower().endswith('.key'):
                errors['Key'] = 'El archivo debe tener la extensión .key'
            else:
                try:
                    self.Key.seek(0)  # Resetear el puntero de archivo al inicio
                    key_data = self.Key.read()
                    if key_data is None:
                        raise ValueError("El archivo .key está vacío.")
                    passphrase_bytes = self.passphrase.encode() if self.passphrase else None
                    print(f"Debug: Nombre del archivo .key - {self.Key.name}")
                    print(f"Debug: Tamaño del archivo .key - {len(key_data)} bytes")
                    # Intentar cargar en formato PEM
                    try:
                        private_key = load_pem_private_key(key_data, password=passphrase_bytes, backend=default_backend())
                        print(f"Clave privada cargada en formato PEM: {private_key}")
                        print(f"Tipo de objeto clave privada: {type(private_key)}")
                    except ValueError:
                        # Si falla, intentar cargar en formato DER
                        private_key = load_der_private_key(key_data, password=passphrase_bytes, backend=default_backend())
                        print(f"Clave privada cargada en formato DER: {private_key}")
                        print(f"Tipo de objeto clave privada: {type(private_key)}")
                except Exception as e:
                    errors['Key'] = f'No se pudo deserializar el archivo .key: {str(e)}'

        # Validación de archivo .cer
        if self.Cer:
            if not self.Cer.name.lower().endswith('.cer'):
                errors['Cer'] = 'El archivo debe tener la extensión .cer'
            else:
                try:
                    self.Cer.seek(0)  # Resetear el puntero de archivo al inicio
                    cer_data = self.Cer.read()
                    if cer_data is None:
                        raise ValueError("El archivo .cer está vacío.")
                    print(f"Debug: Nombre del archivo .cer - {self.Cer.name}")
                    print(f"Debug: Tamaño del archivo .cer - {len(cer_data)} bytes")
                    # Intentar cargar en formato PEM
                    try:
                        cert = x509.load_pem_x509_certificate(cer_data, default_backend())
                        certt = crypto.load_certificate(crypto.FILETYPE_PEM, cer_data)

                        print(f"Certificado cargado en formato PEM: {cert}")
                        print(f"Tipo de objeto certificado: {type(cert)}")
                    except ValueError:
                        # Si falla, intentar cargar en formato DER
                        cert = x509.load_der_x509_certificate(cer_data, default_backend())
                        certt = crypto.load_certificate(crypto.FILETYPE_ASN1, cer_data)
                        print(f"Certificado cargado en formato DER: {cert}")
                        print(f"Tipo de objeto certificado: {type(cert)}")

                    # Validar vigencia del certificado
                    try:
                        print(certt)
                        noww = dt.now(timezone.utc)
                        not_valid_before = dt.strptime(certt.get_notBefore().decode('ascii'), "%Y%m%d%H%M%SZ").replace(tzinfo=timezone.utc)
                        not_valid_after = dt.strptime(certt.get_notAfter().decode('ascii'), "%Y%m%d%H%M%SZ").replace(tzinfo=timezone.utc)

                        print("Fecha Actual: ", noww)
                        print("Fecha emisión: ", not_valid_before)
                        print("Fecha expiración: ", not_valid_after)
                        
                        if not_valid_before > noww or not_valid_after < noww:
                            errors['Cer'] = errors.get('Cer', []) + ['El certificado no es vigente.']
                    except ValueError as ve:
                        errors['Cer'] = errors.get('Cer', []) + [str(ve)]


                    # Validar estado del certificado  
                    # Verificar si es un certificado de sello digital
                    try:
                        # Verificar si es un certificado de sello digital
                        extensions = {ext.get_short_name().decode(): ext for ext in (certt.get_extension(i) for i in range(certt.get_extension_count()))}
                        
                        if '2.5.29.37' in extensions:
                            ext = extensions['2.5.29.37']
                            if b'1.3.6.1.5.5.7.3.2' not in ext.get_data():
                                raise ValueError('El certificado no es un Certificado de Sello Digital (CSD)')
                    except ValueError as ve:
                        errors['Cer'] = errors.get('Cer', []) + [str(ve)]
                        
                    # Extraer el RFC del certificado
                    try:
                        # Extraer el RFC del certificado
                        rfc_certificado = None
                        for attr in cert.subject:
                            if attr.oid == NameOID.X500_UNIQUE_IDENTIFIER:
                                rfc_certificado = attr.value.strip().split('/')
                                break
                        
                        # Asegurarse de que se encontró un RFC
                        if rfc_certificado is None:
                            raise ValueError("No se encontró el RFC en el certificado.")
                        
                        # Comparar RFCs
                        print("RFC CERTIFICADO: ", rfc_certificado)
                        print("RFC CLIENTE:", self.rfc)
                        for rfc in rfc_certificado:
                            print(rfc.strip(), " = ", self.rfc)
                            if rfc.strip() == self.rfc:
                                print('El RFC ingresado coincide con el RFC del certificado.')
                                break
                        else:
                            # Este bloque se ejecuta solo si el bucle termina sin encontrar una coincidencia
                            errors['Cer'] = errors.get('Cer', []) + ['El RFC ingresado no coincide con el RFC del certificado.']

                    except ValueError as ve:
                        errors['Cer'] = errors.get('Cer', []) + [str(ve)]
                   
                except Exception as e:
                    errors['Cer'] = f'No se pudo deserializar el archivo .cer: {str(e)}'


        # Validación de la relación entre el archivo .key y .cer
        # Validación de la relación entre la clave privada y el certificado
        if self.Cer and self.Key:
            if 'Key' not in errors and 'Cer' not in errors:
                try:
                    public_key = cert.public_key()
                    print("public_key: ",public_key)
                    mensaje = os.urandom(32)
                    print("mensaje: ",mensaje)
                    firma = private_key.sign(
                        mensaje,
                        padding.PKCS1v15(),
                        hashes.SHA256()
                    )
                    print("firma: ",firma)
                    public_key.verify(
                        firma,
                        mensaje,
                        padding.PKCS1v15(),
                        hashes.SHA256()
                    )
                    print("Verificación de la firma con la clave pública",public_key.verify(
                        firma,
                        mensaje,
                        padding.PKCS1v15(),
                        hashes.SHA256()
                    ))
                except Exception as e:
                    errors['Key'] = f'La clave privada y el certificado no corresponden: {str(e)}'
       
        # Verificar si los alguno de los campos a sido llenado
        fields_filled = [bool(self.passphrase), bool(self.Cer), bool(self.Key)]
        print(fields_filled)
        # Si alguno de los campos ha sido llenado requerir los demas
        if any(fields_filled) and not all(fields_filled):
            missing_fields = []

            if not self.passphrase:
                missing_fields.append('passphrase')
            if not self.Cer:
                missing_fields.append('Cer')
            if not self.Key:
                missing_fields.append('Key')

            present_fields = [field for field, value in zip(['passphrase', 'Cer', 'Key'], fields_filled) if value]

            errors['Key'] = (
                f"Todos los campos (passphrase, Cer, Key) son requeridos si alguno de ellos es llenado. "
                f"Faltan los campos: {', '.join(missing_fields)}. "
                f"Campos presentes: {', '.join(present_fields)}."
            )

        if errors:
            raise ValidationError(errors)

        # Llamar al servicio SOAP para registrar al usuario
        ctx = ''
        key_base64 = ''
        cer_base64 = ''
        passh = ''
        if self.Cer and self.Key and self.passphrase:
            self.Key.seek(0)  # Asegurarse de que el puntero de archivo esté al principio
            key_base64 = base64.b64encode(self.Key.read()).decode('utf-8')
            self.Cer.seek(0)  # Asegurarse de que el puntero de archivo esté al principio
            cer_base64 = base64.b64encode(self.Cer.read()).decode('utf-8')
            passh = self.passphrase
        try:
            print('usuario log', self.usuario_logueado)
            # Obtén los servicios relacionados con el usuario logueado
            user_services = User_Service.objects.filter(idUser=self.usuario_logueado).first()
            print('service:',user_services)
            # Obtén los Service_Plan relacionados con el usuario logueado
            service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()
            print("Debug: Llamando al servicio SOAP con los siguientes datos:")
            print(f"Email: {service_plans.supplierStamp.user}, RFC: {self.rfc}, Tipo Cliente: {self.tipoCliente}, passphrase: {passh}")
            # Validar si es un usuario nuevo se llama el servicio soap addd
            if self.id is None:
            # Es un nuevo cliente, llamar al servicio SOAP add
                print('add')
                resultado = register.RegisterService.add(
                    ctx,
                    service_plans.supplierStamp.user,
                    service_plans.supplierStamp.decrypt_password(),
                    self.rfc,
                    'O', #Se guardaran siempre como ondemant en finkok
                    cer_base64,
                    key_base64,
                    passh
                )
                print("Debug: Resultado del servicio SOAP - ", resultado)
                if not resultado:
                    errors['Key'] = 'Error al registrar al usuario en el servicio SOAP'
            # Si no es un nuevo usuaio entra en el else
            else:
            # Cliente existente, revisar si se han actualizado archivos cer y key
                print('edit cer: ', self.Cer)
                print('edit cer_actual: ', self._cer_actual)
                # Valida que los archivos CSD sean diferentes a los ya almacenados si 
                # son diferntes usar el servicio web edit para remplazarlos por los nuevos
                if self.Cer != self._cer_actual and self.Key != self._key_actual:
                    print('EDIT')
                    resultado = register.RegisterService.edit(
                        ctx,
                        service_plans.supplierStamp.user,
                        service_plans.supplierStamp.decrypt_password(),
                        self.rfc,
                        'A',
                        cer_base64,
                        key_base64,
                        passh
                    )
                    print("Debug: Resultado del servicio SOAP - ", resultado)
                    if not resultado:
                        errors['Key'] = 'Error al editar al usuario en el servicio SOAP'
                if self.tipoCliente != self._tipoCliente_Actual:
                    # print('switch')
                    # resultado = register.RegisterService.switch(
                    #     ctx,
                    #     service_plans.supplierStamp.user,
                    #     service_plans.supplierStamp.decrypt_password(),
                    #     self.rfc,
                    #     self.tipoCliente
                    # )
                    # print("Debug: Resultado del servicio SOAP - ", resultado)
                    # if not resultado:
                    #     errors['Key'] = 'Error al cambiar el tipo al usuario en el servicio SOAP'
                    if self.tipoCliente == 'O':
                        user_cliente = User_Cliente.objects.get(idCliente=self, idUser=self.usuario_logueado)
                        print('onde', user_cliente.id)
                        # Se optiene el timbre actual
                        timbre_actual = Timbre.objects.get(user_cliente=user_cliente, estatus='A')
                        # Se crea un nuevo timbre de tipo ondeman
                        timbre = Timbre(user_cliente=user_cliente, isOnDemmand=True, stamp=-1, cont_stamped_cliente=timbre_actual.cont_stamped_cliente,  cont_stamped_day=timbre_actual.cont_stamped_day)
                        timbre_actual.estatus = 'S'  # Cambiar el estatus a suspendido
                        timbre_actual.save()
                        timbre.save()
                    else:
                        user_cliente = User_Cliente.objects.get(idCliente=self, idUser=self.usuario_logueado)
                        # Se optiene el timbre actual
                        timbre_actual = Timbre.objects.get(user_cliente=user_cliente, estatus='A')
                        # Se crea un nuevo timbre de tipo prepago
                        timbre = Timbre(user_cliente=user_cliente, cont_stamped_cliente=timbre_actual.cont_stamped_cliente,  cont_stamped_day=timbre_actual.cont_stamped_day)
                        timbre_actual.estatus = 'S'  # Cambiar el estatus a suspendido
                        timbre_actual.save()
                        timbre.save()

        except Exception as e:
            print(f"Error llamando al servicio SOAP: {str(e)}")
            errors['Key'] = f'Error al registrar al usuario en el servicio SOAP: {str(e)}'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Almacenar los archivos anteriores
        old_instance = Cliente.objects.filter(pk=self.pk).first()  # Recuperar la instancia anterior
        old_key = old_instance.Key if old_instance else None
        old_cer = old_instance.Cer if old_instance else None

        # Guardar la nueva instancia
        super().save(*args, **kwargs)

        # Eliminar archivos antiguos si son reemplazados o eliminados
        if old_key and old_key != self.Key:
            old_key.delete(save=False)
        if old_cer and old_cer != self.Cer:
            old_cer.delete(save=False)

        if self.Key:
            self.Key.seek(0)
            self.key_base64 = base64.b64encode(self.Key.read()).decode('utf-8')
        if self.Cer:
            self.Cer.seek(0)
            self.cer_base64 = base64.b64encode(self.Cer.read()).decode('utf-8')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        #Eliminar los achivos asociados
        self.Cer.delete(save=False)
        self.Key.delete(save=False)
        super(Cliente, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['id']


class User_Cliente(models.Model):
    
    class Meta:
        unique_together = (('idCliente', 'idUser'),)
        verbose_name = 'User_Cliente'
        verbose_name_plural = 'User_Clientes'
        ordering = ['id']

    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    idUser = models.ForeignKey(User, on_delete=models.CASCADE)

    estatus = models.CharField(max_length=20, choices=estatus, default='A')
    #Imanol Corregir. Adicione el campo. Este campo será el contador de timbres
    #cada que un cliente de un usuario de invoice timbre a través del servicio
    # de timbrado de la app invoice
    countStamp = models.IntegerField(verbose_name='Contador de timbres', default=0)

    def __str__(self):
        return self.idCliente.nombre
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Guardar el estado inicial de cer y key para comparaciones posteriores
        self.actual_estatus = self.estatus

    def clean(self):
        errors = {}
        # Validación de campos requeridos
        # # Obtén los servicios relacionados con el usuario logueado
        # user_services = User_Service.objects.filter(idUser=self.idUser).first()
        # print('service:',user_services)
        # # Obtén los Service_Plan relacionados con el usuario logueado
        # service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()

        # ctx = ''
        # try:
        #     print("Debug: Llamando al servicio SOAP con los siguientes datos:")
        #     print(f"Email: {service_plans.supplierStamp.user}, RFC: {self.idCliente.rfc}, Estatus: {self.estatus}")
        #     if self.estatus != self.actual_estatus:
        #             # Utilizar el servicio web para cambiar el estatus del cliente
        #             print(self.estatus)
        #             if self.estatus == 'A':
        #                 print('Estatus: Activo')
        #                 print('update_token')
        #                 resultado = register.RegisterService.edit(
        #                     ctx,
        #                     service_plans.supplierStamp.user,
        #                     service_plans.supplierStamp.decrypt_password(),
        #                     self.idCliente.rfc,
        #                     self.estatus,
        #                     '',
        #                     '',
        #                     '',
        #                 )
        #                 print("Debug: Resultado del servicio SOAP - ", resultado)
        #             else:
        #                 print('Estatus: Suspendido')
        #                 print('Estatus: Activo')
        #                 print('update_token')
        #                 resultado = register.RegisterService.edit(
        #                     ctx,
        #                     service_plans.supplierStamp.user,
        #                     service_plans.supplierStamp.decrypt_password(),
        #                     self.idCliente.rfc,
        #                     self.estatus,
        #                     '',
        #                     '',
        #                     '',
        #                 )
        #                 print("Debug: Resultado del servicio SOAP - ", resultado)

        # except Exception as e:
        #     print(f"Error llamando al servicio SOAP: {str(e)}")
        #     errors[NON_FIELD_ERRORS] = f'Error en el servicio: {str(e)}'

        # Validación: verificar que el usuario no tenga otro cliente con el mismo RFC
        print('validaciones user cliente', self.idCliente.rfc)
        if User_Cliente.objects.filter(idUser=self.idUser, idCliente__rfc=self.idCliente.rfc).exists():
            errors['idCliente'] = f'Ya has registrado un cliente con este RFC: {self.idCliente.rfc}'
        
        if errors:
            print('errores', errors)
            raise ValidationError(errors)
    
#class TimbreCliente(models.Model):
class Timbre(models.Model):
    user_cliente = models.ForeignKey(User_Cliente, on_delete=models.CASCADE, related_name='timbres_de_cliente')
    fecha =models.DateTimeField(auto_now_add=True, verbose_name='Fecha')

    estatus = models.CharField(max_length=20, choices=estatus_timbre, default='A')
    isOnDemmand = models.BooleanField(default=False)

    #Este campo tendrá el número de timbres que le asigna el user invoice
    #Este campo será actualizado cada vez que un cliente del user invoice se le asigne timbres
    #ESto tambien debe actualizarse en el PAC
    stamp = models.IntegerField(default=0)
    #Adicione el campo. Este campo será el contador de timbres
    #cada que un cliente de un usuario de invoice timbre a través del servicio
    # de timbrado de la app invoice
    cont_stamped_cliente = models.IntegerField(default=0) #Imanol: Este campo es para llevar el conteo de timbres asignados a un cliente
    cont_stamped_day = models.IntegerField(default=0) #Imanol: Este campo es para llevar el conteo de timbres asignados a un cliente


    def clean(self):
        errors = {} 

        # Obtén los servicios relacionados con el usuario logueado
        user_services = User_Service.objects.filter(idUser=self.user_cliente.idUser).first()
        print('service:',user_services)
        # Obtén los Service_Plan relacionados con el usuario logueado
        service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()

        print("Debug: Método clean() ejecutado para Timbre")
        # Obtener el RFC del cliente asociado
        rfc_cliente = self.user_cliente.idCliente.rfc
        
        # Debug: Imprimir el RFC del cliente
        print(f"Debug: RFC del Cliente - {rfc_cliente}")

        # # Llamar al servicio SOAP para crear timbre
        # ctx = ''
        # try:
        #     print("Debug: Llamando al servicio SOAP con los siguientes datos:")
        #     print(f"Email: {service_plans.supplierStamp.user}, RFC: {rfc_cliente}, Estatus: {self.stamp}")
        #     #obtener timbre anterior
        #     anterior = Timbre.objects.filter(user_cliente=self.user_cliente, estatus='A').first()
        #     anteriorStamp = anterior.stamp if anterior else 0  # 0 si no hay timbre anterior
        #     print('Creditos anteriores', anterior)
        #     # se le asignan creditos, llamar al servicio SOAP assing
        #     print('add')
        #     resultado = register.RegisterService.assign(
        #         ctx,
        #         service_plans.supplierStamp.user,
        #         service_plans.supplierStamp.decrypt_password(),
        #         rfc_cliente,
        #         self.stamp-anteriorStamp,
        #     )
        #     print("Debug: Resultado del servicio SOAP - ", resultado)
        #     # Suponiendo que 'resultado' es un objeto con 'message' y 'token'
        #     print('success',resultado.success)
            
        #     if not resultado.success:  # Si success es False
        #         errors[NON_FIELD_ERRORS] = f'Error en el servicio: {resultado.message}'
        #     else:
        #         print('message response:', resultado.message) 
            
        # except Exception as e:
        #     print(f"Error llamando al servicio SOAP: {str(e)}")
        #     errors[NON_FIELD_ERRORS] = f'Error en el servicio SOAP: {str(e)}'

        # Validación: 'stamp' no puede ser un número negativo
        if self.stamp < 0:
            errors['stamp'] = 'El número de timbres no puede ser mayor al numero de timbres disponibles por el cliente.'
            
        if errors:
            raise ValidationError(errors)

    class meta:
        verbose_name = 'Timbre'
        verbose_name_plural = 'Timbres'
        ordering = ['id']

    def __str__(self):
        return f"Timbre de {self.user_cliente} - Facturas: {self.stamp}"
    
########################################################

    
        

class Tokens(models.Model):
    #Imanol: Ajustar 
    #Estos serian los neuvos campos ppropuestas

    # Campo idUserToken utilizando un nombre único para la relación inversa
    idUserToken = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='token_user'
    )
    
    # Campo idUserParent utilizando otro nombre único para la relación inversa
    idUserParent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parent_tokens'
    )
    taxpayer_id = models.CharField(max_length=13, verbose_name='RFC', blank=True, null=True)
    
    # Variable adicional para almacenar el usuario logueado
    usuario_logueado = None  # Esta variable no es un campo de la base de datos


    #Los campos sigueintes campos de abajo se almacenarian y quedarian cuando se registre el nuevo User
    #Imanol: Corregir. Quitar todos los campos de abajo, ya estan en el modelo User
    #de Dajango.
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    userName = models.CharField(max_length=150, verbose_name='Nombre de Usuario')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    estatus = models.CharField(max_length=20, choices=estatus_token, blank=True, default='true')
    token = models.CharField(max_length=255, blank=True, null=True)

    #y despues se inserta registro en modelo token, 
    # se asocia el usuario creado con el registro toeken en el campo idUserToken.
    # y despues se asigna  el usuario auntenticado con el token en el campo idUserParent
    

    def __str__(self):
        return self.nombre
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Guardar el estado inicial de cer y key para comparaciones posteriores
        self.actual_estatus = self.estatus

    def clean(self):
        errors = {}
         # Validación de campos requeridos
        if not self.nombre:
            errors['nombre'] = 'El nombre es obligatorio.'
        if not self.userName:
            errors['userName'] = 'El nombre de usuario es obligatorio.'
        # Validación de la RFC
        if self.taxpayer_id and not re.match(r'^[A-Z&Ñ]{3,4}\d{6}(?:[A-Z\d]{3})?$', self.taxpayer_id):
            errors['taxpayer_id'] = 'El RFC no tiene un formato válido.'
        if errors:
            raise ValidationError(errors)
        # Llamar al servicio SOAP para crear token
        ctx = ''
        try:
            print('try', self.usuario_logueado)
            if self.id is None:
                # Obtén los servicios relacionados con el usuario logueado
                user_services = User_Service.objects.filter(idUser=self.usuario_logueado).first()
                print('service:',user_services)
                # Obtén los Service_Plan relacionados con el usuario logueado
                service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()
                    
                print("Debug: Llamando al servicio SOAP con los siguientes datos:")
                print(f"Email: {service_plans.supplierStamp.user}, RFC: {self.taxpayer_id}, Estatus: {self.estatus}")
                
                # Es un nuevo token, llamar al servicio SOAP add
                print('add')
                resultado = register.UtilitiesSOAP.add_tokens(
                    ctx,
                    service_plans.supplierStamp.user,
                    service_plans.supplierStamp.decrypt_password(),
                    self.nombre,
                    self.userName,
                    self.taxpayer_id,
                    self.estatus
                )
                print("Debug: Resultado del servicio SOAP - ", resultado)
                # Suponiendo que 'resultado' es un objeto con 'message' y 'token'
                if hasattr(resultado, 'message'):
                    errors[NON_FIELD_ERRORS] = f'Error al registrar al usuario en el servicio SOAP: {resultado.message}'
                elif hasattr(resultado, 'token'):
                    self.token = resultado.token

                print('token response:',self.token)

            elif self.estatus != self.actual_estatus:
                    # Obtén los servicios relacionados con el usuario logueado
                    user_services = User_Service.objects.filter(idUser=self.idUserParent).first()
                    print('service:',user_services)
                    # Obtén los Service_Plan relacionados con el usuario logueado
                    service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()
                    
                    print("Debug: Llamando al servicio SOAP con los siguientes datos:")
                    print(f"Email: {service_plans.supplierStamp.user}, RFC: {self.taxpayer_id}, Estatus: {self.estatus}")
                
                    # Utilizar el servicio web para cambiar el estatus del token
                    print(self.estatus)
                    if self.estatus == 'true':
                        print('Estatus: Activo')
                        print('update_token')
                        resultado = register.UtilitiesSOAP.update_token(
                            ctx,
                            service_plans.supplierStamp.user,
                            service_plans.supplierStamp.decrypt_password(),
                            self.userName,
                            '1'
                        )
                        print("Debug: Resultado del servicio SOAP - ", resultado)
                    else:
                        print('Estatus: Suspendido')
                        print('Estatus: Activo')
                        print('update_token')
                        resultado = register.UtilitiesSOAP.update_token(
                            ctx,
                            service_plans.supplierStamp.user,
                            service_plans.supplierStamp.decrypt_password(),
                            self.userName,
                            '0'
                        )
                        print("Debug: Resultado del servicio SOAP - ", resultado)
            else:
                # Obtén los servicios relacionados con el usuario logueado
                user_services = User_Service.objects.filter(idUser=self.idUserParent).first()
                print('service:',user_services)
                # Obtén los Service_Plan relacionados con el usuario logueado
                service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()
                
                print("Debug: Llamando al servicio SOAP con los siguientes datos:")
                print(f"Email: {service_plans.supplierStamp.user}, RFC: {self.taxpayer_id}, Estatus: {self.estatus}")
                
                # Es un token existente, llamar al servicio SOAP reset
                print('reset_token')
                resultado = register.UtilitiesSOAP.reset_token(
                    ctx,
                    service_plans.supplierStamp.user,
                    service_plans.supplierStamp.decrypt_password(),
                    self.userName
                )
                print("Debug: Resultado del servicio SOAP - ", resultado)
                 # Suponiendo que 'resultado' es un objeto con 'message' y 'token'
                if hasattr(resultado, 'message'):
                    errors[NON_FIELD_ERRORS] = f'Error al reset el token en el servicio SOAP: {resultado.message}'
                elif hasattr(resultado, 'token'):
                    self.token = resultado.token

                print('token response:',resultado.token)

        except Exception as e:
            print(f"Error llamando al servicio SOAP token: {str(e)}")
            errors[NON_FIELD_ERRORS] = f'Error al registrar al usuario en el servicio SOAP: {str(e)}'

        if errors:
            raise ValidationError(errors)
        
    class Meta:
            verbose_name = 'Gestion_token'
            verbose_name_plural = 'Gestion_tokens'
            ordering = ['id']
    
# Modelo para los contratos
class Contratos(models.Model):
    Cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contrato_cliente')
    fecha = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Firma')
    estado_firma = models.CharField(max_length=10, choices=ESTADO_FIRMA, default='false', )
    contratoXML = models.TextField(null=True, blank=True)  # Cambiado de BinaryField a TextField
    contratoPDF = models.TextField(null=True, blank=True)  # Almacena el PDF en Base64

    class Meta:
        verbose_name = 'Gestion_firma'
        verbose_name_plural = 'Gestion_firmas'
        ordering = ['id']

    def __str__(self):
        return f"Contrato de {self.Cliente} - Estatus: {self.estado_firma}"
    


def get_default_user():
    return User.objects.first().id 

class TimbreUserPerfil(models.Model):
    # Relación con el usuario del servicio de facturación
    userInvoice = models.ForeignKey(User, on_delete=models.CASCADE, default=get_default_user)  # Valor por defecto agregado
    fecha = models.DateTimeField(auto_now_add=True)
    idUser_ServicePlan = models.ForeignKey(User_Service, on_delete=models.DO_NOTHING)  # No blanco ni nulo
    estatus = models.CharField(max_length=20, choices=estatus_timbre, default='A')
    isOnDemmand = models.BooleanField(default=False)
    stamp = models.IntegerField(default=0)  # Número de timbres asignados por el plan
    cont_stamped_user = models.IntegerField(default=0)
    cont_stamped_day = models.IntegerField(default=0)

    def clean(self):
        errors = {}
        print("Debug: Método clean() ejecutado para TimbreUserPerfil")

        # Obtener el RFC del perfil asociado
        try:
            rfc_perfil = self.userInvoice.perfilfiscaluser.rfc  # Acceder al campo 'rfc' a través de la relación OneToOne
        except PerfilFiscalUser.DoesNotExist:
            errors[NON_FIELD_ERRORS] = 'El perfil fiscal asociado no existe para este usuario.'

        # Debug: Imprimir el RFC del perfil
        if 'rfc_perfil' in locals():
            print(f"Debug: RFC del Perfil - {rfc_perfil}")
        else:
            print("Debug: RFC del Perfil no encontrado.")

        # # Llamar al servicio SOAP para asinarle creditos al usuario
        # ctx = ''
        # try:
        #     # Obtén los servicios relacionados con el usuario logueado
        #     user_services = User_Service.objects.filter(idUser=self.userInvoice).first()
        #     print('service:',user_services)
        #     # Obtén los Service_Plan relacionados con el usuario logueado
        #     service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()
            
        #     if 'rfc_perfil' in locals():
        #         print("Debug: Llamando al servicio SOAP con los siguientes datos:")
        #         print(f"Email: {service_plans.supplierStamp}, RFC: {rfc_perfil}, Estatus: {self.stamp}")
        #         anterior = TimbreUserPerfil.objects.filter(userInvoice=self.userInvoice, estatus='A').first()
        #         anteriorStamp = anterior.stamp if anterior else 0  # 0 si no hay timbre anterior
        #         print('clean timbre anteroir', anteriorStamp)
        #         # Es un nuevo token, llamar al servicio SOAP add
        #         print('add')
        #         resultado = register.RegisterService.assign(
        #             ctx,
        #             service_plans.supplierStamp.user,
        #             service_plans.supplierStamp.decrypt_password(),
        #             rfc_perfil,
        #             self.stamp - anteriorStamp,
        #         )
        #         print("Debug: Resultado del servicio SOAP - ", resultado)

        #         if not resultado.success:
        #             errors[NON_FIELD_ERRORS] = f'Error al registrar al usuario en el servicio SOAP: {resultado.message}'
        #         else:
        #             print('message response:', resultado.message)
        #     else:
        #         print("Error: RFC no encontrado, no se puede proceder con el servicio SOAP.")

        # except Exception as e:
        #     print(f"Error llamando al servicio SOAP: {str(e)}")
        #     errors[NON_FIELD_ERRORS] = f'Error al registrar al usuario en el servicio SOAP: {str(e)}'
        
        # Validación: 'stamp' no puede ser un número negativo
        if self.stamp < 0:
            errors['stamp'] = 'El número de timbres no puede ser mayor al numero de timbres disponibles por el Usuario.'
        if errors:
            raise ValidationError(errors)
    class Meta:
        verbose_name = 'Timbre User Perfil'
        verbose_name_plural = 'Timbres User Perfil'
        ordering = ['id']

    def __str__(self):
        return f"Timbre de perfil {self.userInvoice} - Créditos: {self.stamp}"  # Ajuste en el __str__ method
        #return f"Contrato de {self.Cliente} - Estatus: {self.estado_firma}"


class PerfilFiscalUser(models.Model):

    
  
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    apellidoP = models.CharField(max_length=150, verbose_name='Apellido Paterno', null=True, blank=True)
    apellidoM = models.CharField(max_length=150, verbose_name='Apellido Materno', null=True, blank=True)  
    email = models.EmailField(max_length=150, verbose_name='Correo Electronico')
    rfc = models.CharField(max_length=13, verbose_name='RFC', blank=True, null=True)  # RFC único
    curp = models.CharField(max_length=18, verbose_name='CURP', blank=True)
    telefono = models.BigIntegerField(verbose_name='Telefono', blank=True, null=True)
    tipoCliente = models.CharField(max_length=20, choices=tipo_Cliente, blank=True, default='P')
    Cer = models.FileField(upload_to='cers/', null=True, blank=True)
    Key = models.FileField(upload_to='keys/', null=True, blank=True)
    passphrase = models.CharField(max_length=150,verbose_name='Passphrase', blank=True)
    calle = models.CharField(max_length=150,verbose_name='Calle', blank=True)
    numeroExterior = models.PositiveIntegerField(verbose_name='Numero Exterior', blank=True, null=True)
    numeroInterior = models.PositiveIntegerField(verbose_name='Numero Interior', blank=True, null=True)
    colonia = models.CharField(max_length=150,verbose_name='Colonia', blank=True)
    localidad = models.CharField(max_length=150,verbose_name='Localidad', blank=True)
    municipio = models.CharField(max_length=150,verbose_name='Municipio', blank=True)
    estado = models.CharField(max_length=150,verbose_name='Estado', blank=True)
    pais = models.CharField(max_length=150,verbose_name='pais', null=True, blank=True)
    codigoPostal = models.CharField(max_length=150,verbose_name='Codigo Postal', blank=True)
    tipoReceptor = models.CharField(max_length=15, blank=True, default='moral')
    
    # Campos nuevos
    localizado = models.BooleanField(default=False, verbose_name='Localizado en una zona fronteriza')
    compartir_datos = models.BooleanField(default=False, verbose_name='Compartir datos fiscales (live connect)')
    mostrar_razon_social = models.BooleanField(default=False, verbose_name='Mostrar nombre o razón social en CFDI')
    mostrar_domicilio = models.BooleanField(default=False, verbose_name='Mostrar en domicilio fiscal CFDI')
    mostrar_direccion_expedicion = models.BooleanField(default=False, verbose_name='Mostrar dirección de expedición en CFDI')
    mostrar_nombre_cliente = models.BooleanField(default=False, verbose_name='Mostrar nombre o razón social de cliente en CFDI')
    mostrar_direccion_cliente = models.BooleanField(default=False, verbose_name='Mostrar dirección del cliente en CFDI')

    regimen_Fiscal = models.CharField(max_length=20, choices=REGIMENES_FISCAL, blank=True, default='601') 


    cer_base64 = models.TextField(null=True, blank=True, verbose_name='Certificado Base64')
    key_base64 = models.TextField(null=True, blank=True, verbose_name='Clave Privada Base64')

    #Efren: Se agregaro estos campos al modelo para almacenar estatus de firma de contrato 
    # y el contrato en XML y PDF
    #Campos para almacenar el estatus de firma del comtrato
    fecha = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Firma') # Se actuliza cuanso se sepa que el contrato  ya fue firmado 
    estado_firma = models.CharField(max_length=10, choices=ESTADO_FIRMA, default='false', )
    contratoXML = models.TextField(null=True, blank=True)  # Cambiado de BinaryField a TextField
    contratoPDF = models.TextField(null=True, blank=True)  # Almacena el PDF en Base64
    token = models.CharField(max_length=255, blank=True, null=True)
    estatus = models.CharField(max_length=20, choices=estatus, default='S')
    validado = models.BooleanField(default=False)  # Bandera para saber si ya se validó

    usuario_logueado = None 
    def __str__(self):
        return self.nombre
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cipher = Fernet(settings.ENCRYPTION_KEY)
        # Guardar el estado inicial de cer y key para comparaciones posteriores
        self._cer_actual = self.Cer
        self._key_actual = self.Key
        self._tipoCliente_Actual = self.tipoCliente


#########################################################  ENCRIPTACION DE TOKENS  ######################################################################
    def encrypt_token(self, token):
        # Encriptar la contraseña
        return self.cipher.encrypt(token.encode()).decode()

    def decrypt_token(self):
        # Desencriptar la contraseña
        return self.cipher.decrypt(self.token.encode()).decode()
    
########################################################################################################################################################
    def clean(self):
        errors = {}
        # Leer archivos una vez y almacenar en variables
        key_data = self.Key.read() if self.Key else None
        cer_data = self.Cer.read() if self.Cer else None
        
        
        # Validación personalizada para el nombre
        if not re.match(r'^[a-zA-Z\s]+$', self.nombre):
            errors['nombre'] = 'El nombre solo puede contener letras y espacios.'

         # Validación personalizada para los apellidos
        if self.apellidoP and not re.match(r'^[a-zA-Z\s]+$', self.apellidoP):
            errors['apellidoP'] = 'El apellido paterno solo puede contener letras y espacios.'
        if self.apellidoM and not re.match(r'^[a-zA-Z\s]+$', self.apellidoM):
            errors['apellidoM'] = 'El apellido materno solo puede contener letras y espacios.'
        
        # Validación para el numero de telefono de que solo debe tener 10 numeros y no letras o simbolos
        if self.telefono and not re.match(r'^\d{10}$', str(self.telefono)):
            errors['telefono'] = 'Formato no valido, tiene que ser un numero de telefono correcto.'

        # Validación para el codigo postal de que solo debe tener 5 numeros y no letras o simbolos
        if self.codigoPostal and not re.match(r'^\d{5}$', self.codigoPostal):
            errors['codigoPostal'] = 'Formato no valido, tiene que ser un codigo postal correcto.'

        # Validación de la CURP
        if self.curp and not re.match(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]{2}$', self.curp):
            errors['curp'] = 'La CURP no tiene un formato válido.'

        # Validación de la dirección de correo electrónico
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', self.email):
            errors['email'] = 'El correo electrónico no tiene un formato válido.'

        # Validación personalizada para RFC
        if self.tipoReceptor in ['fisica', 'moral'] and not self.rfc:
            errors['rfc'] = 'El campo RFC es obligatorio para clientes físicos y morales.'
        elif self.tipoReceptor in ['fisica', 'moral'] and self.rfc:
            if not re.match(r'^[A-Z&Ñ]{3,4}\d{6}(?:[A-Z\d]{3})?$', self.rfc):
                errors['rfc'] = 'El RFC no tiene un formato válido.'
        if self.tipoReceptor == 'extranjero' and self.rfc:
            errors['rfc'] = 'El campo RFC no debe estar presente para clientes extranjeros.'

       # Validación de archivo .key
        if self.Key:
            if not self.Key.name.lower().endswith('.key'):
                errors['Key'] = 'El archivo debe tener la extensión .key'
            else:
                try:
                    self.Key.seek(0)  # Resetear el puntero de archivo al inicio
                    key_data = self.Key.read()
                    if key_data is None:
                        raise ValueError("El archivo .key está vacío.")
                    passphrase_bytes = self.passphrase.encode() if self.passphrase else None
                    print(f"Debug: Nombre del archivo .key - {self.Key.name}")
                    print(f"Debug: Tamaño del archivo .key - {len(key_data)} bytes")
                    # Intentar cargar en formato PEM
                    try:
                        private_key = load_pem_private_key(key_data, password=passphrase_bytes, backend=default_backend())
                        print(f"Clave privada cargada en formato PEM: {private_key}")
                        print(f"Tipo de objeto clave privada: {type(private_key)}")
                    except ValueError:
                        # Si falla, intentar cargar en formato DER
                        private_key = load_der_private_key(key_data, password=passphrase_bytes, backend=default_backend())
                        print(f"Clave privada cargada en formato DER: {private_key}")
                        print(f"Tipo de objeto clave privada: {type(private_key)}")
                except Exception as e:
                    errors['Key'] = f'No se pudo deserializar el archivo .key: {str(e)}'

        # Validación de archivo .cer
        if self.Cer:
            if not self.Cer.name.lower().endswith('.cer'):
                errors['Cer'] = 'El archivo debe tener la extensión .cer'
            else:
                try:
                    self.Cer.seek(0)  # Resetear el puntero de archivo al inicio
                    cer_data = self.Cer.read()
                    if cer_data is None:
                        raise ValueError("El archivo .cer está vacío.")
                    print(f"Debug: Nombre del archivo .cer - {self.Cer.name}")
                    print(f"Debug: Tamaño del archivo .cer - {len(cer_data)} bytes")
                    # Intentar cargar en formato PEM
                    try:
                        cert = x509.load_pem_x509_certificate(cer_data, default_backend())
                        certt = crypto.load_certificate(crypto.FILETYPE_PEM, cer_data)

                        print(f"Certificado cargado en formato PEM: {cert}")
                        print(f"Tipo de objeto certificado: {type(cert)}")
                    except ValueError:
                        # Si falla, intentar cargar en formato DER
                        cert = x509.load_der_x509_certificate(cer_data, default_backend())
                        certt = crypto.load_certificate(crypto.FILETYPE_ASN1, cer_data)
                        print(f"Certificado cargado en formato DER: {cert}")
                        print(f"Tipo de objeto certificado: {type(cert)}")

                    # Validar vigencia del certificado
                    try:
                        print(certt)
                        noww = dt.now(timezone.utc)
                        not_valid_before = dt.strptime(certt.get_notBefore().decode('ascii'), "%Y%m%d%H%M%SZ").replace(tzinfo=timezone.utc)
                        not_valid_after = dt.strptime(certt.get_notAfter().decode('ascii'), "%Y%m%d%H%M%SZ").replace(tzinfo=timezone.utc)

                        print("Fecha Actual: ", noww)
                        print("Fecha emisión: ", not_valid_before)
                        print("Fecha expiración: ", not_valid_after)
                        
                        if not_valid_before > noww or not_valid_after < noww:
                            errors['Cer'] = errors.get('Cer', []) + ['El certificado no es vigente.']
                    except ValueError as ve:
                        errors['Cer'] = errors.get('Cer', []) + [str(ve)]


                    # Validar estado del certificado  
                    # Verificar si es un certificado de sello digital
                    try:
                        # Verificar si es un certificado de sello digital
                        extensions = {ext.get_short_name().decode(): ext for ext in (certt.get_extension(i) for i in range(certt.get_extension_count()))}
                        
                        if '2.5.29.37' in extensions:
                            ext = extensions['2.5.29.37']
                            if b'1.3.6.1.5.5.7.3.2' not in ext.get_data():
                                raise ValueError('El certificado no es un Certificado de Sello Digital (CSD)')
                    except ValueError as ve:
                        errors['Cer'] = errors.get('Cer', []) + [str(ve)]
                        
                    # Extraer el RFC del certificado
                    try:
                        # Extraer el RFC del certificado
                        rfc_certificado = None
                        for attr in cert.subject:
                            if attr.oid == NameOID.X500_UNIQUE_IDENTIFIER:
                                rfc_certificado = attr.value.strip().split('/')
                                break
                        
                        # Asegurarse de que se encontró un RFC
                        if rfc_certificado is None:
                            raise ValueError("No se encontró el RFC en el certificado.")
                        
                        # Comparar RFCs
                        print("RFC CERTIFICADO: ", rfc_certificado)
                        print("RFC CLIENTE:", self.rfc)
                        for rfc in rfc_certificado:
                            print(rfc.strip(), " = ", self.rfc)
                            if rfc.strip() == self.rfc:
                                print('El RFC ingresado coincide con el RFC del certificado.')
                                break
                        else:
                            # Este bloque se ejecuta solo si el bucle termina sin encontrar una coincidencia
                            errors['Cer'] = errors.get('Cer', []) + ['El RFC ingresado no coincide con el RFC del certificado.']

                    except ValueError as ve:
                        errors['Cer'] = errors.get('Cer', []) + [str(ve)]
                   
                except Exception as e:
                    errors['Cer'] = f'No se pudo deserializar el archivo .cer: {str(e)}'


        # Validación de la relación entre el archivo .key y .cer
        # Validación de la relación entre la clave privada y el certificado
        if self.Cer and self.Key:
            if 'Key' not in errors and 'Cer' not in errors:
                try:
                    public_key = cert.public_key()
                    print("public_key: ",public_key)
                    mensaje = os.urandom(32)
                    print("mensaje: ",mensaje)
                    firma = private_key.sign(
                        mensaje,
                        padding.PKCS1v15(),
                        hashes.SHA256()
                    )
                    print("firma: ",firma)
                    public_key.verify(
                        firma,
                        mensaje,
                        padding.PKCS1v15(),
                        hashes.SHA256()
                    )
                    print("Verificación de la firma con la clave pública",public_key.verify(
                        firma,
                        mensaje,
                        padding.PKCS1v15(),
                        hashes.SHA256()
                    ))
                except Exception as e:
                    errors['Key'] = f'La clave privada y el certificado no corresponden: {str(e)}'
       
        # Verificar si los alguno de los campos a sido llenado
        fields_filled = [bool(self.passphrase), bool(self.Cer), bool(self.Key)]
        print(fields_filled)
        # Si alguno de los campos ha sido llenado requerir los demas
        if any(fields_filled) and not all(fields_filled):
            missing_fields = []

            if not self.passphrase:
                missing_fields.append('passphrase')
            if not self.Cer:
                missing_fields.append('Cer')
            if not self.Key:
                missing_fields.append('Key')

            present_fields = [field for field, value in zip(['passphrase', 'Cer', 'Key'], fields_filled) if value]

            errors['Key'] = (
                f"Todos los campos (passphrase, Cer, Key) son requeridos si alguno de ellos es llenado. "
                f"Faltan los campos: {', '.join(missing_fields)}. "
                f"Campos presentes: {', '.join(present_fields)}."
            )

        if errors:
            raise ValidationError(errors)

        # Llamar al servicio SOAP para registrar al usuario
        ctx = ''
        key_base64 = ''
        cer_base64 = ''
        passh = ''
        if self.Cer and self.Key and self.passphrase:
            self.Key.seek(0)  # Asegurarse de que el puntero de archivo esté al principio
            key_base64 = base64.b64encode(self.Key.read()).decode('utf-8')
            self.Cer.seek(0)  # Asegurarse de que el puntero de archivo esté al principio
            cer_base64 = base64.b64encode(self.Cer.read()).decode('utf-8')
            passh = self.passphrase
        try:
            print('debug id',self.id)
            if not self.validado:
                print('usuario log', self.usuario_logueado)
                # Obtén los servicios relacionados con el usuario logueado
                user_services = User_Service.objects.filter(idUser=self.usuario_logueado).first()
                print('service:',user_services)
                
                if user_services.idPlan.tipo == 'bajo consumo':
                    self.tipoCliente = 'O'
                
                # Obtén los Service_Plan relacionados con el usuario logueado
                service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()
                print("Debug: Llamando al servicio SOAP con los siguientes datos:")
                print(f"Email: {service_plans.supplierStamp.user}, RFC: {self.rfc}, Tipo Cliente: {self.tipoCliente}, passphrase: {passh}")
                # Validar si es un usuario nuevo se llama el servicio soap addd
                # Es un nuevo cliente, llamar al servicio SOAP add
                print('add')
                resultado = register.RegisterService.add(
                    ctx,
                    service_plans.supplierStamp.user,
                    service_plans.supplierStamp.decrypt_password(),
                    self.rfc,
                    'O', # guardar siempre el usuario como ondeman en el web servise
                    cer_base64,
                    key_base64,
                    passh
                )

    
                print("Debug: Resultado del servicio SOAP - ", resultado)
                

                 

                if not resultado:
                    errors['Key'] = 'Error al registrar al usuario en el servicio SOAP'
                # Marcamos el perfil como validado para que no se valide más en futuras ediciones
                self.validado = True
            # Si no es un nuevo usuaio entra en el else
            else:
                # Cliente existente, revisar si se han actualizado archivos cer y key
                print('edit cer: ', self.Cer)
                print('edit cer_actual: ', self._cer_actual)
                # Valida que los archivos CSD sean diferentes a los ya almacenados si 
                # son diferntes usar el servicio web edit para remplazarlos por los nuevos
                if self.Cer != self._cer_actual and self.Key != self._key_actual:
                    print('usuario log', self.usuario_logueado)
                    # Obtén los servicios relacionados con el usuario logueado
                    user_services = User_Service.objects.filter(idUser=self.usuario_logueado).first()
                    print('service:',user_services)
                    # Obtén los Service_Plan relacionados con el usuario logueado
                    service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()
                    print("Debug: Llamando al servicio SOAP con los siguientes datos:")
                    print(f"Email: {service_plans.supplierStamp.user}, RFC: {self.rfc}, Tipo Cliente: {self.tipoCliente}, passphrase: {passh}")
                    # Validar si es un usuario nuevo se llama el servicio soap addd
                    print('EDIT')
                    resultado = register.RegisterService.edit(
                        ctx,
                        service_plans.supplierStamp.user,
                        service_plans.supplierStamp.decrypt_password(),
                        self.rfc,
                        'A',
                        cer_base64,
                        key_base64,
                        passh
                    )
                    print("Debug: Resultado del servicio SOAP - ", resultado)
                    if not resultado:
                        errors['Key'] = 'Error al editar al usuario en el servicio SOAP'
                if self.tipoCliente != self._tipoCliente_Actual:
                    # print('switch')
                    # print('usuario log', self.usuario_logueado)
                    # # Obtén los servicios relacionados con el usuario logueado
                    # user_services = User_Service.objects.filter(idUser=self.usuario_logueado).first()
                    # print('service:',user_services)
                    # # Obtén los Service_Plan relacionados con el usuario logueado
                    # service_plans = Service_Plan.objects.filter(service=user_services.idService, plan=user_services.idPlan).first()
                    # print("Debug: Llamando al servicio SOAP con los siguientes datos:")
                    # print(f"Email: {service_plans.supplierStamp.user}, RFC: {self.rfc}, Tipo Cliente: {self.tipoCliente}, passphrase: {passh}")
                    # # Validar si es un usuario nuevo se llama el servicio soap add
                    # resultado = register.RegisterService.switch(
                    #     ctx,
                    #     service_plans.supplierStamp.user,
                    #     service_plans.supplierStamp.decrypt_password(),
                    #     self.rfc,
                    #     self.tipoCliente
                    # )
                    # print("Debug: Resultado del servicio SOAP - ", resultado)
                    # if not resultado:
                    #     errors['Key'] = 'Error al cambiar el tipo al usuario en el servicio SOAP'
                    if self.tipoCliente == 'O':
                        user_perfil = TimbreUserPerfil.objects.get(userInvoice=self.user, estatus = 'A')
                        user_perfil.isOnDemmand = True  # Cambia 'isOnDemmand' a True para activar Ondemand
                        user_perfil.save()
                    else:
                        user_perfil = TimbreUserPerfil.objects.get(userInvoice=self.user, estatus = 'A')
                        user_perfil.isOnDemmand = False  # Cambia 'isOnDemmand' False para desactivar Ondemant
                        user_perfil.save()

        except Exception as e:
            print(f"Error llamando al servicio SOAP: {str(e)}")
            errors['Key'] = f'Error al registrar al usuario en el servicio SOAP: {str(e)}'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Solo encriptar si la contraseña no parece estar cifrada (verificamos longitud o estructura)
        if self.token and not self.token.startswith('gAAAAAB'):  # Fernet encrypted strings start with 'gAAAAAB'
            self.token = self.encrypt_token(self.token)
        
        # Almacenar los archivos anteriores
        old_instance = Cliente.objects.filter(pk=self.pk).first()  # Recuperar la instancia anterior
        old_key = old_instance.Key if old_instance else None
        old_cer = old_instance.Cer if old_instance else None

        # Guardar la nueva instancia
        super().save(*args, **kwargs)

        # Eliminar archivos antiguos si son reemplazados o eliminados
        if old_key and old_key != self.Key:
            old_key.delete(save=False)
        if old_cer and old_cer != self.Cer:
            old_cer.delete(save=False)

        if self.Key:
            self.Key.seek(0)
            self.key_base64 = base64.b64encode(self.Key.read()).decode('utf-8')
        if self.Cer:
            self.Cer.seek(0)
            self.cer_base64 = base64.b64encode(self.Cer.read()).decode('utf-8')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        #Eliminar los achivos asociados
        self.Cer.delete(save=False)
        self.Key.delete(save=False)
        super(PerfilFiscalUser, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['id']
        
        

# Modelo para Bitácora de timbrado base cancelación
class LogStamp(models.Model):
    UUID = models.CharField(max_length=255, null=True, blank=True)
    Fecha = models.CharField(max_length=255, null=True, blank=True) 
    Emisor = models.CharField(max_length=13, null=True, blank=True)  
    CodEstatus = models.CharField(max_length=255, null=True, blank=True)
    SatSeal = models.TextField(null=True, blank=True)
    NoCertificadoSAT = models.CharField(max_length=50, null=True, blank=True)
    idUser_ServicePlan = models.ForeignKey(Service_Plan, on_delete=models.CASCADE)
    idUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) #Imanol: Este debe ser el usuario que se pasa como parametro en el metodo del webservice
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    typeOperation = models.CharField(max_length=20, choices=OPERATION_CHOICES)
    fechaLog =models.DateTimeField(auto_now_add=True, verbose_name='FechaRegistro')

    class Meta:
        verbose_name = 'LogStamp'
        verbose_name_plural = 'LogStamps'
        ordering = ['id']

    def __str__(self):
        return f" {self.id} - Bitácora de {self.idUser} - Operacion: {self.typeOperation} - Estatus: {self.status}"
