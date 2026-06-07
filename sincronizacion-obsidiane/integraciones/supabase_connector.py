import os
import json
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class SupabaseConnector:
    """Clase para conectar con Supabase y gestionar datos del sistema YO Estructural"""
    
    def __init__(self):
        # Cargar configuración desde variables de entorno
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY son requeridos en el archivo .env")
        
        # Inicializar cliente de Supabase
        self.client = create_client(self.supabase_url, self.supabase_key)
    
    def guardar_preinstancia(self, preinstancia):
        """Guarda una preinstancia en Supabase"""
        try:
            # Asegurar que tenga un ID único
            if 'id_unico' not in preinstancia:
                preinstancia['id_unico'] = self._generar_id()
            
            # Asegurar timestamp
            if 'timestamp_sistema' not in preinstancia:
                preinstancia['timestamp_sistema'] = datetime.now().isoformat()
            
            # Insertar en tabla de preinstancias
            result = self.client.table('preinstancias').insert(preinstancia).execute()
            
            return {
                'success': True,
                'id': preinstancia['id_unico'],
                'data': result.data[0] if result.data else None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def guardar_instancia(self, instancia):
        """Guarda una instancia en Supabase"""
        try:
            # Asegurar que tenga un ID único
            if 'id_unico' not in instancia:
                instancia['id_unico'] = self._generar_id()
            
            # Asegurar timestamp
            if 'timestamp_sistema' not in instancia:
                instancia['timestamp_sistema'] = datetime.now().isoformat()
            
            # Insertar en tabla de instancias
            result = self.client.table('instancias').insert(instancia).execute()
            
            return {
                'success': True,
                'id': instancia['id_unico'],
                'data': result.data[0] if result.data else None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def guardar_fenomeno(self, fenomeno):
        """Guarda un fenómeno en Supabase"""
        try:
            # Asegurar que tenga un ID único
            if 'id_unico' not in fenomeno:
                fenomeno['id_unico'] = self._generar_id()
            
            # Asegurar timestamp
            if 'timestamp_sistema' not in fenomeno:
                fenomeno['timestamp_sistema'] = datetime.now().isoformat()
            
            # Insertar en tabla de fenomenos
            result = self.client.table('fenomenos').insert(fenomeno).execute()
            
            return {
                'success': True,
                'id': fenomeno['id_unico'],
                'data': result.data[0] if result.data else None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def guardar_contexto(self, contexto):
        """Guarda un contexto en Supabase"""
        try:
            # Asegurar que tenga un ID único
            if 'id_unico' not in contexto:
                contexto['id_unico'] = self._generar_id()
            
            # Asegurar timestamp
            if 'timestamp_sistema' not in contexto:
                contexto['timestamp_sistema'] = datetime.now().isoformat()
            
            # Insertar en tabla de contextos
            result = self.client.table('contextos').insert(contexto).execute()
            
            return {
                'success': True,
                'id': contexto['id_unico'],
                'data': result.data[0] if result.data else None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def obtener_por_id(self, tabla, id_unico):
        """Obtiene un registro por su ID único"""
        try:
            result = self.client.table(tabla).select('*').eq('id_unico', id_unico).execute()
            
            if result.data and len(result.data) > 0:
                return {
                    'success': True,
                    'data': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'error': 'No se encontró el registro'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def buscar_por_campo(self, tabla, campo, valor):
        """Busca registros por un campo específico"""
        try:
            result = self.client.table(tabla).select('*').eq(campo, valor).execute()
            
            return {
                'success': True,
                'data': result.data,
                'count': len(result.data)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas de las tablas en Supabase"""
        try:
            # Contar registros en cada tabla
            preinstancias = self.client.table('preinstancias').select('id_unico', count='exact').execute()
            instancias = self.client.table('instancias').select('id_unico', count='exact').execute()
            fenomenos = self.client.table('fenomenos').select('id_unico', count='exact').execute()
            contextos = self.client.table('contextos').select('id_unico', count='exact').execute()
            
            # Contar emergencias de YO
            yo_emergentes = self.client.table('contextos').select('id_unico', count='exact').eq('yo_emergente', True).execute()
            
            return {
                'success': True,
                'estadisticas': {
                    'preinstancias_total': preinstancias.count,
                    'instancias_total': instancias.count,
                    'fenomenos_total': fenomenos.count,
                    'contextos_total': contextos.count,
                    'yo_emergentes_total': yo_emergentes.count,
                    'tasa_emergencia_yo': yo_emergentes.count / contextos.count if contextos.count > 0 else 0
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generar_id(self):
        """Genera un ID único para los registros"""
        import uuid
        return str(uuid.uuid4())