
# QueueuManager

Este proyecto es una aplicación de procesamiento de tareas en segundo plano usando FastAPI, Celery, Redis y Flower, todo orquestado con Docker Compose.

## Componentes principales

- **FastAPI**: Servicio web para recibir peticiones y gestionar tareas.
- **Celery**: Sistema de cola para ejecutar tareas asíncronas.
- **Redis**: Broker y backend de resultados para Celery.
- **Flower**: Dashboard web para monitorear tareas de Celery.

## Estructura del proyecto

```
QueueuManager/
├── app/
│   ├── main.py         # API FastAPI
│   ├── tasks.py        # Definición de tareas Celery
│   └── .env            # Variables de entorno
├── requirements.txt    # Dependencias Python
├── Dockerfile          # Imagen base para los servicios
├── docker-compose.yml  # Orquestación de servicios
```

## Uso rápido

1. **Clona el repositorio y entra a la carpeta:**
    ```bash
    git clone <repo_url>
    cd QueueuManager
    ```

2. **Configura las variables de entorno:**
    Edita `app/.env` si necesitas cambiar los valores por defecto.

3. **Levanta todos los servicios:**
    ```bash
    docker-compose up --build
    ```

4. **Accede a los servicios:**
    - FastAPI: [http://localhost:8000](http://localhost:8000)
    - Flower (monitor Celery): [http://localhost:5555](http://localhost:5555)

## Clave para persistencia de tareas (Flower)

**Para que las tareas y el historial de Flower se mantengan incluso si se regenera el contenedor Docker, es fundamental el uso del volumen persistente `flower_db_volume`.**

Esto está definido en `docker-compose.yml`:

```yaml
volumes:
  flower_db_volume:
```

Y en el servicio `flower`:

```yaml
     volumes:
        - ./app:/app/app
        - flower_db_volume:/var/flower_data
     command: celery -A app.tasks flower ... --persistent=True --db=/var/flower_data/flower.db
```

**Así, la base de datos de Flower se guarda fuera del contenedor y no se pierde al reiniciar o reconstruir.**

## Notas adicionales

- Puedes modificar el código en `app/` y los cambios se reflejarán automáticamente si usas el volumen mapeado.
- Para producción, revisa la configuración de Celery y los parámetros de seguridad de Flower.

---

¡Listo! Ahora tienes una aplicación de gestión de tareas asíncronas lista para usar y monitorear.

