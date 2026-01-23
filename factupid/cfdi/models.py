from decimal import Decimal, InvalidOperation
import gettext
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils.timezone import now
from jsonschema import ValidationError
from console.models import User_Service
from cfdi.choices import *
from django.db import models
from django.contrib.auth.models import Group, User  # o tu AUTH_USER_MODEL
from django.conf import settings
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group,Permission
from django.utils.autoreload import autoreload_started, file_changed
from django.utils.functional import lazy
from django.utils.regex_helper import _lazy_re_compile
from django.contrib.auth.hashers import check_password, identify_hasher, make_password
from cryptography.fernet import Fernet, InvalidToken
from datetime import date, timedelta
from django.utils import timezone
from django.db import models, transaction
from django.db.models.signals import post_save
from console.models import SupplierStamp
from invoice.views import UtilitiesSOAP

import logging
log = logging.getLogger(__name__)

# Create your models here.
#orden de los modelos catalogos
# Pais
# Estado
# Localidad
# Municipio
# CodigoPostal(LugarExpedicion)
# Colonia
# ImpuestoCat

# 
# TipoFactor
# TasaOCuota
# FormaPago
# Moneda
# TipoDeComprobante

#
# Exportacion
# MetodoPago
# RegimenFiscal
# ClaveProdServ
# ClaveUnidad
# ObjetoImp
# Periodicidad
# Meses
# TipoRelacion
# UsoCFDI
class Pais(models.Model):
    c_Pais = models.CharField(max_length=3, primary_key=True)
    descripcion = models.CharField(max_length=100)
    formato_codigo_postal = models.CharField(max_length=50, blank=True, null=True)
    formato_rfc = models.CharField(max_length=200, blank=True, null=True)
    validacion_rfc = models.CharField(max_length=100, blank=True, null=True)
    agrupaciones = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'cfdi_pais'

    def __str__(self):
        return f'{self.c_Pais} | {self.descripcion}'
    
class Estado(models.Model):
    c_Estado = models.CharField(max_length=3, unique=True)
    c_Pais = models.ForeignKey(Pais, to_field='c_Pais',on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'cfdi_estado'
        constraints = [
            models.UniqueConstraint(fields=['c_Estado', 'c_Pais'], name='unique_estado_pais')
        ]

    def __str__(self):
        return f"{self.nombre} ({self.c_Pais})"    
    
class Localidad(models.Model):
    c_Localidad = models.IntegerField(unique=True)
    c_Estado = models.ForeignKey(Estado, to_field='c_Estado',on_delete=models.CASCADE, related_name='localidades')
    descripcion = models.CharField(max_length=100)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    
    def clean(self):
        estado = Estado.objects.filter(c_Estado=self.c_Estado.c_Estado).first()
        if not estado or estado.c_Pais != self.c_Estado.c_Pais:
            raise ValidationError("La localidad no pertenece al estado y país especificado.")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['c_Localidad', 'c_Estado'], name='unique_localidad_estado')
        ]

    def __str__(self):
        return f"{self.descripcion} ({self.c_Estado})"
     
class Municipio(models.Model):
    c_Municipio = models.IntegerField(unique=True)
    c_Estado = models.ForeignKey(Estado, to_field='c_Estado',on_delete=models.CASCADE, related_name='municipios')
    descripcion = models.CharField(max_length=100)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    
    def clean(self):
        estado = Estado.objects.filter(c_Estado=self.c_Estado.c_Estado).first()
        if not estado or estado.c_Pais != self.c_Estado.c_Pais:
            raise ValidationError("El estado y país no coinciden.")
    
    class Meta:
        db_table = 'cfdi_municipio'
        constraints = [
            models.UniqueConstraint(fields=['c_Municipio', 'c_Estado'], name='unique_municipio_estado')
        ]

    def __str__(self):
        return f" {self.c_Municipio} {self.descripcion} ({self.c_Estado})"   
    
class CodigoPostal(models.Model):
    c_CodigoPostal = models.CharField(max_length=10,primary_key=True)
    c_Estado = models.ForeignKey(Estado, to_field='c_Estado',on_delete=models.CASCADE, null=True, blank=True, related_name='codigos_postales')
    c_Municipio = models.ForeignKey(Municipio, to_field='c_Municipio',on_delete=models.CASCADE, null=True, blank=True, related_name='codigos_postales')
    c_Localidad = models.ForeignKey(Localidad, to_field='c_Localidad',on_delete=models.CASCADE, null=True, blank=True, related_name='codigos_postales')
    estimulo_franja_fronteriza = models.BooleanField(default=False)
    fecha_inicio_vigencia = models.DateField(null=True, blank=True)
    fecha_fin_vigencia = models.DateField(null=True, blank=True)
    descripcion_huso_horario = models.CharField(max_length=100, null=True, blank=True)
    mes_inicio_horario_verano = models.CharField(max_length=50, null=True, blank=True)
    dia_inicio_horario_verano = models.CharField(max_length=50, null=True, blank=True)
    hora_inicio_verano = models.TimeField(null=True, blank=True)
    diferencia_horaria_verano = models.IntegerField(null=True, blank=True)
    mes_inicio_horario_invierno = models.CharField(max_length=50, null=True, blank=True)
    dia_inicio_horario_invierno = models.CharField(max_length=50, null=True, blank=True)
    hora_inicio_invierno = models.TimeField(null=True, blank=True)
    diferencia_horaria_invierno = models.IntegerField(null=True, blank=True)
    
    def clean(self):
        errors = {}
        
        # Estado
        if self.c_Estado:
            estado = Estado.objects.filter(c_Estado=self.c_Estado.c_Estado).first()
            if not estado or estado.c_Pais != self.c_Estado.c_Pais:
                errors['c_Estado'] = "El estado no pertenece al país correcto."

        # Municipio
        if self.c_Municipio:
            municipio = Municipio.objects.filter(
                c_Municipio=self.c_Municipio.c_Municipio,
                c_Estado=self.c_Municipio.c_Estado
            ).first()
            if not municipio:
                errors['c_Municipio'] = "El municipio no pertenece al estado correcto."

        # Localidad
        if self.c_Localidad:
            localidad = Localidad.objects.filter(
                c_Localidad=self.c_Localidad.c_Localidad,
                c_Estado=self.c_Localidad.c_Estado
            ).first()
            if not localidad:
                errors['c_Localidad'] = "La localidad no pertenece al estado correcto."

        if errors:
            raise ValidationError(errors)
        
    class Meta:
        db_table = 'cfdi_codigopostal'

    def __str__(self):
        # Muestra el código y una descripción amigable
        estado = self.c_Estado.nombre if self.c_Estado else ''
        municipio = self.c_Municipio.descripcion if self.c_Municipio else ''
        return f"{self.c_CodigoPostal} | {estado} | {municipio}"

    
class Colonia(models.Model):
    c_Colonia = models.IntegerField(unique=True)
    c_CodigoPostal = models.ForeignKey(CodigoPostal, to_field='c_CodigoPostal',on_delete=models.CASCADE, related_name='colonias')  # Relación con CodigoPostal
    nombre_asentamiento = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'cfdi_colonia'
        constraints = [
            models.UniqueConstraint(fields=['c_Colonia', 'c_CodigoPostal'], name='unique_colonia_codigo_postal')
        ]

    def __str__(self):
        return f"{self.nombre_asentamiento} ({self.c_CodigoPostal})"     
    
class Impuesto(models.Model):
    c_Impuesto = models.CharField(max_length=3, primary_key= True)
    descripcion = models.CharField(max_length=100)
    retencion = models.BooleanField(default=False)
    traslado = models.BooleanField(default=False)
    local_o_federal = models.CharField(max_length=10)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'cfdi_impuesto'

    def __str__(self):
        return f'{self.c_Impuesto} - {self.descripcion}'    
    
class TipoFactor(models.Model):
    c_TipoFactor = models.CharField(max_length=10, primary_key=True)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'cfdi_tipofactor'

    def __str__(self):
        return self.c_TipoFactor
    
class TasaOCuota(models.Model):
    RANGO_O_FIJO_CHOICES = [
        ('Fijo', 'Fijo'),
        ('Rango', 'Rango'),
    ]
    
    rango_o_fijo = models.CharField(max_length=10, choices=RANGO_O_FIJO_CHOICES)
    valor_minimo = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    valor_maximo = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    representacionporcentual = models.CharField(max_length=10, blank=True, null=True)
    impuesto = models.ForeignKey(Impuesto, to_field='c_Impuesto', on_delete=models.CASCADE, related_name='tasaocuota', null=True, blank=True)
    factor = models.ForeignKey(TipoFactor, to_field='c_TipoFactor',on_delete=models.CASCADE, related_name='tasaocuota', null=True, blank=True)
    traslado = models.BooleanField(default=False)  # 'Sí' o 'No' representado como un booleano
    retencion = models.BooleanField(default=False)  # 'Sí' o 'No' representado como un booleano
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'cfdi_tasaocuota'

    def __str__(self):
        return f"{self.impuesto} {self.representacionporcentual}"    
    
class FormaPago(models.Model):
    c_FormaPago = models.CharField(max_length=2, primary_key=True)
    descripcion = models.CharField(max_length=100)
    bancarizado = models.BooleanField(default=False)
    numero_operacion = models.CharField(max_length=100, blank=True, null=True)
    rfc_emisor_cuenta_ordenante = models.CharField(max_length=13, blank=True, null=True)
    cuenta_ordenante = models.CharField(max_length=100, blank=True, null=True)
    patron_cuenta_ordenante = models.CharField(max_length=100, blank=True, null=True)
    rfc_emisor_cuenta_beneficiario = models.CharField(max_length=13, blank=True, null=True)
    cuenta_beneficiario = models.CharField(max_length=100, blank=True, null=True)
    patron_cuenta_beneficiaria = models.CharField(max_length=100, blank=True, null=True)
    tipo_cadena_pago = models.CharField(max_length=100, blank=True, null=True)
    nombre_banco_emisor_extranjero = models.CharField(max_length=100, blank=True, null=True)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'cfdi_formapago'

    def __str__(self):
        return f"{self.c_FormaPago} | {self.descripcion}"
    
class Moneda(models.Model):
    c_Moneda = models.CharField(max_length=3, primary_key=True)
    descripcion = models.CharField(max_length=100)
    decimales = models.IntegerField(blank=True, null=True)
    porcentaje_variacion = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'cfdi_moneda'

    def __str__(self):
        return f'{self.c_Moneda} | {self.descripcion}' 
        
class TipoComprobante(models.Model):
    c_TipoDeComprobante = models.CharField(max_length=1, primary_key=True, unique=True)
    descripcion = models.CharField(max_length=100)
    valor_maximo = models.CharField(max_length=30) 
    valor_maximoNS = models.CharField(max_length=30, blank=True, null=True) 
    valor_maximoNDS = models.CharField(max_length=30, blank=True, null=True)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'cfdi_tipocomprobante'  # Asegura que Django use la tabla SQL exacta

    def __str__(self):
        return self.descripcion   
    
class Exportacion(models.Model):
    c_Exportacion = models.CharField(max_length=3, primary_key=True)
    descripcion = models.CharField(max_length=100)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)


    class Meta:
        db_table = 'cfdi_exportacion'

    def __str__(self):
        return self.descripcion 
      
class MetodoPago(models.Model):
    c_MetodoPago = models.CharField(max_length=3,primary_key=True)
    descripcion = models.CharField(max_length=100)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'cfdi_metodopago'

    def __str__(self):
        return f'{self.c_MetodoPago} | {self.descripcion}'
    
class RegimenFiscal(models.Model):
    c_RegimenFiscal = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=200)
    fisica = models.BooleanField(default=False)
    moral = models.BooleanField(default=False)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'cfdi_regimenfiscal'

    def __str__(self):
        return f"{self.c_RegimenFiscal} | {self.descripcion}"     
    
class ClaveProdServ(models.Model):
    c_ClaveProdServ = models.CharField(max_length=10, primary_key=True)
    descripcion = models.CharField(max_length=200)
    incluir_iva_trasladado = models.CharField(max_length=50, blank=True, null=True)
    incluir_ieps_trasladado = models.CharField(max_length=50, blank=True, null=True)
    complemento_incluir = models.CharField(max_length=100, blank=True, null=True)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    estimulo_franja_fronteriza = models.BooleanField(default=False)
    palabras_similares = models.CharField(max_length=99999, blank=True, null=True)
    
    class Meta:
        db_table = 'cfdi_claveprodserv'

    def __str__(self):
        return f"{self.c_ClaveProdServ} | {self.descripcion}"
    
    
class ClaveUnidad(models.Model):
    c_ClaveUnidad = models.CharField(max_length=5,primary_key=True)
    nombre = models.CharField(max_length=500)
    descripcion = models.TextField(blank=True, null=True)
    nota = models.TextField(blank=True, null=True)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    simbolo = models.CharField(max_length=50, blank=True, null=True)
    
    
    class Meta:
        db_table = 'cfdi_claveunidad'

    def __str__(self):
        return f"{self.c_ClaveUnidad} | {self.nombre}"

    
    
class ObjetoImp(models.Model):
    c_ObjetoImp = models.CharField(max_length=3, primary_key=True)
    descripcion = models.CharField(max_length=200)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    class Meta:
        db_table = 'cfdi_objetoimp'

    def __str__(self):
        return f'{self.c_ObjetoImp} | {self.descripcion}'

class PeriodicidadPago(models.Model):
    c_PeriodicidadPago = models.CharField(
        max_length=3,
        primary_key=True,
        verbose_name="Clave de Periodicidad de Pago"
    )
    descripcion = models.CharField(
        max_length=100,
        verbose_name="Descripción"
    )
    fecha_inicio_vigencia = models.DateField(
        verbose_name="Fecha inicio de vigencia"
    )
    fecha_fin_vigencia = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha fin de vigencia"
    )

    class Meta:
        verbose_name = "Periodicidad de Pago"
        verbose_name_plural = "Periodicidades de Pago"
        ordering = ["c_PeriodicidadPago"]

    def __str__(self):
        return f"{self.c_PeriodicidadPago} | {self.descripcion}"   
    
class Periodicidad(models.Model):
    c_Periodicidad = models.CharField(max_length=3, primary_key=True)
    descripcion = models.CharField(max_length=100)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    class Meta:
        db_table = 'cfdi_periodicidad'

    def __str__(self):
        return f'{self.c_Periodicidad} | {self.descripcion}'  
    
    
class Meses(models.Model):
    c_Meses = models.CharField(max_length=3, primary_key=True)
    descripcion = models.CharField(max_length=100)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'cfdi_meses'

    def __str__(self):
        return f'{self.c_Meses} | {self.descripcion}'  
    
class TipoRelacion(models.Model):
    c_TipoRelacion = models.CharField(max_length=3, primary_key=True)
    descripcion = models.CharField(max_length=200)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'cfdi_tiporelacion'

    def __str__(self):
        return f'{self.c_TipoRelacion} | {self.descripcion}'
    
class UsoCFDI(models.Model):
    c_UsoCFDI = models.CharField(max_length=4, primary_key=True)
    descripcion = models.CharField(max_length=200)
    aplica_fisica = models.BooleanField(default=False)
    aplica_moral = models.BooleanField(default=False)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    regimen_fiscal_receptor = models.ManyToManyField(RegimenFiscal)  # Relación con Régimen Fiscal
    
    class Meta:
        db_table = 'cfdi_usocfdi' 
        
    def __str__(self):
        return f'{self.c_UsoCFDI} | {self.descripcion}'
    
class Aduana(models.Model):
    c_Aduana = models.CharField(max_length=3, primary_key=True)
    descripcion = models.CharField(max_length=200)
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)
    class Meta:
        db_table = 'cfdi_aduana'

    def __str__(self):
        return f'{self.c_Aduana} | {self.descripcion}'
    
class PatenteAduanal(models.Model):
    c_PatenteAduanal = models.CharField(max_length=5, primary_key=True)
    inicio_vigencia = models.DateField()
    fin_vigencia = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'cfdi_patenteaduanal'

    def __str__(self):
         return str(self.c_PatenteAduanal)
 
    
     
class VersionCFDI(models.Model):
    version_cfdi = models.CharField(max_length=10)  # Ejemplo: "4.0"
    version_catalogo = models.DecimalField(max_digits=5, decimal_places=1)  # Ejemplo: 70.0
    revision_catalogo = models.PositiveIntegerField()  # Ejemplo: 0
    fecha_publicacion_catalogo = models.DateField()  # Ejemplo: 26/09/2024
    fecha_inicio_vigencia = models.DateField()  # Ejemplo: 01/01/2022

    def __str__(self):
        return f"CFDI {self.version_cfdi} - Catálogo {self.version_catalogo}- Revision {self.revision_catalogo}- Fecha publicacion {self.fecha_publicacion_catalogo} -fecha inicio {self.fecha_inicio_vigencia}"
 
#Los usuarios  de la app CFDI S
class UsersCFDI(models.Model):
    # Usuario que creo el usuario CFDI. El usuario principal es el unico que no tiene padre. Nodo raiz
    userParent = models.ForeignKey('UsersCFDI', on_delete=models.DO_NOTHING, null=True, blank=True)
    # Usuario de la app CFDI. Se crea al mismo tiempo un User de Django
    # para poder usar el sistema de permisos de Django
    token = models.CharField(max_length=255, blank=True, null=True)
    idUserCFDI = models.OneToOneField(User, on_delete=models.DO_NOTHING,  primary_key=True)
    #Servicio plan contratado activado activo
    idUserServicePlan_id = models.ForeignKey(User_Service, on_delete=models.DO_NOTHING)
    
    # Nuevo campo para negocio activo
    negocio_activo = models.ForeignKey(
        'InformacionFiscal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_cfdi_que_usan_este_negocio'
    )
    
    def __str__(self):
        return f"{self.idUserCFDI} - {self.idUserServicePlan_id}"
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cipher = Fernet(settings.ENCRYPTION_KEY)

    def save(self, *args, **kwargs):
        if self.token and not self._is_token_encrypted(self.token):
            self.token = self.encrypt_token(self.token)
        super().save(*args, **kwargs)

    def encrypt_token(self, token):
        if token in (None, ''):
            return token
        return self.cipher.encrypt(token.encode()).decode()

    def decrypt_token(self):
        if not self.token:
            return ''
        if not self._is_token_encrypted(self.token):
            return self.token
        try:
            return self.cipher.decrypt(self.token.encode()).decode()
        except InvalidToken:
            return self.token

    def _is_token_encrypted(self, token):
        return isinstance(token, str) and token.startswith('gAAAAAB')


    def get_raiz(self):
        """
        Retorna el nodo raíz de la jerarquía.
        """
        nodo = self
        while nodo.userParent is not None:
            nodo = nodo.userParent
        return nodo
    
    def get_descendientes(self, incluir_self=True):
        """
        Retorna todos los subusuarios descendientes recursivos de este usuario.
        """
        hijos = []

        def buscar_hijos(usuario):
            subusuarios = UsersCFDI.objects.filter(userParent=usuario)
            for sub in subusuarios:
                hijos.append(sub)
                buscar_hijos(sub)

        buscar_hijos(self)
        if incluir_self:
            hijos.insert(0, self)
        return hijos
    
    def generar_token_inicial(self):
        """
        Genera o resetea token SOLO para usuarios raíz.
        Nunca para subusuarios.
        """
        # Solo usuarios raíz pueden tener token
        if self.userParent is not None:
            return None

        idServicePlan = self.idUserServicePlan_id.idServicePlan
        supplier_stamp = getattr(idServicePlan, 'supplierStamp', None)
        
        print("Generando token inicial para usuario raíz:", self.idUserCFDI)
        print("SupplierStamp asociado:", idServicePlan)
        
        print("SupplierStamp detalles:", supplier_stamp)
        print("idServicePlan:", idServicePlan)

        if not supplier_stamp:
            print("No hay SupplierStamp asociado al ServicePlan.")
            return None

        user = self.idUserCFDI

        try:
            print("Llamando a add_tokens para usuario:", user.username)
            
            token_response = UtilitiesSOAP.add_tokens(
                '',
                supplier_stamp.user,
                supplier_stamp.decrypt_password(),
                user.get_full_name() or user.email or user.username,
                user.username,
                '',
                'true'
            )
            
            print("Respuesta de add_tokens:", token_response)

            # Pac dice: ya existe token → reset
            if getattr(token_response, 'success', False) is False and \
               getattr(token_response, 'message', '') == "Token added previously.":

                reset_response = UtilitiesSOAP.reset_token(
                    '',
                    supplier_stamp.user,
                    supplier_stamp.decrypt_password(),
                    user.username
                )
                
                print("Token ya existía, se reseteó:", reset_response)
                
                if getattr(reset_response, 'success', False):
                    self.token = reset_response.token
                    self.save(update_fields=['token'])
                    return self.token
                else:
                    return None
                
            

            # Token creado normalmente
            if hasattr(token_response, 'token'):
                self.token = token_response.token
                self.save(update_fields=['token'])
                return self.token

        except Exception as exc:
            log.error(f"Error al generar token inicial para {user.username}: {exc}")
            return None
    
    # ===== Conteo de timbres =====
    def _calcular_periodo(self, plan_tipo: str):
        """
        Devuelve (inicio, fin) del periodo de vigencia según el tipo de plan.
        Usa timezone.localdate() para respetar la TZ del proyecto.
        """
        hoy = timezone.localdate()  # en vez de date.today() si USE_TZ=True
        if plan_tipo == 'mensual'or plan_tipo == 'bajo consumo':
            inicio = hoy.replace(day=1)
            # último día del mes
            if inicio.month == 12:
                fin = inicio.replace(year=inicio.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                fin = inicio.replace(month=inicio.month + 1, day=1) - timedelta(days=1)
        elif plan_tipo == 'anual':
            inicio = date(hoy.year, 1, 1)
            fin = date(hoy.year, 12, 31)
        else:
            # bajo consumo u otros: no resetea solo (periodo “abierto”)
            inicio = date(2024, 1, 1)
            fin = date(2099, 12, 31)
        return inicio, fin

    def get_conteo_timbres_actual(self):
        """
        Obtiene o crea el conteo activo del periodo vigente para el usuario raíz.
        Asegura un único registro 'activo' por periodo.
        """
        raiz = self.get_raiz()
        user_service = raiz.idUserServicePlan_id

        # Validaciones defensivas
        if not user_service or not user_service.idPlan:
            raise ValueError("El usuario raíz no tiene un plan asignado.")

        plan = user_service.idPlan
        if plan.tipo not in ('mensual', 'anual', 'bajo consumo'):
            raise ValueError(f"Tipo de plan desconocido: {plan.tipo}")

        inicio, fin = self._calcular_periodo(plan.tipo)
        # print("plan tipo:", plan.tipo, " Plan:",plan)

        conteo, creado = UserTimbreCount.objects.get_or_create(
            user_cfdi=raiz,
            periodo_inicio=inicio,
            periodo_fin=fin,
            plan = plan,
            defaults={
                'limite_timbres': plan.limite_operaciones_plan,
                # Si estás migrando desde contadores legacy y quieres arrancar con ese valor:
                # 'contador_actual': user_service.cont_stamped_user or 0,
                'contador_actual': 0,
                'activo': True,   
            }
        )
        
        # print("Conteo timbres actual:", conteo, "Creado:", creado)

        # Desactiva otros periodos del mismo usuario
        UserTimbreCount.objects.filter(user_cfdi=raiz).exclude(pk=conteo.pk).update(activo=False)
        return conteo

    def _plan_es_enterprise(self):
        raiz = self.get_raiz()
        plan = getattr(raiz.idUserServicePlan_id, 'idPlan', None)
        if not plan or not getattr(plan, 'nombre', None):
            return False
        return plan.nombre.strip().lower() == 'enterprise'

    def _sync_invoice_timbre_counter(self, conteo=None, cantidad=1):
        if not self._plan_es_enterprise():
            return
        try:
            from invoice.models import TimbreUserPerfil
        except Exception as exc:
            log.warning("No se pudo importar TimbreUserPerfil para sincronizar: %s", exc)
            return

        raiz = self.get_raiz()
        timbre_user = TimbreUserPerfil.objects.filter(
            userInvoice=raiz.idUserCFDI, estatus='A'
        ).first()
        if not timbre_user:
            return

        if conteo is None:
            conteo = raiz.get_conteo_timbres_actual()

        timbre_user.cont_stamped_user = conteo.contador_actual
        if cantidad:
            timbre_user.cont_stamped_day = max(0, timbre_user.cont_stamped_day + cantidad)

        if not timbre_user.isOnDemmand and conteo.limite_timbres is not None:
            nuevo_stamp = conteo.limite_timbres - conteo.contador_actual
            if nuevo_stamp < 0:
                nuevo_stamp = 0
            timbre_user.stamp = nuevo_stamp

        update_fields = ['cont_stamped_user', 'cont_stamped_day']
        if not timbre_user.isOnDemmand and conteo.limite_timbres is not None:
            update_fields.append('stamp')
        timbre_user.save(update_fields=update_fields)

    def registrar_timbre(self, cantidad=1, sync_invoice=True):
        """
        Incremento seguro (transaccional y con bloqueo) del contador del periodo activo.
        Soporta concurrencia (dos timbrados simultáneos no provocan desbordes).
        """
        raiz = self.get_raiz()
        with transaction.atomic():
            # Recalcula dentro de la transacción para evitar carreras al cambiar de mes/año
            conteo = raiz.get_conteo_timbres_actual()

            # Bloquea el registro en BD hasta el final de la transacción
            bloqueado = UserTimbreCount.objects.select_for_update().get(pk=conteo.pk)

            # 🔹 Solo valida el límite si existe (mayor a 0)
            if bloqueado.limite_timbres and bloqueado.contador_actual + cantidad > bloqueado.limite_timbres:
                raise ValueError("Límite de timbres alcanzado para este periodo.")

            bloqueado.contador_actual += cantidad
            bloqueado.save(update_fields=['contador_actual', 'fecha_actualizacion'])

            if sync_invoice:
                try:
                    raiz._sync_invoice_timbre_counter(conteo=bloqueado, cantidad=cantidad)
                except Exception as exc:
                    log.warning("No se pudo sincronizar timbres con Invoice: %s", exc)

            return bloqueado

class UserTimbreCount(models.Model):
    """
    Historial de consumo de timbres por usuario CFDI.
    Un registro por periodo (mensual o anual) según el plan activo.
    """
    user_cfdi = models.ForeignKey('UsersCFDI', on_delete=models.CASCADE, related_name='timbres')
    periodo_inicio = models.DateField()
    periodo_fin = models.DateField()
    contador_actual = models.PositiveIntegerField(default=0)
    limite_timbres = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_suspension = models.DateField(null=True, blank=True)
    razon_suspension = models.TextField(blank=True)
    plan = models.ForeignKey('console.Plan', on_delete=models.SET_NULL, null=True, blank=True) 

    class Meta:
        verbose_name = "Conteo de Timbres"
        verbose_name_plural = "Conteos de Timbres"
        ordering = ['-periodo_inicio']
        unique_together = ('user_cfdi', 'periodo_inicio', 'periodo_fin', 'plan')

    def __str__(self):
        return (
            f"{self.user_cfdi.idUserCFDI.username} "
            f"({self.periodo_inicio} - {self.periodo_fin}) "
            f"{self.contador_actual}/{self.limite_timbres}"
        )

    def incrementar_timbre(self, cantidad=1):
        """
        Incrementa o decrementa el contador de timbres de forma segura y atómica.
        - Usa una transacción para evitar condiciones de carrera.
        - Bloquea la fila actual con select_for_update() durante la actualización.
        - Permite decrementos (si cantidad < 0) pero nunca baja de 0.
        """

        with transaction.atomic():
            # Bloquear este registro en la base de datos
            bloqueado = UserTimbreCount.objects.select_for_update().get(pk=self.pk)

            nuevo_valor = bloqueado.contador_actual + cantidad

            # Evita números negativos
            if nuevo_valor < 0:
                nuevo_valor = 0

            # Verifica que no se exceda el límite de timbres del plan
            if nuevo_valor > bloqueado.limite_timbres:
                raise ValueError("Límite de timbres alcanzado para este periodo.")

            # Asigna y guarda solo los campos necesarios
            bloqueado.contador_actual = nuevo_valor
            bloqueado.save(update_fields=['contador_actual', 'fecha_actualizacion'])

            # Devuelve el objeto actualizado (ya con contador_actual nuevo)
            return bloqueado



class InformacionFiscal(models.Model):
    # Información fiscal
    idUserCFDI = models.ForeignKey(UsersCFDI, on_delete=models.CASCADE, blank=True, null=True)
    nombre = models.CharField(max_length=255)
    manifiesto_firmado = models.BooleanField(default=False, verbose_name="¿Manifiesto firmado?")
    manifiesto_contrato_xml = models.TextField(blank=True, null=True, verbose_name="Contrato de manifiesto (XML)")
    manifiesto_contrato_pdf = models.TextField(blank=True, null=True, verbose_name="Contrato de manifiesto (PDF)")
    # Nuevo campo de activación
    activo = models.BooleanField(default=True, verbose_name="estado de activación")
    es_principal = models.BooleanField(default=False, verbose_name="¿Es principal?")

    imagen = models.ImageField(upload_to='cfdi/media/imagenes/', null=True, blank=True)
    confirmar_datos_cfdi = models.BooleanField(default=False, verbose_name="Confirmar datos para CFDI 4.0")
    ignorar_validacion_sociedad = models.BooleanField(default=False, verbose_name="Ignorar validador de Soc. Mercantil en Razón Social")
    rfc = models.CharField(max_length=13)

    curp = models.CharField(max_length=18, blank=True, null=True)
    razon_social = models.CharField(max_length=255)
    regimen_fiscal = models.ForeignKey(
        RegimenFiscal, to_field='c_RegimenFiscal', related_name="informacion_fiscal", verbose_name="Régimen Fiscal", on_delete=models.CASCADE
        )
    regimen_receptor = models.ForeignKey(
        RegimenFiscal, to_field='c_RegimenFiscal', on_delete=models.SET_NULL, null=True, related_name="receptor_informacion_fiscal",
        verbose_name="Régimen Fiscal como Receptor"
        )
    
    # Domicilio
    calle = models.CharField(max_length=255, blank=True, null=True)
    numero_exterior = models.CharField(max_length=10, blank=True, null=True, verbose_name="No. Ext.")
    numero_interior = models.CharField(max_length=10, blank=True, null=True, verbose_name="No. Int.")
    colonia = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=255, blank=True, null=True)
    municipio = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=255, blank=True, null=True)
    pais = models.CharField(max_length=255, default="MEXICO")
    codigo_postal = models.CharField(max_length=5)
    referencia = models.CharField(max_length=255, blank=True, null=True)
    clave_pais = models.CharField(max_length=3, blank=True, null=True)
    residencia_fiscal = models.CharField(max_length=255, blank=True, null=True)

    # Datos de contacto
    telefono = models.CharField(max_length=15, blank=True, null=True)
    correo_electronico = models.EmailField(verbose_name="Correo electrónico", blank=True, null=True)

    class Meta:
        verbose_name = "Información Fiscal"
        verbose_name_plural = "Información Fiscal"
        ordering = ['nombre']
        
    def __str__(self):
        return self.nombre
    
    @classmethod
    def get_para_usuario(cls, user):
        """
        Devuelve todos los objetos de InformacionFiscal asociados al usuario raíz del usuario dado.
        """
        from cfdi.models import UsersCFDI  # Asegúrate de importar bien si estás en otro archivo

        try:
            usuario_cfdi = UsersCFDI.objects.get(idUserCFDI=user)
            usuario_raiz = usuario_cfdi.get_raiz()
            return cls.objects.filter(idUserCFDI=usuario_raiz, activo=True)
        except UsersCFDI.DoesNotExist:
            return cls.objects.none()
      
    @classmethod
    def get_principal_para_usuario(cls, user):
        """
        Devuelve la InformacionFiscal principal (es_principal=True) del usuario raíz.
        """
        return cls.get_para_usuario(user).filter(es_principal=True).first()
        
    def save(self, *args, **kwargs):
        """
        Al guardar, si este objeto es principal, desactiva los demás que pertenecen al mismo idUserCFDI.
        """
        if self.es_principal:
            InformacionFiscal.objects.filter(
                idUserCFDI=self.idUserCFDI,
                es_principal=True
            ).exclude(pk=self.pk).update(es_principal=False)
        super().save(*args, **kwargs)

        
    def clean(self):
        # Validar RFC
        if self.rfc:
            rfc = self.rfc.strip().upper()  # Limpiar espacios y forzar mayúsculas
            if len(rfc) not in [12, 13]:
                raise ValidationError({'rfc': "El RFC debe tener exactamente 12 caracteres (persona moral) o 13 caracteres (persona física)."})

            if len(rfc) == 12:
                # Podrías agregar reglas extras aquí si quieres confirmar que sean persona moral (opcional)
                pass

            if len(rfc) == 13:
                # Podrías agregar reglas extras aquí si quieres confirmar que sean persona física (opcional)
                pass

        # validar CURP (depende de si CFDI lo requiere)
        if self.curp:
            curp = self.curp.strip().upper()
            if len(curp) != 18:
                raise ValidationError({'curp': "La CURP debe tener exactamente 18 caracteres."})

    

    

class InformacionGlobal(models.Model):
    Comprobante = models.ForeignKey('Comprobante', on_delete=models.CASCADE, null=True, blank=True)

    ES_COMPROBANTE_LEGAL_CHOICES = [
        ('SI', 'Sí'),
        ('NO', 'No'),
    ]
    Escomprobantelegal = models.CharField(max_length=2, choices=ES_COMPROBANTE_LEGAL_CHOICES, default='NO')
    Periodicidad = models.ForeignKey(Periodicidad, to_field='c_Periodicidad',on_delete=models.CASCADE, null=True, related_name='Periodicidad_informacion_global')
    Meses = models.ForeignKey(Meses, to_field='c_Meses',on_delete=models.CASCADE, null=True, related_name='Meses_informacion_global')

   
    @staticmethod
    def get_year_choices():
        start_year = 2023
        current_year = now().year
        end_year = max(start_year + 5, current_year + 5)  # Genera 5 años hacia el futuro
        return [(str(year), str(year)) for year in range(start_year, end_year + 1)]

    # Campo de año con choices dinámicos
    Anio = models.CharField(max_length=4,default=str(now().year))

    class Meta:
        db_table = 'cfdi_informacionglobal'
        verbose_name_plural = "Información global"

    # Sobrescribir el método save para actualizar los choices dinámicamente
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field('Anio').choices = self.get_year_choices()

    
class CfdiRelacionados(models.Model):
    comprobante = models.ForeignKey('Comprobante', on_delete=models.CASCADE, null=True, blank=True)
    c_TipoRelacion = models.ForeignKey(TipoRelacion, to_field='c_TipoRelacion', on_delete=models.CASCADE, null=True)
    uuid = models.CharField(max_length=255, verbose_name="UUID relacionado")  

    
    class Meta:
        verbose_name = "CFDI Relacionados"
        verbose_name_plural = "CFDI Relacionados"
        ordering = ['c_TipoRelacion']
        db_table = 'cfdi_cfdi_relacionados'
        
    def __str__(self):
        return f"{self.c_TipoRelacion}" if self.c_TipoRelacion else "CFDI Relacionado sin Tipo de Relación" 

class Emisor(models.Model):
    comprobante = models.ForeignKey('Comprobante', on_delete=models.CASCADE, null=True, blank=True)
    rfc = models.CharField(max_length=13)
    nombre = models.CharField(max_length=255)
    c_RegimenFiscal = models.ForeignKey(RegimenFiscal, to_field='c_RegimenFiscal', on_delete=models.CASCADE)
    facAtrAdquirente = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = "Emisor"
        verbose_name_plural = "Emisores"
        ordering = ['rfc']
        db_table = 'cfdi_emisor'
        
    def __str__(self):
        return f"{self.rfc} - {self.nombre}" if self.rfc and self.nombre else "Emisor sin RFC o Nombre"
    
    def clean(self):
        # Validar que RFC esté capturado
        if not self.rfc:
            raise ValidationError({'rfc': "El campo RFC es obligatorio para el Emisor."})

        # Validar que régimen fiscal esté capturado
        if not self.c_RegimenFiscal:
            raise ValidationError({'c_RegimenFiscal': "El Régimen Fiscal del Emisor es obligatorio."})

        # Validar que nombre esté capturado si el régimen fiscal indica persona moral
        if self.c_RegimenFiscal:
            if self.c_RegimenFiscal.moral and not self.nombre:
                raise ValidationError({'nombre': "El nombre es obligatorio para emisores con régimen fiscal de Persona Moral."})

        # Opcional: si RFC tiene longitud distinta de 12 o 13 caracteres, puedes advertir
        if self.rfc and len(self.rfc) not in [12, 13]:
            raise ValidationError({'rfc': "El RFC debe tener 12 (moral) o 13 (física) caracteres válidos."})

class Receptor(models.Model):
    comprobante = models.ForeignKey('Comprobante', on_delete=models.CASCADE, null=True, blank=True)
    rfc = models.CharField(max_length=13)
    nombre = models.CharField(max_length=255)
    c_DomicilioFiscalReceptor = models.ForeignKey(CodigoPostal, to_field='c_CodigoPostal',on_delete=models.CASCADE, null=True)
    c_ResidenciaFiscal = models.ForeignKey(Pais, to_field='c_Pais', on_delete=models.CASCADE, null=True, blank=True)
    numRegldTrib = models.CharField(max_length=255, blank=True, null=True)
    c_RegimenFiscalReceptor = models.ForeignKey(RegimenFiscal, to_field='c_RegimenFiscal',on_delete=models.CASCADE, null=True)
    c_UsoCFDI = models.ForeignKey(UsoCFDI, to_field='c_UsoCFDI', on_delete=models.CASCADE, null=True)
    
    class Meta:
        verbose_name = "Receptor"
        verbose_name_plural = "Receptores"
        ordering = ['rfc']
        db_table = 'cfdi_receptor'
        
    def __str__(self):
        return f"{self.rfc} - {self.nombre}" if self.rfc and self.nombre else "Receptor sin RFC o Nombre"
    
    # def clean(self):
    #     # Solo aplicar validaciones si residencia fiscal está especificada
    #     if self.c_ResidenciaFiscal:
    #         if self.c_ResidenciaFiscal.c_Pais != 'MEX':
    #             # Si es extranjero, debe capturar numRegldTrib
    #             if not self.numRegldTrib:
    #                 raise ValidationError({
    #                     'numRegldTrib': "Si el receptor es extranjero (c_ResidenciaFiscal distinto de 'MEX'), debe proporcionar el número de registro tributario extranjero (numRegldTrib)."
    #                 })
    #         else:
    #             # Si es MEX, no debe tener numRegldTrib
    #             if self.numRegldTrib:
    #                 raise ValidationError({
    #                     'numRegldTrib': "Si el receptor tiene residencia fiscal 'MEX', no debe capturar numRegldTrib."
    #                 })
    #     else:
    #         # Si no indica residencia fiscal, se supone MEX por defecto
    #         if self.numRegldTrib:
    #             raise ValidationError({
    #                 'numRegldTrib': "Si no se indica una residencia fiscal extranjera, no debe capturar numRegldTrib."
    #             })

  

class Impuestos(models.Model):
    idConcepto = models.ForeignKey('Conceptos', on_delete=models.CASCADE, null=True, blank=True, related_name='impuestos')
    # traslado o retencion
    TIPO_APLICABLE_CHOICES = [
        ('Traslado', 'Traslado'),
        ('Retención', 'Retención'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_APLICABLE_CHOICES)
    base = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    c_Impuesto = models.ForeignKey(Impuesto, to_field='c_Impuesto', on_delete=models.CASCADE, blank=True, null=True, related_name='impuestos')
    c_TipoFactor = models.ForeignKey(TipoFactor, to_field='c_TipoFactor',on_delete=models.CASCADE, blank=True, null=True, related_name='impuestos')
    c_TasaOCuota = models.ForeignKey(TasaOCuota, on_delete=models.CASCADE, blank=True, null=True , related_name='impuestos')
    porcentaje = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    incluido = models.BooleanField(default=False, verbose_name="¿Incluido en el precio?")
    importe = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
    
    class Meta:
        verbose_name = "Impuestos"
        verbose_name_plural = "Impuestos"
        ordering = ['tipo']
        db_table = 'cfdi_impuestos'
        
    def __str__(self):
        return f"{self.tipo} - {self.base} - {self.idConcepto.comprobante}" if self.tipo else "Impuesto sin Traslado o Retención"
  
class ACuentaTerceros(models.Model):
    idConcepto = models.ForeignKey('Conceptos', on_delete=models.CASCADE, null=True, blank=True, related_name='aCuentaTerceros')
    rfcACuentaTerceros = models.CharField(max_length=13, blank=True, null=True)
    nombreACuentaTerceros = models.CharField(max_length=255, blank=True, null=True)
    c_RegimenFiscalACuentaTerceros = models.ForeignKey(RegimenFiscal, to_field='c_RegimenFiscal',on_delete=models.CASCADE, null=True, blank=True)
    domicilioFiscalACuentaTerceros = models.CharField(max_length=5, blank=True, null=True)  # Código Postal
    
    class Meta:
        verbose_name = "A Cuenta de Terceros"
        verbose_name_plural = "A Cuenta de Terceros"
        ordering = ['rfcACuentaTerceros']
        db_table = 'cfdi_acuentaterceros'
    
    def __str__(self):
        return f"{self.rfcACuentaTerceros} - {self.nombreACuentaTerceros}" if self.rfcACuentaTerceros and self.nombreACuentaTerceros else "A Cuenta de Terceros sin RFC o Nombre"

class InformacionAduanera(models.Model):
    idConcepto = models.ForeignKey('Conceptos', on_delete=models.CASCADE, null=True, blank=True, related_name='informacionAduanera')
    aduana = models.ForeignKey(Aduana, on_delete=models.CASCADE, related_name='pedimentos')
    patente = models.ForeignKey(PatenteAduanal, on_delete=models.CASCADE, related_name='aduanas')
    ejercicio = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField()
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ('aduana', 'patente', 'ejercicio')
        verbose_name = "Información Aduanera"
        verbose_name_plural = "Informaciones Aduaneras"
        db_table = 'cfdi_informacionaduanera'
        ordering = ['fecha_fin_vigencia']


    def __str__(self):
        return f"Aduana {self.aduana} - Patente {self.patente} - vigencia {self.fecha_fin_vigencia}"

class PedimentoCFDI(models.Model):
    concepto = models.ForeignKey('Conceptos', on_delete=models.CASCADE, related_name='pedimentos',  null=True, blank=True,)
    aduana = models.ForeignKey(Aduana, on_delete=models.PROTECT)
    patente = models.ForeignKey(PatenteAduanal, on_delete=models.PROTECT)
    ejercicio = models.PositiveIntegerField()
    numero = models.CharField(max_length=21, blank=True, null=True)

    class Meta:
        unique_together = ('concepto', 'aduana', 'patente', 'ejercicio')
        db_table = 'cfdi_pedimentocfdi'
        
    def __str__(self):
        return f"Pedimento {self.numero} - Aduana {self.aduana} - Patente {self.patente} - Ejercicio {self.ejercicio}" if self.numero else "Pedimento sin número"
    

class CuentaPredial(models.Model):
    idConcepto = models.ForeignKey('Conceptos', on_delete=models.CASCADE, null=True, blank=True, related_name='cuentaPredial')
    numero = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name = "Cuenta Predial"
        verbose_name_plural = "Cuentas Prediales"
        ordering = ['numero']
        db_table = 'cfdi_cuentapredial'
        
    def __str__(self):
        return f"{self.numero}" if self.numero else "Cuenta Predial sin número"

class ComplementoConcepto(models.Model):
    idConcepto = models.ForeignKey('Conceptos', on_delete=models.CASCADE, null=True, blank=True, related_name='complementoConcepto')
    complementoConcepto = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name = "Complemento de Concepto"
        verbose_name_plural = "Complementos de Concepto"
        ordering = ['complementoConcepto']
        db_table = 'cfdi_complementoconcepto'
        
    def __str__(self): 
        return f"{self.complementoConcepto}" if self.complementoConcepto else "Complemento de Concepto sin nombre"

class Parte(models.Model):
    idConcepto = models.ForeignKey('Conceptos', on_delete=models.CASCADE, null=True, blank=True, related_name='parte')
    claveProdServ = models.ForeignKey(ClaveProdServ, to_field='c_ClaveProdServ', on_delete=models.CASCADE, null=True)
    noIdentificacion = models.CharField(max_length=255, blank=True, null=True)  
    cantidad = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)  
    unidad = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255,  blank=True, null=True)
    valorUnitario = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    importe = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)     
    informacionAduanera = models.ForeignKey(InformacionAduanera, on_delete=models.CASCADE, blank=True, null=True)
    
    class Meta:
        verbose_name = "Parte"
        verbose_name_plural = "Partes"
        ordering = ['claveProdServ']
        db_table = 'cfdi_partes'
    
    def __str__(self):
        return f"{self.cantidad} - {self.descripcion}" if self.cantidad and self.descripcion else "Parte sin Cantidad o Descripción"
                       

    
    
class ImpuestosTotales(models.Model):
    comprobante = models.ForeignKey('Comprobante', on_delete=models.CASCADE, null=True, blank=True)
    totalImpuestosRetenidos = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    totalImpuestosTraslados = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    # traslado o retencion
    TIPO_APLICABLE_CHOICES = [
        ('Traslado', 'Traslado'),
        ('Retención', 'Retención'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_APLICABLE_CHOICES)
    base = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    c_Impuesto = models.ForeignKey(Impuesto, to_field='c_Impuesto', on_delete=models.CASCADE, related_name='impuestos_totales')
    c_TipoFactor = models.ForeignKey(TipoFactor, to_field='c_TipoFactor',on_delete=models.CASCADE, blank=True, null=True, related_name='impuestos_totales')
    c_TasaOCuota = models.ForeignKey(TasaOCuota, on_delete=models.CASCADE, blank=True, null=True , related_name='impuestos_totales')
    importe = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
    class Meta:
        verbose_name = "Impuestos Totales"
        verbose_name_plural = "Impuestos Totales"
        ordering = ['totalImpuestosRetenidos']
        db_table = 'cfdi_impuestostotales'
    
    def __str__(self):
        return f"{self.totalImpuestosRetenidos} - {self.totalImpuestosTraslados}" if self.totalImpuestosRetenidos and self.totalImpuestosTraslados else "Impuesto Total sin Retenido o Traslado"

class TimbreFiscalDigital(models.Model):
    idComplemento = models.ForeignKey('Complemento', on_delete=models.CASCADE, null=True, blank=True)
    version = models.CharField(max_length=5, default='1.1')
    uuid = models.CharField(max_length=36)  # UUID es fijo de 36 caracteres
    fechaTimbrado = models.DateTimeField()  # Fecha y hora
    rfcProvCertif = models.CharField(max_length=255)
    leyenda = models.CharField(max_length=255, blank=True, null=True)  # Leyenda es opcional
    selloCFD = models.TextField()  # Firma electrónica muy larga
    noCerticadoSAT = models.CharField(max_length=255)
    selloSAT = models.TextField()  # Sello digital del SAT, largo también
    
    class Meta:
        verbose_name = "Timbre Fiscal Digital"
        verbose_name_plural = "Timbrados"
        ordering = ['uuid']
        db_table = 'cfdi_timbrefiscaldigital'
        
    def __str__(self):
        return f"{self.uuid} - {self.fechaTimbrado}" if self.uuid and self.fechaTimbrado else "Timbre Fiscal Digital sin UUID o Fecha de Timbrado"

class TiposComplemento(models.Model):
    nombre = models.CharField(max_length=255, null=True, blank=True)
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    version = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name = "Tipos de Complemento"
        verbose_name_plural = "Tipos de Complemento"
        ordering = ['nombre']
        db_table = 'cfdi_tiposcomplemento'
        
    def __str__(self):
        return f"{self.nombre}" if self.nombre else "Tipo de Complemento sin nombre"

class Complemento(models.Model):
    idComrobante = models.ForeignKey('Comprobante', on_delete=models.CASCADE, null=True, blank=True)
    idTipoComplemento = models.ForeignKey(TiposComplemento, on_delete=models.CASCADE, null=True, blank=True)

    
    class Meta:
        verbose_name = "Complemento"
        verbose_name_plural = "Complementos"
        ordering = ['idTipoComplemento']
        db_table = 'cfdi_complemento'
        
    def __str__(self):
        return f"{self.idTipoComplemento}" if self.idTipoComplemento else "Complemento sin Tipo de Complemento"

class Addenda(models.Model):
    comprobante = models.ForeignKey('Comprobante', on_delete=models.CASCADE, null=True, blank=True)
    addenda = models.CharField(max_length=50, choices=TIPO_ADDENDAS , null=True, blank=True)
    
    class Meta:
        verbose_name = "Addenda"
        verbose_name_plural = "Addendas"
        ordering = ['addenda']
        db_table = 'cfdi_addenda'
    
    def __str__(self):
        return f"{self.comprobante} - {self.addenda}" if self.addenda else "Addenda sin nombre"
    
class AddendaSiemensGamesa(models.Model):
    addenda = models.OneToOneField(Addenda, on_delete=models.CASCADE, related_name='siemens_gamesa')
    tipodocumento = models.CharField(max_length=50, choices=SIEMENS_TIPO_DOCUMENTO, null=True, blank=True)
    numero_orden = models.CharField(max_length=100)
    nota_entrega = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Addenda Siemens Gamesa"
        verbose_name_plural = "Addendas Siemens Gamesas"
        
    def __str__(self):
        return f"{self.addenda} - {self.tipodocumento} - {self.numero_orden}"

class AddendaGrupoADO(models.Model):
    addenda = models.OneToOneField(Addenda, on_delete=models.CASCADE, related_name='grupo_ado')
    tipo_addenda = models.CharField(max_length=50, choices=ADO_TIPO_ADDENDA, null=True, blank=True)
    pedido = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Addenda Grupo ADO"
        verbose_name_plural = "Addendas Grupos ADOS"
        
    def __str__(self):
        return f"{self.id} - {self.addenda} - {self.tipo_addenda} - {self.pedido}"

class AddendaWaldos(models.Model):
    addenda = models.OneToOneField(Addenda, on_delete=models.CASCADE, related_name='waldos')
    numero_orden = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Addenda Waldo"
        verbose_name_plural = "Addenda Waldos"
        
    def __str__(self):
        return f"{self.addenda} - {self.numero_orden}"

class AddendaTerraMultitransportes(models.Model):
    addenda = models.ForeignKey(Addenda, on_delete=models.CASCADE, related_name='terra_multitransportes', blank=True, null=True)
    
    contenedor = models.CharField(max_length=100)
    reservacion = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True)
    referencia = models.CharField(max_length=100, blank=True)
    
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    iva = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    retencion = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = "Addenda Terra Multitransporte"
        verbose_name_plural = "Addenda Terra Multitransportes"
        
    def __str__(self):
        return f"{self.addenda} - {self.contenedor} - {self.reservacion}"
                           
class Comprobante(models.Model): 
    version = models.CharField(max_length=10, default='4.0')
    informacionFiscal = models.ForeignKey('InformacionFiscal', on_delete=models.CASCADE, null=True, related_name='comprobantes')
    serie = models.CharField(max_length=255, null=True, blank=True)
    folio = models.CharField(max_length=255, null=True, blank=True)
    fechaEmision = models.DateField()
    fechaPago = models.DateField(blank=True, null=True)
    sello = models.TextField(blank=True, null=True)
    c_FormaPago = models.ForeignKey(FormaPago, to_field='c_FormaPago', on_delete=models.CASCADE, null=True, blank=True )
    noCertificado = models.CharField(max_length=255, null=True, blank=True)
    certificado = models.TextField(blank=True, null=True)
    condicionesDePago = models.CharField(max_length=255, null=True, blank=True)
    subTotal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    descuento = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    c_Moneda = models.ForeignKey(Moneda, to_field='c_Moneda', on_delete=models.CASCADE, null=True, blank=True)
    tipoCambio = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    c_TipoDeComprobante = models.ForeignKey(TipoComprobante, to_field='c_TipoDeComprobante',on_delete=models.CASCADE, null=True)
    c_Exportacion = models.ForeignKey(Exportacion, to_field='c_Exportacion', on_delete=models.CASCADE, null=True)
    c_MetodoPago = models.ForeignKey(MetodoPago, to_field='c_MetodoPago', on_delete=models.CASCADE, null=True, blank=True)
    c_LugarExpedicion = models.ForeignKey(CodigoPostal, to_field='c_CodigoPostal', on_delete=models.CASCADE, null=True)
    confirmacion = models.CharField(max_length=255, null=True, blank=True)
    tipo_documento = models.CharField(
        max_length=10,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='borrador'
    )
    
    class Meta:
        verbose_name = "Comprobante"
        verbose_name_plural = "Comprobantes"
        
        db_table = 'cfdi_comprobante'
        
    def __str__(self):
        return f"{self.id} - {self.informacionFiscal.idUserCFDI.idUserCFDI} - {self.informacionFiscal} - {self.c_TipoDeComprobante}"

class ComprobanteEgreso(Comprobante):
    class Meta:
        proxy = True
        verbose_name = "Comprobante de Egreso"
        verbose_name_plural = "Comprobantes de Egreso"
        
    def __str__(self):
        return f"{self.id} - {self.informacionFiscal} - {self.c_TipoDeComprobante}"   
    
    def save(self, *args, **kwargs):
        # Asignar tipo de comprobante "N" si no está definido
        if not self.c_TipoDeComprobante:
            try:
                self.c_TipoDeComprobante = TipoComprobante.objects.get(c_TipoDeComprobante='E')
            except TipoComprobante.DoesNotExist:
                pass
            
        super().save(*args, **kwargs)

 
    
class ComprobanteTraslado(Comprobante):
    class Meta:
        proxy = True
        verbose_name = "Comprobante de Traslado"
        verbose_name_plural = "Comprobantes de Traslado"
        
    def __str__(self):
        return f"{self.id} - {self.informacionFiscal} - {self.c_TipoDeComprobante}"   

class ComprobanteCartaPorteTraslado(Comprobante):
    class Meta:
        proxy = True
        verbose_name = "Comprobante carta Porte Traslado"
        verbose_name_plural = "Comprobante carta Porte Traslados"

class ComprobanteNomina12(Comprobante):
    class Meta:
        proxy = True
        verbose_name = "Comprobante Nomina 1.2"
        verbose_name_plural = "Comprobante Nomina 12"
        
    def save(self, *args, **kwargs):
        # Asignar tipo de comprobante "N" si no está definido
        if not self.c_TipoDeComprobante:
            try:
                self.c_TipoDeComprobante = TipoComprobante.objects.get(c_TipoDeComprobante='N')
            except TipoComprobante.DoesNotExist:
                pass

        # Asignar método de pago "PUE" si no está definido
        if not self.c_MetodoPago:
            try:
                self.c_MetodoPago = MetodoPago.objects.get(c_MetodoPago='PUE')
            except MetodoPago.DoesNotExist:
                pass

        # Asignar exportación "01" si no está definida
        if not self.c_Exportacion:
            try:
                self.c_Exportacion = Exportacion.objects.get(c_Exportacion='01')
            except Exportacion.DoesNotExist:
                pass

        super().save(*args, **kwargs)


    
    
class Conceptos(models.Model):
    comprobante = models.ForeignKey(Comprobante, on_delete=models.CASCADE, related_name='conceptos', null=True, blank=True)
    c_ClaveProdServ = models.ForeignKey(ClaveProdServ, to_field='c_ClaveProdServ',on_delete=models.CASCADE, null=True)
    noIdentificacion = models.CharField(max_length=255, blank=True, null=True)
    cantidad = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True) 
    c_ClaveUnidad = models.ForeignKey(ClaveUnidad, to_field='c_ClaveUnidad', on_delete=models.CASCADE, null=True)
    unidad = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255)
    valorUnitario = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True) 
    importe = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)   
    descuento_incluido = models.BooleanField(default=False, verbose_name="Descuento incluido")
    descuento_porcentaje = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    descuento = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)     
    c_ObjetoImp = models.ForeignKey(ObjetoImp, to_field='c_ObjetoImp',on_delete=models.CASCADE, null=True)
    
    complemento_tipo = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        choices=[
            (None, 'Sin complemento'),  # Opción para "ningún complemento"
            ('cuenta_terceros', 'A Cuenta de Terceros'),
            ('cuenta_predial', 'Cuenta Predial'),
            ('informacion_aduanera', 'Información Aduanera'),
            ('parte', 'Parte'),
        ],
        verbose_name="Tipo de Complemento"
    )
    
    
    class Meta: 
        verbose_name = "Concepto"
        verbose_name_plural = "Conceptos"
        ordering = ['id']
        db_table = 'cfdi_concepto'
    
    def __str__(self):
        return f"{self.id} {self.descripcion} ({self.c_ClaveProdServ})" if self.descripcion else f"{self.c_ClaveProdServ}"

    

    









class Banco(models.Model):
    c_Banco = models.CharField(
        max_length=5,
        primary_key=True,
        blank=True,
        verbose_name="Clave de Banco"
    )
    descripcion = models.CharField(
        max_length=100,
        verbose_name="Descripción"
    )
    razon_social = models.CharField(
        max_length=255,
        verbose_name="Nombre o razón social"
    )
    fecha_inicio_vigencia = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha inicio de vigencia"
    )
    fecha_fin_vigencia = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha inicio de vigencia"
    )
   

    class Meta:
        verbose_name = "Banco"
        verbose_name_plural = "Bancos"
        ordering = ["c_Banco"]

    def __str__(self):
        return f"{self.c_Banco} - {self.descripcion}"
    



class OrigenRecurso(models.Model):
    c_OrigenRecurso = models.CharField(
        max_length=2,
        primary_key=True,
        verbose_name="Clave de Origen del Recurso"
    )
    descripcion = models.CharField(
        max_length=100,
        verbose_name="Descripción"
    )

    class Meta:
        verbose_name = "Origen del Recurso"
        verbose_name_plural = "Origenes del Recurso"
        ordering = ["c_OrigenRecurso"]

    def __str__(self):
        return f"{self.c_OrigenRecurso} - {self.descripcion}"


class RiesgoPuesto(models.Model):
    c_RiesgoPuesto = models.CharField(
        max_length=3,
        primary_key=True,
        verbose_name="Clave de Riesgo Puesto"
    )
    descripcion = models.CharField(
        max_length=100,
        verbose_name="Descripción"
    )
    fecha_inicio_vigencia = models.DateField(
        verbose_name="Fecha inicio de vigencia"
    )
    fecha_fin_vigencia = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha fin de vigencia"
    )

    class Meta:
        verbose_name = "Riesgo Puesto"
        verbose_name_plural = "Riesgos Puesto"
        ordering = ["c_RiesgoPuesto"]
    c_RiesgoPuesto = models.CharField(
        max_length=3,
        primary_key=True,
        verbose_name="Clave de Riesgo Puesto"
    )
    descripcion = models.CharField(
        max_length=100,
        verbose_name="Descripción"
    )
    fecha_inicio_vigencia = models.DateField(
        verbose_name="Fecha inicio de vigencia"
    )
    fecha_fin_vigencia = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha fin de vigencia"
    )

    class Meta:
        verbose_name = "Riesgo Puesto"
        verbose_name_plural = "Riesgos Puesto"
        ordering = ["c_RiesgoPuesto"]

    def __str__(self):
        return f"{self.c_RiesgoPuesto} - {self.descripcion}"
    

class TipoContrato(models.Model):
    c_TipoContrato = models.CharField(
        max_length=3,
        primary_key=True,
        verbose_name="Clave de Tipo de Contrato"
    )
    descripcion = models.CharField(
        max_length=255,
        verbose_name="Descripción"
    )

    class Meta:
        verbose_name = "Tipo de Contrato"
        verbose_name_plural = "Tipos de Contrato"
        ordering = ["c_TipoContrato"]

    def __str__(self):
        return f"{self.c_TipoContrato} - {self.descripcion}"



class TipoJornada(models.Model):
    c_TipoJornada = models.CharField(
        max_length=3,
        primary_key=True,
        verbose_name="Clave de Tipo de Jornada"
    )
    descripcion = models.CharField(
        max_length=100,
        verbose_name="Descripción"
    )

    class Meta:
        verbose_name = "Tipo de Jornada"
        verbose_name_plural = "Tipos de Jornada"
        ordering = ["c_TipoJornada"]

    def __str__(self):
        return f"{self.c_TipoJornada} - {self.descripcion}"
    

class TipoNomina(models.Model):
    c_TipoNomina = models.CharField(max_length=5, primary_key=True,  blank=True)

    opcion = models.CharField(max_length=30, unique=True, null=True, blank=True)

    def __str__(self):
        return self.opcion if self.opcion else "No especificado"



# class PeriodicidadPago(models.Model):
#     c_PeriodicidadPago = models.CharField(
#         max_length=3,
#         primary_key=True,
#         verbose_name="Clave de Periodicidad de Pago"
#     )
#     descripcion = models.CharField(
#         max_length=100,
#         verbose_name="Descripción"
#     )
#     fecha_inicio_vigencia = models.DateField(
#         verbose_name="Fecha inicio de vigencia"
#     )
#     fecha_fin_vigencia = models.DateField(
#         null=True,
#         blank=True,
#         verbose_name="Fecha fin de vigencia"
#     )

#     class Meta:
#         verbose_name = "Periodicidad de Pago"
#         verbose_name_plural = "Periodicidades de Pago"
#         ordering = ["c_PeriodicidadPago"]

#     def __str__(self):
#         return f"{self.c_PeriodicidadPago} - {self.descripcion}" 


class TipoRegimen(models.Model):
    c_TipoRegimen = models.CharField(
        max_length=5,  # Ajusta el tamaño según el SAT (normalmente 2 o 3)
        primary_key=True,
        verbose_name="Clave del Tipo de Régimen"
    )
    descripcion = models.CharField(
        max_length=255,
        verbose_name="Descripción"
    )
    fecha_inicio_vigencia = models.DateField(
        verbose_name="Fecha inicio de vigencia"
    )
    fecha_fin_vigencia = models.DateField(
        verbose_name="Fecha fin de vigencia",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Tipo de Régimen"
        verbose_name_plural = "Tipos de Régimen"
        ordering = ['c_TipoRegimen']

    def __str__(self):
        return f"{self.c_TipoRegimen} - {self.descripcion}"
    

class Genero(models.Model):
    opcion = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def __str__(self):
        return self.opcion if self.opcion else "No especificado"
    

class Sindicalizado(models.Model):
    opcion = models.CharField(max_length=2, unique=True, null=True, blank=True)

    def __str__(self):
        return self.opcion if self.opcion else "No especificado"


class Nomina(models.Model):
    comprobanteNomina12 = models.ForeignKey(
        ComprobanteNomina12,
        on_delete=models.CASCADE,
        null=True,
        related_name='nomina',
        verbose_name="Comprobante Nomina",
        

    )

    # Relación con Tipo de Nómina
    tipo_nomina = models.ForeignKey(TipoNomina, to_field='c_TipoNomina', on_delete=models.CASCADE, null=True, blank=True)
   

    numero_dias_pagados = models.IntegerField(verbose_name="Número de días pagados", blank=True, null=True)
    fecha_pago = models.DateField(verbose_name="Fecha de pago de nómina", blank=True, null=True)
    fecha_inicial_pago = models.DateField(verbose_name="Fecha inicial pago", blank=True, null=True)
    fecha_final_pago = models.DateField(verbose_name="Fecha final pago", blank=True, null=True)

    # Emisor
    curp = models.CharField(max_length=18, verbose_name="CURP", blank=True, null=True)
    rfc_patron_origen = models.CharField(max_length=13, verbose_name="RFC patrón origen", blank=True, null=True)
    entidad_sncf = models.CharField(max_length=50, verbose_name="Entidad SNCF", blank=True, null=True)


    origen_recurso = models.ForeignKey(OrigenRecurso, to_field='c_OrigenRecurso', on_delete=models.CASCADE, null=True, blank=True)


    

    monto_recurso_propio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto recurso propio", blank=True, null=True)

    # Trabajador
    rfc_trabajador = models.CharField(max_length=13, verbose_name="RFC del trabajador", blank=True, null=True)
    curp_trabajador = models.CharField(max_length=18, verbose_name="CURP del trabajador", blank=True, null=True)
    numero_empleado = models.CharField(max_length=20, verbose_name="Número de empleado", blank=True, null=True)
    numero_seguro_social = models.CharField(max_length=20, verbose_name="Número de seguro social", blank=True, null=True)
    registro_patronal = models.CharField(max_length=50, verbose_name="Registro patronal", blank=True, null=True)

    # Información personal
    nombre = models.CharField(max_length=100, verbose_name="Nombre", blank=True, null=True)
    apellido_paterno = models.CharField(max_length=100, verbose_name="Apellido paterno", blank=True, null=True)
    apellido_materno = models.CharField(max_length=100, verbose_name="Apellido materno", blank=True, null=True)

    # Relación con Género
    genero = models.ForeignKey(
        Genero,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Género"
    )

    # Domicilio
    entidad_presto_servicio = models.ForeignKey(
        Estado,to_field='c_Estado',  # Relación con Estado
        on_delete=models.CASCADE,
        verbose_name="Entidad donde prestó el servicio",
        blank=True,
        null=True
    )
    calle = models.CharField(max_length=255, verbose_name="Calle", blank=True, null=True)
    numero_exterior = models.CharField(max_length=10, verbose_name="No. Ext.", blank=True, null=True)
    numero_interior = models.CharField(max_length=10, verbose_name="No. Int.", blank=True, null=True)
    colonia = models.CharField(max_length=100, verbose_name="Colonia", blank=True, null=True)
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad", blank=True, null=True)
    municipio = models.CharField(max_length=100, verbose_name="Municipio", blank=True, null=True)
    estado = models.CharField(max_length=100, verbose_name="Estado", blank=True, null=True)
    pais = models.CharField(max_length=100, verbose_name="País", blank=True, null=True)
    c_CodigoPostal = models.ForeignKey(CodigoPostal, to_field='c_CodigoPostal',on_delete=models.CASCADE, null=True, blank=True)  # Relación con CodigoPostal
    referencia = models.CharField(max_length=255, verbose_name="Referencia", blank=True, null=True)
    clave_pais = models.CharField(max_length=10, verbose_name="Clave país", blank=True, null=True)
    c_ResidenciaFiscal = models.ForeignKey(Pais, to_field='c_Pais', on_delete=models.CASCADE, null=True, blank=True)
   

    # Información de contacto
    telefono = models.CharField(max_length=20, verbose_name="Teléfono", blank=True, null=True)
    correo_electronico = models.EmailField(verbose_name="Correo electrónico", blank=True, null=True)

    # Información laboral
    fecha_inicio_relacion_laboral = models.DateField(verbose_name="Fecha inicio de relación laboral", blank=True, null=True)
    tipo_regimen = models.ForeignKey(TipoRegimen, to_field='c_TipoRegimen', on_delete=models.CASCADE, null=True, blank=True)
    departamento = models.CharField(max_length=100, verbose_name="Departamento", blank=True, null=True)

    # Relación con Sindicalizado
    sindicalizado = models.ForeignKey(
        Sindicalizado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Sindicalizado"
    )

    puesto = models.CharField(max_length=100, verbose_name="Puesto", blank=True, null=True)


    riesgo_puesto = models.ForeignKey(RiesgoPuesto, to_field='c_RiesgoPuesto', on_delete=models.CASCADE, null=True, blank=True)


    # Relación con TipoContrato
    tipo_contrato = models.ForeignKey(
        TipoContrato, to_field='c_TipoContrato',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de contrato"
    )

    # Relación con TipoJornada
    tipo_jornada = models.ForeignKey(
        TipoJornada, to_field='c_TipoJornada',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de jornada"
    )

    # Información de pago
    salario_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salario base", blank=True, null=True, default=0.0)
    salario_diario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salario diario", blank=True, null=True)


    banco = models.ForeignKey(Banco, to_field='c_Banco', on_delete=models.CASCADE, null=True, blank=True)

  
    periodicidad = models.ForeignKey(PeriodicidadPago, to_field='c_PeriodicidadPago', on_delete=models.CASCADE, null=True, blank=True)

    cuenta_bancaria = models.CharField(max_length=50, verbose_name="Cuenta bancaria", blank=True, null=True)

    

    class Meta:
        verbose_name = "Nomina"
        verbose_name_plural = "Nominas"
        ordering = ['fecha_pago']

    def __str__(self):
        return f"Nómina de {self.nombre} - {self.fecha_pago}"


class TipoDeduccion(models.Model):
    c_TipoDeduccion = models.CharField(
        max_length=5,
        primary_key=True,
        verbose_name="Clave del Tipo de Deducción"
    )
    descripcion = models.CharField(
        max_length=255,
        verbose_name="Descripción"
    )
    fecha_inicio_vigencia = models.DateField(
        verbose_name="Fecha inicio de vigencia"
    )
    fecha_fin_vigencia = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha fin de vigencia"
    )

    class Meta:
        verbose_name = "Tipo de Deducción"
        verbose_name_plural = "Tipos de Deducción"
        ordering = ['c_TipoDeduccion']

    def __str__(self):
        return f"{self.c_TipoDeduccion} - {self.descripcion}"

class Deduccion(models.Model):
    comprobanteNomina12 = models.ForeignKey(
        ComprobanteNomina12,
        on_delete=models.CASCADE,
        null=True,
        related_name='nominaDeducciones'
    )

    nomina = models.ForeignKey(Nomina,null=True, on_delete=models.CASCADE, related_name="deducciones")
    tipo_deduccion = models.ForeignKey(TipoDeduccion, to_field='c_TipoDeduccion', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de Deducción")
    clave = models.CharField(max_length=20, verbose_name="Clave", blank=False, null=False)
    importe = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Importe", default=0.00)

    class Meta:
        verbose_name = "Deducción"
        verbose_name_plural = "Deducciones"

    def __str__(self):
        return f"{self.tipo_deduccion} - {self.importe}"

class TipoPercepcion(models.Model):
    c_TipoPercepcion = models.CharField(
        max_length=5,
        primary_key=True,
        verbose_name="Clave del Tipo de Percepción"
    )
    descripcion = models.CharField(
        max_length=255,
        verbose_name="Descripción"
    )
    fecha_inicio_vigencia = models.DateField(
        verbose_name="Fecha inicio de vigencia"
    )
    fecha_fin_vigencia = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha fin de vigencia"
    )

    class Meta:
        verbose_name = "Tipo de Percepción"
        verbose_name_plural = "Tipos de Percepción"
        ordering = ['c_TipoPercepcion']

    class Meta:
        verbose_name = "Percepción"
        verbose_name_plural = "Percepciones"
    def __str__(self):
        return f"{self.c_TipoPercepcion} - {self.descripcion}"


class TipoOtroPago(models.Model):
    c_TipoOtroPago = models.CharField(
        max_length=5,
        primary_key=True,
        verbose_name="Clave del Tipo de Otro Pago"
    )
    descripcion = models.CharField(
        max_length=500,
        verbose_name="Descripción"
    )
    fecha_inicio_vigencia = models.DateField(
        verbose_name="Fecha inicio de vigencia"
    )
    fecha_fin_vigencia = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha fin de vigencia"
    )

    class Meta:
        verbose_name = "Tipo de Otro Pago"
        verbose_name_plural = "Tipos de Otros Pagos"
        ordering = ["c_TipoOtroPago"]

    def __str__(self):
        return f"{self.c_TipoOtroPago} - {self.descripcion}"


class subcontratacion(models.Model):
    comprobanteNomina12 = models.ForeignKey(ComprobanteNomina12, on_delete=models.CASCADE, related_name='subcontrataciones')

    rfclaboral = models.CharField(max_length=13,blank=True, null=True, verbose_name="RFC Laboral")
    porcentaje = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Porcentaje")
    class Meta:
        verbose_name = "Subcontratación"
        verbose_name_plural = "Subcontrataciones"

class OtroPago(models.Model):
    comprobanteNomina12 = models.ForeignKey(
        ComprobanteNomina12,
        on_delete=models.CASCADE,
        null=True,
        related_name='nominaOtrosPagos'
    )
    nomina = models.ForeignKey(Nomina,null=True,blank=True, on_delete=models.CASCADE, related_name="otros_pagos")
    tipo_otro_pago = models.ForeignKey(TipoOtroPago, to_field='c_TipoOtroPago', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de Otro Pago")
    
    subsidioCausado = models.CharField(max_length=255, blank=True, null=True)
    saldoAfavor = models.CharField(max_length=255, blank=True, null=True)
    anio = models.CharField(max_length=255, blank=True, null=True)
    remanente = models.CharField(max_length=255, blank=True, null=True)
    clave = models.CharField(max_length=20, verbose_name="Clave", blank=True, null=True)
    importe = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Importe", default=0.00)

    class Meta:
        verbose_name = "Otro Pago"
        verbose_name_plural = "Otros Pagos"

    def __str__(self):
        return f"{self.tipo_otro_pago} - {self.importe}"


class TipoIncapacidad(models.Model):
    c_TipoIncapacidad = models.CharField(
        max_length=2,
        primary_key=True,
        verbose_name="Clave"
    )
    descripcion = models.CharField(
        max_length=255,
        verbose_name="Descripción"
    )

    def __str__(self):
        return f"{self.c_TipoIncapacidad} - {self.descripcion}"


class TipoHoras(models.Model):
    c_TipoHoras = models.CharField(
        max_length=2,
        primary_key=True,
        verbose_name="Clave"
    )
    descripcion = models.CharField(
        max_length=100,
        verbose_name="Descripción"
    )

    def __str__(self):
        return f"{self.c_TipoHoras} - {self.descripcion}"


class Percepcion(models.Model):
    comprobanteNomina12 = models.ForeignKey(
        ComprobanteNomina12,
        on_delete=models.CASCADE,
        null=True,
        related_name='nominaPercepciones'
    )
   
    nomina = models.ForeignKey(Nomina,null=True, on_delete=models.CASCADE, related_name="percepciones")
    tipo_percepcion = models.ForeignKey(TipoPercepcion, to_field='c_TipoPercepcion', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de Percepción")
    clave = models.CharField(max_length=20, verbose_name="Clave", blank=False, null=False)
    importe_exento = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Importe Exento", default=0.00)
    importe_gravado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Importe Gravado", default=0.00)
   
    class Meta:
        verbose_name = "Percepción"
        verbose_name_plural = "Percepciones"
    def __str__(self):
        return f"{self.id} - {self.nomina}"
    
class Incapacidad(models.Model):
    percepcion = models.ForeignKey(Percepcion, on_delete=models.CASCADE, null=True, blank=True, related_name='incapacidad')
    Deduccion = models.ForeignKey(Deduccion, on_delete=models.CASCADE, null=True, blank=True, related_name='incapacidad_deduccion') 
    tipo_incapacidad = models.ForeignKey(TipoIncapacidad, to_field='c_TipoIncapacidad', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de Incapacidad")
    dias_incapacidad = models.IntegerField(verbose_name="Dias Incapacidad", blank=True, null=True)
    importe_Monetario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Importe Monetario", default=0.00)
    
    class Meta:
        verbose_name = "Incapacidad"
        verbose_name_plural = "Incapacidades"
    def __str__(self):
        return f"{self.tipo_incapacidad} - {self.dias_incapacidad}"


class HorasExtra(models.Model):
    percepcion = models.ForeignKey(Percepcion, on_delete=models.CASCADE, null=True, blank=True, related_name='horas_extra')
    horas_extra = models.IntegerField(verbose_name="Horas Extra", blank=True, null=True)
    tipo_horas = models.ForeignKey(TipoHoras, to_field='c_TipoHoras', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Horas Extra")
    dias = models.IntegerField(verbose_name="Dias Extra", blank=True, null=True)
    importe_pagado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Importe Pagado", default=0.00)

    class Meta:
        verbose_name = "Horas Extra"
        verbose_name_plural = "Horas Extras"

    def __str__(self):
        return f"{self.tipo_horas} - {self.horas_extra}"

class SeparacionIndemnizacion(models.Model):
    percepcion = models.ForeignKey(Percepcion, on_delete=models.CASCADE, null=True, blank=True, related_name='separacion_indemnizacion')
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Pagado", default=0.00)
    num_anos_servicio = models.IntegerField(verbose_name="Número de Años de Servicio", blank=True, null=True)
    ultimo_sueldo_mens_ord = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Último Sueldo Mensual Ordinario", default=0.00)
    ingreso_acumulable = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ingreso Acumulable", default=0.00)
    ingreso_no_acumulable = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ingreso No Acumulable", default=0.00)

    class Meta:
        verbose_name = "Separación Indemnización"
        verbose_name_plural = "Separaciones Indemnización"
    def __str__(self):
        return f"Separación Indemnización - Total Pagado: {self.total_pagado} - Años de Servicio: {self.num_anos_servicio}"
    
class JubilacionPensionRetiro(models.Model):
    percepcion = models.ForeignKey(Percepcion, on_delete=models.CASCADE, null=True, blank=True, related_name='jubilacion_pension_retiro')
    total_una_exhibicion = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Una Exhibicion", default=0.00, null=True, blank=True)
    ingreso_acumulable = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ingreso Acumulable", default=0.00, null=True, blank=True)
    ingreso_no_acumulable = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ingreso No Acumulable", default=0.00,)

    class Meta:
        verbose_name = "Jubilación Pensión Retiro"
        verbose_name_plural = "Jubilaciones Pensiones Retiro"
    def __str__(self):
        return (
                f"Jubilación Pensión Retiro - Total Una Exhibición: {self.total_una_exhibicion} "
                f"Ingreso Acumulable: {self.ingreso_acumulable} "
                f"Ingreso No Acumulable: {self.ingreso_no_acumulable}"
            )





class FacturaElectronica(models.Model):
    # Relación con Información Fiscal
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True, related_name='facturas')
    informacion_fiscal = models.ForeignKey(
        InformacionFiscal,
        on_delete=models.CASCADE,
        related_name="FacturaElectronica",
        verbose_name="Información Fiscal"
    )
    
    regimen_fiscal = models.ForeignKey(
        RegimenFiscal,
        on_delete=models.SET_NULL,
        null=True,
        related_name="FacturaElectronicas",
        verbose_name="Régimen Fiscal Principal"
    )

    # Otros campos adicionales del FacturaElectronica
    
    nombre = models.CharField(max_length=255, verbose_name="Nombre del FacturaElectronica")
    rfc = models.CharField(max_length=13)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Domicilio")
    codigo_postal = models.CharField(max_length=5)
    activo = models.BooleanField(default=True, verbose_name="Estado Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "FacturaElectronica"
        verbose_name_plural = "FacturaElectronicas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
    

class InformacionPago(models.Model):
    Comprobante = models.ForeignKey('Comprobante', on_delete=models.CASCADE, null=True, blank=True)
  
    Metodopago = models.ForeignKey(MetodoPago, to_field='c_MetodoPago', on_delete=models.CASCADE, null=True, related_name='Metodo_pago')
    Formapago = models.ForeignKey(FormaPago, to_field='c_FormaPago', on_delete=models.CASCADE, null=True, related_name='Forma_pago')
    Fechapago = models.DateField(null=True, blank=True, verbose_name="Fecha de Pago")
    Moneda = models.ForeignKey(Moneda, to_field='c_Moneda', on_delete=models.CASCADE, null=True, related_name='Moneda')
    Tipocambio = models.FloatField(null=True, blank=True, verbose_name="Tipo de Cambio")
    Condicionespago = models.CharField(max_length=255, null=True, blank=True, verbose_name="Condiciones de Pago")
    
    class Meta:
        db_table = 'cfdi_InformacionPago'

    def __str__(self):
        # Devuelve un texto representativo del objeto
        return f"Pago {self.Fechapago} - Método: {self.Metodopago}"




class Conceptosimpuesto(models.Model):
    Conceptos = models.ForeignKey(
        Conceptos,
        on_delete=models.CASCADE,
        null=True,
        related_name='Conceptosimpuesto'
    )
    
    Impuesto = models.ForeignKey(
        TasaOCuota,
        on_delete=models.CASCADE,
        null=True,
        related_name='Impuesto'
    )
    FacturaElectronica = models.ForeignKey(
        FacturaElectronica,
        on_delete=models.CASCADE,
        null=True
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        help_text="Porcentaje del impuesto (ej. 16.000000 para IVA)"
    )
    incluido = models.BooleanField(
        default=False,
        null=True,
        help_text="Indica si el impuesto ya está incluido en el importe del concepto"
    )

    valorImpuesto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        help_text="calculo del impuesto"
    )


    base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        help_text="Base sobre la cual se calcula el impuesto"
    )
   

    def __str__(self):
        return f"{self.Impuesto} ({self.valor}%)"



        


class origenCFDI(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    tipo = models.CharField(max_length=255, verbose_name="Tipo")

    def __str__(self):
        return f"{self.nombre} - {self.tipo}"  # ✅ Formato correcto
    
class ComprobantesRelacionados(models.Model):
    Comprobante = models.ForeignKey(Comprobante, on_delete=models.CASCADE, null=True, blank=True)
   
    Tiporelacion = models.ForeignKey('TipoRelacion', on_delete=models.CASCADE, null=True, related_name='Relacion')
    origenCFDI = models.ForeignKey('origenCFDI', on_delete=models.CASCADE, null=True, related_name='Origen_CFDI')
    receptorRFC = models.CharField(max_length=255,null=True, verbose_name="Receptor RFC")
    uuid = models.CharField(max_length=255, null=True)
    
    
    class Meta:
        db_table = 'cfdi_ComprobantesRelacionados'
    


class LeyendasFiscales(models.Model):
    Comprobante = models.ForeignKey('Comprobante', on_delete=models.CASCADE, null=True, blank=True)
   
    TextoLeyenda = models.CharField(max_length=300, blank=True)
    Disposicionfiscal = models.CharField(max_length=300, blank=True)
    Norma = models.CharField(max_length=300, blank=True)

    class Meta:
        db_table = 'cfdi_LeyendasFiscales'  # Si es necesario agregar el nombre de la tabla

    
    





class FacturaElectronicaBorrador(models.Model):
    # Relación con Información Fiscal
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True, related_name='facturas_borrador')
    informacion_fiscal = models.OneToOneField(
        InformacionFiscal,
        on_delete=models.CASCADE,
        related_name="FacturaElectronicaBorrador",
        verbose_name="Información Fiscal"
    )
    
    regimen_fiscal = models.ForeignKey(
        RegimenFiscal,
        on_delete=models.SET_NULL,
        null=True,
        related_name="FacturaElectronicasBorrador",
        verbose_name="Régimen Fiscal Principal"
    )

    

    # Otros campos adicionales del FacturaElectronicaBorrador
    nombre = models.CharField(max_length=255, verbose_name="Nombre del FacturaElectronicaBorrador")
    rfc = models.CharField(max_length=13)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Domicilio")
    codigo_postal = models.CharField(max_length=5)
    activo = models.BooleanField(default=True, verbose_name="Estado Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Factura Electrónica (Borrador)"
        verbose_name_plural = "Facturas Electrónicas (Borrador)"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
    




# class FacturaElectronicaBorrador(models.Model):
#     # Cambiar de OneToOneField a ForeignKey
#     informacion_fiscal = models.ForeignKey(
#         InformacionFiscal,
#         on_delete=models.CASCADE,
#         related_name="facturas_electronicas_borrador",
#         verbose_name="Información Fiscal"
#     )
    
#     regimen_fiscal = models.ForeignKey(
#         RegimenFiscal,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name="facturas_electronicas_borrador",
#         verbose_name="Régimen Fiscal Principal"
#     )

#     # Otros campos
#     nombre = models.CharField(max_length=255, verbose_name="Nombre del FacturaElectronicaBorrador")
#     rfc = models.CharField(max_length=13)
#     descripcion = models.TextField(blank=True, null=True, verbose_name="Domicilio")
#     codigo_postal = models.CharField(max_length=5)
#     activo = models.BooleanField(default=True, verbose_name="Estado Activo")
#     fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

#     class Meta:
#         verbose_name = "Factura Electrónica (Borrador)"
#         verbose_name_plural = "Facturas Electrónicas (Borrador)"
#         ordering = ['nombre']

#     def __str__(self):
#         return self.nombre



class CertificadoSelloDigital(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="certificados",
        verbose_name="Usuario",
        help_text="Usuario propietario del certificado"
    )
    informacionFiscal = models.ForeignKey(
        InformacionFiscal,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="certificados_csd",
        verbose_name="Información Fiscal",
        help_text="Información fiscal asociada a este certificado de sello digital."
    )
    nombre_certificado = models.CharField(
        max_length=255, 
        verbose_name="Nombre del Certificado"
    )
    archivo_certificado = models.FileField(
        upload_to='certificados/', 
        verbose_name="Certificado (*.cer)", 
        help_text="Sube el archivo .cer"
    )
    clave_privada = models.FileField(
        upload_to='claves/', 
        verbose_name="Clave privada del certificado (*.key)", 
        help_text="Sube el archivo .key"
    )
    contrasena = models.CharField(
        max_length=128, 
        verbose_name="Contraseña", 
        help_text="Introduce la contraseña del certificado"
    )
    
    # Campos adicionales
    numero_certificado = models.CharField(
        max_length=255, 
        verbose_name="Número de Certificado", 
        blank=True, 
        null=True
    )
    vigencia = models.DateField(
        ("Fecha de Vigencia"),  # Nombre traducible
        null=True,  # Puede ser nulo
        blank=True,  # Puede estar en blanco
        auto_now=False,  # No se actualiza automáticamente al guardar
        auto_now_add=False,  # No se establece automáticamente al crear el registro
        help_text="Fecha en la que expira la vigencia del certificado."
    )
    descripcion = models.CharField(
        max_length=255, 
        verbose_name="Descripción", 
        blank=True, 
        null=True
    )
    sucursal = models.CharField(
        max_length=255, 
        verbose_name="Sucursal", 
        blank=True, 
        null=True
    )
    tipo= models.CharField(
        max_length=5, 
        verbose_name="Tipo", 
        blank=True, 
        null=True
    )
    defecto = models.BooleanField(
        default=False, 
        verbose_name="Certificado por defecto"
    )
    estado = models.BooleanField(
        default=True, 
        verbose_name="Estado Activo"
    )
    notas = models.TextField(
        verbose_name="Notas", 
        blank=True, 
        null=True
    )

    class Meta:
        verbose_name = "Certificado de Sello Digital"
        verbose_name_plural = "Certificados de Sello Digital"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cipher = Fernet(settings.ENCRYPTION_KEY)

    def _is_password_encrypted(self, value):
        return isinstance(value, str) and value.startswith('gAAAAAB')

    def save(self, *args, **kwargs):
        if self.contrasena and not self._is_password_encrypted(self.contrasena):
            self.contrasena = self.encrypt_password(self.contrasena)
        super().save(*args, **kwargs)

    def encrypt_password(self, password):
        if password in (None, ''):
            return password
        return self.cipher.encrypt(password.encode()).decode()

    def decrypt_password(self):
        if not self.contrasena:
            return ''
        if not self._is_password_encrypted(self.contrasena):
            return self.contrasena
        try:
            return self.cipher.decrypt(self.contrasena.encode()).decode()
        except InvalidToken:
            return self.contrasena

    def get_plain_password(self):
        return self.decrypt_password()


    def __str__(self):
        return self.nombre_certificado
    
    
    
    
    
class ComprobanteEmitido(models.Model):
    idUserCFDI = models.ForeignKey(UsersCFDI, on_delete=models.CASCADE,blank=True,null=True, related_name='comprobantes_emitidos')
    # Relación con Factura electronica
    comprobante_relacionado = models.ForeignKey(
        Comprobante,  # Nombre del modelo relacionado
        on_delete=models.SET_NULL,  # Evita problemas si el comprobante es eliminado
        null=True,  # Permite que algunas facturas no tengan comprobante relacionado
        blank=True,
        related_name="comprobantes_emitidos",
        verbose_name="Comprobante Relacionado",
        help_text="Factura relacionado con esta comprobante (por ejemplo, nota de crédito, CFDI anterior)."
    )
    fecha = models.DateTimeField(verbose_name="Fecha de emisión")
    folio = models.CharField(max_length=50, verbose_name="Folio", blank=True, null=True)
    uuid = models.CharField(max_length=36, unique=False, verbose_name="UUID", blank=True, null=True) 
    rfc = models.CharField(max_length=13, verbose_name="RFC")
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    fecha_pago = models.DateField(verbose_name="Fecha de pago", blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")
    
    # Nuevos campos separados
    xml_timbrado = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=255, blank=True, null=True)
    cod_estatus = models.CharField(max_length=100, blank=True, null=True)
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    forma_pago = models.CharField(max_length=50, blank=True, null=True)
    version_cfdi = models.CharField(max_length=10, blank=True, null=True)
    
    cancelado = models.BooleanField(default=False , verbose_name="Comprobante Cancelado", help_text="Indica si el comprobante ha sido cancelado")
    detallesError = models.TextField(blank=True, null=True, verbose_name="Detalles del Error", help_text="Detalles del error si el comprobante no se pudo emitir correctamente")

    class Meta:
        verbose_name = "Comprobante Emitido"
        verbose_name_plural = "Comprobantes Emitidos"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.comprobante_relacionado} - {self.folio} - {self.nombre} - {self.uuid}"

################## modelos para el formulario ################################
    
STATUS_CHOICES = [
    ('draft', 'Borrador'),
    ('published', 'Publicado'),
    ('archived', 'Archivado'),
]
TIPO_COMPROBANTE_CHOICES = [
    ('I', 'Ingreso'),
    ('E', 'Egreso'),
    ('N', 'Nómina'),
    ('P', 'Pago'),
    # Agrega otros tipos si es necesario
]

class Plantilla(models.Model):
    idUserCFDI = models.ForeignKey(UsersCFDI, on_delete=models.CASCADE, related_name='plantillas', null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    html = models.TextField()
    css = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    imagen = models.ImageField(upload_to='plantillas/', null=True)
    tipo_comprobante = models.CharField(max_length=2, choices=TIPO_COMPROBANTE_CHOICES, default='I')  # <--- NUEVO

    def __str__(self):
        return f"{self.name} ({self.name})"


class PDFPersonalizado(models.Model):
    """Plantillas de PDF creadas en el editor visual."""

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pdf_personalizados")
    name = models.CharField(max_length=150)
    html = models.TextField()
    css = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to="pdf_personalizados/", null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("created_by", "name")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name} ({self.created_by})"

##################################################



class FacturaCartaPorteTraslado(models.Model):
    # Relación con Información Fiscal
 
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='facturascartaportetraslado')
    informacion_fiscal = models.ForeignKey(
        InformacionFiscal,
        on_delete=models.CASCADE,
        related_name="facturas_cartaporte_traslado",
        verbose_name="Información Fiscal"
    )

    regimen_fiscal = models.ForeignKey(
        RegimenFiscal,
        on_delete=models.SET_NULL,
        null=True,
        related_name="FacturaCartaPorteTraslado",
        verbose_name="Régimen Fiscal Principal"
    )

    nombre = models.CharField(max_length=255, verbose_name="Nombre de la nómina")
    rfc = models.CharField(max_length=13, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Domicilio")
    codigo_postal = models.CharField(max_length=5, blank=True, null=True)
    activo = models.BooleanField(default=True, verbose_name="Estado Activo", blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación", blank=True, null=True)

    class Meta:
        verbose_name = "Carta Porte Traslado"
        verbose_name_plural = "Carta Porte Traslados"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
    


class Ubicacion(models.Model):
    ComprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='ubicaciones')
    TIPO_UBICACION_CHOICES = [
        ('Origen', 'Origen'),
        ('Destino', 'Destino'),
    ]
    
    tipo_ubicacion = models.CharField(max_length=10, choices=TIPO_UBICACION_CHOICES)
    id_ubicacion = models.CharField(max_length=50, unique=True)
    distancia_recorrida_km = models.FloatField(blank=True, null=True)

    # Estación
    tipo_estacion = models.CharField(max_length=255, blank=True, null=True)
    numero_estacion = models.CharField(max_length=255, blank=True, null=True)
    nombre_estacion = models.CharField(max_length=255, blank=True, null=True)
    fecha_salida_llegada = models.DateField(blank=True, null=True)
    hora_salida_llegada = models.TimeField(blank=True, null=True)
    navegacion_trafico = models.CharField(max_length=255, blank=True, null=True)

    # Remitente/Destinatario
    rfc_remitente_destinatario = models.CharField(max_length=13, blank=True, null=True)
    numero_registro_tributario = models.CharField(max_length=50, blank=True, null=True)
    nombre_remitente = models.CharField(max_length=255, blank=True, null=True)
    residencia_fiscal = models.CharField(max_length=255, blank=True, null=True)
    descripcion_resid_fiscal = models.TextField(blank=True, null=True)

    class Meta:
     verbose_name = "Ubicación"
     verbose_name_plural = "Ubicaciones"

    def __str__(self):
        return f'Ubicación {self.id_ubicacion} - {self.tipo_ubicacion}'


class Ubicaciondomicilio(models.Model):
    FacturaCartaPorteTraslado = models.ForeignKey(FacturaCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='ubicaciones_domicilio')
    ubicacion = models.OneToOneField(Ubicacion, on_delete=models.CASCADE, related_name='domicilio')
    
    pais = models.CharField(max_length=255)
    codigo_postal = models.CharField(max_length=10)
    calle = models.CharField(max_length=255, blank=True, null=True)
    numero_exterior = models.CharField(max_length=10, blank=True, null=True)
    numero_interior = models.CharField(max_length=10, blank=True, null=True)
    colonia = models.CharField(max_length=255, blank=True, null=True)
    localidad = models.CharField(max_length=255, blank=True, null=True)
    municipio = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=255)
    referencia = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Domicilio en {self.pais} - {self.codigo_postal}'



    from django.db import models

class CartaPorte(models.Model):

    comprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='cartas_porte')
    VERSION_CP_CHOICES = [
        ('3.1', '3.1'),
    ]
    
    TRANSPORTE_INTERNACIONAL_CHOICES = [
        ('Sí', 'Sí'),
        ('No', 'No'),
    ]
    
    VIA_TRANSPORTE_CHOICES = [
        ('Aéreo', 'Aéreo'),
        ('Marítimo', 'Marítimo'),
        ('Terrestre', 'Terrestre'),
        ('Ferroviario', 'Ferroviario'),
    ]
    
    version_cp = models.CharField(max_length=5, choices=VERSION_CP_CHOICES, default='3.1')
    transporte_internacional = models.CharField(max_length=2, choices=TRANSPORTE_INTERNACIONAL_CHOICES, default='No')
    entrada_salida_mercancia = models.CharField(max_length=255, blank=True, null=True)
    via_transporte = models.CharField(max_length=20, choices=VIA_TRANSPORTE_CHOICES, blank=True, null=True)
    pais_origen_destino = models.CharField(max_length=255, blank=True, null=True)
    total_distancia_recorrida = models.FloatField(blank=True, null=True)
    registro_istmo = models.CharField(max_length=255, blank=True, null=True)
    polo_origen = models.CharField(max_length=255, blank=True, null=True)
    polo_destino = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
     verbose_name = "Carta Porte Traslado"
     verbose_name_plural = "Carta Porte Traslados"


    def __str__(self):
        return f'Carta Porte {self.id} - {self.version_cp}'
    
    

class Mercancia(models.Model):
    comprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='mercancias')
    # Datos generales
    numero_total_mercancias = models.PositiveIntegerField()
    logistica_inversa = models.CharField(max_length=255, blank=True, null=True)
    
    # Peso y unidad
    clave_unidad_peso = models.CharField(max_length=50, blank=True, null=True)
    unidad_peso = models.CharField(max_length=50, blank=True, null=True)
    peso_bruto_total = models.FloatField(blank=True, null=True)
    peso_neto_total = models.FloatField(blank=True, null=True)
    cargo_por_tasacion = models.FloatField(blank=True, null=True)

    # Detalles de bienes transportados
    cantidad = models.PositiveIntegerField()
    descripcion_producto = models.TextField()
    clave_bienes_transp = models.CharField(max_length=50, blank=True, null=True)
    clave_producto_STCC = models.CharField(max_length=50, blank=True, null=True)

    # Características de bienes
    clave_unidad = models.CharField(max_length=50, blank=True, null=True)
    unidad = models.CharField(max_length=50, blank=True, null=True)
    peso_kg = models.FloatField(blank=True, null=True)
    dimensiones = models.CharField(max_length=255, blank=True, null=True)
    unidad_dimension = models.CharField(max_length=50, blank=True, null=True)

    # Material peligroso
    material_peligroso = models.BooleanField(default=False)
    clave_material_peligroso = models.CharField(max_length=50, blank=True, null=True)
    descripcion_material_peligroso = models.TextField(blank=True, null=True)
    embalaje = models.CharField(max_length=255, blank=True, null=True)
    descripcion_embalaje = models.TextField(blank=True, null=True)

    # Valor y clasificación
    valor_mercancia = models.FloatField(blank=True, null=True)
    moneda = models.CharField(max_length=50, blank=True, null=True)
    fraccion_arancelaria = models.CharField(max_length=50, blank=True, null=True)
    descripcion_fraccion_arancelaria = models.TextField(blank=True, null=True)
    uuid_cfdi_com_ext = models.CharField(max_length=50, blank=True, null=True)

    # Sector COFEPRIS
    sector_cofepris = models.CharField(max_length=255, blank=True, null=True)
    nombre_ingrediente_activo = models.CharField(max_length=255, blank=True, null=True)
    nombre_quimico = models.CharField(max_length=255, blank=True, null=True)
    denominacion_generica = models.CharField(max_length=255, blank=True, null=True)
    denominacion_distintiva = models.CharField(max_length=255, blank=True, null=True)
    
    # Medicamentos y sustancias
    fabricante = models.CharField(max_length=255, blank=True, null=True)
    fecha_caducidad = models.DateField(blank=True, null=True)
    lote_medicamento = models.CharField(max_length=255, blank=True, null=True)
    registro_sanitario = models.CharField(max_length=255, blank=True, null=True)
    numero_cas = models.CharField(max_length=50, blank=True, null=True)

    # Datos adicionales
    datos_fabricante = models.TextField(blank=True, null=True)
    datos_formulador = models.TextField(blank=True, null=True)
    datos_maquilador = models.TextField(blank=True, null=True)
    uso_autorizado = models.TextField(blank=True, null=True)
    estado_materia = models.CharField(max_length=255, blank=True, null=True)

    # Permisos de importación
    folio_permiso_importacion = models.CharField(max_length=255, blank=True, null=True)
    folio_vucem = models.CharField(max_length=255, blank=True, null=True)
    razon_social_importadora = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Mercancía {self.id} - {self.descripcion_producto[:50]}'
    
    class Meta:
        verbose_name = "Mercancia"
        verbose_name_plural = "Mercancias"
    



class CantidadTransportada(models.Model):
    comprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='cantidades_transportadas')
    cantidad = models.PositiveIntegerField()
    id_origen = models.CharField(max_length=50)
    id_destino = models.CharField(max_length=50)
    clave_transporte = models.CharField(max_length=50)

    # Detalles de mercancía (Solo para transporte marítimo)
    unidad_peso = models.CharField(max_length=50)
    descripcion_unidad_peso = models.CharField(max_length=255, blank=True, null=True)
    numero_piezas = models.PositiveIntegerField(blank=True, null=True)
    peso_bruto = models.FloatField()
    peso_neto = models.FloatField()
    peso_tara = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = "Cantidad Transportada"
        verbose_name_plural = "Cantidades Transportadas"

    def __str__(self):
        return f'Cantidad Transportada: {self.cantidad} - Origen: {self.id_origen} - Destino: {self.id_destino}'


class DetalleMercanciaMaritima(models.Model):
    comprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, null = True, blank= True, on_delete=models.CASCADE, related_name='detalles_mercancia_maritima')
    unidad_peso = models.CharField(max_length=50)
    descripcion_unidad_peso = models.CharField(max_length=255, blank=True, null=True)
    numero_piezas = models.PositiveIntegerField(blank=True, null=True)
    peso_bruto = models.FloatField()
    peso_neto = models.FloatField()
    peso_tara = models.FloatField()

    class Meta:
        verbose_name = "Detalle de Mercancía (Marítimo)"
        verbose_name_plural = "Detalles de Mercancía (Marítimo)"

    def __str__(self):
        return f'Detalle Marítimo - Unidad: {self.unidad_peso}, Peso Bruto: {self.peso_bruto} kg'

class Pedimento(models.Model):
    comprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='pedimentos')
    tipo_documento = models.CharField(max_length=255, blank=True, null=True)
    folio_documento = models.CharField(max_length=255, blank=True, null=True)
    rfc_importador = models.CharField(max_length=13, blank=True, null=True)
    numero_pedimento = models.CharField(max_length=21, unique=True)

    class Meta:
        verbose_name = "Pedimento"
        verbose_name_plural = "Pedimentos"

    def __str__(self):
        return f'Pedimento: {self.numero_pedimento}'



class GuiaIdentificacion(models.Model):
    comprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='guias_identificacion')
    numero_guia = models.CharField(max_length=255, unique=True)
    descripcion_contenido = models.TextField(blank=True, null=True)
    peso_kg = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = "Guía de Identificación"
        verbose_name_plural = "Guías de Identificación"

    def __str__(self):
        return f'Guía: {self.numero_guia} - Peso: {self.peso_kg} kg'
    

class TipopermisoSCT (models.Model):
    codigo = models.CharField(max_length=255,blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=255,blank=True, null=True)

    def __str__(self):
        return f'Permiso SCT {self.codigo} - {self.descripcion}'
    

class configuracionvehicular(models.Model):
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Configuración Vehicular {self.codigo} - {self.descripcion}'
    

class subtiporemolque (models.Model):
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Subtipo Remolque {self.codigo} - {self.descripcion}'





class Autotransporte(models.Model):
    comprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='autotransportes')
    tipo_permiso_sct = models.ForeignKey(TipopermisoSCT, on_delete=models.SET_NULL, null=True)
    numero_permiso_sct = models.CharField(max_length=255, unique=True)

    # Identificación vehicular
    configuracion_vehicular = models.ForeignKey(configuracionvehicular, on_delete=models.SET_NULL, null=True)
    placa = models.CharField(max_length=10, unique=True)
    modelo_anio = models.PositiveIntegerField()
    peso_bruto_vehicular = models.FloatField(blank=True, null=True)

    # Remolques
    subtipo_remolque = models.ForeignKey(subtiporemolque, on_delete=models.SET_NULL, null=True)
    placa_remolque = models.CharField(max_length=10, unique=True, blank=True, null=True)

    # Seguros
    prima_seguro = models.FloatField(blank=True, null=True)
    aseguradora_resp_civil = models.CharField(max_length=255)
    poliza_resp_civil = models.CharField(max_length=255)
    aseguradora_ambiental = models.CharField(max_length=255, blank=True, null=True)
    poliza_ambiental = models.CharField(max_length=255, blank=True, null=True)
    aseguradora_carga = models.CharField(max_length=255, blank=True, null=True)
    poliza_carga = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Autotransporte"
        verbose_name_plural = "Autotransportes"

    def __str__(self):
        return f'Autotransporte {self.numero_permiso_sct} - {self.placa}'
    




class TipopermisoSCTmaritimo (models.Model):
    codigo = models.CharField(max_length=255,blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=255,blank=True, null=True)

    def __str__(self):
        return f'Permiso SCT maritimo {self.codigo} - {self.descripcion}'
    
class Tipoembarcacion(models.Model):
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Tipo Embarcación {self.codigo} - {self.descripcion}'

class tipodecarga(models.Model):
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Tipo de Carga {self.codigo} - {self.descripcion}'
    

class numeroregautnaviera (models.Model):
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Numero de Registro Aut. Naviera  {self.descripcion}'


class TransporteMaritimo(models.Model):
    comprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='transportes_maritimos')
    tipo_permiso_sct = models.ForeignKey(TipopermisoSCTmaritimo, on_delete=models.SET_NULL, null=True)
    numero_permiso_sct = models.CharField(max_length=255, unique=True)
    nombre_aseguradora = models.CharField(max_length=255, blank=True, null=True)
    numero_poliza_seguro = models.CharField(max_length=255, blank=True, null=True)

    # Embarcación
    tipo_embarcacion = models.ForeignKey(Tipoembarcacion, on_delete=models.SET_NULL, null=True)
    matricula = models.CharField(max_length=50, unique=True)
    numero_id_omi = models.CharField(max_length=50, unique=True)
    modelo_embarcacion_anio = models.PositiveIntegerField(blank=True, null=True)
    nombre_embarcacion = models.CharField(max_length=255, blank=True, null=True)
    nacionalidad_embarcacion = models.CharField(max_length=255)
    descripcion_nacionalidad = models.TextField(blank=True, null=True)

    # Capacidad de la embarcación
    numero_cert_itc = models.CharField(max_length=255, blank=True, null=True)
    permiso_navegacion = models.CharField(max_length=255, blank=True, null=True)
    unidades_arqueo = models.CharField(max_length=255)
    tipo_carga = models.ForeignKey(tipodecarga, on_delete=models.SET_NULL, null=True)
    eslora_pies = models.FloatField(blank=True, null=True)
    manga_pies = models.FloatField(blank=True, null=True)
    calado_pies = models.FloatField(blank=True, null=True)
    puntal_pies = models.FloatField(blank=True, null=True)

    # Línea naviera
    linea_naviera = models.CharField(max_length=255, blank=True, null=True)
    nombre_agente_naviero = models.CharField(max_length=255)
    numero_reg_aut_naviera = models.ForeignKey(numeroregautnaviera, on_delete=models.SET_NULL, null=True)
    numero_viaje = models.CharField(max_length=255, blank=True, null=True)
    numero_conocimiento_embarque = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Transporte Marítimo"
        verbose_name_plural = "Transportes Marítimos"

    def __str__(self):
        return f'Transporte Marítimo {self.numero_permiso_sct} - {self.matricula}'



class tipocontenedor(models.Model):
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Tipo de Contenedor {self.codigo} - {self.descripcion}'


class Contenedor(models.Model):
    tipo_contenedor = models.ForeignKey(tipocontenedor, on_delete=models.SET_NULL, null=True)
    id_ccp_uuid = models.CharField(max_length=255, unique=True, blank=True, null=True)
    matricula_id_contenedor = models.CharField(max_length=15, unique=True)
    numero_sello_precinto = models.CharField(max_length=20, blank=True, null=True)
    fecha_certificacion_cfdi = models.DateTimeField(blank=True, null=True)

    # Remolques CCP (CPP 3.1)
    subtipo_remolque_ccp = models.ForeignKey(subtiporemolque, on_delete=models.SET_NULL, null=True)
    placa_ccp = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f'Contenedor {self.matricula_id_contenedor}'



class TipopermisoSCTaereo (models.Model):
    codigo = models.CharField(max_length=255,blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=255,blank=True, null=True)

    def __str__(self):
        return f'Permiso SCT aereo {self.codigo} - {self.descripcion}'
    
class codigotransportista(models.Model):
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Código Transportista {self.codigo} - {self.descripcion}'


class TransporteAereo(models.Model):
    comprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='transporteAereo')
    tipo_permiso_sct = models.ForeignKey(TipopermisoSCTaereo, on_delete=models.SET_NULL, null=True)
    numero_permiso_sct = models.CharField(max_length=255, unique=True)
    codigo_transportista = models.ForeignKey(codigotransportista, on_delete=models.SET_NULL, null=True)
    lugar_contrato = models.CharField(max_length=255, blank=True, null=True)

    # Aseguradora
    nombre_aseguradora = models.CharField(max_length=255, blank=True, null=True)
    numero_poliza_seguro = models.CharField(max_length=255, blank=True, null=True)

    # Información de la aeronave
    numero_matricula_aeronave = models.CharField(max_length=255, unique=True)
    numero_guia = models.CharField(max_length=255)

    # Embarcador
    rfc_embarcador = models.CharField(max_length=13, blank=True, null=True)
    nombre_embarcador = models.CharField(max_length=255, blank=True, null=True)
    residencia_fiscal_embarcador = models.CharField(max_length=255, blank=True, null=True)
    descripcion_residencia_fiscal = models.TextField(blank=True, null=True)
    numero_id_reg_trib_embarcador = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Transporte Aéreo"
        verbose_name_plural = "Transportes Aéreos"


    def __str__(self):
        return f'Transporte Aéreo {self.numero_permiso_sct} - {self.numero_matricula_aeronave}'



class tiposervicio(models.Model):
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Tipo de Servicio {self.codigo} - {self.descripcion}'
    
class tipotrafico(models.Model):
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Tipo de Tráfico {self.codigo} - {self.descripcion}'
    

class tipoderechopaso(models.Model):
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Tipo de Derecho de Paso {self.codigo} - {self.descripcion}'
    
class tipocarro (models.Model):
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Tipo de Carro {self.codigo} - {self.descripcion}'


class tipocontenedorcarro(models.Model):
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Tipo de Contenedor Carro {self.codigo} - {self.descripcion}'

class TransporteFerroviario(models.Model):
    comprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='transporteFerroviario')
    tipo_servicio = models.CharField(max_length=255)
    tipo_trafico = models.CharField(max_length=255)
    nombre_aseguradora = models.CharField(max_length=255, blank=True, null=True)
    numero_poliza_seguro = models.CharField(max_length=255, blank=True, null=True)

    # Derechos de paso (si aplica)
    tipos_derechos_paso =  models.ForeignKey(tipoderechopaso, on_delete=models.SET_NULL, null=True)

    # Carro ferroviario
    tipo_carro = models.ForeignKey(tipocarro, on_delete=models.SET_NULL, null=True)
    matricula_carro = models.CharField(max_length=255, unique=True)
    guia_carro = models.CharField(max_length=255, blank=True, null=True)
    toneladas_netas_carro = models.FloatField(blank=True, null=True)

    # Contenedor en tren
    tipo_contenedor = models.ForeignKey(tipocontenedorcarro, on_delete=models.SET_NULL, null=True)
    peso_contenedor_vacio_kg = models.FloatField()
    peso_neto_mercancia_kg = models.FloatField()

    class Meta:
        verbose_name = "Transporte Ferroviario"
        verbose_name_plural = "Transportes Ferroviarios"

    def __str__(self):
        return f'Transporte Ferroviario {self.tipo_servicio} - Carro {self.matricula_carro}'


class tipofigura(models.Model):
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Tipo de Figura {self.codigo} - {self.descripcion}'

class FiguraTransporte(models.Model):
    comprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='figuras_transporte')
    tipo_figura = models.ForeignKey(tipofigura, on_delete=models.SET_NULL, null=True)
    numero_licencia = models.CharField(max_length=50, blank=True, null=True)
    rfc = models.CharField(max_length=13, blank=True, null=True)  # RFC en México tiene 13 caracteres
    numero_registro_trib = models.CharField(max_length=50, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    residencia_fiscal = models.CharField(max_length=255, blank=True, null=True)
    descripcion_residencia_fiscal = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
     verbose_name = "Figura de Transporte"
     verbose_name_plural = "Figuras de Transporte"

    def __str__(self):
        return f'{self.tipo_figura} - {self.nombre}'

class partetransporte(models.Model):
    comprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='partetransportes')
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Parte de Transporte"
        verbose_name = "Parte de Transporte"

    def __str__(self):
        return f'Parte de Transporte {self.codigo} - {self.descripcion}'

class Domicilio(models.Model):
    ComprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='domicilios')
    figura_transporte = models.OneToOneField(FiguraTransporte, on_delete=models.CASCADE, related_name="domicilio", blank=True, null=True)
    pais = models.CharField(max_length=100, blank=False, null=False)  # Obligatorio
    codigo_postal = models.CharField(max_length=10, blank=False, null=False)  # Obligatorio
    calle = models.CharField(max_length=255, blank=True, null=True)
    numero_exterior = models.CharField(max_length=20, blank=True, null=True)
    numero_interior = models.CharField(max_length=20, blank=True, null=True)
    colonia = models.CharField(max_length=255, blank=True, null=True)
    localidad = models.CharField(max_length=255, blank=True, null=True)
    municipio = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=255, blank=False, null=False)  # Obligatorio
    referencia = models.TextField(blank=True, null=True)

    class Meta:
     verbose_name = "Domicilio"
     verbose_name_plural = "Domicilioss"

    def __str__(self):
        return f'{self.pais} - {self.codigo_postal}'


class regimenaduaneroccptresuno(models.Model):
    comprobanteCartaPorteTraslado = models.ForeignKey(ComprobanteCartaPorteTraslado, on_delete=models.CASCADE,null = True, blank= True, related_name='regimenes_aduaneros')
    codigo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        verbose_name_plural = "Regimen Aduanero Ccp 31"
        verbose_name = "Regimen Aduanero Ccp 31"

    def __str__(self):
        return f'Regimen Aduanero Ccp 31 {self.codigo} - {self.descripcion}'
    
    
class CancelacionCFDI(models.Model):
    comprobante = models.ForeignKey(ComprobanteEmitido, on_delete=models.CASCADE, related_name='cancelaciones')
    uuid_original = models.CharField(max_length=36)
    motivo = models.CharField(max_length=2, choices=MOTIVOS_CANCELACION)
    uuid_sustitucion = models.CharField(max_length=36, blank=True, null=True)
    fecha_inicio_cancelacion = models.DateTimeField(blank=True, null=True)  # primer intento (del SAT)
    fecha_ultimo_intento = models.DateTimeField(blank=True, null=True)   # se actualiza con cada intento
    estado_cancelacion = models.CharField(max_length=100, blank=True, null=True)  # e.g., "Cancelado sin aceptación"
    usuario = models.ForeignKey(UsersCFDI, on_delete=models.SET_NULL, null=True, blank=True)
    respuesta_sat = models.TextField(blank=True, null=True)  # Para guardar el acuse o XML si aplica
    exitoso = models.BooleanField(default=False) # El SAT aceptó la solicitud de cancelación
    cancelado = models.BooleanField(default=False)  # El CFDI ya fue confirmado como cancelado

    class Meta:
        verbose_name = "Cancelación de CFDI"
        verbose_name_plural = "Cancelaciones de CFDI"
        ordering = ['-fecha_inicio_cancelacion']

    def __str__(self):
        return f"Cancelación de {self.uuid_original} ({self.get_motivo_display()})"



class GroupMeta(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='meta')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='groups_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='groups_updated')
    updated_at = models.DateTimeField(auto_now=True)
   

    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "Detalle grupos"

    def __str__(self):
        return f"Meta({self.group.name})"
    









   

class GroupManager(models.Manager):
    """
    The manager for the auth's Group model.
    """

    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)
    





    
class GruposCFDI(models.Model):
    """
    Los grupos son una forma genérica de categorizar a los usuarios para aplicar permisos, 
    u otra etiqueta, a dichos usuarios. Un usuario puede pertenecer a cualquier número de grupos.

    Un usuario que pertenece a un grupo obtiene automáticamente todos los permisos que le hayan sido 
    concedidos a ese grupo. Por ejemplo, si el grupo 'Editores del sitio' tiene el permiso 
    can_edit_home_page, cualquier usuario dentro de ese grupo tendrá también ese permiso.

    Más allá de los permisos, los grupos son una manera conveniente de categorizar usuarios para 
    aplicarles alguna etiqueta o funcionalidad extendida. Por ejemplo, podrías crear un grupo llamado 
    'Usuarios especiales' y escribir código que haga cosas específicas para esos usuarios, como 
    darles acceso a una sección exclusiva de tu sitio o enviarles correos electrónicos solo para miembros.
    """


    name = models.CharField("name", max_length=150, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name="permissions",
        blank=True,
    )

    objects = GroupManager()

    class Meta:
        verbose_name = "grupoCFDI"
        verbose_name_plural = "grupos CFDI"

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)



class BitacoraCFDI(models.Model):
    comprobante = models.OneToOneField(Comprobante, on_delete=models.CASCADE, related_name='bitacora')

    # Creación
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cfdi_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ip_creacion = models.GenericIPAddressField(blank=True, null=True)
    ubicacion_creacion  = models.CharField(max_length=100, null=True, blank=True)

    # Edición
    editado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cfdi_editados')
    fecha_edicion = models.DateTimeField(blank=True, null=True)
    ip_edicion = models.GenericIPAddressField(blank=True, null=True)
    ubicacion_edicion  = models.CharField(max_length=100, null=True, blank=True)

    # Timbrado
    timbrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cfdi_timbrados')
    fecha_timbrado = models.DateTimeField(blank=True, null=True)
    ip_timbrado = models.GenericIPAddressField(blank=True, null=True)
    ubicacion_timbrado   = models.CharField(max_length=100, null=True, blank=True)


    # Cancelación
    cancelado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cfdi_cancelados')
    fecha_cancelacion = models.DateTimeField(blank=True, null=True)
    ip_cancelacion = models.GenericIPAddressField(blank=True, null=True)
    ubicacion_cancelacion  = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        folio = self.comprobante.folio or f"ID {self.comprobante.id}"
        return f"Bitácora CFDI - {self.comprobante} - {folio}"
    
    class Meta:
        verbose_name = "Bitacora CFDI"
        verbose_name_plural = "Bitacoras CFDI" 
