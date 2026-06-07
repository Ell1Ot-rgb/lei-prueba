"""
MemGraphClient — Conexión Bolt al servidor Memgraph
====================================================

Maneja la conexión al servidor Memgraph vía protocolo Bolt (puerto 7687).
Compatible con el driver Neo4j de Python (Memgraph implementa Bolt 4.x).

Memgraph usa el mismo protocolo Bolt que Neo4j, por lo que el driver
neo4j>=5.x funciona perfectamente. Alternativamente se puede usar gqlalchemy.

Puertos por defecto de Memgraph:
    7687 → Bolt (drivers Python/Java/JS)
    3000 → Memgraph Lab (UI web)
    7444 → Streaming de logs

Referencia: https://memgraph.com/docs/getting-started
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class MemGraphClient:
    """
    Cliente de conexión a Memgraph vía protocolo Bolt.

    Compatibilidad: usa el driver neo4j>=5.0 o gqlalchemy.
    Fallback: si ninguno está disponible, opera en modo "sin base de datos"
    almacenando los datos en memoria RAM local (para tests/desarrollo).
    """

    BOLT_TIMEOUT = 10  # segundos

    def __init__(
        self,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
    ):
        self.host = host or os.environ.get("MEMGRAPH_HOST", "localhost")
        self.port = int(port or os.environ.get("MEMGRAPH_PORT", "7687"))
        self.username = username or os.environ.get("MEMGRAPH_USERNAME", "")
        self.password = password or os.environ.get("MEMGRAPH_PASSWORD", "")

        self._driver = None
        self._modo_memoria = False
        self._datos_mem: Dict[str, List[Dict]] = {
            "nodos": [], "relaciones": []
        }  # Almacenamiento en RAM cuando Memgraph no está disponible

        self._conectar()

    def _conectar(self) -> None:
        """Intenta conectar a Memgraph. Si falla, activa modo memoria."""
        # Intentar con driver neo4j (Memgraph es compatible con Bolt)
        try:
            from neo4j import GraphDatabase, basic_auth

            uri = f"bolt://{self.host}:{self.port}"
            if self.username and self.password:
                auth = basic_auth(self.username, self.password)
            else:
                auth = ("", "")  # Sin autenticación (default Memgraph)

            self._driver = GraphDatabase.driver(
                uri,
                auth=auth,
                connection_timeout=self.BOLT_TIMEOUT,
                max_connection_lifetime=300,
            )
            # Verificar conexión
            with self._driver.session() as session:
                session.run("RETURN 1 AS ping").single()

            logger.info(f"[MemGraphClient] Conectado a Memgraph en {uri}")
            self._modo_memoria = False
            return

        except ImportError:
            logger.warning(
                "[MemGraphClient] Driver neo4j no disponible. "
                "Instalarlo con: pip install neo4j>=5.0"
            )
        except Exception as e:
            logger.warning(
                f"[MemGraphClient] No se pudo conectar a Memgraph "
                f"({self.host}:{self.port}): {e}"
            )

        # Intentar con gqlalchemy como alternativa
        try:
            from gqlalchemy import Memgraph

            self._memgraph_gql = Memgraph(
                host=self.host,
                port=self.port,
            )
            if self._memgraph_gql.is_running():
                logger.info(
                    f"[MemGraphClient] Conectado a Memgraph vía gqlalchemy "
                    f"en {self.host}:{self.port}"
                )
                self._driver = self._memgraph_gql
                self._modo_memoria = False
                self._usando_gql = True
                return
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"[MemGraphClient] gqlalchemy falló: {e}")

        # Modo memoria: operación sin base de datos
        logger.warning(
            "[MemGraphClient] Operando en modo MEMORIA LOCAL. "
            "Para persistencia en grafos, instalar Docker y ejecutar Memgraph. "
            "Ver: docs/DOCKER_MEMGRAPH_SETUP.md"
        )
        self._modo_memoria = True

    def esta_conectado(self) -> bool:
        """Verifica si la conexión a Memgraph está activa."""
        if self._modo_memoria:
            return False
        try:
            if hasattr(self, '_usando_gql') and self._usando_gql:
                return self._driver.is_running()
            with self._driver.session() as session:
                session.run("RETURN 1").single()
            return True
        except Exception:
            return False

    def ejecutar_cypher(
        self,
        query: str,
        params: Dict = None,
    ) -> List[Dict]:
        """
        Ejecuta una consulta Cypher en Memgraph.

        Args:
            query: Consulta Cypher
            params: Parámetros de la consulta

        Returns:
            Lista de registros resultantes como dicts
        """
        params = params or {}

        if self._modo_memoria:
            return self._ejecutar_en_memoria(query, params)

        try:
            if hasattr(self, '_usando_gql') and self._usando_gql:
                resultados = []
                for row in self._driver.execute_and_fetch(query, params):
                    resultados.append(dict(row))
                return resultados

            with self._driver.session() as session:
                result = session.run(query, params)
                return [dict(record) for record in result]

        except Exception as e:
            logger.error(f"[MemGraphClient] Error en query Cypher: {e}")
            logger.error(f"  Query: {query[:200]}...")
            return []

    def ejecutar_cypher_write(self, query: str, params: Dict = None) -> bool:
        """
        Ejecuta una consulta Cypher de escritura (CREATE, MERGE, SET, DELETE).

        Returns:
            True si fue exitosa, False si hubo error
        """
        params = params or {}

        if self._modo_memoria:
            self._escribir_en_memoria(query, params)
            return True

        try:
            if hasattr(self, '_usando_gql') and self._usando_gql:
                self._driver.execute(query, params)
                return True

            with self._driver.session() as session:
                session.run(query, params)
            return True

        except Exception as e:
            logger.error(f"[MemGraphClient] Error escribiendo en Memgraph: {e}")
            return False

    def _ejecutar_en_memoria(self, query: str, params: Dict) -> List[Dict]:
        """Simulación mínima de consultas en modo memoria (solo para dev/tests)."""
        query_lower = query.strip().lower()
        # Retornar datos en memoria para consultas básicas de lectura
        if "match" in query_lower and "return" in query_lower:
            return self._datos_mem.get("nodos", [])
        return []

    def _escribir_en_memoria(self, query: str, params: Dict) -> None:
        """Almacena datos de escritura en RAM (modo sin Memgraph)."""
        if params:
            self._datos_mem["nodos"].append(params)

    def inicializar_esquema(self) -> None:
        """
        Inicializa el esquema de índices y constraints en Memgraph.
        Crea índices en las propiedades más consultadas.
        """
        queries_indices = [
            # Índices en nodos de entidades
            "CREATE INDEX ON :Entity(id);",
            "CREATE INDEX ON :Entity(nombre);",
            "CREATE INDEX ON :Schema(tipo);",
            "CREATE INDEX ON :Schema(frecuencia);",
            "CREATE INDEX ON :Fact(id);",
            "CREATE INDEX ON :Passage(id);",
            # Índices para nodos del sistema fenomenológico
            "CREATE INDEX ON :Fenomeno(id);",
            "CREATE INDEX ON :ContextoMG(id);",
            "CREATE INDEX ON :YoEmergente(id);",
        ]

        for query in queries_indices:
            try:
                self.ejecutar_cypher_write(query)
            except Exception:
                pass  # Ignorar si el índice ya existe

        logger.info("[MemGraphClient] Esquema de índices inicializado")

    def limpiar_grafo(self) -> None:
        """Elimina todos los nodos y relaciones (usar con cuidado en producción)."""
        self.ejecutar_cypher_write("MATCH (n) DETACH DELETE n;")
        logger.warning("[MemGraphClient] Grafo de Memgraph limpiado completamente")

    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas del grafo actual."""
        if self._modo_memoria:
            return {
                "modo": "memoria_local",
                "nodos": len(self._datos_mem.get("nodos", [])),
                "relaciones": 0,
                "memgraph_activo": False,
            }

        stats = {}
        try:
            # Contar nodos por etiqueta
            res = self.ejecutar_cypher(
                "MATCH (n) RETURN labels(n)[0] AS etiqueta, count(n) AS total "
                "ORDER BY total DESC LIMIT 20;"
            )
            stats["nodos_por_etiqueta"] = {
                r.get("etiqueta", "?"): r.get("total", 0) for r in res
            }

            # Contar relaciones
            res2 = self.ejecutar_cypher(
                "MATCH ()-[r]->() RETURN type(r) AS tipo, count(r) AS total "
                "ORDER BY total DESC LIMIT 20;"
            )
            stats["relaciones_por_tipo"] = {
                r.get("tipo", "?"): r.get("total", 0) for r in res2
            }
            stats["memgraph_activo"] = True
            stats["modo"] = "memgraph"

        except Exception as e:
            stats["error"] = str(e)
            stats["memgraph_activo"] = False

        return stats

    def cerrar(self) -> None:
        """Cierra la conexión con Memgraph limpiamente."""
        if self._driver and not self._modo_memoria:
            try:
                if not (hasattr(self, '_usando_gql') and self._usando_gql):
                    self._driver.close()
                logger.info("[MemGraphClient] Conexión a Memgraph cerrada")
            except Exception:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar()

    def __repr__(self) -> str:
        if self._modo_memoria:
            return "MemGraphClient(modo=MEMORIA_LOCAL)"
        return f"MemGraphClient(host={self.host}:{self.port})"
