# Modelos Data Transfer Object de Pydantic para la API de gestión de tareas
from datetime import date, datetime
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    titulo: str = Field(min_length=1, description="Título de la tarea")
    contenido: str = Field(min_length=1, description="Contenido de la tarea")
    deadline: date = Field(description="Fecha de vencimiento")

class TaskResponse(BaseModel):
    id: int
    titulo: str
    contenido: str
    deadline: date
    completada: bool
    fecha_creacion: datetime
