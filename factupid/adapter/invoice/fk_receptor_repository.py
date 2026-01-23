
from dominio.invoice.ReceptorRepository import ReceptorRepository
from  dominio.invoice.Receptor import Receptor


class FKReceptorRepository (ReceptorRepository):
    def add(self, receptor):
        #llamar al web service que inserta cliente de la plataforma 
        # de  timbrado 
        
        return Receptor()
        
   