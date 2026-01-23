#import os
from pathlib import Path
from decouple import config
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = Path(__file__).resolve().parent.parent

SQLITE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

POSTGRESSQL = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "factupiddatabase",
        "USER": "factupid", 
        "PASSWORD": "raspbian",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

POSTGRESSQLREMOTE = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        "OPTIONS": {
                'sslmode': 'disable', 
            },
    }
}

MySQL = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Factupid',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',  # O la dirección IP de tu servidor MySQL
        'PORT': '3306',  # El puerto predeterminado de MySQL es 3306
    }
}

POSTGRESSQLLAN = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        # Cuando se ejecuta con Docker Compose el servicio de base de datos se
        # expone bajo el nombre "postgres". Usamos ese alias como valor por
        # defecto para evitar dependencias externas o hosts de túneles que
        # puedan no estar disponibles.
        'HOST': config('DB_HOST', default='postgres'),
        'PORT': config('DB_PORT', default='5432'),
        "OPTIONS": {
                'sslmode': 'disable', 
            },
    }
}