from fastapi import BackgroundTasks, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .excepciones import ContenidoInapropiadoError, TaskError
from .servicio_email import EmailService, EmailServiceSimulado

email_service: EmailService = EmailServiceSimulado()


async def task_error_handler(request: Request, exc: TaskError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})

async def contenido_inapropiado_handler(request: Request, exc: ContenidoInapropiadoError) -> JSONResponse:
    """Responde con el error y, después de enviar la respuesta, avisa por email con la IP del cliente."""
    ip = request.client.host if request.client else "desconocida"
    background_tasks = BackgroundTasks()
    background_tasks.add_task(email_service.enviar_aviso_palabrota, ip, exc.campo)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
        background=background_tasks,
    )

async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Responde 400 en vez del 422 de FastAPI cuando el body, la ruta o la query no son válidos."""
    errores = [
        {"campo": ".".join(str(parte) for parte in error["loc"]), "mensaje": error["msg"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Datos de entrada no válidos", "errores": errores},
    )

def registrar_manejadores(app: FastAPI) -> None:
    """Asocia cada excepción con la función que construye su respuesta HTTP."""
    # Starlette elige el manejador de la clase más cercana a la de la excepción:
    # ContenidoInapropiadoError usa el suyo, y el resto de subclases de TaskError el genérico.
    app.add_exception_handler(ContenidoInapropiadoError, contenido_inapropiado_handler)
    app.add_exception_handler(TaskError, task_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
