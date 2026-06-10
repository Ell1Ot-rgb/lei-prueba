FROM python:3.11-slim

# Evitar prompts de interactividad
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requerimientos e instalar
COPY deploy_docker/requirements_lite.txt .
RUN pip install --no-cache-dir -r requirements_lite.txt

# Copiar el sistema biológico completo
COPY . .

# Variables de entorno por defecto
ENV BIO_DIGITAL_HMAC_KEY="7f8e9d0a1b2c3d4e5f6g7h8i9j0k1l2m"
ENV PYTHONPATH="/app/antigravity-connect/sistema biologico/sistema_terminado/interfaces:/app/antigravity-connect/sistema biologico/sistema_terminado"

# Comando por defecto: Ejecutar el test global para verificar integridad al arrancar
CMD ["python", "global_system_check.py"]
