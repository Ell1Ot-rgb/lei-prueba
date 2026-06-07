"""
Adaptador de Entrada: Webhook Handler para n8n
================================================

Patrón: Adaptador Hexagonal (Inbound)
Expone un endpoint Flask que recibe señales de n8n y dispara el pipeline.

Uso:
    from adapters.inbound.webhook_handler import WebhookHandler
    handler = WebhookHandler(callback=procesar, port=5679)
    handler.iniciar()
"""

import json
import logging
from typing import Callable, Dict
from flask import Flask, request, jsonify

logger = logging.getLogger(__name__)


class WebhookHandler:
    """
    Servidor HTTP que recibe webhooks de n8n y los enruta al pipeline.

    Endpoints:
        POST /webhook/procesar   → Procesa datos brutos (texto/json)
        POST /webhook/consultar  → Consulta estado del sistema
        GET  /webhook/status     → Health check
    """

    def __init__(
        self,
        callback_procesar: Callable[[Dict], Dict],
        callback_estado: Callable[[], Dict] = None,
        host: str = "0.0.0.0",
        port: int = 5679,
    ):
        self.app = Flask("OrganismoVivo_Webhook")
        self.callback_procesar = callback_procesar
        self.callback_estado = callback_estado
        self.host = host
        self.port = port
        self._registrar_rutas()

    def _registrar_rutas(self):
        @self.app.route("/webhook/procesar", methods=["POST"])
        def procesar():
            try:
                datos = request.get_json(force=True, silent=True) or {}
                if not datos and request.data:
                    datos = {"texto": request.data.decode("utf-8", errors="replace")}

                logger.info(f"Webhook recibido: {len(str(datos))} bytes")
                resultado = self.callback_procesar(datos)
                return jsonify({"status": "ok", "resultado": resultado}), 200

            except Exception as e:
                logger.error(f"Error en webhook: {e}")
                return jsonify({"status": "error", "mensaje": str(e)}), 500

        @self.app.route("/webhook/consultar", methods=["POST"])
        def consultar():
            try:
                if self.callback_estado:
                    estado = self.callback_estado()
                    return jsonify({"status": "ok", "estado": estado}), 200
                return jsonify({"status": "ok", "estado": "sin callback"}), 200
            except Exception as e:
                return jsonify({"status": "error", "mensaje": str(e)}), 500

        @self.app.route("/webhook/status", methods=["GET"])
        def status():
            return jsonify({
                "status": "online",
                "servicio": "Organismo Vivo v4.0",
                "endpoints": [
                    "POST /webhook/procesar",
                    "POST /webhook/consultar",
                    "GET  /webhook/status",
                ],
            }), 200

    def iniciar(self, bloquear: bool = True):
        """Inicia el servidor webhook."""
        print(f"[WEBHOOK] Servidor iniciado en http://{self.host}:{self.port}")
        print(f"[WEBHOOK] Endpoints:")
        print(f"  POST http://localhost:{self.port}/webhook/procesar")
        print(f"  POST http://localhost:{self.port}/webhook/consultar")
        print(f"  GET  http://localhost:{self.port}/webhook/status")
        if bloquear:
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        else:
            import threading
            hilo = threading.Thread(
                target=self.app.run,
                kwargs={"host": self.host, "port": self.port, "debug": False, "use_reloader": False},
                daemon=True
            )
            hilo.start()
