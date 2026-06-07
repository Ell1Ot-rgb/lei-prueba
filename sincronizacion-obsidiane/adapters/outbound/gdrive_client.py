import os
import json
import time
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import hashlib
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Si modificas estos SCOPES, elimina el archivo token.json
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveConnector:
    """Clase para conectar con Google Drive y procesar archivos"""
    
    def __init__(self, token_path="token.json", credentials_path="credentials.json"):
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.service = self._autenticar()
        self.monitored_folders = []
        
        # Cargar carpetas monitoreadas desde variables de entorno
        self._cargar_carpetas_monitoreadas()
    
    def _autenticar(self):
        """Autentica con Google Drive API"""
        creds = None
        
        # Verificar si ya existe un token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_info(
                json.load(open(self.token_path, 'r'))
            )
        
        # Si no hay credenciales válidas, solicitar autenticación
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Guardar credenciales para la próxima ejecución
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        # Construir servicio
        return build('drive', 'v3', credentials=creds)
    
    def _cargar_carpetas_monitoreadas(self):
        """Carga las carpetas a monitorear desde variables de entorno"""
        folders_str = os.getenv('GOOGLE_DRIVE_MONITORED_FOLDERS', '')
        if folders_str:
            folders = folders_str.split(',')
            for folder in folders:
                parts = folder.split('::')
                if len(parts) == 2:
                    self.monitored_folders.append({
                        'id': parts[0].strip(),
                        'name': parts[1].strip()
                    })
    
    def listar_carpetas(self):
        """Lista las carpetas en Google Drive"""
        results = self.service.files().list(
            q="mimeType='application/vnd.google-apps.folder'",
            fields="nextPageToken, files(id, name)"
        ).execute()
        
        return results.get('files', [])
    
    def listar_archivos_en_carpeta(self, folder_id):
        """Lista los archivos en una carpeta específica"""
        results = self.service.files().list(
            q=f"'{folder_id}' in parents",
            fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size)"
        ).execute()
        
        return results.get('files', [])
    
    def descargar_archivo(self, file_id, output_path=None):
        """Descarga un archivo de Google Drive"""
        request = self.service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        file_content.seek(0)
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(file_content.read())
            return output_path
        else:
            return file_content
    
    def obtener_metadatos_archivo(self, file_id):
        """Obtiene los metadatos de un archivo"""
        return self.service.files().get(
            fileId=file_id,
            fields="id, name, mimeType, createdTime, modifiedTime, size, parents"
        ).execute()
    
    def monitorear_cambios(self, callback_function, intervalo_segundos=60):
        """Monitorea cambios en las carpetas configuradas"""
        print(f"Iniciando monitoreo de {len(self.monitored_folders)} carpetas en Google Drive...")
        
        # Almacenar último timestamp de verificación
        last_check = datetime.now().isoformat()
        
        try:
            while True:
                for folder in self.monitored_folders:
                    print(f"Verificando carpeta: {folder['name']} ({folder['id']})")
                    
                    # Buscar archivos modificados desde la última verificación
                    query = f"'{folder['id']}' in parents and modifiedTime > '{last_check}'"
                    results = self.service.files().list(
                        q=query,
                        fields="files(id, name, mimeType, createdTime, modifiedTime, size)"
                    ).execute()
                    
                    files = results.get('files', [])
                    if files:
                        print(f"Se encontraron {len(files)} archivos modificados")
                        for file in files:
                            # Procesar archivo mediante callback
                            callback_function(file, self)
                    
                # Actualizar timestamp de última verificación
                last_check = datetime.now().isoformat()
                
                # Esperar hasta el próximo intervalo
                time.sleep(intervalo_segundos)
                
        except KeyboardInterrupt:
            print("Monitoreo detenido por el usuario")
        except Exception as e:
            print(f"Error durante el monitoreo: {str(e)}")
    
    def procesar_archivo_para_yo_estructural(self, file, download=True):
        """Procesa un archivo para el sistema YO Estructural"""
        # Obtener metadatos completos
        metadata = self.obtener_metadatos_archivo(file['id'])
        
        # Determinar tipo de archivo
        mime_type = metadata['mimeType']
        tipo_archivo = mime_type.split('/')[0]
        
        # Preparar estructura de datos
        datos_procesados = {
            "id_unico": metadata['id'],
            "timestamp_sistema": datetime.now().isoformat(),
            "fase": {
                "numero": 0,
                "nombre": "preinstancia",
                "descripcion": "Fase inicial de procesamiento",
                "nivel_jerarquico": -4
            },
            "origen": {
                "tipo_archivo": tipo_archivo,
                "ruta_archivo": metadata['name'],
                "nombre_archivo": metadata['name'],
                "extension": os.path.splitext(metadata['name'])[1] if '.' in metadata['name'] else "",
                "fuente": "Google Drive",
                "timestamp_creacion": metadata['createdTime'],
                "tamaño_bytes": metadata.get('size', 0)
            }
        }
        
        # Si se requiere descargar el contenido
        if download:
            try:
                # Descargar contenido
                file_content = self.descargar_archivo(file['id'])
                
                # Generar hash del contenido
                file_content.seek(0)
                content_bytes = file_content.read()
                hash_archivo = hashlib.sha256(content_bytes).hexdigest()
                
                # Agregar hash al diccionario
                datos_procesados["origen"]["hash_archivo"] = hash_archivo
                
                # Procesar contenido según tipo
                if tipo_archivo == "text":
                    # Decodificar contenido de texto
                    try:
                        contenido_texto = content_bytes.decode('utf-8')
                        datos_procesados["contenido_bruto"] = contenido_texto
                    except UnicodeDecodeError:
                        # Intentar con otra codificación
                        try:
                            contenido_texto = content_bytes.decode('latin-1')
                            datos_procesados["contenido_bruto"] = contenido_texto
                        except:
                            datos_procesados["contenido_bruto"] = "[Error al decodificar contenido]"
                else:
                    # Para archivos binarios, solo indicar tamaño
                    datos_procesados["contenido_bruto"] = f"[Contenido binario: {len(content_bytes)} bytes]"
            
            except Exception as e:
                print(f"Error al procesar contenido del archivo: {str(e)}")
                datos_procesados["error_procesamiento"] = str(e)
        
        return datos_procesados