
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class BaseDatos:
    def __init__(self, database_url: str):
        self.__engine = create_engine(database_url)

        # Fábrica de sesiones: cada llamada a crea_sesion() devuelve una sesión nueva.
        self.__sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=self.__engine)

    def crear_base_datos(self):
        Base.metadata.create_all(bind=self.__engine)

    def crea_sesion(self):
        return self.__sessionmaker()
