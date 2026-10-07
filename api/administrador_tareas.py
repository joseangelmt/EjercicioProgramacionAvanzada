from sqlalchemy.orm import Session
from datetime import date

from .filtro_contenido import FiltroContenido
from . import dtos
from .excepciones import ContenidoInapropiadoError, TaskNotFoundError
from .models import Task

class TaskManager:
    def __init__(self, db : Session, filtro_contenido: FiltroContenido):
        self.__db = db
        self.__filtro_contenido  = filtro_contenido

    def create_task(self, datos: dtos.TaskCreate) -> Task:
        for campo, texto in (("titulo", datos.titulo), ("contenido", datos.contenido)):
            if self.__filtro_contenido.contiene_palabrotas(texto):
                raise ContenidoInapropiadoError(campo)

        task = Task(titulo=datos.titulo, contenido=datos.contenido, deadline=datos.deadline)
        self.__db.add(task)
        self.__db.commit()
        # Refresca la instancia de la tarea para obtener el id generado automáticamente
        self.__db.refresh(task)
        return task

    def get_task(self, task_id: int) -> Task:
        task = self.__db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise TaskNotFoundError(task_id)
        return task

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        self.__db.delete(task)
        self.__db.commit()

    def complete_task(self, task_id: int) -> Task:
        task = self.get_task(task_id)
        task.completada = True
        self.__db.commit()
        self.__db.refresh(task)
        return task

    def get_expired_tasks(self) -> list[Task]:
        today = date.today()
        expired_tasks = self.__db.query(Task).filter(Task.deadline < today).all()
        return expired_tasks
