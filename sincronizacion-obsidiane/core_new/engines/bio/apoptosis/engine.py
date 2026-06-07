from __future__ import annotations
import asyncio
import time
from typing import Dict, Optional, Set
from dataclasses import dataclass, field
import structlog

logger = structlog.get_logger()

@dataclass
class ComponentHealth:
    """Health tracking for a single component."""
    __slots__ = ('component_id', 'last_heartbeat', 'failure_count', 'status')
    component_id: str
    last_heartbeat: float = field(default_factory=time.monotonic)
    failure_count: int = 0
    status: str = 'healthy'

class ApoptosisManager:
    """Monitors component health and triggers programmed cell death.
    
    Thread-safe, memory-efficient health monitoring with configurable
    timeout and restart policies.
    """
    __slots__ = ('_registry', '_scheduler', '_running', '_timeout', '_lock',
                 '_monitor_task', '_check_interval', '_max_failures')
    
    def __init__(
        self,
        scheduler,
        timeout: float = 30.0,
        check_interval: float = 5.0,
        max_failures: int = 3
    ):
        self._registry: Dict[str, ComponentHealth] = {}
        self._scheduler = scheduler
        self._running = False
        self._timeout = timeout
        self._lock = asyncio.Lock()
        self._monitor_task: Optional[asyncio.Task] = None
        self._check_interval = check_interval
        self._max_failures = max_failures

    async def start(self) -> None:
        """Start the apoptosis monitoring loop."""
        if self._running:
            logger.warning('apoptosis_already_running')
            return
            
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info('apoptosis_started', timeout=self._timeout)

    async def stop(self) -> None:
        """Gracefully stop monitoring."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info('apoptosis_stopped')

    async def heartbeat(self, component_id: str) -> None:
        """Register a heartbeat from a component."""
        async with self._lock:
            if component_id not in self._registry:
                self._registry[component_id] = ComponentHealth(component_id)
            
            health = self._registry[component_id]
            health.last_heartbeat = time.monotonic()
            health.status = 'healthy'
            health.failure_count = 0  # Reset on successful heartbeat

    async def _monitor_loop(self) -> None:
        """Main monitoring loop with exponential backoff on errors."""
        error_count = 0
        while self._running:
            try:
                await self._check_health()
                error_count = 0
                await asyncio.sleep(self._check_interval)
            except Exception as e:
                error_count += 1
                backoff = min(60, 2 ** error_count)
                logger.error('monitor_loop_error', error=str(e), backoff=backoff)
                await asyncio.sleep(backoff)

    async def _check_health(self) -> None:
        """Check all component healths and trigger apoptosis if needed."""
        now = time.monotonic()
        async with self._lock:
            dead_components: Set[str] = set()
            
            for cid, health in self._registry.items():
                if now - health.last_heartbeat > self._timeout:
                    health.failure_count += 1
                    
                    if health.failure_count >= self._max_failures:
                        health.status = 'dead'
                        dead_components.add(cid)
                        logger.warning(
                            'component_death_detected',
                            component=cid,
                            last_seen=now - health.last_heartbeat
                        )
        
        # Trigger apoptosis outside the lock to avoid deadlocks
        for cid in dead_components:
            await self._trigger_apoptosis(cid)

    async def _trigger_apoptosis(self, component_id: str) -> None:
        """Execute apoptosis and optional restart."""
        logger.warning('apoptosis_triggered', component=component_id)
        
        try:
            if hasattr(self._scheduler, 'release_resources'):
                await self._scheduler.release_resources(component_id)
            
            if hasattr(self._scheduler, 'restart_component'):
                await self._scheduler.restart_component(component_id)
                
            # Remove from registry after cleanup
            async with self._lock:
                self._registry.pop(component_id, None)
                
        except Exception as e:
            logger.error('apoptosis_failed', component=component_id, error=str(e))
