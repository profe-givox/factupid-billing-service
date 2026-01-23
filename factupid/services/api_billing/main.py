from fastapi import FastAPI, Request
import stripe
import psycopg2
import os

app = FastAPI()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

pg_conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    dbname=os.getenv("POSTGRES_DB"),
    port=os.getenv("POSTGRES_PORT"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/create-payment-intent")
def create_payment_intent(amount: int):
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency="mxn",
        automatic_payment_methods={"enabled": True},
    )

    cur = pg_conn.cursor()
    cur.execute(
        "INSERT INTO pagos (id, monto) VALUES (%s, %s)",
        (intent["id"], amount)
    )
    pg_conn.commit()

    return {"client_secret": intent["client_secret"]}


@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    event = stripe.Event.construct_from(
        request.json(), stripe.api_key
    )

    if event["type"] == "payment_intent.succeeded":
        payment = event["data"]["object"]

        cur = pg_conn.cursor()
        cur.execute(
            "UPDATE pagos SET status='success' WHERE id=%s",
            (payment["id"],)
        )
        pg_conn.commit()

    return {"received": True}