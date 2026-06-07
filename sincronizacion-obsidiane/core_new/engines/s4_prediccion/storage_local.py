"""
Almacenamiento Local SQLite para S4
====================================

Persistencia local ligera para el historial de tensores,
predicciones y patrones detectados por S4.
"""

import sqlite3
import numpy as np
import json
import time
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

# Import condicional
try:
    from .tensor_fusionado import TensorFusionado
    from .motor_s4 import PrediccionS4
except ImportError:
    from tensor_fusionado import TensorFusionado
    from motor_s4 import PrediccionS4


@dataclass
class S4StorageConfig:
    """Configuración del almacenamiento."""
    db_path: str = "s4_local.db"
    max_tensores: int = 10000       # Mantener últimos N tensores
    max_predicciones: int = 1000    # Mantener últimas N predicciones
    auto_vacuum: bool = True        # Limpiar automáticamente


class S4LocalStorage:
    """
    Almacenamiento SQLite local para S4.
    
    TABLAS:
    =======
    - tensores: Historial de TensorFusionado
    - predicciones: Cache de predicciones
    - patrones_spa: Patrones detectados
    - metricas: Métricas de rendimiento
    - configuracion: Configuración persistente
    
    VENTAJAS:
    =========
    - Ligero (~1MB para 10K tensores)
    - Sin servidor externo
    - Persistencia entre sesiones
    - Queries SQL para análisis
    """
    
    def __init__(self, config: Optional[S4StorageConfig] = None):
        if config is None:
            config = S4StorageConfig()
        self.config = config
        self.db_path = config.db_path
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.db_path) or '.', exist_ok=True)
        
        # Inicializar DB
        self._crear_tablas()
    
    @contextmanager
    def _conexion(self):
        """Context manager para conexión."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _crear_tablas(self):
        """Crea las tablas necesarias."""
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            # Tabla de tensores fusionados
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tensores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    embedding BLOB NOT NULL,
                    esn_state BLOB NOT NULL,
                    pad_emotions BLOB NOT NULL,
                    grundzug_freq BLOB NOT NULL,
                    lyapunov_features BLOB NOT NULL,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            
            # Índice por timestamp
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tensores_timestamp 
                ON tensores(timestamp)
            """)
            
            # Tabla de predicciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predicciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    horizonte INTEGER NOT NULL,
                    prediccion BLOB NOT NULL,
                    incertidumbre BLOB NOT NULL,
                    lyapunov REAL,
                    regimen TEXT,
                    patrones_spa TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            
            # Tabla de patrones SPA
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patrones_spa (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    n_patrones INTEGER,
                    centroides BLOB,
                    matriz_transicion BLOB,
                    distribucion_estacionaria BLOB,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            
            # Tabla de métricas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metricas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    tipo TEXT NOT NULL,
                    valor REAL NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Tabla de configuración
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracion (
                    clave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL,
                    updated_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
    
    # =========================================================================
    # TENSORES
    # =========================================================================
    
    def guardar_tensor(self, tensor: TensorFusionado) -> int:
        """
        Guarda un tensor fusionado.
        
        Args:
            tensor: TensorFusionado a guardar
        
        Returns:
            ID del tensor guardado
        """
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tensores (
                    timestamp, embedding, esn_state, pad_emotions, 
                    grundzug_freq, lyapunov_features
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tensor.timestamp,
                tensor.embedding.tobytes(),
                tensor.esn_state.tobytes(),
                tensor.pad_emotions.tobytes(),
                tensor.grundzug_freq.tobytes(),
                tensor.lyapunov_features.tobytes()
            ))
            
            tensor_id = cursor.lastrowid
            
            # Auto-limpieza
            if self.config.auto_vacuum:
                self._limpiar_tensores_antiguos(conn)
            
            return tensor_id
    
    def guardar_tensores_batch(self, tensores: List[TensorFusionado]) -> int:
        """
        Guarda múltiples tensores en batch.
        
        Args:
            tensores: Lista de TensorFusionado
        
        Returns:
            Número de tensores guardados
        """
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            data = [
                (
                    t.timestamp,
                    t.embedding.tobytes(),
                    t.esn_state.tobytes(),
                    t.pad_emotions.tobytes(),
                    t.grundzug_freq.tobytes(),
                    t.lyapunov_features.tobytes()
                )
                for t in tensores
            ]
            
            cursor.executemany("""
                INSERT INTO tensores (
                    timestamp, embedding, esn_state, pad_emotions, 
                    grundzug_freq, lyapunov_features
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, data)
            
            if self.config.auto_vacuum:
                self._limpiar_tensores_antiguos(conn)
            
            return len(tensores)
    
    def cargar_tensor(self, tensor_id: int) -> Optional[TensorFusionado]:
        """
        Carga un tensor por ID.
        
        Args:
            tensor_id: ID del tensor
        
        Returns:
            TensorFusionado o None
        """
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM tensores WHERE id = ?
            """, (tensor_id,))
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            return self._row_to_tensor(row)
    
    def cargar_tensores_recientes(self, n: int = 100) -> List[TensorFusionado]:
        """
        Carga los N tensores más recientes.
        
        Args:
            n: Número de tensores a cargar
        
        Returns:
            Lista de TensorFusionado
        """
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM tensores 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (n,))
            
            rows = cursor.fetchall()
            return [self._row_to_tensor(row) for row in reversed(rows)]
    
    def cargar_tensores_rango(self, 
                              desde: float, 
                              hasta: float) -> List[TensorFusionado]:
        """
        Carga tensores en un rango de tiempo.
        
        Args:
            desde: Timestamp inicial
            hasta: Timestamp final
        
        Returns:
            Lista de TensorFusionado
        """
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM tensores 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            """, (desde, hasta))
            
            rows = cursor.fetchall()
            return [self._row_to_tensor(row) for row in rows]
    
    def _row_to_tensor(self, row: sqlite3.Row) -> TensorFusionado:
        """Convierte una fila SQL a TensorFusionado."""
        return TensorFusionado(
            embedding=np.frombuffer(row['embedding'], dtype=np.float32),
            esn_state=np.frombuffer(row['esn_state'], dtype=np.float32),
            pad_emotions=np.frombuffer(row['pad_emotions'], dtype=np.float32),
            grundzug_freq=np.frombuffer(row['grundzug_freq'], dtype=np.float32),
            lyapunov_features=np.frombuffer(row['lyapunov_features'], dtype=np.float32),
            timestamp=row['timestamp']
        )
    
    def _limpiar_tensores_antiguos(self, conn: sqlite3.Connection):
        """Elimina tensores antiguos si excede el límite."""
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tensores")
        count = cursor.fetchone()[0]
        
        if count > self.config.max_tensores:
            # Eliminar los más antiguos
            cursor.execute("""
                DELETE FROM tensores 
                WHERE id IN (
                    SELECT id FROM tensores 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                )
            """, (count - self.config.max_tensores,))
    
    # =========================================================================
    # PREDICCIONES
    # =========================================================================
    
    def guardar_prediccion(self, prediccion: PrediccionS4, horizonte: int) -> int:
        """
        Guarda una predicción.
        
        Args:
            prediccion: PrediccionS4 a guardar
            horizonte: Horizonte usado
        
        Returns:
            ID de la predicción guardada
        """
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            # Clasificar régimen
            if prediccion.lyapunov > 0.1:
                regimen = "CAOTICO"
            elif prediccion.lyapunov < -0.1:
                regimen = "ORDENADO"
            else:
                regimen = "BORDE_DEL_CAOS"
            
            cursor.execute("""
                INSERT INTO predicciones (
                    timestamp, horizonte, prediccion, incertidumbre,
                    lyapunov, regimen, patrones_spa
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                prediccion.timestamp,
                horizonte,
                prediccion.prediccion.tobytes(),
                prediccion.incertidumbre.tobytes(),
                prediccion.lyapunov,
                regimen,
                json.dumps(prediccion.patrones_spa) if prediccion.patrones_spa else None
            ))
            
            pred_id = cursor.lastrowid
            
            # Auto-limpieza
            if self.config.auto_vacuum:
                self._limpiar_predicciones_antiguas(conn)
            
            return pred_id
    
    def cargar_predicciones_recientes(self, n: int = 50) -> List[Dict[str, Any]]:
        """
        Carga las N predicciones más recientes.
        
        Args:
            n: Número de predicciones
        
        Returns:
            Lista de diccionarios con predicciones
        """
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, horizonte, lyapunov, regimen, patrones_spa
                FROM predicciones 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (n,))
            
            rows = cursor.fetchall()
            return [
                {
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'horizonte': row['horizonte'],
                    'lyapunov': row['lyapunov'],
                    'regimen': row['regimen'],
                    'patrones_spa': json.loads(row['patrones_spa']) if row['patrones_spa'] else None
                }
                for row in rows
            ]
    
    def _limpiar_predicciones_antiguas(self, conn: sqlite3.Connection):
        """Elimina predicciones antiguas si excede el límite."""
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM predicciones")
        count = cursor.fetchone()[0]
        
        if count > self.config.max_predicciones:
            cursor.execute("""
                DELETE FROM predicciones 
                WHERE id IN (
                    SELECT id FROM predicciones 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                )
            """, (count - self.config.max_predicciones,))
    
    # =========================================================================
    # PATRONES SPA
    # =========================================================================
    
    def guardar_patrones_spa(self, 
                             centroides: np.ndarray,
                             matriz_transicion: np.ndarray,
                             distribucion: np.ndarray) -> int:
        """
        Guarda los patrones SPA entrenados.
        
        Args:
            centroides: Centroides de clusters
            matriz_transicion: Matriz Markoviana
            distribucion: Distribución estacionaria
        
        Returns:
            ID del registro
        """
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO patrones_spa (
                    timestamp, n_patrones, centroides, 
                    matriz_transicion, distribucion_estacionaria
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                time.time(),
                len(centroides),
                centroides.tobytes(),
                matriz_transicion.tobytes(),
                distribucion.tobytes()
            ))
            
            return cursor.lastrowid
    
    def cargar_patrones_spa_reciente(self) -> Optional[Dict[str, np.ndarray]]:
        """
        Carga los patrones SPA más recientes.
        
        Returns:
            Diccionario con centroides, matriz y distribución
        """
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM patrones_spa 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            n_patrones = row['n_patrones']
            
            return {
                'n_patrones': n_patrones,
                'centroides': np.frombuffer(row['centroides'], dtype=np.float32).reshape(n_patrones, -1),
                'matriz_transicion': np.frombuffer(row['matriz_transicion'], dtype=np.float32).reshape(n_patrones, n_patrones),
                'distribucion': np.frombuffer(row['distribucion_estacionaria'], dtype=np.float32)
            }
    
    # =========================================================================
    # MÉTRICAS
    # =========================================================================
    
    def registrar_metrica(self, tipo: str, valor: float, metadata: Optional[Dict] = None):
        """
        Registra una métrica.
        
        Args:
            tipo: Tipo de métrica (ej: 'lyapunov', 'latencia', 'memoria')
            valor: Valor numérico
            metadata: Datos adicionales
        """
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO metricas (timestamp, tipo, valor, metadata)
                VALUES (?, ?, ?, ?)
            """, (
                time.time(),
                tipo,
                valor,
                json.dumps(metadata) if metadata else None
            ))
    
    def obtener_metricas(self, 
                         tipo: str, 
                         ultimas_n: int = 100) -> List[Tuple[float, float]]:
        """
        Obtiene métricas de un tipo.
        
        Args:
            tipo: Tipo de métrica
            ultimas_n: Número de métricas
        
        Returns:
            Lista de (timestamp, valor)
        """
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, valor FROM metricas 
                WHERE tipo = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (tipo, ultimas_n))
            
            return [(row['timestamp'], row['valor']) for row in cursor.fetchall()]
    
    # =========================================================================
    # CONFIGURACIÓN
    # =========================================================================
    
    def set_config(self, clave: str, valor: Any):
        """Guarda una configuración."""
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO configuracion (clave, valor, updated_at)
                VALUES (?, ?, ?)
            """, (clave, json.dumps(valor), time.time()))
    
    def get_config(self, clave: str, default: Any = None) -> Any:
        """Obtiene una configuración."""
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT valor FROM configuracion WHERE clave = ?
            """, (clave,))
            
            row = cursor.fetchone()
            if row is None:
                return default
            
            return json.loads(row['valor'])
    
    # =========================================================================
    # ESTADÍSTICAS
    # =========================================================================
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del almacenamiento."""
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Contar tensores
            cursor.execute("SELECT COUNT(*) FROM tensores")
            stats['total_tensores'] = cursor.fetchone()[0]
            
            # Rango de tiempo
            cursor.execute("""
                SELECT MIN(timestamp), MAX(timestamp) FROM tensores
            """)
            row = cursor.fetchone()
            stats['timestamp_min'] = row[0]
            stats['timestamp_max'] = row[1]
            
            # Contar predicciones
            cursor.execute("SELECT COUNT(*) FROM predicciones")
            stats['total_predicciones'] = cursor.fetchone()[0]
            
            # Distribución de regímenes
            cursor.execute("""
                SELECT regimen, COUNT(*) as count 
                FROM predicciones 
                GROUP BY regimen
            """)
            stats['regimenes'] = {row['regimen']: row['count'] for row in cursor.fetchall()}
            
            # Contar patrones
            cursor.execute("SELECT COUNT(*) FROM patrones_spa")
            stats['total_patrones_guardados'] = cursor.fetchone()[0]
            
            # Tamaño de la DB
            stats['db_size_bytes'] = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            stats['db_size_mb'] = stats['db_size_bytes'] / (1024 * 1024)
            
            return stats
    
    def vaciar(self):
        """Vacía todas las tablas."""
        with self._conexion() as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM tensores")
            cursor.execute("DELETE FROM predicciones")
            cursor.execute("DELETE FROM patrones_spa")
            cursor.execute("DELETE FROM metricas")
            cursor.execute("VACUUM")


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    import tempfile
    
    print("=" * 60)
    print("  TEST: S4 Local Storage (SQLite)")
    print("=" * 60)
    
    # Crear storage temporal
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_s4.db")
        
        config = S4StorageConfig(
            db_path=db_path,
            max_tensores=100
        )
        
        storage = S4LocalStorage(config)
        print(f"\n  DB creada: {db_path}")
        
        # Guardar tensores
        print("\n  Guardando tensores...")
        for i in range(50):
            tensor = TensorFusionado(
                embedding=np.random.randn(64).astype(np.float32),
                esn_state=np.random.randn(100).astype(np.float32),
                pad_emotions=np.random.rand(3).astype(np.float32),
                grundzug_freq=np.random.rand(10).astype(np.float32),
                lyapunov_features=np.random.rand(5).astype(np.float32),
                timestamp=time.time() + i * 0.1
            )
            storage.guardar_tensor(tensor)
        
        # Cargar tensores
        recientes = storage.cargar_tensores_recientes(10)
        print(f"  Tensores recientes: {len(recientes)}")
        
        # Guardar predicción mock
        from motor_s4 import PrediccionS4
        pred = PrediccionS4(
            prediccion=np.random.randn(10, 182).astype(np.float32),
            incertidumbre=np.random.rand(10).astype(np.float32),
            lyapunov=0.15,
            timestamp=time.time()
        )
        pred_id = storage.guardar_prediccion(pred, horizonte=10)
        print(f"  Predicción guardada: ID={pred_id}")
        
        # Métricas
        storage.registrar_metrica('lyapunov', 0.15)
        storage.registrar_metrica('lyapunov', 0.12)
        storage.registrar_metrica('latencia_ms', 125)
        
        metricas = storage.obtener_metricas('lyapunov', 10)
        print(f"  Métricas lyapunov: {len(metricas)}")
        
        # Configuración
        storage.set_config('horizonte_default', 10)
        valor = storage.get_config('horizonte_default')
        print(f"  Config horizonte_default: {valor}")
        
        # Estadísticas
        stats = storage.obtener_estadisticas()
        print(f"\n  📊 ESTADÍSTICAS:")
        print(f"     - Tensores: {stats['total_tensores']}")
        print(f"     - Predicciones: {stats['total_predicciones']}")
        print(f"     - DB Size: {stats['db_size_mb']:.4f} MB")
    
    print("\n" + "=" * 60)
    print("  STORAGE SQLite OPERATIVO ✓")
    print("=" * 60)
