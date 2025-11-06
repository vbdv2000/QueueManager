# Usar una imagen base de Python oficial
FROM python:3.11-slim

# Establecer la carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de dependencias e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY app/ app/

# Comando por defecto para el web service (FastAPI)
# Este comando será sobrescrito para el servicio 'worker'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]