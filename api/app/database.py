# api/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Ruta al archivo SQLite creado por Flask.
# En desarrollo, api/ está en la misma raíz que web/, así que ../web/taskmanager.db
# En producción se usará una variable de entorno con la URL de PostgreSQL.
DATABASE_URL = os.environ.get('DATABASE_URL') or \
                'sqlite:///../web/taskmanager.db'

# check_same_thread=False es necesario para SQLite en entornos multihilo
# (FastAPI puede procesar peticiones en threads distintos).
# PostgreSQL no necesita este argumento.
connect_args = {'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Función de dependencia para obtener una sesión de BD en cada petición.
# Se usa con Depends() en los endpoints.
def get_db():
    db = SessionLocal()
    try:
        yield db # Ceder el control al endpoint
    finally:
        db.close() # Siempre cerrar la sesión, incluso si hay un error