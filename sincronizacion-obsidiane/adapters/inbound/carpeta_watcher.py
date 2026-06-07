"""
Adaptador de Entrada: Monitor de Carpeta Compartida
====================================================

Patrón: Adaptador Hexagonal (Inbound)
Monitorea una carpeta de entrada por archivos nuevos y dispara el pipeline.

Uso:
    from adapters.inbound.carpeta_watcher import CarpetaWatcher
    watcher = CarpetaWatcher(carpeta="C:/ruta/input", callback=procesar)
    watcher.iniciar()
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import Callable, Optional, Dict, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

logger = logging.getLogger(__name__)


class ManejadorArchivos(FileSystemEventHandler):
    """Maneja eventos de creación de archivos en la carpeta monitoreada."""

    EXTENSIONES_VALIDAS = {".txt", ".json", ".md", ".csv", ".yaml", ".yml"}

    def __init__(self, callback: Callable[[Dict], None], extensiones: set = None):
        self.callback = callback
        self.extensiones = extensiones or self.EXTENSIONES_VALIDAS
        self.procesados = {}  # ruta -> timestamp de proceso
        self._max_procesados = 1000  # l`u00edmite para evitar crecimiento infinito
        self._timeout_reproceso = 30  # segundos antes de permitir reprocesar el mismo archivo

    def on_created(self, event):
        if event.is_directory:
            return
        ruta = Path(event.src_path)
        if ruta.suffix.lower() not in self.extensiones:
            return
        import time as _time
        ahora = _time.time()
        ultima_vez = self.procesados.get(str(ruta), 0)
        if ahora - ultima_vez < self._timeout_reproceso:
            return
        # Limpiar si el dict es demasiado grande
        if len(self.procesados) > self._max_procesados:
            self.procesados.clear()

        logger.info(f"Nuevo archivo detectado: {ruta.name}")
        import time as _time
        self.procesados[str(ruta)] = _time.time()

        # Esperar a que el archivo termine de escribirse
        time.sleep(1)

        try:
            datos = self._leer_archivo(ruta)
            if datos:
                self.callback(datos)
                logger.info(f"Archivo procesado: {ruta.name}")
        except Exception as e:
            logger.error(f"Error procesando {ruta.name}: {e}")

    def _leer_archivo(self, ruta: Path) -> Optional[Dict]:
        """Lee un archivo y devuelve sus datos estructurados."""
        contenido = ruta.read_text(encoding="utf-8", errors="replace")

        if ruta.suffix == ".json":
            try:
                return json.loads(contenido)
            except json.JSONDecodeError:
                return {"texto": contenido, "formato": "json_invalido"}

        return {
            "texto": contenido,
            "formato": ruta.suffix.lstrip("."),
            "nombre": ruta.stem,
            "ruta_original": str(ruta),
            "tamanio": ruta.stat().st_size,
        }


class CarpetaWatcher:
    """
    Monitor de carpeta de entrada del Organismo Vivo.

    Observa una carpeta por archivos nuevos y los envía al pipeline
    de procesamiento como entrada bruta (Nivel -4: PreInstancia).
    """

    def __init__(
        self,
        carpeta: str,
        callback: Callable[[Dict], None],
        extensiones: set = None,
    ):
        self.carpeta = Path(carpeta)
        self.carpeta.mkdir(parents=True, exist_ok=True)
        self.callback = callback
        self.extensiones = extensiones
        self.observer = Observer()
        self._corriendo = False

    def iniciar(self, bloquear: bool = True):
        """Inicia el monitoreo de la carpeta."""
        manejador = ManejadorArchivos(
            callback=self.callback,
            extensiones=self.extensiones,
        )
        self.observer.schedule(manejador, str(self.carpeta), recursive=False)
        self.observer.start()
        self._corriendo = True

        logger.info(f"Watcher iniciado en: {self.carpeta}")
        print(f"[WATCHER] Monitoreando: {self.carpeta}")
        print("[WATCHER] Coloca archivos .txt/.json/.md para procesar")
        print("[WATCHER] Ctrl+C para detener")

        if bloquear:
            try:
                while self._corriendo:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.detener()

    def detener(self):
        """Detiene el monitoreo."""
        self._corriendo = False
        self.observer.stop()
        self.observer.join()
        logger.info("Watcher detenido")
        print("[WATCHER] Detenido")

    def procesar_existentes(self):
        """Procesa archivos que ya existen en la carpeta."""
        manejador = ManejadorArchivos(callback=self.callback, extensiones=self.extensiones)
        for archivo in sorted(self.carpeta.iterdir()):
            if archivo.is_file() and archivo.suffix.lower() in manejador.extensiones:
                evento = FileCreatedEvent(str(archivo))
                manejador.on_created(evento)
