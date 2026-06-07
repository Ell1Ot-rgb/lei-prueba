"""
Orquestador de Sistemas de Capa 2
==================================

Integra los 3 sistemas de Capa 2:
1. Sistema Principal (YO Estructural)
2. Sistema de Emergencia de Conceptos (S2)
3. Sistema de Lógica Pura (S3)

Con Sistema de Capa 1 (Monje Gemelo vía Redis)
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Sistema Principal (S1 de Capa 2)
from core.sistema_principal import SistemaYoEstructural

# Sistema 2: Emergencia de Conceptos
from emergencia_concepto.motor_emergencia import MotorEmergenciaConceptos

# Sistema 3: Lógica Pura
from logica_pura.motor_hipotetico import MotorHipotetico

# Conexión con Capa 1
from integraciones.redis_connector import RedisMonjeConnector

logger = logging.getLogger("OrquestadorCapa2")


class OrquestadorCapa2:
    """
    Orquestador maestro de los 3 sistemas de Capa 2.
    
    Flujo:
    ======
    
    1. Capa 1 (Monje) -> Redis -> Vector Físico
    2. S1 (Principal) -> Procesa -> Grundzugs
    3. S2 (Emergencia) -> Refina conceptos desde Grundzugs
    4. S3 (Lógica) -> Valida axiomas lógicos
    5. Feedback loop -> Auto-calibración
    
    """
    
    def __init__(self, config_path: str):
        """
        Inicializa los 3 sistemas de Capa 2.
        
        Args:
            config_path: Ruta a config YAML
        """
        self.config_path = config_path
        
        logger.info("="*70)
        logger.info("INICIALIZANDO ORQUESTADOR CAPA 2")
        logger.info("="*70)
        
        # ============================================
        # SISTEMA 1: YO ESTRUCTURAL (Principal)
        # ============================================
        logger.info("\n[1/3] Inicializando Sistema Principal...")
        self.sistema_principal = SistemaYoEstructural(config_path)
        logger.info("✅ Sistema Principal listo")
        
        # ============================================
        # SISTEMA 2: EMERGENCIA DE CONCEPTOS
        # ============================================
        logger.info("\n[2/3] Inicializando Sistema de Emergencia...")
        self.sistema_emergencia = MotorEmergenciaConceptos(
            state_file="estado_emergencia_capa2.pkl"
        )
        logger.info("✅ Sistema de Emergencia listo")
        
        # ============================================
        # SISTEMA 3: LÓGICA PURA
        # ============================================
        logger.info("\n[3/3] Inicializando Sistema de Lógica Pura...")
        self.sistema_logica = MotorHipotetico(
            state_file="estado_logica_pura_capa2.pkl"
        )
        logger.info("✅ Sistema de Lógica Pura listo")
        
        # ============================================
        # CONEXIÓN CON CAPA 1 (MONJE GEMELO)
        # ============================================
        logger.info("\n[REDIS] Conectando con Capa 1 (Monje Gemelo)...")
        try:
            self.conector_monje = RedisMonjeConnector(
                host="localhost",
                port=6379
            )
            if self.conector_monje.conectar():
                logger.info("✅ Conexión Redis establecida")
                self.monje_disponible = True
            else:
                logger.warning("⚠️ Redis no disponible - modo standalone")
                self.monje_disponible = False
        except Exception as e:
            logger.warning(f"⚠️ Error conectando Redis: {e}")
            self.monje_disponible = False
        
        # Estado del orquestador
        self.iteracion = 0
        self.estadisticas = {
            'total_procesados': 0,
            'grundzugs_generados': 0,
            'conceptos_emergidos': 0,
            'axiomas_aprendidos': 0,
            'convergencias_detectadas': 0
        }
        
        logger.info("\n" + "="*70)
        logger.info("✅ ORQUESTADOR CAPA 2 LISTO")
        logger.info("="*70 + "\n")
    
    def procesar_desde_monje(self, duracion_segundos: int = 60) -> Dict[str, Any]:
        """
        Escucha eventos de Monje Gemelo (Capa 1) y procesa en tiempo real.
        
        Args:
            duracion_segundos: Tiempo de escucha
        
        Returns:
            Estadísticas de procesamiento
        """
        if not self.monje_disponible:
            logger.error("❌ Monje no disponible")
            return {'error': 'monje_no_disponible'}
        
        logger.info(f"👂 Escuchando Monje por {duracion_segundos}s...")
        
        import time
        inicio = time.time()
        eventos_procesados = 0
        
        self.conector_monje.suscribirse(["monje/fenomenologia/*"])
        
        for evento in self.conector_monje.escuchar_eventos():
            # Procesar evento
            resultado = self.procesar_evento_fisico(evento)
            eventos_procesados += 1
            
            logger.info(f"  ✓ Evento {eventos_procesados} procesado")
            
            # Verificar tiempo
            if time.time() - inicio > duracion_segundos:
                logger.info(f"⏱️ Tiempo cumplido: {eventos_procesados} eventos")
                break
        
        return {
            'eventos_procesados': eventos_procesados,
            'duracion': time.time() - inicio,
            'estadisticas': self.estadisticas
        }
    
    def procesar_evento_fisico(self, vector_fenomenologico: Dict) -> Dict[str, Any]:
        """
        Procesa un evento físico a través de los 3 sistemas.
        
        Flujo:
        ------
        Vector Físico -> S1 -> Grundzugs -> S2 + S3 -> Validación cruzada
        
        Args:
            vector_fenomenologico: Dict con intensidad, complejidad, tipo_base, origen_fisico
        
        Returns:
            Resultado consolidado de los 3 sistemas
        """
        self.iteracion += 1
        
        logger.info(f"\n{'='*70}")
        logger.info(f"PROCESANDO EVENTO #{self.iteracion}")
        logger.info(f"{'='*70}")
        
        # =============================================
        # PASO 1: SISTEMA PRINCIPAL (S1)
        # =============================================
        logger.info("\n[S1] Procesando en Sistema Principal...")
        
        # Extraer origen físico
        origen_fisico = vector_fenomenologico.get('origen_fisico', {})
        hash_fisico = origen_fisico.get('hash', 'unknown')
        
        # Procesar con motor YO
        # (Aquí conectar con método específico del sistema principal)
        grundzugs_generados = self._procesar_con_s1(vector_fenomenologico)
        
        self.estadisticas['total_procesados'] += 1
        self.estadisticas['grundzugs_generados'] += len(grundzugs_generados)
        
        logger.info(f"  ✓ S1: {len(grundzugs_generados)} Grundzugs generados")
        
        # =============================================
        # PASO 2: SISTEMA DE EMERGENCIA (S2)
        # =============================================
        logger.info("\n[S2] Procesando emergencia de conceptos...")
        
        resultado_s2 = self.sistema_emergencia.ciclo_incremental(
            nuevos_grundzugs=grundzugs_generados
        )
        
        self.estadisticas['conceptos_emergidos'] += len(resultado_s2.get('conceptos', []))
        
        if resultado_s2.get('convergencia'):
            self.estadisticas['convergencias_detectadas'] += 1
        
        logger.info(f"  ✓ S2: Certeza patrón={resultado_s2['patron_certeza']:.3f}")
        logger.info(f"  ✓ S2: Convergencia={'SÍ' if resultado_s2['convergencia'] else 'NO'}")
        
        # =============================================
        # PASO 3: SISTEMA DE LÓGICA PURA (S3)
        # =============================================
        logger.info("\n[S3] Procesando lógica pura...")
        
        # Crear observaciones desde Grundzugs
        observaciones = self._grundzugs_to_observaciones(grundzugs_generados)
        
        resultado_s3 = self.sistema_logica.ciclo_incremental(
            mundo_nombre="mundo_capa2",
            nuevos_grundzugs=grundzugs_generados,
            observaciones=observaciones
        )
        
        self.estadisticas['axiomas_aprendidos'] += resultado_s3.get('axiomas_nuevos_aprendidos', 0)
        
        logger.info(f"  ✓ S3: {resultado_s3['objetos_totales']} objetos en mundo")
        logger.info(f"  ✓ S3: {resultado_s3['axiomas_totales']} axiomas totales")
        
        # =============================================
        # PASO 4: VALIDACIÓN CRUZADA
        # =============================================
        logger.info("\n[VALIDACIÓN] Comparando S2 vs S3...")
        
        validacion = self._validar_s2_vs_s3(resultado_s2, resultado_s3)
        
        logger.info(f"  ✓ Consistencia: {validacion['consistencia']:.2%}")
        
        # =============================================
        # RESULTADO CONSOLIDADO
        # =============================================
        resultado = {
            'iteracion': self.iteracion,
            'timestamp': datetime.now().isoformat(),
            'hash_fisico': hash_fisico,
            
            's1_resultado': {
                'grundzugs': len(grundzugs_generados),
                'grundzugs_list': grundzugs_generados
            },
            
            's2_resultado': {
                'patron_certeza': resultado_s2['patron_certeza'],
                'convergencia': resultado_s2['convergencia'],
                'conceptos': resultado_s2.get('conceptos', [])
            },
            
            's3_resultado': {
                'objetos_totales': resultado_s3['objetos_totales'],
                'axiomas_totales': resultado_s3['axiomas_totales'],
                'axiomas_nuevos': resultado_s3['axiomas_nuevos_aprendidos'],
                'validacion': resultado_s3.get('validacion', {})
            },
            
            'validacion_cruzada': validacion,
            'estadisticas_globales': self.estadisticas
        }
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ EVENTO #{self.iteracion} COMPLETADO")
        logger.info(f"{'='*70}\n")
        
        return resultado
    
    def _procesar_con_s1(self, vector_fenomenologico: Dict) -> List[Dict]:
        """
        Procesa con Sistema Principal y extrae Grundzugs.
        
        Returns:
            Lista de Grundzugs en formato dict
        """
        # Consultar Neo4j para obtener Grundzugs recientes
        # (Simplificado - en producción consultar BD)
        
        grundzugs = [
            {
                'nombre': 'concepto_ejemplo',
                'certeza': 0.75,
                'nivel': 1,
                'instancias_count': 10,
                'qualia_dominante': 'visual',
                'origen': 'sistema_principal'
            }
        ]
        
        return grundzugs
    
    def _grundzugs_to_observaciones(self, grundzugs: List[Dict]) -> List[Dict]:
        """
        Convierte Grundzugs a observaciones para S3.
        """
        observaciones = []
        
        for g in grundzugs:
            if g.get('certeza', 0) > 0.7:
                observaciones.append({
                    'sujeto': g['nombre'],
                    'predicado': 'existente',
                    'objeto': 'realidad',
                    'certeza': g['certeza']
                })
                
                if g.get('nivel', 1) > 1:
                    observaciones.append({
                        'sujeto': g['nombre'],
                        'predicado': 'abstracto',
                        'objeto': 'concepto',
                        'certeza': g['certeza']
                    })
        
        return observaciones
    
    def _validar_s2_vs_s3(self, resultado_s2: Dict, resultado_s3: Dict) -> Dict:
        """
        Valida consistencia entre S2 y S3.
        """
        # Verificar que conceptos emergidos (S2) tengan soporte lógico (S3)
        
        conceptos_s2 = len(resultado_s2.get('conceptos', []))
        axiomas_s3 = resultado_s3.get('axiomas_totales', 0)
        
        # Heurística simple: si hay axiomas, hay consistencia
        consistencia = min(1.0, axiomas_s3 / max(1, conceptos_s2))
        
        return {
            'consistencia': consistencia,
            'conceptos_s2': conceptos_s2,
            'axiomas_s3': axiomas_s3,
            'validacion_exitosa': consistencia > 0.7
        }
    
    def generar_reporte_completo(self) -> Dict[str, Any]:
        """
        Genera reporte consolidado de los 3 sistemas.
        """
        return {
            'iteracion_actual': self.iteracion,
            'estadisticas_globales': self.estadisticas,
            
            's1_estado': {
                'activo': True,
                'grundzugs_generados': self.estadisticas['grundzugs_generados']
            },
            
            's2_estado': self.sistema_emergencia.generar_reporte_completo(),
            
            's3_estado': self.sistema_logica.generar_reporte_completo(),
            
            'monje_disponible': self.monje_disponible
        }


# =============================================
# EJEMPLO DE USO
# =============================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Inicializar orquestador
    orquestador = OrquestadorCapa2("configuracion/config_4gb.yaml")
    
    # OPCIÓN 1: Escuchar Monje en tiempo real
    if orquestador.monje_disponible:
        resultado = orquestador.procesar_desde_monje(duracion_segundos=60)
        print(f"\n✅ Procesados {resultado['eventos_procesados']} eventos")
    
    # OPCIÓN 2: Procesar evento manual
    else:
        evento_test = {
            'intensidad': 0.512,
            'complejidad': 0.755,
            'tipo_base': 'narrativo',
            'origen_fisico': {
                'hash': 'a7f3e2d9c1b4a8f3',
                'energia_uj': 5120,
                'ciclos': 2450000
            }
        }
        
        resultado = orquestador.procesar_evento_fisico(evento_test)
        print(f"\n✅ Evento procesado")
        print(f"  - Grundzugs: {resultado['s1_resultado']['grundzugs']}")
        print(f"  - Conceptos S2: {len(resultado['s2_resultado']['conceptos'])}")
        print(f"  - Axiomas S3: {resultado['s3_resultado']['axiomas_nuevos']}")
    
    # Generar reporte final
    reporte = orquestador.generar_reporte_completo()
    
    import json
    with open("reporte_orquestador_capa2.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📊 Reporte guardado: reporte_orquestador_capa2.json")
