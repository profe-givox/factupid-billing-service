from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routers import plans, payments, webhooks, subscriptions
from app.db.seed import seed_plans

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Ya no crear tablas aquí
#     # seed_plans()
#     yield
#     # aquí iría lógica de cierre si algún día la necesitas

app = FastAPI(
    title="Factupid Billing Service",
    version="0.1.0",
)


app.include_router(plans.router)
app.include_router(payments.router)
app.include_router(webhooks.router)
app.include_router(subscriptions.router)

    
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {"message": "Hola Mundo FastAPI está funcionando"}
