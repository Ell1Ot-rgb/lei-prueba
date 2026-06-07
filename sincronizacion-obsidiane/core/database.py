from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, ClientError, TransientError
import logging
import time
import random

class Neo4jConnection:
    """Clase mejorada para gestionar conexiones a Neo4j con manejo de errores robusto"""
    
    def __init__(self, uri, user, password, database=None, timeout=30, max_retry=3, pool_size=50):
        """Inicializa la conexión a Neo4j con parámetros avanzados
        
        Args:
            uri (str): URI de conexión a Neo4j (bolt://host:port)
            user (str): Nombre de usuario
            password (str): Contraseña
            database (str, optional): Nombre de la base de datos. Por defecto None (usa la predeterminada)
            timeout (int, optional): Tiempo de espera en segundos. Por defecto 30
            max_retry (int, optional): Número máximo de reintentos. Por defecto 3
            pool_size (int, optional): Tamaño del pool de conexiones. Por defecto 50
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self.timeout = timeout
        self.max_retry = max_retry
        self.logger = logging.getLogger("Neo4jConnection")
        
        # Configuración del driver con parámetros avanzados
        try:
            self._driver = GraphDatabase.driver(
                uri, 
                auth=(user, password),
                max_connection_pool_size=pool_size,
                connection_timeout=timeout
            )
            # Verificar conexión al inicializar
            self.verify_connection()
            self.logger.info(f"Conexión a Neo4j establecida exitosamente: {uri}")
        except Exception as e:
            self.logger.error(f"Error al inicializar conexión a Neo4j: {str(e)}")
            raise

    def close(self):
        """Cierra la conexión a Neo4j de manera segura"""
        if self._driver is not None:
            try:
                self._driver.close()
                self.logger.info("Conexión a Neo4j cerrada correctamente")
            except Exception as e:
                self.logger.error(f"Error al cerrar conexión a Neo4j: {str(e)}")

    def verify_connection(self):
        """Verifica que la conexión a Neo4j esté activa
        
        Returns:
            bool: True si la conexión está activa, False en caso contrario
        """
        try:
            with self._driver.session(database=self.database) as session:
                result = session.run("RETURN 1 AS num")
                return result.single()["num"] == 1
        except Exception as e:
            self.logger.error(f"Error al verificar conexión a Neo4j: {str(e)}")
            return False

    def query(self, query, parameters=None):
        """Ejecuta una consulta en Neo4j con reintentos y manejo de errores
        
        Args:
            query (str): Consulta Cypher a ejecutar
            parameters (dict, optional): Parámetros para la consulta. Por defecto None
            
        Returns:
            list: Lista de registros resultantes de la consulta
        """
        data = []
        retry_count = 0
        last_exception = None
        
        while retry_count <= self.max_retry:
            try:
                with self._driver.session(database=self.database) as session:
                    result = session.run(query, parameters)
                    for record in result:
                        data.append(record.data())
                    return data
            except (ServiceUnavailable, TransientError) as e:
                # Errores transitorios que pueden resolverse con reintentos
                last_exception = e
                retry_count += 1
                if retry_count <= self.max_retry:
                    # Backoff exponencial con jitter para evitar tormentas de conexiones
                    wait_time = (2 ** retry_count) + (random.randint(0, 1000) / 1000)
                    self.logger.warning(f"Reintento {retry_count}/{self.max_retry} después de {wait_time:.2f}s. Error: {str(e)}")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Máximo de reintentos alcanzado ({self.max_retry}). Error: {str(e)}")
                    raise
            except ClientError as e:
                # Errores de cliente (consulta mal formada, etc.) que no se resuelven con reintentos
                self.logger.error(f"Error de cliente en consulta Neo4j: {str(e)}")
                raise
            except Exception as e:
                # Otros errores inesperados
                self.logger.error(f"Error inesperado en consulta Neo4j: {str(e)}")
                raise
        
        if last_exception:
            raise last_exception
        return data
    
    def execute_transaction(self, tx_function, *args, **kwargs):
        """Ejecuta una transacción en Neo4j con reintentos
        
        Args:
            tx_function (callable): Función que recibe una transacción como primer argumento
            *args: Argumentos posicionales para tx_function
            **kwargs: Argumentos de palabra clave para tx_function
            
        Returns:
            any: Resultado de la transacción
        """
        retry_count = 0
        last_exception = None
        
        while retry_count <= self.max_retry:
            try:
                with self._driver.session(database=self.database) as session:
                    return session.execute_write(tx_function, *args, **kwargs)
            except (ServiceUnavailable, TransientError) as e:
                last_exception = e
                retry_count += 1
                if retry_count <= self.max_retry:
                    wait_time = (2 ** retry_count) + (random.randint(0, 1000) / 1000)
                    self.logger.warning(f"Reintento de transacción {retry_count}/{self.max_retry} después de {wait_time:.2f}s")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Máximo de reintentos de transacción alcanzado ({self.max_retry})")
                    raise
            except Exception as e:
                self.logger.error(f"Error en transacción Neo4j: {str(e)}")
                raise
        
        if last_exception:
            raise last_exception

