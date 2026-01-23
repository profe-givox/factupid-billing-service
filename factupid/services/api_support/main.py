from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime
import os

app = FastAPI()

mongo = MongoClient(os.getenv("MONGO_URL"))
db = mongo["factupid"]
tickets = db["tickets"]


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/ticket")
def create_ticket(msg: str):
    record = {
        "mensaje": msg,
        "fecha": datetime.utcnow()
    }
    tickets.insert_one(record)
    return {"status": "ticket creado", "data": record}