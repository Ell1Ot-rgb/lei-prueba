from __future__ import annotations
import asyncio
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
import structlog

try:
    import yaml
except ImportError:
    yaml = None

logger = structlog.get_logger()

# Import all subsystems
from ..apoptosis.engine import ApoptosisManager
from ..immune.engine import ImmuneEngine, AntigenMemory
from ..temporal.engine import TemporalPredictor
from ..epigenetic.engine import EpigeneticEngine
from ..metabolic.scheduler import MetabolicScheduler
from ..evolution.genetic import GeneticAlgorithm
from ..quantum.simulator import QuantumSimulator
from ..explainability.engine import ExplainabilityEngine
from ..dream.engine import DreamEngine, MemoryReplay
from ..emotion.engine import EmotionEngine
from ..identity.did_engine import DIDEngine
from ..governance.engine import GovernanceEngine
from ..ecosystem.simulator import EcosystemSimulator
from ..autonomy.engine import ResourceAutonomy
from ..trust.engine import TrustEngine
from ..plasticity.engine import PlasticityEngine

@dataclass
class SystemConfig:
    """Configuration for bio-digital system."""
    enable_apoptosis: bool = True
    enable_immune: bool = True
    enable_temporal: bool = False
    enable_quantum: bool = False
    enable_dream: bool = False
    enable_emotion: bool = False
    enable_evolution: bool = False
    temporal_input_dim: int = 128
    hmac_key: Optional[bytes] = None
    device: str = 'cpu'

    @classmethod
    def from_yaml(cls, path: str) -> SystemConfig:
        """Load configuration from YAML file."""
        if yaml is None:
            raise ImportError("PyYAML not installed. Run: pip install pyyaml")
            
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        
        hmac_key_env = config.get('security', {}).get('hmac_key_env', 'BIO_DIGITAL_HMAC_KEY')
        hmac_key = os.getenv(hmac_key_env)
        
        return cls(
            enable_apoptosis=config.get('system', {}).get('enable_apoptosis', True),
            enable_immune=config.get('system', {}).get('enable_immune', True),
            enable_temporal=config.get('system', {}).get('enable_temporal', False),
            enable_quantum=config.get('system', {}).get('enable_quantum', False),
            enable_dream=config.get('system', {}).get('enable_dream', False),
            enable_emotion=config.get('system', {}).get('enable_emotion', False),
            enable_evolution=config.get('system', {}).get('enable_evolution', False),
            temporal_input_dim=config.get('temporal', {}).get('input_dim', 128),
            hmac_key=hmac_key.encode() if hmac_key else None,
            device=config.get('system', {}).get('device', 'cpu')
        )


class SistemaBioDigital:
    """
    Unified bio-digital organism with optimized subsystems.
    
    This is the main orchestrator that manages lifecycle and
    coordinates all biological improvements (v60-v100).
    """
    __slots__ = ('config', '_running', '_tasks',
                 '_apoptosis', '_immune', '_antigen_memory',
                 '_temporal', '_epigenetic', '_metabolic',
                 '_evolution', '_quantum', '_explainability',
                 '_dream', '_memory_replay', '_emotion',
                 '_identity', '_governance', '_ecosystem',
                 '_autonomy', '_trust', '_plasticity')
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self._running = False
        self._tasks: list = []
        
        # --- 1. Vital Systems ---
        
        # Apoptosis (v60)
        if config.enable_apoptosis:
            self._apoptosis = ApoptosisManager(health_registry={}, scheduler=self)
        else:
            self._apoptosis = None
            
        # Immune System (v68)
        if config.enable_immune:
            self._antigen_memory = AntigenMemory()
            self._immune = ImmuneEngine(
                self._antigen_memory,
                hmac_key=config.hmac_key or b'default_key'
            )
        else:
            self._antigen_memory = None
            self._immune = None
            
        # Metabolism (v67)
        self._metabolic = MetabolicScheduler()
        
        # --- 2. Cognitive Systems ---
        
        # Temporal Predictor (v71)
        if config.enable_temporal:
            self._temporal = TemporalPredictor(
                input_dim=config.temporal_input_dim,
                device=config.device
            )
        else:
            self._temporal = None
            
        # Explainability (v74)
        self._explainability = ExplainabilityEngine()
        
        # Dream & Memory (v75)
        self._memory_replay = MemoryReplay()
        if config.enable_dream:
            self._dream = DreamEngine(self._memory_replay, self._temporal)
        else:
            self._dream = None
            
        # Emotion (v83)
        if config.enable_emotion:
            self._emotion = EmotionEngine()
        else:
            self._emotion = None
            
        # --- 3. Evolutionary & Structural ---
        
        # Epigenetic (v80)
        self._epigenetic = EpigeneticEngine(
            storage_dir="data/epigenetic",
            hmac_key=config.hmac_key or b'default_key'
        )
        
        # Evolution (v88)
        if config.enable_evolution:
            self._evolution = GeneticAlgorithm()
        else:
            self._evolution = None
            
        # Plasticity (v64)
        self._plasticity = PlasticityEngine()
        
        # --- 4. Social & Quantum ---
        
        # Identity (v97)
        self._identity = DIDEngine()
        
        # Governance (v99)
        self._governance = GovernanceEngine(policies={})
        
        # Trust (v86)
        self._trust = TrustEngine()
        
        # Ecosystem (v95)
        self._ecosystem = EcosystemSimulator(agents=[], resources={'cpu': 1.0})
        
        # Autonomy (v85)
        self._autonomy = ResourceAutonomy(self._metabolic)
        
        # Quantum (v90)
        if config.enable_quantum:
            self._quantum = QuantumSimulator()
        else:
            self._quantum = None

    async def bootstrap(self) -> None:
        """Initialize all subsystems."""
        logger.info('bio_digital_bootstrap_started', config=self.config)
        
        if self._apoptosis:
            await self._apoptosis.start()
            self._tasks.append(asyncio.create_task(self._heartbeat_loop()))
            
        if self._dream:
            # Dream loop runs in background but only active during idle
            pass
        
        self._running = True
        logger.info('bio_digital_bootstrap_complete')

    async def shutdown(self) -> None:
        """Gracefully shutdown all subsystems."""
        logger.info('bio_digital_shutdown_initiated')
        self._running = False
        
        if self._apoptosis:
            await self._apoptosis.stop()
            
        if self._dream:
            await self._dream.stop_dreaming()
        
        # Cancel background tasks
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        
        logger.info('bio_digital_shutdown_complete')

    async def process_event(self, raw_input: bytes, source_id: str = 'unknown') -> Dict[str, Any]:
        """
        Process an input event through the bio-digital pipeline.
        """
        results = {'success': False, 'stages': []}
        
        try:
            # 1. Immune Check
            if self._immune:
                if not await self._immune.scan_payload(raw_input, source_id):
                    results['blocked_by'] = 'immune_system'
                    return results
                results['stages'].append('immune_passed')
            
            # 2. Metabolic Check
            if not await self._metabolic.allocate_energy('normal'):
                results['blocked_by'] = 'metabolism_throttled'
                return results
            
            # 3. Temporal Prediction (if enabled)
            if self._temporal:
                # Placeholder: convert input to tensor
                # pred = await self._temporal.predict(...)
                results['stages'].append('temporal_prediction')
                
            # 4. Emotional Reaction (if enabled)
            if self._emotion:
                self._emotion.update({'valency': 0.1, 'intensity': 0.5, 'control': 0.0})
                results['mood'] = self._emotion.get_mood()
            
            # 5. Record for Dreaming
            self._memory_replay.add({'input': raw_input, 'source': source_id})
            
            results['success'] = True
            logger.info('event_processed', source=source_id, stages=len(results['stages']))
            
        except Exception as e:
            logger.error('event_processing_failed', source=source_id, error=str(e))
            results['error'] = str(e)
        
        return results

    async def _heartbeat_loop(self) -> None:
        """Send heartbeats to apoptosis manager."""
        while self._running:
            try:
                if self._apoptosis:
                    await self._apoptosis.heartbeat('bio_digital_core')
                
                # Check autonomy
                await self._autonomy.auto_scale()
                
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error('heartbeat_error', error=str(e))

    # Scheduler interface methods
    async def release_resources(self, component_id: str) -> None:
        logger.info('releasing_resources', component=component_id)

    async def restart_component(self, component_id: str) -> None:
        logger.info('restarting_component', component=component_id)
