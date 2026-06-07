from __future__ import annotations
import asyncio
import json
import hmac
import hashlib
import base64
import os
import aiofiles
import structlog
from typing import Dict, Any, Optional

logger = structlog.get_logger()

class EpigeneticEngine:
    """
    Manages persistent state snapshots with cryptographic integrity.
    Simulates epigenetic memory (modifications on top of code).
    """
    __slots__ = ('storage_dir', 'hmac_key', '_lock')
    
    def __init__(self, storage_dir: str, hmac_key: bytes):
        self.storage_dir = storage_dir
        self.hmac_key = hmac_key
        self._lock = asyncio.Lock()
        
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

    async def snapshot(self, state: Dict[str, Any], name: str) -> str:
        """
        Save a signed snapshot of the system state.
        Atomic write to prevent corruption.
        """
        async with self._lock:
            # Serialize and sign
            raw_data = json.dumps(state, sort_keys=True).encode()
            signature = self._sign(raw_data)
            
            payload = {
                "state": base64.b64encode(raw_data).decode(),
                "signature": signature,
                "version": "1.0"
            }
            
            # Atomic write
            filename = f"{name}.json"
            temp_path = os.path.join(self.storage_dir, f"{filename}.tmp")
            final_path = os.path.join(self.storage_dir, filename)
            
            try:
                async with aiofiles.open(temp_path, "w") as f:
                    await f.write(json.dumps(payload))
                
                os.replace(temp_path, final_path)
                logger.info('epigenetic_snapshot_saved', path=final_path)
                return final_path
                
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                logger.error('snapshot_failed', error=str(e))
                raise

    async def load(self, name: str) -> Optional[Dict[str, Any]]:
        """Load and verify a snapshot."""
        path = os.path.join(self.storage_dir, f"{name}.json")
        if not os.path.exists(path):
            return None
            
        async with self._lock:
            async with aiofiles.open(path, "r") as f:
                data = json.loads(await f.read())
            
            raw_state = base64.b64decode(data['state'])
            expected_sig = self._sign(raw_state)
            
            if not hmac.compare_digest(expected_sig, data['signature']):
                logger.error('epigenetic_integrity_failure', path=path)
                raise ValueError("Snapshot integrity check failed")
                
            return json.loads(raw_state)

    def _sign(self, data: bytes) -> str:
        return hmac.new(self.hmac_key, data, hashlib.sha256).hexdigest()
