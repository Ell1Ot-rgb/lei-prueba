"""
Orquestador del Pipeline Evolucionado — v4.0
=============================================

Conecta TODOS los motores del sistema hexagonal:
    S1 ∂ → S2 ∫ → Fenómeno ◉ → Contexto ⊞ → Macrocontexto ⊡ →
    Metacontexto ⊠ → YO ☉ → Retroalimentación ⟳ → Voluntad → Lógica

Entrada del sistema: :-....yo...
Salida: Obsidian (9 niveles + 5 sistemas lógicos) + Neo4j + n8n webhook

Cambios v4.0:
    - _sincronizar_obsidian: añade generar_moc_relaciones()
    - _sincronizar_logica_extendida: 5 sistemas lógicos + ciclo ⟳
    - procesar(): llama a ambas sincronizaciones en paso 10
    - Simbología corregida: Metacontexto = ⊠ (Nivel +3), Macrocontexto = ⊡ (Nivel +2)

Este archivo NO modifica ningún motor existente.
Solo ORQUESTA la comunicación entre módulos.
"""

import logging
import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger("pipeline_evolucionado")


class PipelineEvolucionado:
    """
    Orquestador que conecta los módulos nuevos con los existentes.

    Pipeline completo:
        1. Entrada bruta → S1 ∂ (existente)
        2. S1 → S2 ∫ (existente) → Genera grundzugs
        3. S2 → Fenómeno ◉ (NUEVO) → Agrupa vohexistencias
        4. Fenómeno → Contexto ⊞ (NUEVO) → Estructura narrativa
        5. Contexto → Macrocontexto ⊡ (NUEVO) → Agrupación
        6. Macrocontexto → Metacontexto ⊠ (NUEVO) → Reflexión
        7. Metacontexto → YO ☉ (NUEVO) → Emergencia
        8. YO → Retroalimentación ⟳ (NUEVO) → Resignificación
        9. YO → Voluntad → (NUEVO) → Proyección
       10. Todo → Obsidian (NUEVO) + Neo4j + YAML (existente)
    """

    ENTRADA_SISTEMA = ":-....yo..."

    def __init__(
        self,
        vault_obsidian_path: str = None,
        carpeta_entrada: str = None,
        neo4j_config: Dict = None,
        n8n_webhook_url: str = None,
    ):
        """
        Args:
            vault_obsidian_path: Ruta al vault de Obsidian
            carpeta_entrada: Carpeta compartida para datos brutos
            neo4j_config: Config de Neo4j Azure (host, port, user, pass)
            n8n_webhook_url: URL del webhook de n8n
        """
        # ── Configuración ───────────────────────────────
        self.vault_path = vault_obsidian_path
        self.carpeta_entrada = carpeta_entrada
        self.neo4j_config = neo4j_config or {}
        self.n8n_webhook_url = n8n_webhook_url

        # ── Motores existentes (se inyectan) ────────────
        self._motor_s1 = None  # Se conecta externamente
        self._motor_s2 = None
        self._motor_s3 = None
        self._motor_s4 = None
        self._motor_bio = None
        self._motor_chaos = None

        # ── Motores nuevos ──────────────────────────────
        from core_new.engines.yo_emergente.motor_yo import MotorYoEmergente
        from core_new.engines.relaciones.generador_relaciones import GeneradorRelaciones
        from core_new.engines.retroalimentacion.ciclo_resignificacion import CicloResignificacion
        from core_new.engines.voluntad.motor_voluntad import MotorVoluntad

        self.motor_yo = MotorYoEmergente()
        self.generador_relaciones = GeneradorRelaciones()
        self.ciclo_retroalimentacion = CicloResignificacion()
        self.motor_voluntad = MotorVoluntad()

        # ── Adaptador Obsidian ──────────────────────────
        self.obsidian = None
        if vault_obsidian_path:
            from adapters.outbound.obsidian_sync import ObsidianSync
            self.obsidian = ObsidianSync(vault_obsidian_path)

        # ── Estado de procesamiento ─────────────────────
        self.procesamiento_id = 0
        self.ultimo_resultado = None

        logger.info("Pipeline Evolucionado inicializado")
        logger.info(f"  Entrada: {self.ENTRADA_SISTEMA}")
        logger.info(f"  Obsidian: {vault_obsidian_path or 'desactivado'}")

    def conectar_motores_existentes(
        self,
        s1=None, s2=None, s3=None, s4=None,
        bio=None, chaos=None,
    ):
        """Inyecta los motores existentes del sistema hexagonal"""
        self._motor_s1 = s1
        self._motor_s2 = s2
        self._motor_s3 = s3
        self._motor_s4 = s4
        self._motor_bio = bio
        self._motor_chaos = chaos

    def procesar(
        self,
        datos_s1: Optional[Dict] = None,
        datos_s2: Optional[Dict] = None,
        vohexistencias: Optional[List[Dict]] = None,
        estado_emocional: Optional[Dict] = None,
    ) -> Dict:
        """
        Ejecuta el pipeline evolucionado completo.

        Args:
            datos_s1: Salida de S1 (grundzugs, embeddings)
            datos_s2: Salida de S2 (conceptos emergentes)
            vohexistencias: Vohexistencias activas
            estado_emocional: Valencia emocional actual

        Returns:
            Dict con resultados de todos los niveles
        """
        self.procesamiento_id += 1
        timestamp = datetime.datetime.now().isoformat()
        resultado = {
            "id": self.procesamiento_id,
            "timestamp": timestamp,
            "entrada": self.ENTRADA_SISTEMA,
        }

        # ═══════════════════════════════════════════════
        # PASO 3: Vohexistencias → Fenómenos ◉
        # ═══════════════════════════════════════════════
        fenomenos = self._generar_fenomenos(vohexistencias or [])
        resultado["fenomenos"] = [f.to_dict() for f in fenomenos]

        # ═══════════════════════════════════════════════
        # PASO 4: Fenómenos → Contextos ⊞
        # ═══════════════════════════════════════════════
        contextos = self._generar_contextos(fenomenos, estado_emocional)
        resultado["contextos"] = [c.to_dict() for c in contextos]

        # ═══════════════════════════════════════════════
        # PASO 5: Contextos → Macrocontextos ⊡
        # ═══════════════════════════════════════════════
        macrocontextos = self._generar_macrocontextos(contextos, fenomenos)
        resultado["macrocontextos"] = [m.to_dict() for m in macrocontextos]

        # ═══════════════════════════════════════════════
        # PASO 6: Macrocontextos → Metacontextos ⊠
        # ═══════════════════════════════════════════════
        metacontextos = self._generar_metacontextos(macrocontextos)
        resultado["metacontextos"] = [m.to_dict() for m in metacontextos]

        # ═══════════════════════════════════════════════
        # PASO 7: Metacontextos → YO ☉
        # ═══════════════════════════════════════════════
        estado_yo = self.motor_yo.evaluar(
            metacontextos=[m.to_dict() for m in metacontextos],
            fenomenos_activos=[f.to_dict() for f in fenomenos],
            estado_bio=None,
            estado_s1=datos_s1,
            estado_emocional=estado_emocional,
            conceptos_emergentes=(
                datos_s2.get("conceptos", []) if datos_s2 else None
            ),
            axiomas_derivados=None,
        )
        resultado["yo_emergente"] = estado_yo

        # ═══════════════════════════════════════════════
        # PASO 8: YO → Retroalimentación ⟳
        # ═══════════════════════════════════════════════
        resignificaciones = list(
            self.ciclo_retroalimentacion.resignificar(
                yo_estado=estado_yo,
                instancias_origen=vohexistencias or [],
            )
        )
        resultado["retroalimentacion"] = resignificaciones

        # ═══════════════════════════════════════════════
        # PASO 9: YO → Voluntad →
        # ═══════════════════════════════════════════════
        proyeccion = self.motor_voluntad.proyectar(
            estado_yo=estado_yo,
            contextos_activos=[c.to_dict() for c in contextos],
        )
        resultado["voluntad"] = proyeccion

        # ═══════════════════════════════════════════════
        # PASO 10: Sincronización Obsidian — v4.0
        # ═══════════════════════════════════════════════
        if self.obsidian:
            # 10a. Niveles ontológicos (◉ ⊞ ⊡ ⊠ ☉ →)
            self._sincronizar_obsidian(
                fenomenos, contextos, macrocontextos,
                metacontextos, estado_yo, proyeccion
            )
            # 10b. Sistemas lógicos (⊢ □◇ ⊂∪ OFP) + ciclo ⟳
            self._sincronizar_logica_extendida(
                metacontextos=metacontextos,
                proyeccion=proyeccion,
                instancias_origen=vohexistencias or [],
                estado_yo=estado_yo,
            )

        self.ultimo_resultado = resultado
        return resultado

    # ─────────────────────────────────────────────────────
    # GENERADORES DE NIVELES
    # ─────────────────────────────────────────────────────

    def _generar_fenomenos(self, vohexistencias: List[Dict]):
        """Agrupa vohexistencias en fenómenos por co-ocurrencia"""
        from core_new.domain.fenomeno import Fenomeno

        fenomenos = []

        if not vohexistencias:
            return fenomenos

        # Crear un fenómeno por cada vohexistencia con peso > umbral
        for vohex in vohexistencias:
            peso = vohex.get("peso_coexistencial", 0.0)
            if peso > 0.3:
                fen = Fenomeno(
                    contenido=vohex.get("constante_emergente",
                                       vohex.get("nombre", "")),
                    tipo="general",
                )
                fen.agregar_vohexistencia_origen(vohex.get("id", ""))
                fen.intensidad = peso
                fen.frecuencia = len(vohex.get("instancias", []))
                fen.evaluar_nuclearidad()
                fenomenos.append(fen)

        return fenomenos

    def _generar_contextos(self, fenomenos, estado_emocional):
        """Agrupa fenómenos en contextos con estructura narrativa"""
        from core_new.domain.contexto import Contexto

        if not fenomenos:
            return []

        # Crear un contexto que agrupe todos los fenómenos activos
        ctx = Contexto(
            descripcion=f"Contexto de procesamiento #{self.procesamiento_id}"
        )

        for fen in fenomenos:
            ctx.agregar_fenomeno(fen.id)

        # Si hay estado emocional, activar YO presente
        if estado_emocional:
            ctx.activar_yo()

        ctx.evaluar_nivel_narrativo()

        return [ctx]

    def _generar_macrocontextos(self, contextos, fenomenos):
        """Agrupa contextos por fenómenos compartidos"""
        from core_new.domain.metacontexto import Macrocontexto

        if len(contextos) < 1:
            return []

        macro = Macrocontexto(
            nombre=f"Macro #{self.procesamiento_id}"
        )
        for ctx in contextos:
            macro.agregar_contexto(ctx.id)

        # Fenómenos compartidos = todos los que aparecen en >1 contexto
        fen_ids = set()
        for ctx in contextos:
            fen_ids.update(ctx.fenomenos)
        macro.fenomenos_compartidos = list(fen_ids)

        macro.evaluar_coherencia()

        return [macro]

    def _generar_metacontextos(self, macrocontextos):
        """Genera metacontextos por variación eidética"""
        from core_new.domain.metacontexto import Metacontexto

        if not macrocontextos:
            return []

        meta = Metacontexto()
        for macro in macrocontextos:
            meta.agregar_macrocontexto(macro.id)
            if macro.patron_emergente:
                meta.agregar_invariante(macro.patron_emergente)

        meta.patron_emergente = (
            f"Convergencia de {len(macrocontextos)} macrocontextos"
        )
        meta.evaluar_coherencia()

        return [meta]

    # ─────────────────────────────────────────────────────
    # SINCRONIZACIÓN OBSIDIAN
    # ─────────────────────────────────────────────────────

    def _sincronizar_obsidian(
        self, fenomenos, contextos, macrocontextos,
        metacontextos, estado_yo, proyeccion,
    ):
        """Sincroniza todos los resultados con Obsidian"""
        try:
            # Guardar cada nivel
            for fen in fenomenos:
                self.obsidian.guardar_entidad(0, fen.id, fen.to_obsidian_md())

            for ctx in contextos:
                self.obsidian.guardar_entidad(1, ctx.id, ctx.to_obsidian_md())

            for macro in macrocontextos:
                self.obsidian.guardar_entidad(
                    2, macro.id, macro.to_obsidian_md()
                )

            for meta in metacontextos:
                self.obsidian.guardar_entidad(
                    3, meta.id, meta.to_obsidian_md()
                )

            # YO Emergente
            self.obsidian.guardar_entidad(
                4, self.motor_yo.id, self.motor_yo.to_obsidian_md()
            )

            # Voluntad
            self.obsidian.guardar_voluntad(
                proyeccion.get("id", "proy"),
                self.motor_voluntad.to_obsidian_md()
            )

            # Relaciones MOC
            self.obsidian.guardar_relaciones(
                "mapa_relaciones",
                self.generador_relaciones.generar_obsidian_moc()
            )

            # Actualizar MOCs
            self.obsidian.generar_moc_pipeline()
            self.obsidian.generar_moc_niveles()
            self.obsidian.generar_moc_relaciones()

            # Estado
            self.obsidian.actualizar_estado({
                "procesamiento_id": self.procesamiento_id,
                "tipo_yo": estado_yo.get("estado", {}).get("tipo", "?"),
                "fenomenos": len(fenomenos),
                "contextos": len(contextos),
                "macrocontextos": len(macrocontextos),
                "metacontextos": len(metacontextos),
            })

            self.obsidian.log_procesamiento(
                f"Pipeline #{self.procesamiento_id} completado: "
                f"YO={estado_yo.get('estado', {}).get('tipo', '?')}",
                tipo="ok"
            )

        except Exception as e:
            logger.error(f"Error sincronizando Obsidian: {e}")
            if self.obsidian:
                self.obsidian.log_procesamiento(
                    f"Error: {str(e)}", tipo="error"
                )


    # ─────────────────────────────────────────────────────
    # SINCRONIZACION LOGICA EXTENDIDA v4.0
    # ─────────────────────────────────────────────────────

    def _sincronizar_logica_extendida(
        self,
        metacontextos,
        axiomas_nuevos=None,
        mundos_hipoteticos=None,
        proyeccion=None,
        instancias_origen=None,
        estado_yo=None,
    ):
        '''Sincroniza los 5 sistemas logicos y el ciclo hermeneutico.'''
        if not self.obsidian:
            return
        try:
            # 1. Axiomas Horn
            if axiomas_nuevos:
                for ax in axiomas_nuevos:
                    ax_dict = ax.parsed if hasattr(ax, 'parsed') else {}
                    self.obsidian.guardar_axioma(
                        id_axioma='ax_' + str(id(ax))[:6],
                        regla_raw=getattr(ax, 'regla_raw', str(ax)),
                        premisa=ax_dict.get('premisa', '?'),
                        conclusion=ax_dict.get('conclusion', '?'),
                        inferencias=0,
                    )
                self.obsidian.log_procesamiento(
                    str(len(axiomas_nuevos)) + ' axiomas (S3)',
                    tipo='logica'
                )

            # 2. Mundos Hipoteticos
            if mundos_hipoteticos:
                for mundo in mundos_hipoteticos:
                    self.obsidian.guardar_mundo_hipotetico(
                        id_mundo=mundo.get('id', 'mhip'),
                        hechos_base=mundo.get('hechos_base', []),
                        proposiciones=mundo.get('proposiciones', []),
                    )

            # 3. Logica Modal en Metacontextos (Kripke)
            for meta in metacontextos:
                mundos_acc = list(getattr(meta, 'invariantes', []))[:3]
                if mundos_acc:
                    self.obsidian.guardar_estado_modal(
                        id_meta=meta.id,
                        mundos_accesibles=mundos_acc,
                        necesidad=len(mundos_acc) > 1,
                        posibilidad=len(mundos_acc) >= 1,
                    )

            # 4. Logica Deontica en Voluntad
            if proyeccion and proyeccion.get('id'):
                proy_id = proyeccion.get('id', 'proy_?')
                permitido = proyeccion.get('intensidad', 0) > 0
                violaciones = []
                if not permitido:
                    violaciones.append('Proyeccion sin intensidad')
                self.obsidian.guardar_estado_deontico(
                    id_proyeccion=proy_id,
                    permitido=permitido,
                    violaciones=violaciones,
                )

            # 5. Ciclo de Retroalimentacion hermeneutica (usa el ciclo ya ejecutado en paso 8)
            if estado_yo and instancias_origen:
                # Reutilizar el ciclo ya ejecutado en paso 8 para evitar doble procesamiento
                for resignif in self.ciclo_retroalimentacion.resignificaciones:
                    self.obsidian.agregar_resignificacion_a_instancia(
                        instancia_id=resignif.instancia_id,
                        yo_id=resignif.yo_id,
                        tipo_yo=resignif.tipo_yo,
                        sig_original=resignif.significado_original,
                        sig_nuevo=resignif.significado_nuevo,
                        peso=resignif.peso_resignificacion,
                    )
                self.obsidian.log_procesamiento(
                    'Retroalimentacion: ' + str(self.ciclo_retroalimentacion.ciclos_completados) + ' ciclo(s)',
                    tipo='ok'
                )

        except Exception as e:
            logger.error('Error logica extendida: ' + str(e))
            if self.obsidian:
                self.obsidian.log_procesamiento('Error: ' + str(e), tipo='error')
