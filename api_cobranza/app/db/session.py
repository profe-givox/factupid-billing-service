from sqlmodel import create_engine, Session
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine_kwargs = {
    "echo": False,
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(DATABASE_URL, **engine_kwargs)


def get_session():
    with Session(engine) as session:
        yield session