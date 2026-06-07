from __future__ import annotations
import asyncio
import hashlib
import hmac
import base64
import time
from typing import Dict, Optional, Tuple
from collections import deque
import structlog

logger = structlog.get_logger()

class AntigenMemory:
    """Thread-safe memory of known threat signatures with TTL."""
    __slots__ = ('_signatures', '_lock', '_max_size', '_ttl')
    
    def __init__(self, max_size: int = 10_000, ttl: float = 86400.0):
        self._signatures: Dict[str, Tuple[str, float]] = {}  # sig -> (desc, timestamp)
        self._lock = asyncio.Lock()
        self._max_size = max_size
        self._ttl = ttl

    async def add(self, signature: str, description: str) -> None:
        """Add a threat signature with automatic eviction of old entries."""
        async with self._lock:
            # Evict expired entries if at capacity
            if len(self._signatures) >= self._max_size:
                await self._evict_expired()
                
            self._signatures[signature] = (description, time.monotonic())
            logger.info('antigen_added', signature=signature[:16])

    async def match(self, signature: str) -> bool:
        """Check if signature matches a known threat."""
        async with self._lock:
            if signature in self._signatures:
                desc, ts = self._signatures[signature]
                # Check if still valid
                if time.monotonic() - ts < self._ttl:
                    return True
                else:
                    # Expired, remove
                    del self._signatures[signature]
        return False

    async def _evict_expired(self) -> None:
        """Remove expired signatures (called within lock)."""
        now = time.monotonic()
        expired = [
            sig for sig, (_, ts) in self._signatures.items()
            if now - ts >= self._ttl
        ]
        for sig in expired:
            del self._signatures[sig]
        logger.debug('antigens_evicted', count=len(expired))


class ImmuneEngine:
    """Adaptive immune system with rate limiting and entropy analysis."""
    __slots__ = ('_memory', '_hmac_key', '_max_payload_size', '_rate_limiter',
                 '_lock', '_entropy_threshold')
    
    def __init__(
        self,
        antigen_memory: AntigenMemory,
        hmac_key: bytes,
        max_payload_size: int = 1_000_000,
        rate_limit_max: int = 100,
        entropy_threshold: float = 7.5
    ):
        self._memory = antigen_memory
        self._hmac_key = hmac_key
        self._max_payload_size = max_payload_size
        self._rate_limiter: deque = deque(maxlen=rate_limit_max)
        self._lock = asyncio.Lock()
        self._entropy_threshold = entropy_threshold

    async def scan_payload(self, data: bytes, source_id: str = 'unknown') -> bool:
        """
        Scan payload for threats using multiple heuristics.
        
        Returns:
            True if payload is safe, False if threat detected
        """
        # 1. Rate limiting
        if not await self._check_rate_limit(source_id):
            logger.warning('immune_rate_limited', source=source_id)
            return False
        
        # 2. Size check
        if len(data) > self._max_payload_size:
            logger.warning('immune_oversized_payload', size=len(data))
            return False
        
        # 3. HMAC fingerprint
        fingerprint = self._compute_fingerprint(data)
        if await self._memory.match(fingerprint):
            logger.warning('immune_known_threat', fingerprint=fingerprint[:16])
            return False
        
        # 4. Entropy check (detect encryption/compression bombs)
        if self._calculate_entropy(data) > self._entropy_threshold:
            logger.warning('immune_high_entropy', source=source_id)
            await self._memory.add(fingerprint, 'high_entropy')
            return False
        
        return True

    def _compute_fingerprint(self, data: bytes) -> str:
        """Compute HMAC-SHA256 fingerprint."""
        h = hmac.new(self._hmac_key, data, hashlib.sha256)
        return base64.urlsafe_b64encode(h.digest()).decode().rstrip('=')

    @staticmethod
    def _calculate_entropy(data: bytes) -> float:
        """Calculate Shannon entropy of payload."""
        if not data:
            return 0.0
        
        # Count byte frequencies
        freq = [0] * 256
        for byte in data:
            freq[byte] += 1
        
        # Calculate entropy
        import math
        length = len(data)
        entropy = 0.0
        for count in freq:
            if count > 0:
                p = count / length
                entropy -= p * math.log2(p)
        
        return entropy

    async def _check_rate_limit(self, source_id: str) -> bool:
        """Check if source has exceeded rate limit."""
        now = time.monotonic()
        async with self._lock:
            # Add current request
            self._rate_limiter.append((source_id, now))
            
            # Count recent requests from this source
            recent_count = sum(
                1 for sid, ts in self._rate_limiter
                if sid == source_id
            )
            
            return recent_count < len(self._rate_limiter)
