# 1. Usar una imagen oficial de Python ligera (Debian Linux)
FROM python:3.10-slim

# 2. Definir el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Instalar herramientas del sistema necesarias para compilar librerías
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copiar primero el archivo de dependencias (Aprovecha la caché de Docker)
COPY requirements.txt .

# 5. Instalar las librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar el resto del código y los datos procesados al contenedor
COPY src/ /app/src/
COPY data/processed/ /app/data/processed/

# 7. Exponer el puerto por donde escuchará FastAPI
EXPOSE 8000

# 8. El comando exacto que levantará el servidor al encender el contenedor
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]