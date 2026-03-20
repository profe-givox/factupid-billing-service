from sqlmodel import create_engine, Session

DATABASE_URL = "sqlite:///./billing.db"  # temporal para desarrollo

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Muestra SQL en consola (solo dev)
)

def get_session():
    with Session(engine) as session:
        yield session