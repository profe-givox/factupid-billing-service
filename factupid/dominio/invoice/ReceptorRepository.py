from abc import ABC, abstractmethod

class ReceptorRepository(ABC):
    """description of class"""
    
    @abstractmethod
    def add (self, receptor):
        pass    

    @abstractmethod
    def assign (self, receptor, credit):
        pass
    
    @abstractmethod
    def customers(self):
        pass
    
    @abstractmethod
    def get (self):
        pass
    
    @abstractmethod
    def edit (self):
        pass
    
    @abstractmethod 
    def switch(self):
        pass
    