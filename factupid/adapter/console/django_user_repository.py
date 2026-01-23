from django.contrib.auth import get_user_model
from django.db.models import Q

# Obtiene el modelo de usuario definido en la configuración de Django
User = get_user_model()

class CustomAuthAdapter:
    """
    CustomAuthAdapter es una clase adaptadora que maneja la autenticación de usuarios.
    Permite la autenticación de usuarios ya sea por nombre de usuario o por correo electrónico.

    Métodos:
        authenticate(self, identifier, password):
            Autentica un usuario utilizando el nombre de usuario o el correo electrónico como identificador.

        email_exists(self, email):
            Verifica si existe un usuario con el correo electrónico proporcionado.
    """

    def authenticate(self, identifier, password):
        """
        Autentica un usuario basado en el identificador (nombre de usuario o correo electrónico)
        y la contraseña proporcionados.

        Args:
            identifier (str): El nombre de usuario o correo electrónico del usuario.
            password (str): La contraseña del usuario.

        Returns:
            User: El objeto de usuario autenticado si las credenciales son correctas.
            None: Si las credenciales no son correctas.
        """
        try:
            user = User.objects.get(Q(username__iexact=identifier) | Q(email__iexact=identifier))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def email_exists(self, email):
        """
        Verifica si existe un usuario con el correo electrónico proporcionado.

        Args:
            email (str): El correo electrónico a verificar.

        Returns:
            bool: True si existe un usuario con el correo electrónico proporcionado.
            False si no existe ningún usuario con ese correo electrónico.
        """
        return User.objects.filter(email=email).exists()
