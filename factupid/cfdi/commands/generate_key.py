from django.core.management.base import BaseCommand
from cryptography.fernet import Fernet

class Command(BaseCommand):
    help = 'Genera una nueva clave de encriptación para el sistema'

    def handle(self, *args, **kwargs):
        # Generar una nueva clave de encriptación
        key = Fernet.generate_key()
        # Mostrar la clave generada en la consola
        self.stdout.write(self.style.SUCCESS(f'Clave generada: {key.decode()}'))
