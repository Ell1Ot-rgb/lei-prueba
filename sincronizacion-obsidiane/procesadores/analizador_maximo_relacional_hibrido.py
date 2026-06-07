"""
ANALIZADOR HÍBRIDO: NetworkX + Neo4j GDS
==========================================
Combina análisis local rápido (NetworkX) con cómputo remoto pesado (Neo4j GDS).

ESTRATEGIA:
- PC1 (dual-core): Usa NetworkX para análisis <100k nodos (rápido, <1 min)
- PC2 (potente): Delegación de GDS para grafos >100k nodos (remoto)
- Híbrido: Combina resultados para máxima eficiencia

OPTIMIZADO PARA: AMD Dual-Core + 8GB RAM + Neo4j remoto
"""

import gc
import yaml
import logging
import asyncio
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
import networkx as nx
from neo4j import AsyncGraphDatabase, AsyncSession
import warnings

warnings.filterwarnings("ignore")

# ============================================================
# 1. LOGGING CONFIGURADO
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("HibridoAnalisis")

# ============================================================
# 2. DATACLASSES PARA RESULTADOS
# ============================================================
@dataclass
class ResultadoCentralidad:
    """Resultado de análisis de centralidad"""
    nodo: str
    pagerank: float
    betweenness: float
    score_hibrido: float  # Combinación normalizada
    fuente: str  # "networkx" o "neo4j_gds"

@dataclass
class ResultadoAnalisiscentralizado:
    """Análisis centralizado del grafo"""
    total_nodos: int
    total_arcos: int
    top_10_nodos: List[ResultadoCentralidad]
    densidad: float
    diametro: Optional[int]
    componentes_conexas: int
    tiempo_ejecucion_ms: float
    optimizacion_usado: str  # "networkx", "gds", o "hibrido"

# ============================================================
# 3. CLIENTE NETWORKX - ANÁLISIS LOCAL RÁPIDO
# ============================================================
class AnalizadorNetworkX:
    """
    Análisis de grafos local usando NetworkX.
    
    VENTAJAS:
    - Cero latencia de red
    - Procesa rápidamente <100k nodos
    - Usa Python puro
    
    LIMITACIONES:
    - Todo en RAM
    - Single-thread por defecto
    - No escala a >1M nodos
    """
    
    def __init__(self):
        self.grafo = None
        logger.info("[NetworkX] Inicializado")
    
    def cargar_grafo_desde_dict(self, 
                                nodos: List[Dict],
                                arcos: List[Tuple]) -> nx.Graph:
        """
        Cargar grafo desde datos de Neo4j.
        
        OPTIMIZACIÓN:
        - Crea grafo vacío
        - Agrega nodos por lotes
        - Agrega arcos por lotes
        - Libera memoria intermedia
        """
        logger.info(f"[NetworkX] Cargando grafo: {len(nodos)} nodos, {len(arcos)} arcos")
        
        self.grafo = nx.Graph()
        
        # Agregar nodos por lotes
        batch_size = 5000
        for i in range(0, len(nodos), batch_size):
            lote = nodos[i:i+batch_size]
            self.grafo.add_nodes_from([(n['id'], n) for n in lote])
            logger.debug(f"  ├─ Nodos {i}-{i+len(lote)}")
        
        # Agregar arcos
        for i in range(0, len(arcos), batch_size):
            lote = arcos[i:i+batch_size]
            self.grafo.add_edges_from(lote)
            logger.debug(f"  ├─ Arcos {i}-{i+len(lote)}")
        
        # Limpiar
        gc.collect()
        logger.info(f"[NetworkX] ✓ Grafo cargado")
        
        return self.grafo
    
    def calcular_pagerank(self, 
                         iterations: int = 100) -> Dict[str, float]:
        """
        Calcular PageRank con iteraciones controladas.
        
        PARÁMETRO:
        - iterations: 100 para dual-core (en lugar de 1000)
        """
        logger.info(f"[PageRank] Calculando con {iterations} iteraciones...")
        
        pagerank = nx.pagerank(
            self.grafo,
            max_iter=iterations,
            tol=1e-5,  # Tolerancia relajada para convergencia rápida
            weight='weight'
        )
        
        logger.info(f"[PageRank] ✓ Completado")
        return pagerank
    
    def calcular_betweenness(self,
                            normalized: bool = True) -> Dict[str, float]:
        """
        Calcular Betweenness Centrality.
        
        OPTIMIZACIÓN:
        - k=None por defecto (todos los pares)
        - normalized=True: divide por (N-1)*(N-2)/2
        """
        logger.info("[Betweenness] Calculando...")
        
        betweenness = nx.betweenness_centrality(
            self.grafo,
            normalized=normalized,
            weight='weight'
        )
        
        logger.info("[Betweenness] ✓ Completado")
        return betweenness
    
    def analizar_grafo_completo(self) -> ResultadoAnalisiscentralizado:
        """
        Análisis completo del grafo en local.
        """
        if not self.grafo:
            raise ValueError("[NetworkX] Grafo no cargado")
        
        logger.info("[Análisis] Iniciando análisis completo del grafo...")
        
        import time
        t_inicio = time.time()
        
        # Estadísticas básicas
        n_nodos = self.grafo.number_of_nodes()
        n_arcos = self.grafo.number_of_edges()
        densidad = nx.density(self.grafo)
        
        logger.info(f"  ├─ Nodos: {n_nodos}")
        logger.info(f"  ├─ Arcos: {n_arcos}")
        logger.info(f"  └─ Densidad: {densidad:.4f}")
        
        # Centralidades
        pagerank = self.calcular_pagerank(iterations=100)
        betweenness = self.calcular_betweenness()
        
        # Top 10 nodos
        nodos_rankeados = []
        for nodo_id in list(pagerank.keys())[:10]:
            score_hibrido = 0.6 * pagerank[nodo_id] + 0.4 * betweenness.get(nodo_id, 0)
            nodos_rankeados.append(
                ResultadoCentralidad(
                    nodo=nodo_id,
                    pagerank=pagerank[nodo_id],
                    betweenness=betweenness.get(nodo_id, 0),
                    score_hibrido=score_hibrido,
                    fuente="networkx"
                )
            )
        
        # Componentes conexas
        componentes = nx.number_connected_components(self.grafo)
        
        # Diámetro (solo si es conexo)
        diametro = None
        if nx.is_connected(self.grafo):
            diametro = nx.diameter(self.grafo)
        
        t_fin = time.time()
        tiempo_ms = (t_fin - t_inicio) * 1000
        
        resultado = ResultadoAnalisiscentralizado(
            total_nodos=n_nodos,
            total_arcos=n_arcos,
            top_10_nodos=nodos_rankeados,
            densidad=densidad,
            diametro=diametro,
            componentes_conexas=componentes,
            tiempo_ejecucion_ms=tiempo_ms,
            optimizacion_usado="networkx"
        )
        
        logger.info(f"[Análisis] ✓ Completado en {tiempo_ms:.2f}ms")
        
        gc.collect()
        return resultado


# ============================================================
# 4. CLIENTE NEO4J GDS - ANÁLISIS REMOTO PESADO
# ============================================================
class AnalizadorNeo4jGDS:
    """
    Análisis remoto usando Neo4j Graph Data Science.
    
    VENTAJAS:
    - Escala a 100M+ nodos
    - GPU-acelerado en PC potente
    - Algoritmos optimizados
    
    LIMITACIONES:
    - Latencia de red (~100ms)
    - Requiere Neo4j empresarial
    """
    
    def __init__(self, config_path: str = "./config_dualcore_optimizado.yaml"):
        """Inicializar con configuración de Neo4j"""
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.neo4j_config = config['neo4j']
        self.driver = None
        self.session = None
        
        logger.info("[Neo4j GDS] Inicializado")
    
    async def conectar(self):
        """Conectar a Neo4j de forma asíncrona"""
        logger.info("[Neo4j] Conectando...")
        
        self.driver = AsyncGraphDatabase.driver(
            self.neo4j_config['bolt_url'],
            auth=(
                self.neo4j_config['auth_user'],
                self.neo4j_config['auth_password']
            ),
            max_pool_size=self.neo4j_config['max_pool_size'],
            connection_timeout=self.neo4j_config['connection_timeout']
        )
        
        logger.info("[Neo4j] ✓ Conectado")
    
    async def desconectar(self):
        """Desconectar de Neo4j"""
        if self.driver:
            await self.driver.close()
            logger.info("[Neo4j] ✓ Desconectado")
    
    async def ejecutar_pagerank_gds(self,
                                    nombre_grafo: str,
                                    iteraciones: int = 20) -> Dict[str, float]:
        """
        Ejecutar PageRank en GDS (remoto en PC2).
        
        PARÁMETRO:
        - nombre_grafo: nombre del grafo en Neo4j (ej: "concepto_grafo")
        - iteraciones: reducidas para dual-core (20 en lugar de 100)
        """
        logger.info(f"[GDS PageRank] Ejecutando en Neo4j ({nombre_grafo})...")
        
        query = f"""
        CALL gds.pageRank.stream('{nombre_grafo}', {{
            maxIterations: {iteraciones},
            tolerance: 0.00001,
            concurrency: {self.neo4j_config['gds_use_concurrency']}
        }})
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).id AS node_id, score
        """
        
        async with self.driver.session() as session:
            resultados = await session.run(query)
            pagerank = {}
            async for record in resultados:
                pagerank[record['node_id']] = record['score']
        
        logger.info(f"[GDS PageRank] ✓ {len(pagerank)} nodos")
        return pagerank
    
    async def ejecutar_betweenness_gds(self,
                                       nombre_grafo: str) -> Dict[str, float]:
        """Ejecutar Betweenness Centrality en GDS"""
        logger.info(f"[GDS Betweenness] Ejecutando en Neo4j ({nombre_grafo})...")
        
        query = f"""
        CALL gds.betweenness.stream('{nombre_grafo}', {{
            concurrency: {self.neo4j_config['gds_use_concurrency']}
        }})
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).id AS node_id, score
        """
        
        async with self.driver.session() as session:
            resultados = await session.run(query)
            betweenness = {}
            async for record in resultados:
                betweenness[record['node_id']] = record['score']
        
        logger.info(f"[GDS Betweenness] ✓ {len(betweenness)} nodos")
        return betweenness


# ============================================================
# 5. ORQUESTADOR HÍBRIDO
# ============================================================
class OrquestadorComputacionHibrida:
    """
    Orquesta cuándo usar NetworkX local vs. Neo4j GDS remoto.
    
    ESTRATEGIA:
    - Grafo <100k nodos → NetworkX (local, rápido)
    - Grafo >100k nodos → Neo4j GDS (remoto, escalable)
    - Disponibilidad de Neo4j → Usar GDS si disponible
    """
    
    def __init__(self, config_path: str = "./config_dualcore_optimizado.yaml"):
        self.config_path = config_path
        self.networkx = AnalizadorNetworkX()
        self.gds = AnalizadorNeo4jGDS(config_path)
        
        logger.info("[Orquestador] Inicializado (estrategia híbrida)")
    
    def decidir_estrategia(self, 
                          n_nodos: int,
                          neo4j_disponible: bool) -> str:
        """
        Decidir qué estrategia usar basado en tamaño y disponibilidad.
        
        REGLA:
        - n < 50k & Neo4j no disponible → NetworkX (local)
        - 50k < n < 200k → NetworkX (local) si está disponible
        - n > 200k & Neo4j disponible → GDS (remoto)
        - n > 500k → GDS obligatorio (NetworkX no aguanta)
        """
        if n_nodos > 500000:
            if not neo4j_disponible:
                logger.warning("[Orquestador] ⚠ Grafo >500k nodos pero Neo4j no disponible!")
            return "gds"
        
        if n_nodos > 200000 and neo4j_disponible:
            return "gds"
        
        if n_nodos > 100000:
            logger.info("[Orquestador] Grafo >100k nodos, preferencia GDS si disponible")
            return "gds" if neo4j_disponible else "networkx"
        
        return "networkx"
    
    async def analizar_hibrido(self,
                               nodos: List[Dict],
                               arcos: List[Tuple],
                               nombre_grafo_gds: Optional[str] = None,
                               neo4j_disponible: bool = False) -> ResultadoAnalisiscentralizado:
        """
        Análisis completo usando estrategia híbrida.
        
        ENTRADA:
        - nodos: lista de diccionarios con 'id' y otros atributos
        - arcos: lista de tuplas (origen, destino)
        - nombre_grafo_gds: nombre del grafo en Neo4j GDS
        - neo4j_disponible: si Neo4j está disponible
        """
        
        # Decidir estrategia
        estrategia = self.decidir_estrategia(
            len(nodos),
            neo4j_disponible
        )
        
        logger.info(f"[Orquestador] Estrategia seleccionada: {estrategia.upper()}")
        
        if estrategia == "networkx":
            # Análisis local
            self.networkx.cargar_grafo_desde_dict(nodos, arcos)
            resultado = self.networkx.analizar_grafo_completo()
        
        else:  # estrategia == "gds"
            # Análisis remoto
            await self.gds.conectar()
            
            try:
                pagerank = await self.gds.ejecutar_pagerank_gds(nombre_grafo_gds)
                betweenness = await self.gds.ejecutar_betweenness_gds(nombre_grafo_gds)
                
                # Combinar resultados
                top_10 = []
                for nodo_id in sorted(pagerank.keys(), 
                                     key=lambda x: pagerank[x], 
                                     reverse=True)[:10]:
                    score_hibrido = 0.6 * pagerank[nodo_id] + 0.4 * betweenness.get(nodo_id, 0)
                    top_10.append(
                        ResultadoCentralidad(
                            nodo=nodo_id,
                            pagerank=pagerank[nodo_id],
                            betweenness=betweenness.get(nodo_id, 0),
                            score_hibrido=score_hibrido,
                            fuente="neo4j_gds"
                        )
                    )
                
                resultado = ResultadoAnalisiscentralizado(
                    total_nodos=len(nodos),
                    total_arcos=len(arcos),
                    top_10_nodos=top_10,
                    densidad=-1,  # No disponible en GDS
                    diametro=None,
                    componentes_conexas=-1,
                    tiempo_ejecucion_ms=-1,
                    optimizacion_usado="neo4j_gds"
                )
            
            finally:
                await self.gds.desconectar()
        
        return resultado


# ============================================================
# 6. EJEMPLO DE USO
# ============================================================
if __name__ == "__main__":
    # Crear grafo de ejemplo
    nodos = [
        {"id": f"nodo_{i}", "label": f"Concepto_{i}"}
        for i in range(1000)  # 1000 nodos para demo
    ]
    
    arcos = [
        (f"nodo_{i}", f"nodo_{(i+1) % len(nodos)}")
        for i in range(len(nodos))
    ]
    
    # Orquestador híbrido
    orquestador = OrquestadorComputacionHibrida(
        config_path="./config_dualcore_optimizado.yaml"
    )
    
    # Ejecutar análisis
    async def main():
        resultado = await orquestador.analizar_hibrido(
            nodos=nodos,
            arcos=arcos,
            nombre_grafo_gds="concepto_grafo",
            neo4j_disponible=False  # Cambiar a True si Neo4j está disponible
        )
        
        print(f"""
╔════════════════════════════════════════════════════════════╗
║           ANÁLISIS HÍBRIDO COMPLETADO                    ║
╚════════════════════════════════════════════════════════════╝

Estadísticas del grafo:
  • Nodos:          {resultado.total_nodos}
  • Arcos:          {resultado.total_arcos}
  • Densidad:       {resultado.densidad:.4f}
  • Componentes:    {resultado.componentes_conexas}
  • Optimización:   {resultado.optimizacion_usado}
  • Tiempo:         {resultado.tiempo_ejecucion_ms:.2f}ms

Top 10 nodos (por score híbrido):
""")
        for i, nodo in enumerate(resultado.top_10_nodos, 1):
            print(f"  {i}. {nodo.nodo}")
            print(f"     ├─ PageRank:     {nodo.pagerank:.6f}")
            print(f"     ├─ Betweenness:  {nodo.betweenness:.6f}")
            print(f"     └─ Score híbrido: {nodo.score_hibrido:.6f}")
    
    asyncio.run(main())
