# Dockerfile para Sistema YO Estructural
# =====================================

FROM python:3.11-slim

# Metadatos
LABEL maintainer="Sistema YO Estructural"
LABEL version="3.0"
LABEL description="Sistema de procesamiento fenomenológico automatizado"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Crear usuario no-root
RUN groupadd -r yoestructural && useradd -r -g yoestructural yoestructural

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs_sistema procesado entrada_bruta export_neo4j && \
    chown -R yoestructural:yoestructural /app

# Cambiar a usuario no-root
USER yoestructural

# Exponer puerto
EXPOSE 8000

# Comando de salud
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]