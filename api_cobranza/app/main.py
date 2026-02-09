from fastapi import FastAPI
from app.routers import plans, payments, webhooks, subscriptions
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import create_db_and_tables
from app.db.seed import seed_plans


app = FastAPI(
    title="Factupid Billing Service",
    version="0.1.0",
)


# Permite llamadas desde el front local (Hugo) en desarrollo
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:1313",
#         "http://127.0.0.1:1313",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


app.include_router(plans.router)
app.include_router(payments.router)
app.include_router(webhooks.router)
app.include_router(subscriptions.router)

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
