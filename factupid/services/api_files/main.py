from fastapi import FastAPI, UploadFile, File
import boto3
import os
import uuid
import psycopg2

app = FastAPI()

# ---------- PostgreSQL Connection ----------
pg_conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "postgres"),
    port=os.getenv("POSTGRES_PORT", "16314"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

# ---------- MinIO / S3 Client ----------
s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
    aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
)

BUCKET = os.getenv("MINIO_BUCKET")


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    filename = f"{file_id}-{file.filename}"

    # ---------- Guardar archivo en S3 / MinIO ----------
    s3.upload_fileobj(file.file, BUCKET, filename)

    # ---------- Registrar metadata en PostgreSQL ----------
    cur = pg_conn.cursor()
    cur.execute(
        "INSERT INTO archivos (id, nombre) VALUES (%s, %s)", (file_id, filename)
    )
    pg_conn.commit()

    return {
        "message": "archivo guardado correctamente",
        "id": file_id,
        "filename": filename,
    }
