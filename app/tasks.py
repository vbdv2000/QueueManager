import os
from celery import Celery
from dotenv import load_dotenv
import time
import logging

# Cargar variables de entorno (necesario para el worker)
load_dotenv()

# Configuración del logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Añadir un handler para que se muestre en la consola
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Inicializar Celery App usando las variables de entorno
celery_app = Celery(
    "my_celery_app",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
)

# Configuración adicional para Celery
celery_app.conf.update(
    task_track_started=True,
    # AÑADIR ESTA LÍNEA para asegurar que se envían los eventos intermedios al broker
    worker_send_task_events=True,
    # MÁS IMPORTANTE: Habilitar la monitorización de eventos en el worker.
    # Esta opción es fundamental y a veces soluciona problemas de visibilidad en Flower.
    worker_hijack_root_logger=False,  # Opcional: previene que Celery tome el control del logger raíz.
    # ---
    send_task_events=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Madrid",
    enable_utc=True,
)


@celery_app.task(name="tasks.process_data")
def process_data(data: dict):
    """
    Simula una tarea de procesamiento pesado.
    """
    task_id = process_data.request.id
    logger.info(f"[{task_id}] Tarea de procesamiento iniciada con datos: {data}")

    # Simulación de un trabajo que tarda 10 segundos
    time.sleep(10)

    result_message = f"[{task_id}] Datos {data.get('id', 'N/A')} procesados con éxito después de 10 segundos."
    logger.info(result_message)

    return {"status": "completed", "message": result_message}
