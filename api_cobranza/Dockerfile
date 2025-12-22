# Imagen base de Python
FROM python:3.11.9

# Evitar que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear directorio en el contenedor
WORKDIR /app

# Instalar dependencias del sistema que Django necesita
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalarlos
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del proyecto
COPY . /app/

# Exponer el puerto donde correrá runserver
EXPOSE 8000

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "factupid.wsgi:application"]