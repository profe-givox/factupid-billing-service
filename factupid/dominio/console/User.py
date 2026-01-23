from dataclasses import dataclass
import string


@dataclass
class User:
    username: str
    email: str
    password: str







# @dataclass
# class User(object):
#     """Clase que representa un usuario."""
#     id: str

#     def authenticate(self, user_repository: 'UserRepository'):
#         return user_repository

#     def register(self, user_data: dict) -> 'UserRepository':
#         """Registra un nuevo usuario."""
#        
#         new_user = User(id=user_data['id'])
#         return new_user
