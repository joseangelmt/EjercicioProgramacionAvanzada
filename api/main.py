from typing import List

from fastapi import FastAPI, Response, status
from sqlalchemy.orm import Session

from .administrador_tareas import TaskManager
from .base_datos import BaseDatos
from .filtro_contenido import FiltroContenido
from .manejadores_errores import registrar_manejadores
from .dtos import TaskCreate, TaskResponse

# Creamos la instancia de FastAPI y registramos los manejadores de errores
app = FastAPI(title="Task Management API", version="1.0.0")
registrar_manejadores(app)

# Persistencia en SQLite
# Ruta relativa al directorio desde el que se lanza uvicorn, no al directorio de main.py
DATABASE_URL = "sqlite:///./tasks.db"
base_datos = BaseDatos(DATABASE_URL)
base_datos.crear_base_datos()  # Creamos la base de datos

# Un único filtro para toda la aplicación: Palabrota carga sus listas de palabras al crearse.
filtro_contenido = FiltroContenido()


def crear_task_manager(db: Session) -> TaskManager:
    return TaskManager(db, filtro_contenido)


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea(task: TaskCreate):
    with base_datos.crea_sesion() as db:
        task_manager = crear_task_manager(db)
        tarea_creada = task_manager.create_task(task)
        return tarea_creada

# /tasks/caducadas tiene que declararse antes que /tasks/{task_id};
# si no, FastAPI intentaría interpretar "caducadas" como un id
@app.get("/tasks/caducadas", response_model=List[TaskResponse])
def obtener_tareas_caducadas():
    with base_datos.crea_sesion() as db:
        task_manager = crear_task_manager(db)
        tareas_caducadas = task_manager.get_expired_tasks()
        return tareas_caducadas

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def obtener_tarea(task_id: int):
    with base_datos.crea_sesion() as db:
        task_manager = crear_task_manager(db)
        tarea = task_manager.get_task(task_id)
        return tarea

@app.put("/tasks/{task_id}/completar", response_model=TaskResponse)
def marcar_completada(task_id: int):
    with base_datos.crea_sesion() as db:
        task_manager = crear_task_manager(db)
        tarea = task_manager.complete_task(task_id)
        return tarea

@app.delete("/tasks/{task_id}")
def eliminar_tarea(task_id: int):
    with base_datos.crea_sesion() as db:
        task_manager = crear_task_manager(db)
        task_manager.delete_task(task_id) # delete_task lanza excepción si no existe la tarea
        return Response(status_code=status.HTTP_200_OK)


@app.get("/")
def root():
    return {"message": "Task Management API"}
