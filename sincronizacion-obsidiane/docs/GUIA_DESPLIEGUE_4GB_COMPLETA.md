# GUÍA DE DESPLIEGUE COMPLETA - SISTEMA 4GB RAM

## 📊 ARQUITECTURA DEL SISTEMA

```
┌─────────────────────────────────────────────────────────────┐
│                     RED LAN 192.168.1.0/24                  │
│                                                              │
│  ┌────────────────────┐         ┌─────────────────────┐    │
│  │ PC1: 192.168.1.35  │◄───────►│ PC2: 192.168.1.37   │    │
│  │                    │  LAN    │                     │    │
│  │ • 4GB DDR3 RAM     │         │ • Neo4j (Docker)    │    │
│  │ • 1.2GB disponible │         │   bolt://:7687      │    │
│  │ • Dual-core        │         │   http://:7474      │    │
│  │ • Cliente          │         │                     │    │
│  │                    │         │ • LightRAG (Docker) │    │
│  │ Ejecuta:           │         │   http://:8000      │    │
│  │ - NetworkX local   │         │                     │    │
│  │ - Convergencia     │         │ Credenciales:       │    │
│  │ - Análisis híbrido │         │ - user: neo4j       │    │
│  │                    │         │ - pass: fenomeno... │    │
│  └────────────────────┘         └─────────────────────┘    │
│                                                              │
│           Gateway: 192.168.1.1                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 PARTE 1: CONFIGURAR PC2 (SERVIDOR)

### Paso 1.1: Preparar Docker en PC2

```bash
# Conectar a PC2
ssh usuario@192.168.1.37

# Verificar Docker
docker --version
docker-compose --version

# Si no tiene Docker, instalar:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### Paso 1.2: Copiar archivos a PC2

Desde PC1:
```bash
# Copiar configuración Docker
scp docker-compose-PC2.yml usuario@192.168.1.37:~/fenomenologia/
scp Dockerfile.lightrag usuario@192.168.1.37:~/fenomenologia/

# Conectar a PC2
ssh usuario@192.168.1.37
cd ~/fenomenologia
```

### Paso 1.3: Iniciar servicios en PC2

```bash
# Renombrar archivo
mv docker-compose-PC2.yml docker-compose.yml

# Iniciar Neo4j + LightRAG
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f neo4j
docker-compose logs -f lightrag
```

### Paso 1.4: Verificar Neo4j

```bash
# Esperar 30 segundos para inicio completo
sleep 30

# Acceder a navegador Neo4j
# Abrir: http://192.168.1.37:7474
# Usuario: neo4j
# Password: fenomenologia2024

# Test desde terminal
docker exec neo4j_fenomenologia cypher-shell \
  -u neo4j \
  -p fenomenologia2024 \
  "RETURN 'OK' AS status"
```

### Paso 1.5: Configurar firewall PC2 (si es necesario)

```bash
# Permitir conexiones desde PC1
sudo ufw allow from 192.168.1.35 to any port 7687 proto tcp  # Neo4j Bolt
sudo ufw allow from 192.168.1.35 to any port 7474 proto tcp  # Neo4j HTTP
sudo ufw allow from 192.168.1.35 to any port 8000 proto tcp  # LightRAG

# Verificar reglas
sudo ufw status
```

---

## 💻 PARTE 2: CONFIGURAR PC1 (CLIENTE 4GB)

### Paso 2.1: Verificar recursos disponibles

```bash
# Ver memoria disponible
free -h

# Debería mostrar:
# - Total: ~4GB
# - Disponible: ~1.2GB
# - En uso: ~2.3GB

# Si hay menos de 1GB disponible, cerrar aplicaciones:
# - Navegadores
# - Editores pesados
# - Servicios innecesarios
```

### Paso 2.2: Instalar dependencias

```bash
cd /workspaces/-...Raiz-Dasein/YO\ estructural/

# Ejecutar script de instalación
chmod +x instalar_4gb_optimizado.sh
./instalar_4gb_optimizado.sh

# Debería tardar 5-10 minutos
# Descarga modelos (~100MB total)
```

### Paso 2.3: Test de conectividad a PC2

```bash
# Activar entorno
source venv_4gb/bin/activate

# Test Neo4j
python3 << 'EOF'
from neo4j import GraphDatabase
driver = GraphDatabase.driver(
    "bolt://192.168.1.37:7687",
    auth=("neo4j", "fenomenologia2024")
)
with driver.session() as session:
    result = session.run("RETURN 'Conexión OK' AS msg")
    print(result.single()["msg"])
driver.close()
EOF

# Test LightRAG
curl http://192.168.1.37:8000/health
```

### Paso 2.4: Verificar configuración

```bash
# Ver configuración cargada
python3 << 'EOF'
import yaml
with open('config_4gb_optimizado.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
print(f"Neo4j URL: {config['neo4j']['bolt_url']}")
print(f"Batch size: {config['clustering']['batch_size']}")
print(f"Max memory: {config['optimization']['max_memory_mb']}MB")
print(f"Workers: {config['optimization']['max_workers']}")
EOF
```

---

## 🧪 PARTE 3: PRUEBAS DEL SISTEMA

### Paso 3.1: Prueba básica de convergencia

```bash
# En PC1, con entorno activado
python3 procesadores/analizador_convergencia_optimizado.py
```

**Salida esperada:**
```
=== Analizador de Convergencia Fenomenológica (Optimizado para 4GB RAM) ===
Cargando analizador para 4GB RAM...
RAM disponible: ~1.2GB de 4GB total
Configuración cargada desde: config_4gb_optimizado.yaml

Procesando 10 conceptos de prueba...
Batch 1/10: [====================] 100%
⚠ RAM: 75% usado (800MB de 1024MB) - Limpiando caché...
Batch 2/10: [====================] 100%
...
✓ Convergencia detectada: 99.2% certeza
```

### Paso 3.2: Monitor de recursos

En una terminal separada:
```bash
# Ver uso de RAM en tiempo real
watch -n 2 'free -h'

# Ver procesos Python
watch -n 2 'ps aux | grep python | grep -v grep'
```

### Paso 3.3: Verificar datos en Neo4j

```bash
# Desde PC1
python3 << 'EOF'
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://192.168.1.37:7687",
    auth=("neo4j", "fenomenologia2024")
)

with driver.session() as session:
    # Contar nodos
    result = session.run("MATCH (n) RETURN count(n) AS total")
    print(f"Nodos en Neo4j: {result.single()['total']}")
    
    # Ver tipos de nodos
    result = session.run("""
        MATCH (n)
        RETURN labels(n) AS tipo, count(n) AS cantidad
        ORDER BY cantidad DESC
    """)
    for record in result:
        print(f"  {record['tipo']}: {record['cantidad']}")

driver.close()
EOF
```

---

## 📈 PARTE 4: INTEGRACIÓN CON SISTEMA PRINCIPAL

### Paso 4.1: Modificar sistema_principal_v2.py

```python
# Agregar al inicio de sistema_principal_v2.py

import sys
sys.path.append('./procesadores')

from analizador_convergencia_optimizado import AnalizadorConvergenciaOptimizado

# Inicializar analizador
analizador_convergencia = AnalizadorConvergenciaOptimizado(
    config_path="./config_4gb_optimizado.yaml"
)

# Usar en ciclo principal
def procesar_entrada_fenomenologica(texto_entrada):
    """Analiza entrada y detecta máximo relacional"""
    
    # ... procesamiento existente ...
    
    # NUEVO: Detectar convergencia
    resultado_convergencia = analizador_convergencia.analizar_convergencia(
        conceptos=conceptos_extraidos,
        rutas=rutas_fenomenologicas,
        batch_size=10  # MAX 10 en 4GB RAM
    )
    
    if resultado_convergencia['convergencia_detectada']:
        certeza = resultado_convergencia['certeza_definicion']
        maximo_relacional = resultado_convergencia['concepto_central']
        
        print(f"✓ MÁXIMO RELACIONAL detectado: {maximo_relacional}")
        print(f"  Certeza definitoria: {certeza:.2f}%")
        
        # Guardar en Neo4j
        analizador_convergencia.guardar_resultado_neo4j(
            resultado_convergencia
        )
    
    return resultado_convergencia
```

### Paso 4.2: Configurar límites de memoria

```python
# Agregar al inicio de sistema_principal_v2.py

import resource
import psutil

# Limitar uso de memoria a 1GB
def configurar_limites_memoria():
    """Limita memoria del proceso a 1GB (4GB RAM total)"""
    try:
        # Soft limit: 1GB
        # Hard limit: 1.2GB
        soft_limit = 1024 * 1024 * 1024  # 1GB
        hard_limit = int(1.2 * 1024 * 1024 * 1024)  # 1.2GB
        
        resource.setrlimit(
            resource.RLIMIT_AS,
            (soft_limit, hard_limit)
        )
        print(f"✓ Límite de memoria configurado: 1GB")
        
    except Exception as e:
        print(f"⚠ No se pudo limitar memoria: {e}")

# Llamar al inicio
configurar_limites_memoria()
```

---

## 🔍 PARTE 5: MONITOREO Y MANTENIMIENTO

### Monitoreo continuo

```bash
# Terminal 1: Sistema principal
source venv_4gb/bin/activate
python3 sistema_principal_v2.py

# Terminal 2: Monitor de RAM
watch -n 2 'free -h && echo "---" && ps aux | grep python | head -5'

# Terminal 3: Logs de Neo4j (en PC2)
ssh usuario@192.168.1.37
docker logs -f neo4j_fenomenologia
```

### Mantenimiento Neo4j

```bash
# En PC2, conectar a Neo4j shell
docker exec -it neo4j_fenomenologia cypher-shell \
  -u neo4j \
  -p fenomenologia2024

# Verificar índices
CALL db.indexes();

# Limpiar datos antiguos (si es necesario)
MATCH (n:ConceptoTemporalViejo)
WHERE n.timestamp < datetime() - duration({days: 7})
DETACH DELETE n;

# Salir
:exit
```

### Backup de datos

```bash
# En PC2, crear backup
docker exec neo4j_fenomenologia neo4j-admin database dump \
  --to-path=/backups \
  neo4j

# Copiar a PC1
scp usuario@192.168.1.37:~/fenomenologia/backups/* ./backups/
```

---

## 🚨 TROUBLESHOOTING

### Problema: "Out of Memory" en PC1

**Solución 1: Reducir batch size**
```yaml
# En config_4gb_optimizado.yaml
clustering:
  batch_size: 50  # Reducir de 100 a 50
```

**Solución 2: Limpiar caché**
```bash
# Eliminar caché
rm -rf cache_4gb/*

# Reiniciar Python
pkill -9 python3
```

**Solución 3: Usar perfil minimal**
```python
# En código, usar perfil minimal
analizador = AnalizadorConvergenciaOptimizado(
    config_path="./config_4gb_optimizado.yaml",
    perfil="minimal"  # En vez de "standard"
)
```

### Problema: No conecta a Neo4j

**Verificar conectividad:**
```bash
# Desde PC1
telnet 192.168.1.37 7687

# Si falla, verificar firewall PC2
ssh usuario@192.168.1.37
sudo ufw status
```

**Verificar credenciales:**
```bash
# Test directo
python3 << 'EOF'
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver(
        "bolt://192.168.1.37:7687",
        auth=("neo4j", "fenomenologia2024")
    )
    driver.verify_connectivity()
    print("✓ Conexión exitosa")
except Exception as e:
    print(f"✗ Error: {e}")
EOF
```

### Problema: LightRAG no responde

```bash
# Verificar contenedor
ssh usuario@192.168.1.37
docker ps | grep lightrag

# Ver logs
docker logs lightrag_semantic_refinement

# Reiniciar servicio
docker-compose restart lightrag
```

---

## 📊 MÉTRICAS DE RENDIMIENTO ESPERADAS

### En PC1 (4GB RAM):

| Operación | Tiempo | RAM usada | Notas |
|-----------|--------|-----------|-------|
| Inicialización | 10-15s | 200MB | Carga de modelos |
| Batch 10 conceptos | 2-3s | 300MB | Sin cache |
| Batch 10 conceptos | 1-2s | 250MB | Con cache |
| Convergencia completa | 30-60s | 800MB | 100 conceptos |
| Guardado Neo4j | 1-2s | 100MB | Por red LAN |

### Límites seguros:

- **Batch size máximo:** 10 conceptos
- **Conceptos totales:** Hasta 500 (en lotes)
- **Uso RAM máximo:** 800MB (80% de 1GB límite)
- **Frecuencia GC:** Cada 3 batches

---

## ✅ CHECKLIST DE DESPLIEGUE

### PC2 (Servidor):
- [ ] Docker y docker-compose instalados
- [ ] Archivos `docker-compose.yml` y `Dockerfile.lightrag` copiados
- [ ] Servicios iniciados: `docker-compose up -d`
- [ ] Neo4j accesible en http://192.168.1.37:7474
- [ ] LightRAG accesible en http://192.168.1.37:8000
- [ ] Firewall configurado (puertos 7687, 7474, 8000)

### PC1 (Cliente):
- [ ] RAM disponible > 1GB verificado
- [ ] Script `instalar_4gb_optimizado.sh` ejecutado
- [ ] Entorno virtual `venv_4gb` creado y activado
- [ ] Conectividad a Neo4j verificada
- [ ] Archivo `config_4gb_optimizado.yaml` presente
- [ ] Prueba básica de convergencia exitosa

### Sistema integrado:
- [ ] `sistema_principal_v2.py` modificado
- [ ] Límites de memoria configurados
- [ ] Monitoreo de RAM activo
- [ ] Backups configurados (opcional)

---

## 📞 COMANDOS DE REFERENCIA RÁPIDA

```bash
# PC1: Activar entorno
source venv_4gb/bin/activate

# PC1: Ejecutar análisis
python3 procesadores/analizador_convergencia_optimizado.py

# PC1: Monitor RAM
watch -n 2 'free -h'

# PC2: Estado servicios
docker-compose ps

# PC2: Logs Neo4j
docker logs -f neo4j_fenomenologia

# PC2: Logs LightRAG
docker logs -f lightrag_semantic_refinement

# PC1: Test conectividad
telnet 192.168.1.37 7687
curl http://192.168.1.37:8000/health
```

---

**Última actualización:** Sistema optimizado para 4GB RAM DDR3 @ 1334MHz  
**Red:** 192.168.1.0/24 (PC1: .35, PC2: .37)  
**Credenciales:** neo4j / fenomenologia2024
