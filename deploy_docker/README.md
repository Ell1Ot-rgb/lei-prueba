# 🐳 Despliegue Docker: Organismo Vivo v100

Este entorno permite ejecutar el sistema biológico de forma aislada y segura, incluyendo una base de datos Neo4j para el grafo conceptual.

## 🚀 Cómo empezar

1. **Construir e iniciar los contenedores:**
   ```bash
   cd deploy_docker
   docker-compose up -d --build
   ```

2. **Verificar que el sistema está vivo:**
   ```bash
   docker ps
   ```

3. **Ejecutar el Diagnóstico Global dentro del contenedor:**
   ```bash
   docker exec -it organismo_vivo_v100 python global_system_check.py
   ```

4. **Ejecutar el Stress Test (300 eventos):**
   ```bash
   docker exec -it organismo_vivo_v100 python stress_test_biologico.py
   ```

## 🏗️ Arquitectura del Entorno
- **Contenedor `organismo`**: Basado en Python 3.11-slim. Contiene toda la lógica fenomenológica, cognitiva y biológica.
- **Contenedor `neo4j`**: Base de datos de grafos para la persistencia del conocimiento emergente.
- **Red `bio_net`**: Red aislada para la comunicación interna entre el cerebro y su base de datos.

## ⚙️ Configuración
- El sistema utiliza la versión **Lite** de los componentes para asegurar estabilidad en cualquier entorno Docker estándar.
- Las variables de entorno críticas (HMAC_KEY, DB_URL) están pre-configuradas en el archivo `docker-compose.yml`.
