#!/bin/bash

# ============================================================================
# Script de Inicialización y Configuración — Sistema Vivo Hexagonal
# ============================================================================

# Salir inmediatamente si algún comando falla
set -e

# Colores para salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

echo -e "${GREEN}🧬 Iniciando configuración del entorno del Sistema Vivo Hexagonal...${NC}\n"

# 1. Configurar variables de entorno
if [ ! -f .env ]; then
    echo -e "${YELLOW}[+] Creando archivo .env a partir de la plantilla...${NC}"
    cp .env.template .env
    echo -e "${GREEN}[✓] Archivo .env creado con éxito.${NC}"
    echo -e "${RED}[⚠️] IMPORTANTE: Abre el archivo '.env' y añade tus claves reales para GOOGLE_GEMINI_API_KEY y GROQ_API_KEY.${NC}\n"
else
    echo -e "${GREEN}[✓] El archivo .env ya existe.${NC}\n"
fi

# 2. Verificar dependencias del sistema
echo -e "${YELLOW}[+] Verificando requerimientos del sistema...${NC}"

if command -v docker >/dev/null 2>&1; then
    echo -e "${GREEN}[✓] Docker instalado. Versión: $(docker --version)${NC}"
else
    echo -e "${RED}[❌] Docker no está instalado. Por favor, instálalo antes de continuar.${NC}"
fi

if command -v docker-compose >/dev/null 2>&1; then
    echo -e "${GREEN}[✓] docker-compose instalado. Versión: $(docker-compose --version)${NC}"
elif docker compose version >/dev/null 2>&1; then
    echo -e "${GREEN}[✓] Docker Compose (v2 plugin) instalado.${NC}"
else
    echo -e "${RED}[❌] docker-compose no encontrado. Asegúrate de tener docker-compose disponible en tu terminal.${NC}"
fi
echo ""

# 3. Asignar permisos a scripts auxiliares
echo -e "${YELLOW}[+] Asignando permisos de ejecución a los scripts...${NC}"
chmod +x nethunter_access/conectar.sh || true
echo -e "${GREEN}[✓] Permisos configurados.${NC}\n"

echo -e "${GREEN}===================================================================="
echo -e "¡Configuración inicial completada!"
echo -e "Para levantar la infraestructura RAG ejecuta:"
echo -e "  docker-compose -f sincronizacion-obsidiane/docker-compose.rag.yml up -d"
echo -e "====================================================================${NC}"
