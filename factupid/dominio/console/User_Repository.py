from abc import ABC, abstractmethod
from django.contrib.auth.models import User

class AbstractUserRepository(ABC):
    @abstractmethod
    def create_user(self, username, password):
        pass

    def get_user_by_email(self, email):
        pass


    @abstractmethod
    def get_user_by_username(self, username):
        pass
    
    @abstractmethod
    def authenticate_user(self, username, password):
        pass

class DjangoUserRepository(AbstractUserRepository):
    def create_user(self, username, password):
        return User.objects.create_user(username=username, password=password)

    def get_user_by_username(self, username):
        return User.objects.filter(username=username).first()
    
    def authenticate_user(self, username, password):
        user = self.get_user_by_username(username)
        if user and user.check_password(password):
            return user
        else:
            return None



    