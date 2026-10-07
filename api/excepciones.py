# Implementamos una jerarquía de errores para aplicar polimorfismo en el manejo de errores.
from fastapi import status


class TaskError(Exception):
    """Clase base para errores relacionados con tareas."""

    # declaramos un código de error como atributo de clase 
    # (es como un atributo estático, pero permite que las subclases lo sobrescriban)
    status_code: int = status.HTTP_400_BAD_REQUEST 

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class TaskNotFoundError(TaskError):
    status_code: int = status.HTTP_404_NOT_FOUND

    def __init__(self, task_id: int):
        super().__init__(f"No existe la tarea con id {task_id}")
        self.task_id = task_id

class ContenidoInapropiadoError(TaskError):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, campo: str):
        super().__init__(f"El campo '{campo}' contiene palabrotas")
        self.campo = campo