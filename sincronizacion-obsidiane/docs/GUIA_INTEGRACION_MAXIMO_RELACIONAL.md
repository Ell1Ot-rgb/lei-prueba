# 🔗 Guía de Integración: Máximo Relacional Definicional en sistema_principal_v2.py

## Índice
1. [Resumen de archivos creados](#resumen)
2. [Cómo integrar en sistema_principal_v2.py](#integración)
3. [Flujo de ejecución](#flujo)
4. [Ejemplos de código](#ejemplos)
5. [Checklist de implementación](#checklist)

---

## 📋 Resumen de archivos creados {#resumen}

| Archivo | Propósito | Ubicación |
|---------|-----------|-----------|
| `config_dualcore_optimizado.yaml` | Configuración centralizada para todos los parámetros | Raíz |
| `analizador_convergencia_optimizado.py` | Detecta convergencia de 5 rutas a 99%+ | `procesadores/` |
| `analizador_maximo_relacional_hibrido.py` | Hybrid NetworkX + Neo4j GDS | `procesadores/` |
| `requirements_dualcore.txt` | Dependencias optimizadas para dual-core | Raíz |

---

## 🔌 Cómo integrar en sistema_principal_v2.py {#integración}

### **Paso A: Agregar imports al inicio del archivo**

```python
# Agregado a sistema_principal_v2.py

# ============================================================
# NUEVOS IMPORTS PARA MÁXIMO RELACIONAL DEFINICIONAL
# ============================================================
from procesadores.analizador_convergencia_optimizado import (
    AnalizadorConvergenciaOptimizado,
    ResultadoConvergencia
)

from procesadores.analizador_maximo_relacional_hibrido import (
    OrquestadorComputacionHibrida,
    ResultadoAnalisiscentralizado
)

import asyncio
import yaml
```

### **Paso B: Crear método en clase principal (ej: `SistemaPrincipal`)**

```python
class SistemaPrincipal:
    """Sistema principal con soporte para máximo relacional"""
    
    def __init__(self, config_path: str = "./config_dualcore_optimizado.yaml"):
        # ... inicialización existente ...
        
        # NUEVO: Inicializar analizadores
        self.analizador_convergencia = AnalizadorConvergenciaOptimizado(config_path)
        self.orquestador_hibrido = OrquestadorComputacionHibrida(config_path)
        self.config_path = config_path
        
        logger.info("[INIT] Máximo relacional definicional cargado")
    
    # ============================================================
    # MÉTODO 1: Detectar máximo relacional definicional
    # ============================================================
    def detectar_maximo_relacional_concepto(self, 
                                           concepto: str,
                                           rutas_definiciones: Dict[str, str]) -> bool:
        """
        Detecta si un concepto alcanza MÁXIMO RELACIONAL DEFINICIONAL.
        
        ENTRADA:
        - concepto: "SOPORTE"
        - rutas_definiciones: {
            "Física": "Material que...",
            "Ergonómica": "Superficie que...",
            "Arquitectónica": "Elemento que...",
            "Lógica": "Entidad que...",
            "Ontológica": "Razón que..."
          }
        
        SALIDA:
        - bool: True si certeza >= 0.99
        
        USO:
        ```
        es_maximo = sistema.detectar_maximo_relacional_concepto(
            "SOPORTE",
            rutas_soporte
        )
        ```
        """
        logger.info(f"[MÁXIMO_REL] Analizando concepto: {concepto}")
        
        # Analizar convergencia
        resultado = self.analizador_convergencia.analizar_concepto(
            concepto,
            rutas_definiciones
        )
        
        # Guardar en BD (NUEVO)
        if resultado.es_maximo_relacional:
            self._guardar_maximo_relacional_bd(
                concepto=concepto,
                certeza=resultado.certeza_combinada,
                rutas=resultado.rutas
            )
            logger.info(f"[MÁXIMO_REL] ✓ {concepto} es máximo relacional ({resultado.certeza_combinada:.6f})")
        
        return resultado.es_maximo_relacional
    
    # ============================================================
    # MÉTODO 2: Procesar lote de conceptos
    # ============================================================
    def procesar_lote_maximo_relacional(self,
                                       conceptos_rutas: Dict[str, Dict[str, str]],
                                       batch_size: int = 10) -> List[ResultadoConvergencia]:
        """
        Procesar múltiples conceptos en lotes (OPTIMIZACIÓN para dual-core).
        
        ENTRADA:
        - conceptos_rutas: {
            "SOPORTE": {"Física": "...", "Ergonómica": "...", ...},
            "ESTRUCTURA": {...},
            "RELACIÓN": {...}
          }
        - batch_size: número de conceptos por lote (default 10)
        
        SALIDA:
        - Lista de ResultadoConvergencia
        
        USO:
        ```
        conceptos = {
            "SOPORTE": rutas_soporte,
            "ESTRUCTURA": rutas_estructura,
            "RELACIÓN": rutas_relacion
        }
        resultados = sistema.procesar_lote_maximo_relacional(conceptos)
        ```
        """
        logger.info(f"[MÁXIMO_REL] Procesando lote de {len(conceptos_rutas)} conceptos")
        
        resultados = self.analizador_convergencia.procesar_lote_conceptos(
            conceptos_rutas,
            batch_size=batch_size
        )
        
        # Guardar todos los que sean máximos relacionales
        for resultado in resultados:
            if resultado.es_maximo_relacional:
                self._guardar_maximo_relacional_bd(
                    concepto=resultado.concepto,
                    certeza=resultado.certeza_combinada,
                    rutas=resultado.rutas
                )
        
        return resultados
    
    # ============================================================
    # MÉTODO 3: Análisis híbrido del grafo de conceptos
    # ============================================================
    async def analizar_grafo_hibrido(self,
                                     nodos: List[Dict],
                                     arcos: List[Tuple],
                                     neo4j_disponible: bool = True) -> ResultadoAnalisiscentralizado:
        """
        Análisis híbrido (NetworkX local + Neo4j GDS remoto).
        
        ENTRADA:
        - nodos: lista de nodos del grafo
        - arcos: lista de arcos (origen, destino)
        - neo4j_disponible: si Neo4j está disponible
        
        SALIDA:
        - ResultadoAnalisiscentralizado con top 10 nodos
        
        USO:
        ```
        # Obtener nodos y arcos del grafo de conceptos
        nodos = self.neo4j_db.obtener_nodos_grafo()
        arcos = self.neo4j_db.obtener_arcos_grafo()
        
        resultado = await sistema.analizar_grafo_hibrido(
            nodos, arcos,
            neo4j_disponible=True
        )
        ```
        """
        logger.info("[HIBRIDO] Iniciando análisis híbrido...")
        
        resultado = await self.orquestador_hibrido.analizar_hibrido(
            nodos=nodos,
            arcos=arcos,
            nombre_grafo_gds="concepto_grafo_v2",
            neo4j_disponible=neo4j_disponible
        )
        
        logger.info(f"[HIBRIDO] ✓ Análisis completado ({resultado.optimizacion_usado})")
        
        return resultado
    
    # ============================================================
    # MÉTODO AUXILIAR: Guardar máximo relacional en BD
    # ============================================================
    def _guardar_maximo_relacional_bd(self,
                                      concepto: str,
                                      certeza: float,
                                      rutas: List):
        """Guardar concepto de máximo relacional en Neo4j"""
        
        # PSEUDO-CÓDIGO (adaptar a tu BD existente)
        query = """
        MERGE (m:MaximoRelacional {nombre: $concepto})
        SET m.certeza = $certeza,
            m.timestamp = datetime(),
            m.rutas = $rutas_json
        RETURN m
        """
        
        # Ejecutar query (usar tu cliente Neo4j existente)
        # self.neo4j_db.ejecutar_query(query, {...})
        
        logger.info(f"[BD] Máximo relacional guardado: {concepto}")
```

### **Paso C: Crear endpoint o comando CLI**

```python
# En sistema_principal_v2.py o en main.py

def cli_detectar_maximo_relacional():
    """CLI para detectar máximo relacional"""
    
    sistema = SistemaPrincipal()
    
    # Ejemplo: concepto SOPORTE
    rutas_soporte = {
        "Física": "Material que sostiene peso y distribuye fuerzas hacia abajo",
        "Ergonómica": "Superficie que acomoda la forma del cuerpo humano",
        "Arquitectónica": "Elemento estructural que transfiere cargas al suelo",
        "Lógica": "Entidad que fundamenta la existencia de otra",
        "Ontológica": "Razón de ser fundamental en la estructura del ser"
    }
    
    es_maximo = sistema.detectar_maximo_relacional_concepto("SOPORTE", rutas_soporte)
    
    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║        RESULTADO: MÁXIMO RELACIONAL DEFINICIONAL          ║
    ╚════════════════════════════════════════════════════════════╝
    
    Concepto: SOPORTE
    ¿Es máximo relacional?: {'✓ SÍ' if es_maximo else '✗ NO'}
    """)

# Usar:
# python -c "from sistema_principal_v2 import cli_detectar_maximo_relacional; cli_detectar_maximo_relacional()"
```

---

## 🔄 Flujo de ejecución {#flujo}

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. ENTRADA: Concepto + 5 rutas de definición                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. AnalizadorConvergencia:                                     │
│    - Generar embeddings (lazy load del modelo)                │
│    - Comparar con embedding de referencia                      │
│    - Calcular certeza individual para cada ruta (0-1)         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Combinar certezas:                                          │
│    P(correcto) = 1 - (1-c1)*(1-c2)*(1-c3)*(1-c4)*(1-c5)     │
│    Para 5 rutas de 0.91: P = 99.9998%                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. DECISIÓN:                                                   │
│    Si P >= 99% → ✓ MÁXIMO RELACIONAL DEFINICIONAL            │
│    Si P < 99% → ✗ No alcanza umbral                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. GUARDAR EN BD:                                              │
│    - Crear nodo MaximoRelacional                              │
│    - Almacenar certeza y rutas                                │
│    - Timestamp de detección                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 Ejemplos de código {#ejemplos}

### **Ejemplo 1: Analizar concepto único**

```python
from sistema_principal_v2 import SistemaPrincipal

# Inicializar
sistema = SistemaPrincipal()

# Definir 5 rutas
rutas = {
    "Física": "Superficie material que soporta peso",
    "Ergonómica": "Diseño que minimiza fatiga",
    "Arquitectónica": "Elemento estructural de carga",
    "Lógica": "Proposición que fundamenta otras",
    "Ontológica": "Ente esencial en la realidad"
}

# Detectar máximo relacional
es_maximo = sistema.detectar_maximo_relacional_concepto("SOPORTE", rutas)

if es_maximo:
    print("✓ SOPORTE alcanzó máximo relacional definicional (99%+)")
else:
    print("✗ SOPORTE no alcanzó el umbral de 99%")
```

### **Ejemplo 2: Procesar lote de 1000 conceptos**

```python
# Preparar datos
conceptos = {
    "SOPORTE": rutas_soporte,
    "ESTRUCTURA": rutas_estructura,
    "RELACIÓN": rutas_relacion,
    # ... más 997 conceptos
}

# Procesar en lotes (OPTIMIZADO para dual-core)
resultados = sistema.procesar_lote_maximo_relacional(
    conceptos,
    batch_size=50  # 50 conceptos por lote
)

# Filtrar solo máximos relacionales
maximos = [r for r in resultados if r.es_maximo_relacional]
print(f"Encontrados {len(maximos)} máximos relacionales de {len(conceptos)} conceptos")
```

### **Ejemplo 3: Análisis híbrido del grafo**

```python
import asyncio

async def main():
    # Obtener grafo de Neo4j
    nodos = sistema.neo4j_db.obtener_nodos_grafo()
    arcos = sistema.neo4j_db.obtener_arcos_grafo()
    
    # Análisis híbrido
    resultado = await sistema.analizar_grafo_hibrido(
        nodos, arcos,
        neo4j_disponible=True
    )
    
    # Resultados
    print(f"Total nodos: {resultado.total_nodos}")
    print(f"Total arcos: {resultado.total_arcos}")
    print(f"Optimización usada: {resultado.optimizacion_usado}")
    print(f"\nTop 10 nodos:")
    for i, nodo in enumerate(resultado.top_10_nodos, 1):
        print(f"  {i}. {nodo.nodo} (score: {nodo.score_hibrido:.6f})")

asyncio.run(main())
```

---

## ✅ Checklist de implementación {#checklist}

- [ ] **Crear estructura de directorios**
  ```bash
  mkdir -p procesadores
  ```

- [ ] **Copiar archivos creados**
  - `config_dualcore_optimizado.yaml` → raíz
  - `analizador_convergencia_optimizado.py` → `procesadores/`
  - `analizador_maximo_relacional_hibrido.py` → `procesadores/`

- [ ] **Instalar dependencias optimizadas**
  ```bash
  pip install -r requirements_dualcore.txt
  python -m spacy download es_core_news_sm
  ```

- [ ] **Agregar imports a sistema_principal_v2.py**
  ```python
  from procesadores.analizador_convergencia_optimizado import ...
  from procesadores.analizador_maximo_relacional_hibrido import ...
  ```

- [ ] **Crear métodos en clase principal**
  - `detectar_maximo_relacional_concepto()`
  - `procesar_lote_maximo_relacional()`
  - `analizar_grafo_hibrido()`

- [ ] **Configurar red (si Neo4j está remoto)**
  - Editar `config_dualcore_optimizado.yaml`
  - Cambiar `neo4j.bolt_url` a IP real (ej: `bolt://192.168.1.100:7687`)

- [ ] **Pruebas básicas**
  ```bash
  python -c "from procesadores.analizador_convergencia_optimizado import *; print('✓ Importación exitosa')"
  ```

- [ ] **Monitorear memoria en dual-core**
  ```bash
  # En terminal separada:
  watch -n 1 'free -h && ps aux | grep python | head -3'
  ```

---

## 🎯 Próximos pasos

1. **Integrar en sistema_principal_v2.py** (completar pasos A-C arriba)
2. **Configurar Neo4j remoto** en PC2 (IP y puerto)
3. **Instalar LightRAG en Docker** en PC2
4. **Probar con concepto de ejemplo** (SOPORTE)
5. **Escalar a 1000+ conceptos** con batch processing
6. **Monitorear rendimiento** en dual-core (RAM, CPU)

