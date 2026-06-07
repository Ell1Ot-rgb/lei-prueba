import os
import sys
import json
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# Agregar directorio actual al path para importar módulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar conectores
from n8n_config import N8nIntegrator
from google_drive_connector import GoogleDriveConnector
from supabase_connector import SupabaseConnector

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(f"logs_automatizacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AutomatizacionYO")

class SistemaAutomatizacionYO:
    """Sistema principal de automatización para YO Estructural"""
    
    def __init__(self):
        logger.info("Iniciando Sistema de Automatización YO Estructural")
        
        # Inicializar conectores
        try:
            self.n8n = N8nIntegrator()
            logger.info("Conector n8n inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar conector n8n: {str(e)}")
            self.n8n = None
        
        try:
            self.supabase = SupabaseConnector()
            logger.info("Conector Supabase inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar conector Supabase: {str(e)}")
            self.supabase = None
        
        try:
            self.google_drive = GoogleDriveConnector()
            logger.info("Conector Google Drive inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar conector Google Drive: {str(e)}")
            self.google_drive = None
    
    def procesar_archivo_drive(self, file, drive_connector):
        """Callback para procesar archivos de Google Drive"""
        logger.info(f"Procesando archivo de Google Drive: {file['name']} ({file['id']})")
        
        try:
            # Procesar archivo para YO Estructural
            datos_procesados = drive_connector.procesar_archivo_para_yo_estructural(file)
            
            # Guardar preinstancia en Supabase si está disponible
            if self.supabase:
                resultado_supabase = self.supabase.guardar_preinstancia(datos_procesados)
                logger.info(f"Resultado guardado en Supabase: {resultado_supabase['success']}")
            
            # Enviar a n8n para procesamiento adicional
            if self.n8n:
                resultado_n8n = self.n8n.enviar_datos_webhook(datos_procesados, origen="google_drive")
                logger.info(f"Resultado enviado a n8n: {resultado_n8n['success']}")
            
            return {
                "success": True,
                "mensaje": f"Archivo {file['name']} procesado correctamente"
            }
        
        except Exception as e:
            logger.error(f"Error al procesar archivo {file['name']}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def iniciar_monitoreo_drive(self):
        """Inicia el monitoreo de Google Drive"""
        if not self.google_drive:
            logger.error("No se puede iniciar monitoreo: Conector Google Drive no disponible")
            return False
        
        # Verificar que hay carpetas configuradas para monitorear
        if not self.google_drive.monitored_folders:
            logger.warning("No hay carpetas configuradas para monitorear en Google Drive")
            logger.info("Listando carpetas disponibles en Google Drive...")
            
            # Listar carpetas disponibles
            carpetas = self.google_drive.listar_carpetas()
            for carpeta in carpetas:
                logger.info(f"Carpeta: {carpeta['name']} (ID: {carpeta['id']})")
            
            return False
        
        # Iniciar monitoreo
        try:
            logger.info("Iniciando monitoreo de Google Drive...")
            self.google_drive.monitorear_cambios(
                callback_function=self.procesar_archivo_drive,
                intervalo_segundos=int(os.getenv('DRIVE_MONITOR_INTERVAL', '60'))
            )
            return True
        except Exception as e:
            logger.error(f"Error al iniciar monitoreo de Google Drive: {str(e)}")
            return False
    
    def verificar_conexiones(self):
        """Verifica el estado de las conexiones"""
        estado = {
            "n8n": {
                "disponible": self.n8n is not None,
                "webhook_url": self.n8n.n8n_webhook_url if self.n8n else None
            },
            "supabase": {
                "disponible": self.supabase is not None,
                "url": self.supabase.supabase_url if self.supabase else None
            },
            "google_drive": {
                "disponible": self.google_drive is not None,
                "carpetas_monitoreadas": len(self.google_drive.monitored_folders) if self.google_drive else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Verificar estadísticas de Supabase si está disponible
        if self.supabase:
            try:
                estadisticas = self.supabase.obtener_estadisticas()
                if estadisticas['success']:
                    estado["supabase"]["estadisticas"] = estadisticas["estadisticas"]
            except Exception as e:
                logger.error(f"Error al obtener estadísticas de Supabase: {str(e)}")
        
        # Verificar workflows de n8n si está disponible
        if self.n8n:
            try:
                workflows = self.n8n.obtener_workflows()
                if workflows:
                    estado["n8n"]["workflows"] = len(workflows)
            except Exception as e:
                logger.error(f"Error al obtener workflows de n8n: {str(e)}")
        
        return estado

# Función principal
def main():
    # Crear instancia del sistema de automatización
    sistema = SistemaAutomatizacionYO()
    
    # Verificar conexiones
    estado = sistema.verificar_conexiones()
    logger.info(f"Estado de conexiones: {json.dumps(estado, indent=2)}")
    
    # Iniciar monitoreo de Google Drive si está configurado
    if os.getenv('ENABLE_DRIVE_MONITOR', 'false').lower() == 'true':
        sistema.iniciar_monitoreo_drive()
    else:
        logger.info("Monitoreo de Google Drive deshabilitado por configuración")

if __name__ == "__main__":
    main()