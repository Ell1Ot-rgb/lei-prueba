import json
import logging
import time
from typing import Dict, Any, Generator, Optional, Callable
import redis
from dataclasses import dataclass

# Configuración de logging
logger = logging.getLogger("RedisConnector")

@dataclass
class VectorFisico:
    """Representación estructurada del vector de la Capa 1"""
    tiempo: int
    instrucciones: int
    energia: int
    entropia: int
    concepto: str
    confianza: float
    hash_id: str
    timestamp: float

class TraductorFenomenologico:
    """
    Convierte vectores físicos (Capa 1) en parámetros fenomenológicos (Capa 2).
    """
    
    @staticmethod
    def traducir(vector: VectorFisico) -> Dict[str, Any]:
        """
        Traduce un vector físico a un diccionario de parámetros para Ereignis/REMForge.
        """
        # 1. Intensidad (basada en Energía)
        # Normalización aproximada: 0 uJ -> 0.0, 10000 uJ -> 1.0
        intensidad = min(vector.energia / 10000.0, 1.0)
        
        # 2. Complejidad (basada en Entropía)
        # Entropía es uint32, max ~4e9. Normalizamos logarítmicamente o lineal.
        # Asumimos rango efectivo alto para "caos".
        complejidad = min(vector.entropia / 4000000000.0, 1.0)
        
        # 3. Mapeo de Concepto a Tipo Base
        mapa_conceptos = {
            "TÉCNICO": "estructural",
            "POÉTICO": "narrativo",
            "NUMÉRICO": "logico",
            "CAOS": "caotico"
        }
        tipo_base = mapa_conceptos.get(vector.concepto, "indefinido")
        
        return {
            "intensidad": intensidad,
            "complejidad": complejidad,
            "tipo_base": tipo_base,
            "origen_fisico": {
                "hash": vector.hash_id,
                "energia_uj": vector.energia,
                "ciclos": vector.tiempo
            }
        }

class RedisMonjeConnector:
    """
    Conector para escuchar eventos del Monje Gemelo (Capa 1) vía Redis.
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.redis_client = None
        self.pubsub = None
        self.conectado = False
        
    def conectar(self) -> bool:
        """Establece conexión con Redis."""
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True  # Recibir strings, no bytes
            )
            self.redis_client.ping()
            self.conectado = True
            logger.info(f"✅ Conectado a Redis en {self.host}:{self.port}")
            return True
        except redis.ConnectionError as e:
            logger.error(f"❌ Error conectando a Redis: {e}")
            self.conectado = False
            return False

    def suscribirse(self, canales: list = ["monje/fenomenologia/*"]):
        """Se suscribe a los canales especificados."""
        if not self.conectado:
            if not self.conectar():
                return
        
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.psubscribe(*canales)
        logger.info(f"📡 Suscrito a canales: {canales}")

    def escuchar_eventos(self) -> Generator[Dict[str, Any], None, None]:
        """
        Generador que escucha eventos infinitamente y los traduce.
        Yields: Diccionario con datos del evento traducido.
        """
        if not self.pubsub:
            self.suscribirse()
            
        logger.info("👂 Escuchando eventos de la Capa 1...")
        
        try:
            for mensaje in self.pubsub.listen():
                if mensaje['type'] == 'pmessage':
                    try:
                        datos_raw = json.loads(mensaje['data'])
                        canal = mensaje['channel']
                        
                        # Parsear a VectorFisico
                        vector = VectorFisico(
                            tiempo=datos_raw.get("tiempo", 0),
                            instrucciones=datos_raw.get("instrucciones", 0),
                            energia=datos_raw.get("energia", 0),
                            entropia=datos_raw.get("entropia", 0),
                            concepto=datos_raw.get("concepto", "DESCONOCIDO"),
                            confianza=datos_raw.get("confianza", 0.0),
                            hash_id=datos_raw.get("hash", "0x00"),
                            timestamp=datos_raw.get("meta", {}).get("timestamp_tx", time.time())
                        )
                        
                        # Traducir
                        evento_fenomenologico = TraductorFenomenologico.traducir(vector)
                        evento_fenomenologico['canal_origen'] = canal
                        
                        yield evento_fenomenologico
                        
                    except json.JSONDecodeError:
                        logger.warning(f"⚠️ JSON inválido recibido en {mensaje['channel']}")
                    except Exception as e:
                        logger.error(f"❌ Error procesando mensaje: {e}")
                        
        except KeyboardInterrupt:
            logger.info("🛑 Deteniendo escucha de Redis...")
        except Exception as e:
            logger.error(f"❌ Error crítico en listener: {e}")
            self.conectado = False

    def enviar_feedback(self, mensaje: str, prioridad: str = "normal"):
        """Envía feedback a la Capa 1."""
        if not self.conectado:
            return
        
        payload = {
            "origen": "YO_ESTRUCTURAL",
            "mensaje": mensaje,
            "prioridad": prioridad,
            "timestamp": time.time()
        }
        try:
            self.redis_client.publish("dasein/feedback", json.dumps(payload))
            logger.info(f"🗣️ Feedback enviado: {mensaje}")
        except Exception as e:
            logger.error(f"❌ Error enviando feedback: {e}")

# Ejemplo de uso directo
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    connector = RedisMonjeConnector(host="localhost", port=6379) # Ajustar según entorno
    if connector.conectar():
        for evento in connector.escuchar_eventos():
            print(f"✨ Evento Recibido: {evento['tipo_base']} (Int: {evento['intensidad']:.2f})")
