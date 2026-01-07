from fastapi import FastAPI

app = FastAPI(
    title="Factupid Billing Service",
    version="0.1.0",
)

@app.get("/")
def read_root():
    return {"message": "Hola Mundo FastAPI está funcionando"}
