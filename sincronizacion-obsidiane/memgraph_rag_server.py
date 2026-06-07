"""
memgraph_rag_server.py — Servidor REST HTTP para MemGraphRAG
=============================================================

Servidor web independiente que expone la API REST del subsistema MemGraphRAG.
Se ejecuta en paralelo al Sistema Vivo principal (puerto MEMGRAPH_RAG_PORT=7688).

Endpoints:
    POST /indexar          → Indexa un texto en el sistema MemGraphRAG
    POST /consultar        → Consulta el grafo de conocimiento
    GET  /estadisticas     → Estadísticas del sistema
    GET  /grafo/construir  → Reconstruye el grafo completo
    GET  /memoria/exportar → Exporta la Global Memory
    GET  /health           → Health check

Uso:
    python memgraph_rag_server.py

Variables de entorno relevantes:
    MEMGRAPH_RAG_PORT=7688
    MEMGRAPH_RAG_ENABLED=true
    MEMGRAPH_HOST=localhost
    MEMGRAPH_PORT=7687
"""

import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Any

# Agregar el directorio raíz al path para importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─── Importar el adaptador MemGraphRAG ──────────────────────────────────────
try:
    from adapters.outbound.memgraph_rag import MemGraphRAGAdapter
    _adapter_disponible = True
except ImportError as e:
    logging.warning(f"No se pudo importar MemGraphRAGAdapter: {e}")
    _adapter_disponible = False

# ─── Configuración de logging ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("memgraph_rag_server")

# ─── Instancia global del adaptador ─────────────────────────────────────────
_adapter: "MemGraphRAGAdapter | None" = None


def get_adapter() -> "MemGraphRAGAdapter":
    """Retorna la instancia singleton del adaptador MemGraphRAG."""
    global _adapter
    if _adapter is None and _adapter_disponible:
        _adapter = MemGraphRAGAdapter()
    return _adapter


# ─── Handler HTTP ─────────────────────────────────────────────────────────────

class MemGraphRAGHandler(BaseHTTPRequestHandler):
    """Handler HTTP para la API REST del servidor MemGraphRAG."""

    def log_message(self, format, *args):
        """Override para usar logging estándar."""
        logger.info(f"[HTTP] {self.address_string()} {format % args}")

    def send_json(self, data: Dict, status: int = 200) -> None:
        """Envía respuesta JSON."""
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self) -> Dict:
        """Lee y parsea el body JSON de la request."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length)
        return json.loads(raw.decode("utf-8"))

    def do_OPTIONS(self) -> None:
        """CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        """Maneja requests GET."""
        adapter = get_adapter()

        if self.path == "/health":
            if adapter:
                self.send_json({
                    "estado": "ok",
                    "servicio": "MemGraphRAG",
                    "memgraph_activo": adapter.cliente.esta_conectado(),
                    "paper": "arXiv:2606.00610 (MemGraphRAG KDD 2026)",
                })
            else:
                self.send_json({"estado": "error", "detalle": "Adaptador no disponible"}, 503)

        elif self.path == "/estadisticas":
            if adapter:
                self.send_json(adapter.estadisticas())
            else:
                self.send_json({"error": "Adaptador no disponible"}, 503)

        elif self.path == "/grafo/construir":
            if adapter:
                stats = adapter.construir_grafo_completo()
                self.send_json({"estado": "ok", "estadisticas_grafo": stats})
            else:
                self.send_json({"error": "Adaptador no disponible"}, 503)

        elif self.path == "/memoria/exportar":
            if adapter:
                datos = adapter.exportar_memoria()
                self.send_json(datos)
            else:
                self.send_json({"error": "Adaptador no disponible"}, 503)

        elif self.path == "/":
            self.send_json({
                "servicio": "MemGraphRAG API Server",
                "version": "1.0.0",
                "paper": "arXiv:2606.00610 — MemGraphRAG (KDD 2026)",
                "sistema": "Sistema Vivo Hexagonal v4.0",
                "endpoints": {
                    "POST /indexar": "Indexa un texto en MemGraphRAG",
                    "POST /consultar": "Consulta el grafo de conocimiento",
                    "GET /estadisticas": "Estadísticas del sistema",
                    "GET /grafo/construir": "Reconstruye el grafo completo",
                    "GET /memoria/exportar": "Exporta la Global Memory",
                    "GET /health": "Health check",
                },
            })

        else:
            self.send_json({"error": f"Endpoint no encontrado: {self.path}"}, 404)

    def do_POST(self) -> None:
        """Maneja requests POST."""
        adapter = get_adapter()

        if not adapter:
            self.send_json({"error": "Adaptador MemGraphRAG no disponible"}, 503)
            return

        try:
            body = self.read_json_body()
        except json.JSONDecodeError as e:
            self.send_json({"error": f"JSON inválido: {e}"}, 400)
            return

        if self.path == "/indexar":
            # ── POST /indexar ──
            texto = body.get("texto", "")
            if not texto:
                self.send_json({"error": "Campo 'texto' requerido"}, 400)
                return

            resultado = adapter.indexar(
                texto=texto,
                fuente=body.get("fuente", "api"),
                tipo_fuente=body.get("tipo_fuente", "api_request"),
                metadata=body.get("metadata", {}),
            )
            self.send_json(resultado)

        elif self.path == "/consultar":
            # ── POST /consultar ──
            query = body.get("query", "")
            if not query:
                self.send_json({"error": "Campo 'query' requerido"}, 400)
                return

            resultado = adapter.consultar(
                query=query,
                max_tokens=body.get("max_tokens", 2000),
            )
            self.send_json(resultado)

        elif self.path == "/indexar_pipeline":
            # ── POST /indexar_pipeline (integración con PipelineEvolucionado) ──
            resultado = adapter.indexar_resultado_pipeline(body)
            self.send_json(resultado)

        else:
            self.send_json({"error": f"Endpoint no encontrado: {self.path}"}, 404)


# ─── Punto de entrada principal ──────────────────────────────────────────────

def iniciar_servidor():
    """Inicia el servidor HTTP del MemGraphRAG."""
    puerto = int(os.environ.get("MEMGRAPH_RAG_PORT", "7688"))
    host = "0.0.0.0"

    logger.info(f"[MemGraphRAG Server] Iniciando en http://{host}:{puerto}")
    logger.info(f"[MemGraphRAG Server] Paper: arXiv:2606.00610 — MemGraphRAG (KDD 2026)")

    # Pre-inicializar el adaptador
    adapter = get_adapter()
    if adapter:
        logger.info(f"[MemGraphRAG Server] Adaptador: {adapter}")
    else:
        logger.warning("[MemGraphRAG Server] Adaptador no disponible — verificar instalación")

    server = HTTPServer((host, puerto), MemGraphRAGHandler)

    logger.info(f"[MemGraphRAG Server] Escuchando en puerto {puerto}")
    logger.info("[MemGraphRAG Server] Endpoints disponibles:")
    logger.info(f"  POST http://localhost:{puerto}/indexar")
    logger.info(f"  POST http://localhost:{puerto}/consultar")
    logger.info(f"  GET  http://localhost:{puerto}/estadisticas")
    logger.info(f"  GET  http://localhost:{puerto}/health")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("[MemGraphRAG Server] Detenido por usuario")
        server.shutdown()


if __name__ == "__main__":
    iniciar_servidor()
