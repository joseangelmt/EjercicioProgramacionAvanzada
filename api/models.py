from datetime import datetime
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from .base_datos import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    contenido = Column(Text, nullable=False)
    deadline = Column(Date, nullable=False)
    completada = Column(Boolean, default=False, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
