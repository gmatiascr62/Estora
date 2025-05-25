from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
usuarios_en_memoria = {}  # id -> dict del usuario

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

def cargar_usuarios_en_memoria():
    from models.models import Usuario
    from models.persona_memoria import Persona
    db = SessionLocal()
    usuarios = db.query(Usuario).all()
    for usuario in usuarios:
        usuarios_en_memoria[usuario.user_id] = Persona(usuario)
    db.close()



