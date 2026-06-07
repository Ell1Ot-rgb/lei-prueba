import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class N8nIntegrator:
    """Clase para integrar el sistema YO Estructural con n8n"""
    
    def __init__(self):
        # Cargar configuración desde variables de entorno
        self.n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/fenomenologia')
        self.n8n_api_key = os.getenv('N8N_API_KEY', '')
        self.n8n_base_url = os.getenv('N8N_BASE_URL', 'http://localhost:5678')
        
        # Configurar headers para API de n8n
        self.headers = {
            'Content-Type': 'application/json'
        }
        
        if self.n8n_api_key:
            self.headers['X-N8N-API-KEY'] = self.n8n_api_key
    
    def enviar_datos_webhook(self, datos, origen="api"):
        """Envía datos al webhook de n8n"""
        payload = {
            "datos": datos,
            "origen": origen,
            "timestamp": datetime.now().isoformat(),
            "sistema": "YO_estructural"
        }
        
        try:
            response = requests.post(
                self.n8n_webhook_url,
                headers=self.headers,
                json=payload
            )
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else None,
                "error": None if response.status_code == 200 else response.text
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "response": None,
                "error": str(e)
            }
    
    def obtener_workflows(self):
        """Obtiene la lista de workflows disponibles en n8n"""
        try:
            response = requests.get(
                f"{self.n8n_base_url}/api/v1/workflows",
                headers=self.headers
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Error al obtener workflows: {str(e)}")
            return None
    
    def activar_workflow(self, workflow_id):
        """Activa un workflow específico en n8n"""
        try:
            response = requests.post(
                f"{self.n8n_base_url}/api/v1/workflows/{workflow_id}/activate",
                headers=self.headers
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error al activar workflow: {str(e)}")
            return False
    
    def ejecutar_workflow(self, workflow_id, datos):
        """Ejecuta un workflow específico con datos"""
        try:
            response = requests.post(
                f"{self.n8n_base_url}/api/v1/workflows/{workflow_id}/execute",
                headers=self.headers,
                json=datos
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Error al ejecutar workflow: {str(e)}")
            return None