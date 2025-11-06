import os
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv
import logging
import time

# Importamos la tarea que definimos en tasks.py
from .tasks import process_data

# Cargar variables de entorno
load_dotenv()

# Configuración del logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

app = FastAPI(
    title="Microservicio de Tareas Asíncronas",
    description="Backend que delega tareas pesadas a Celery/Redis.",
)


# Definición del modelo de datos para la petición POST
class DataPayload(BaseModel):
    id: int
    data: str
    priority: str = "medium"


@app.get("/")
async def health_check():
    """Endpoint de verificación de salud."""
    return {"status": "ok", "service": "fastapi"}


@app.post("/process")
async def start_processing(payload: DataPayload):
    """
    Recibe una petición POST, encola una tarea en Celery y devuelve
    una respuesta inmediata.
    """
    # Convertir el payload a diccionario
    data_dict = payload.model_dump()

    # 1. Enviar la tarea a la cola de Celery de forma asíncrona (.delay())
    # Esto devuelve inmediatamente un objeto AsyncResult
    task_result = process_data.delay(data_dict)

    # 2. Registrar el inicio
    logger.info(
        f"Petición POST recibida para ID {payload.id}. Tarea encolada con ID: {task_result.id}"
    )

    # 3. Devolver una respuesta inmediata al cliente (Desacoplamiento)
    return {
        "status": "Task Accepted",
        "message": "El procesamiento ha sido iniciado en segundo plano.",
        "task_id": task_result.id,
        "monitor_url": f"http://localhost:5555/task/{task_result.id}",  # Flower estará en el puerto 5555
    }


# Endpoint opcional para verificar el estado de una tarea
@app.get("/status/{task_id}")
def get_task_status(task_id: str):
    """
    Verifica el estado actual de una tarea Celery.
    """
    # Obtener el objeto de resultado de Celery
    task = process_data.AsyncResult(task_id)

    if task.state == "PENDING":
        response = {
            "state": task.state,
            "status": "La tarea está en cola o no ha sido encontrada.",
        }
    elif task.state != "FAILURE":
        response = {
            "state": task.state,
            "status": "Procesando...",
            "result": task.info,  # Contiene información sobre el progreso si se actualiza
        }
        if task.ready():
            response["result"] = (
                task.result
            )  # Contiene el resultado final si está listo
    else:
        # Algo salió mal en el worker
        response = {
            "state": task.state,
            "status": str(task.info),  # Excepción y traceback
        }

    return response
