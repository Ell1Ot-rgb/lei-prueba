from __future__ import annotations
import asyncio
import random
import structlog
from typing import List, Any, Deque
from collections import deque

logger = structlog.get_logger()

class MemoryReplay:
    """Buffer for storing experiences to be replayed during sleep."""
    __slots__ = ('buffer', 'max_size')
    
    def __init__(self, max_size: int = 10000):
        self.buffer: Deque[Any] = deque(maxlen=max_size)
        self.max_size = max_size

    def add(self, experience: Any):
        self.buffer.append(experience)

    def sample(self, batch_size: int) -> List[Any]:
        if len(self.buffer) < batch_size:
            return list(self.buffer)
        return random.sample(self.buffer, batch_size)

class DreamEngine:
    """
    Consolidates memories during idle time (sleep mode).
    Replays past experiences to reinforce learning.
    """
    __slots__ = ('replay_buffer', 'learner', 'batch_size', '_running', '_task')
    
    def __init__(self, replay_buffer: MemoryReplay, learner: Any, batch_size: int = 32):
        self.replay_buffer = replay_buffer
        self.learner = learner # Reference to a learning model (e.g., TemporalPredictor)
        self.batch_size = batch_size
        self._running = False
        self._task = None

    async def start_dreaming(self):
        """Enter sleep mode and start consolidation."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._dream_loop())
        logger.info('dream_cycle_started')

    async def stop_dreaming(self):
        """Wake up."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info('dream_cycle_stopped')

    async def _dream_loop(self):
        while self._running:
            try:
                if len(self.replay_buffer.buffer) >= self.batch_size:
                    batch = self.replay_buffer.sample(self.batch_size)
                    # In a real system, we would train the learner here
                    # await self.learner.train(batch)
                    logger.debug('dream_consolidation_step', batch_size=len(batch))
                
                await asyncio.sleep(1.0) # Dream cycle interval
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error('dream_error', error=str(e))
                await asyncio.sleep(5.0)
