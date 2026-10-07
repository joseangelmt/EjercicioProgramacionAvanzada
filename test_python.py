import requests
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000"
TAREA_TEST = {"titulo": "Estudiar", "contenido": "FastAPI", "deadline": "2026-12-31"}

def test_crear_tarea(titulo: str, contenido: str, deadline: str) -> int:
    """POST /tasks: Creamos una tarea. El servidor debe devolver 201 (Created) y la tarea creada con su id asignado."""
    datos = {"titulo": titulo, "contenido": contenido, "deadline": deadline}
    respuesta = requests.post(f"{BASE_URL}/tasks", json=datos)

    assert respuesta.status_code == 201, f"Se esperaba 201 y se recibió {respuesta.status_code}"
    tarea = respuesta.json()
    assert tarea["titulo"] == titulo
    assert tarea["contenido"] == contenido
    assert tarea["completada"] is False
    assert tarea["deadline"] == deadline
    return tarea["id"]

def test_obtener_tarea(task_id: int):
    """GET /tasks/{id}: Obtenemos una tarea por su ID. El servidor debe devolver 200 con los datos guardados, y 404 si el id no existe."""
    respuesta = requests.get(f"{BASE_URL}/tasks/{task_id}")
    assert respuesta.status_code == 200, f"Se esperaba 200 y se recibió {respuesta.status_code}"

    tarea = respuesta.json()
    assert tarea["id"] == task_id

    # Comprobamos que los datos de la tarea coinciden con los que enviamos al crearla
    for campo, valor in TAREA_TEST.items():
        assert tarea[campo] == valor, f"{campo}: se esperaba {valor} y se recibió {tarea[campo]}"

    assert tarea["completada"] is False
    assert "fecha_creacion" in tarea

    # Un id que no existe tiene que dar 404.
    respuesta = requests.get(f"{BASE_URL}/tasks/1234567890")
    assert respuesta.status_code == 404, f"Se esperaba 404 y se recibió {respuesta.status_code}"

def test_marcar_completada(task_id: int):
    """PUT /tasks/{id}/completar: Devuelve 200 con completada=True, y 404 si el id no existe."""
    respuesta = requests.put(f"{BASE_URL}/tasks/{task_id}/completar")
    assert respuesta.status_code == 200, f"Se esperaba 200 y se recibió {respuesta.status_code}"

    tarea = respuesta.json()
    assert tarea["id"] == task_id
    assert tarea["completada"] is True, f"completada: se esperaba True y se recibió {tarea['completada']}"

    # Hacemos un GET para comprobar que el cambio se ha guardado
    respuesta = requests.get(f"{BASE_URL}/tasks/{task_id}")
    assert respuesta.json()["completada"] is True, "El GET posterior no devuelve la tarea completada"

    # PUT es idempotente: repetir la petición da el mismo resultado.
    respuesta = requests.put(f"{BASE_URL}/tasks/{task_id}/completar")
    assert respuesta.status_code == 200, f"Repetición: se esperaba 200 y se recibió {respuesta.status_code}"
    assert respuesta.json()["completada"] is True

    # Un id que no existe tiene que dar 404.
    respuesta = requests.put(f"{BASE_URL}/tasks/0/completar")
    assert respuesta.status_code == 404, f"Se esperaba 404 y se recibió {respuesta.status_code}"

def test_obtener_tareas_caducadas():
    """GET /tasks/caducadas: Devuelve 200 con las tareas cuyo deadline es anterior a hoy, y ninguna otra."""
    
    # Creamos una tarea a cada lado del límite: vencida ayer, vence hoy (todavía no caducada) y vence mañana.
    hoy = date.today()
    id_caducada = test_crear_tarea("Caducada ayer", "Prueba de caducadas", (hoy - timedelta(days=1)).isoformat())
    id_hoy = test_crear_tarea("Vence hoy", "Prueba de caducadas", hoy.isoformat())
    id_mañana = test_crear_tarea("Vence mañana", "Prueba de caducadas", (hoy + timedelta(days=1)).isoformat())

    respuesta = requests.get(f"{BASE_URL}/tasks/caducadas")
    assert respuesta.status_code == 200, f"Se esperaba 200 y se recibió {respuesta.status_code}"

    tareas = respuesta.json()
    assert isinstance(tareas, list), f"Se esperaba una lista y se recibió {type(tareas).__name__}"

    ids = {tarea["id"] for tarea in tareas} # set comprehension con los ids de las tareas caducadas

    assert id_caducada in ids, "La tarea caducada ayer no aparece en /tasks/caducadas"
    assert id_hoy not in ids, "Una tarea que caduca hoy todavía no está caducada"
    assert id_mañana not in ids, "La tarea que caduca mañana aparece en /tasks/caducadas"

def test_datos_incorrectos():
    """Peticiones con datos no válidos: el servidor debe devolver 400 y el detalle de los errores."""
    casos = {
        "Título vacío": {"titulo": "", "contenido": "FastAPI", "deadline": "2026-12-31"},
        "Falta el contenido": {"titulo": "Estudiar", "deadline": "2026-12-31"},
        "Fecha con formato incorrecto": {"titulo": "Estudiar", "contenido": "FastAPI", "deadline": "31/12/2026"},
        "Fecha inexistente": {"titulo": "Estudiar", "contenido": "FastAPI", "deadline": "2026-02-30"},
    }
    for descripcion, datos in casos.items():
        respuesta = requests.post(f"{BASE_URL}/tasks", json=datos)
        assert respuesta.status_code == 400, f"{descripcion}: se esperaba 400 y se recibió {respuesta.status_code}"
        assert len(respuesta.json()["errores"]) > 0, f"{descripcion}: la respuesta no detalla los errores"

    # Un id que no es un número en la URL también es un dato incorrecto.
    respuesta = requests.get(f"{BASE_URL}/tasks/abc")
    assert respuesta.status_code == 400, f"id no numérico: se esperaba 400 y se recibió {respuesta.status_code}"

def test_contenido_inapropiado():
    """POST /tasks con palabrotas: el servidor debe devolver 400 indicando el campo, y no crear la tarea."""
    casos = {
        "titulo": {"titulo": "No seas tonto", "contenido": "Prueba", "deadline": "2026-12-31"},
        "contenido": {"titulo": "Prueba", "contenido": "No seas tonto", "deadline": "2026-12-31"},
    }
    for campo, datos in casos.items():
        respuesta = requests.post(f"{BASE_URL}/tasks", json=datos)
        assert respuesta.status_code == 400, f"{campo}: se esperaba 400 y se recibió {respuesta.status_code}"
        assert campo in respuesta.json()["detail"], f"{campo}: el mensaje no indica el campo: {respuesta.json()}"

def test_eliminar_tarea():
    """DELETE /tasks/{id}: devuelve 200 si ha podido eliminar la tarea o 404 si la tarea no existe."""
    task_id = test_crear_tarea("Para eliminar", "Prueba de DELETE", "2026-12-31")

    respuesta = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    assert respuesta.status_code == 200, f"Se esperaba 200 y se recibió {respuesta.status_code}"

    # La tarea ya no existe: un segundo DELETE da 404.
    respuesta = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    assert respuesta.status_code == 404, f"Segundo DELETE: se esperaba 404 y se recibió {respuesta.status_code}"

if __name__ == "__main__":
    print("Ejecutando tests...")

    print("Test: Crear tarea")
    id_tarea = test_crear_tarea(TAREA_TEST["titulo"], TAREA_TEST["contenido"], TAREA_TEST["deadline"])
    print(f"Tarea creada con ID: {id_tarea}")

    # Obtener va antes que completar porque comprueba que la tarea todavía no está completada.
    print("Test: Obtener tarea")
    test_obtener_tarea(id_tarea)

    print("Test: Marcar tarea como completada")
    test_marcar_completada(id_tarea)

    print("Test: Obtener tareas caducadas")
    test_obtener_tareas_caducadas()

    print("Test: Datos incorrectos")
    test_datos_incorrectos()

    print("Test: Contenido inapropiado")
    test_contenido_inapropiado()

    print("Test: Eliminar tarea")
    test_eliminar_tarea()

    print("Tests completados")
