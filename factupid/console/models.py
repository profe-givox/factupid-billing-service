from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser

from dominio.console import SupplierStamp  as SupplierStampDominio 
from cryptography.fernet import Fernet
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from invoice.vistas.user import register
import secrets
from dominio.console import SupplierStamp  as SupplierStampDominio

# Genera una clave y guárdala en un lugar seguro
#key = Fernet.generate_key()
# key = settings.SECRET_KEY_SUPP_STAMP
# cipher_suite = Fernet(key)

#Nota: La clave de encriptación (key) debe almacenarse de manera segura y no debe ser 
# accesible públicamente. En un entorno de producción, podrías almacenarla en una 
# variable de entorno o en un servicio de gestión de secretos.

class SupplierStamp(models.Model):
    user = models.TextField()
    idSocio = models.TextField()
    urlSignManifest = models.TextField()
    password = models.CharField(max_length=256)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cipher = Fernet(settings.ENCRYPTION_KEY)

    def save(self, *args, **kwargs):
        # Solo encriptar si la contraseña no parece estar cifrada (verificamos longitud o estructura)
        if self.password and not self.password.startswith('gAAAAAB'):  # Fernet encrypted strings start with 'gAAAAAB'
            self.password = self.encrypt_password(self.password)
        super().save(*args, **kwargs)

    def encrypt_password(self, password):
        # Encriptar la contraseña
        return self.cipher.encrypt(password.encode()).decode()

    def decrypt_password(self):
        # Desencriptar la contraseña
        return self.cipher.decrypt(self.password.encode()).decode()



class Service_Plan(models.Model):
    class Meta:
        unique_together = (('service', 'plan'),)
    
    service = models.ForeignKey('Service', on_delete=models.DO_NOTHING)
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE)
    isActive = models.BooleanField(default=True)
    fechaVigenciaInicio = models.DateField()
    fechaVigenciaFin = models.DateField()
    supplierStamp = models.ForeignKey('SupplierStamp', on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return f"[ID Servicio: {self.service.id}, Nombre Servicio: {self.service.nombre}, ID Plan: {self.plan.id}, Nombre Plan: {self.plan.nombre}, Tipo de Servicio: {self.get_service_tipo_display()}]"

    def get_service_tipo_display(self):
        return self.service.get_tipo_display()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guarda el objeto primero
        group_name = f"{self.service.nombre}"  # Nombre del grupo basado en el servicio
        group, created = Group.objects.get_or_create(name=group_name)  # Obtiene o crea el grupo
        
        if created and group_name == "CFDI":  # Solo asigna permisos si el grupo es "CFDI"
            permisos_ids = [
                295, 296, 297, 298, 230, 226, 299, 300, 301, 302,
                283, 284, 285, 286, 271, 272, 273, 274, 363, 364, 
                365, 366, 279, 280, 281, 282, 255, 256, 257, 258, 
                291, 292, 293, 294, 311, 312, 313, 314, 247, 248, 
                249, 250, 275, 276, 277, 278, 259, 260, 261, 262, 
                287, 288, 289, 290, 251, 252, 253, 254, 315, 316, 
                317, 318, 359, 360, 361, 362, 379, 380, 381, 382, 
                263, 264, 265, 266, 239, 240, 241, 242, 371, 372, 
                373, 374, 375, 376, 377, 378, 367, 368, 369, 370
            ]
            permisos = Permission.objects.filter(id__in=permisos_ids)
            group.permissions.set(permisos)  # Asigna los permisos al grupo




class Plan(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    caracteristicas = models.TextField()
    TIPO_CHOICES = (
        ('mensual', 'Mensual'),
        ('anual', 'Anual'),
        ('bajo consumo', 'Bajo consumo'),
    )
    tipo = models.CharField(max_length=100, choices=TIPO_CHOICES)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    limite_operaciones_dia = models.IntegerField()
    limite_operaciones_plan = models.IntegerField()

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class Service(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    TIPO_CHOICES = (
        ('app', 'App'),
        ('api', 'API'),
    )
    tipo = models.CharField(max_length=100, choices=TIPO_CHOICES)
    url_servicio = models.CharField(max_length=100)
    enviar_pdf = models.BooleanField(default=False, help_text="¿Adjuntar PDF en correo?")


    def get_full_url(self, host):
        return f"http://{host}{self.url_servicio}"

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class Post(models.Model):
    titulo = models.CharField(max_length=100)
    contenido = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    servicio = models.ForeignKey(Service, on_delete=models.CASCADE, default=1)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo
    

#### Este es el nuevo modelo que hay que usar en este lo diferente es el nombre del modelo, se agrego el campo date_cutoff y no_stamped_day los demas son
# lo mismo pero pero con otro nombre

class User_Service(models.Model):

    class Meta:
        unique_together = (('idUser', 'idService'),)

    idUser = models.ForeignKey(User, on_delete=models.CASCADE)
    idService = models.ForeignKey(Service, on_delete=models.CASCADE)
    idPlan = models.ForeignKey('Plan', on_delete=models.CASCADE, null=True, blank=True)
    idServicePlan = models.ForeignKey(Service_Plan,on_delete=models.DO_NOTHING,null=True, blank=True)
    date_activate = models.DateTimeField(auto_now_add=True)
    date_cutoff = models.DateField()
    aceptarTerminos= models.BooleanField(default=False)
    
    #Terminos y condciones aceptados
    aceptarTerminos = models.BooleanField(default=False)
    #Efren: Este campo tendrá el número de timbres que le asigna el plan
    #Este campo será actualizado cada vez que un cliente del user invoice se le asigne timbres
    #ESto tambien debe actualizarse en el PAC
    stamp = models.IntegerField(default=0)
    cont_stamped_user = models.IntegerField(default=0)
    cont_stamped_day = models.IntegerField(default=0)

    # Define un método property para obtener la URL del servicio
    @property
    def url_servicio(self):
        return self.idService.url_servicio
    
    # # Sincronización con el contador global
    # def sync_timbres(self):
    #     """
    #     Sincroniza el contador global con los campos locales (stamp, cont_stamped_user).
    #     """
    #     user_cfdi = UsersCFDI.objects.filter(idUserCFDI=self.idUser).first()
    #     if not user_cfdi:
    #         return

    #     conteo = user_cfdi.get_conteo_timbres_actual()
    #     self.stamp = conteo.limite_timbres
    #     self.cont_stamped_user = conteo.contador_actual
        self.save()

    def __str__(self):
        return f"Cliente: {self.idUser.username}, Servicio: {self.idService.nombre}, URL Servicio: {self.idService.url_servicio}, Plan: {self.idPlan.nombre if self.idPlan else 'Sin plan'}"


@receiver(pre_delete, sender=User_Service)
def eliminar_plan_asociado(sender, instance, **kwargs):
    if instance.idPlan:
        # Aquí puedes almacenar el ID del ClienteServicio en una lista, o realizar otras acciones necesarias
        pass








class SelectedService(models.Model):
    service_id = models.IntegerField(unique=True)
    service_url = models.URLField()

    def __str__(self):
        return f'Service {self.service_id} - {self.service_url}'
    
################################invoices############################################
class Customer(models.Model):
    nombre = models.CharField(max_length=100)
    correoElectronico = models.EmailField()
    rfc = models.CharField(max_length=100)
    telefono = models.CharField(max_length=100)
    tipoDeCliente = models.CharField(max_length=100)
    certificado = models.FileField(upload_to='certificados/')
    llave = models.FileField(upload_to='llaves/')
    contrasena = models.CharField(max_length=100)
    calle = models.CharField(max_length=100)
    noExterior = models.CharField(max_length=100)
    noInterior = models.CharField(max_length=100)
    colonia = models.CharField(max_length=100)
    localidad = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    codigoPostal = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.id} - {self.nombre}"
    