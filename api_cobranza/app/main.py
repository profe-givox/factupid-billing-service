from fastapi import FastAPI
from app.routers import plans, payments
from app.db.session import engine
from app.db.base import create_db_and_tables
from app.db.seed import seed_plans


app = FastAPI(
    title="Factupid Billing Service",
    version="0.1.0",
)


app.include_router(plans.router)
app.include_router(payments.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables(engine)
    seed_plans()
    
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {"message": "Hola Mundo FastAPI está funcionando"}
