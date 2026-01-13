from sqlmodel import SQLModel

# Importa todos los modelos aqui
from app.models.plan import Plan  
from app.models.subscription import Subscription 
from app.models.payment import Payment

def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)
    

