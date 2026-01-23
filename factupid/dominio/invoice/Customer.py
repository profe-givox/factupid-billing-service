from dataclasses import dataclass

@dataclass
class Customer:
    user_id = str
    username = str
    email = str
    is_active = str
    is_authenticated = str
    roles = str


#from dominio.invoice.customer_repository import CustomerRepository

#class Customer(object):
#    id: int
#
#    def validate(self, customer_repository: CustomerRepository) -> dict:
#        """Valida un cliente."""
#        return customer_repository.validate(self)
#
#    def create_or_update(self, customer_data: dict, customer_repository: CustomerRepository) -> dict:
#        """Crea o actualiza un cliente."""
#        return customer_repository.create_or_update(customer_data)
