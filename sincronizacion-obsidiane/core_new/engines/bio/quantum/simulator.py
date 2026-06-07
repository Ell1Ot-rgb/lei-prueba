from __future__ import annotations
import numpy as np
import asyncio
import structlog
from typing import List, Tuple

logger = structlog.get_logger()

class QuantumSimulator:
    """
    Vectorized quantum circuit simulator.
    Supports basic gates (H, X, CNOT) and measurement.
    """
    __slots__ = ('n_qubits', 'state', '_lock')
    
    def __init__(self, n_qubits: int = 4):
        self.n_qubits = n_qubits
        # State vector initialized to |0...0>
        self.state = np.zeros(2**n_qubits, dtype=np.complex128)
        self.state[0] = 1.0
        self._lock = asyncio.Lock()

    async def apply_gate(self, gate: str, targets: List[int]):
        """Apply a quantum gate to target qubits."""
        async with self._lock:
            if gate == 'H':
                for t in targets:
                    self._apply_hadamard(t)
            elif gate == 'X':
                for t in targets:
                    self._apply_pauli_x(t)
            elif gate == 'CNOT':
                if len(targets) != 2:
                    raise ValueError("CNOT requires 2 targets (control, target)")
                self._apply_cnot(targets[0], targets[1])
            
            # Normalize state to prevent drift
            norm = np.linalg.norm(self.state)
            if norm > 1e-9:
                self.state /= norm
                
            logger.debug('quantum_gate_applied', gate=gate, targets=targets)

    async def measure(self) -> str:
        """Collapse state and return measurement result."""
        async with self._lock:
            probs = np.abs(self.state)**2
            # Handle numerical errors
            probs /= np.sum(probs)
            
            outcome_idx = np.random.choice(len(probs), p=probs)
            
            # Collapse state
            self.state = np.zeros_like(self.state)
            self.state[outcome_idx] = 1.0
            
            # Convert to binary string
            binary = format(outcome_idx, f'0{self.n_qubits}b')
            return binary

    def _apply_hadamard(self, target: int):
        """Vectorized Hadamard gate."""
        n = self.n_qubits
        # Create mask for target bit
        mask = 1 << target
        
        # Indices where target bit is 0
        indices_0 = np.array([i for i in range(2**n) if not (i & mask)])
        # Indices where target bit is 1
        indices_1 = indices_0 | mask
        
        # H|0> = (|0> + |1>)/sqrt(2)
        # H|1> = (|0> - |1>)/sqrt(2)
        state_0 = self.state[indices_0]
        state_1 = self.state[indices_1]
        
        inv_sqrt2 = 1.0 / np.sqrt(2)
        
        self.state[indices_0] = inv_sqrt2 * (state_0 + state_1)
        self.state[indices_1] = inv_sqrt2 * (state_0 - state_1)

    def _apply_pauli_x(self, target: int):
        """Vectorized Pauli-X (NOT) gate."""
        n = self.n_qubits
        mask = 1 << target
        indices_0 = np.array([i for i in range(2**n) if not (i & mask)])
        indices_1 = indices_0 | mask
        
        # Swap amplitudes
        temp = self.state[indices_0].copy()
        self.state[indices_0] = self.state[indices_1]
        self.state[indices_1] = temp

    def _apply_cnot(self, control: int, target: int):
        """Vectorized CNOT gate."""
        n = self.n_qubits
        c_mask = 1 << control
        t_mask = 1 << target
        
        # Apply X to target ONLY where control is 1
        indices_c1_t0 = np.array([i for i in range(2**n) 
                                if (i & c_mask) and not (i & t_mask)])
        indices_c1_t1 = indices_c1_t0 | t_mask
        
        temp = self.state[indices_c1_t0].copy()
        self.state[indices_c1_t0] = self.state[indices_c1_t1]
        self.state[indices_c1_t1] = temp
