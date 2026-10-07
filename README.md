# Task Management API

API REST del ejercicio de Programación Avanzada en FastAPI para gestionar una lista de tareas, con persistencia en SQLite mediante SQLAlchemy.

## Ejecución

Desde la carpeta raíz del proyecto, con el entorno virtual activado:

```powershell
pip install -r requirements.txt
uvicorn api.main:app --reload
```

En otra terminal, ejecuta las pruebas:

```powershell
python test_python.py
```

## Endpoints

| Método | Ruta | Descripción | Respuestas |
|---|---|---|---|
| `POST` | `/tasks` | Crea una tarea | 201, 400 |
| `GET` | `/tasks/{task_id}` | Devuelve una tarea | 200, 404 |
| `PUT` | `/tasks/{task_id}/completar` | Marca una tarea como completada | 200, 404 |
| `GET` | `/tasks/caducadas` | Lista las tareas con `deadline` anterior a hoy | 200 |
| `DELETE` | `/tasks/{task_id}` | Elimina una tarea | 200, 404 |

Body de `POST /tasks`:

```json
{ "titulo": "Estudiar", "contenido": "FastAPI", "deadline": "2026-12-31" }
```

- `POST` crea un recurso nuevo y responde 201.
- `PUT` se usa para completar porque es idempotente: repetir la petición deja la tarea igual.
- La API responde **400** si los datos no son válidos (FastAPI respondería 422) o si el título o el
  contenido contienen palabrotas, y **404** si la tarea no existe.

## Estructura del código

| Fichero | Contenido |
|---|---|
| `api/main.py` | Aplicación FastAPI y endpoints |
| `api/administrador_tareas.py` | `TaskManager`: lógica de negocio de las tareas |
| `api/base_datos.py` | `BaseDatos`: conexión con SQLite y creación de sesiones |
| `api/models.py` | `Task`: modelo de la tabla `tasks` |
| `api/dtos.py` | Modelos Pydantic de entrada y salida (`TaskCreate`, `TaskResponse`) |
| `api/excepciones.py` | `TaskError` y sus subclases, cada una con su código HTTP |
| `api/manejadores_errores.py` | Conversión de las excepciones en respuestas HTTP |
| `api/filtro_contenido.py` | `FiltroContenido`: detección de palabrotas |
| `api/servicio_email.py` | `EmailService` (abstracta) y `EmailServiceSimulado`: aviso por email de intentos con palabrotas |
| `test_python.py` | Pruebas de la API con `requests` |

## Añadidos

- **Método `DELETE`**: `DELETE /tasks/{task_id}` elimina una tarea. Responde 200 si la ha eliminado y 404
  si no existe.
- **Envío asíncrono de email cuando se detecta una palabrota**: cuando se rechaza una tarea por
  palabrotas, la API envía un aviso por email con la IP del cliente. El envío es simulado:
  `EmailServiceSimulado` espera 1 segundo y escribe el aviso en la consola del servidor. En un servicio
  real, la IP es un dato personal según el RGPD y habría que justificar su tratamiento.

  El aviso se envía con `BackgroundTasks`, pero no desde el endpoint `POST /tasks`, sino desde el
  manejador de `ContenidoInapropiadoError`. Cuando se detecta una palabrota, `TaskManager` lanza esa
  excepción, y las tareas que el endpoint hubiera añadido a su `BackgroundTasks` se descartarían. El
  manejador construye la respuesta 400 y le asocia un `BackgroundTasks` que ejecuta el método asíncrono
  `enviar_aviso_palabrota` después de enviar la respuesta, así que el aviso no la retrasa.

## Notas

- Las palabrotas se detectan con el paquete [spanlp](https://github.com/jfreddypuentes/spanlp). Si se
  detecta una palabrota en el título o en el contenido al crear una tarea, la API responde 400 y no crea
  la tarea.
- `test_python.py` usa `127.0.0.1` en lugar de `localhost`: en Windows, `localhost` se resuelve primero a
  IPv6 y cada petición tardaba unos 2 segundos más, porque uvicorn solo escucha en IPv4.
