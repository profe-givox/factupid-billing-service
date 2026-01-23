from abc import ABC, abstractmethod


class CustomerRepository(ABC):
    @abstractmethod
    def is_valid_user(self, user_id):
        return self.customer_repository.is_valid_user(user_id)
    @abstractmethod
    def get_customer_by_id(self, customer_id):
        pass

    @abstractmethod
    def get_customer_by_username(self, username):
        pass

    @abstractmethod
    def create_customer(self, customer):
        pass

    @abstractmethod
    def update_customer(self, customer):
        pass

    @abstractmethod
    def delete_customer(self, customer_id):
        pass


#import abc
#from typing import Optional
#from dominio.invoice.Customer import Customer

#class CustomerRepository(metaclass=abc.ABCMeta):

#    """Un repositorio de clientes con la capacidad de crear o actualizar."""

#    @abc.abstractmethod
#    def validate(self, customer: Customer) -> Customer:
#        """Valida un cliente."""
#        return Customer()

#    @abc.abstractmethod
#    def create_or_update(self, customer_data: dict) -> Customer:
#        """Crea o actualiza un cliente."""
#        raise NotImplementedError
        
#    """description of class"""
    
#    @abc.abstractmethod
#    def validate(self, customer: Customer) -> Customer:
#        return Customer()

