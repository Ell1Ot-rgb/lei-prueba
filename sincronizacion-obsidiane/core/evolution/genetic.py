from __future__ import annotations
import random
import structlog
from typing import List, Dict, Any, Callable

logger = structlog.get_logger()

class GeneticAlgorithm:
    """
    Evolutionary engine for optimizing system parameters.
    Implements selection, crossover, and mutation.
    """
    __slots__ = ('population_size', 'mutation_rate', 'population', 'generations')
    
    def __init__(
        self,
        population_size: int = 20,
        mutation_rate: float = 0.1
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population: List[Dict[str, Any]] = []
        self.generations = 0

    def initialize_population(self, template: Dict[str, Any]):
        """Create initial population based on a template configuration."""
        self.population = []
        for _ in range(self.population_size):
            individual = template.copy()
            # Add slight random variations
            for k, v in individual.items():
                if isinstance(v, (int, float)):
                    individual[k] = v * random.uniform(0.9, 1.1)
            self.population.append(individual)
        logger.info('evolution_population_initialized', size=self.population_size)

    def evolve(self, fitness_fn: Callable[[Dict], float]) -> Dict[str, Any]:
        """
        Run one generation of evolution.
        Returns the best individual from the new generation.
        """
        # 1. Evaluate fitness
        scored_pop = []
        for ind in self.population:
            score = fitness_fn(ind)
            scored_pop.append((ind, score))
        
        # Sort by fitness (descending)
        scored_pop.sort(key=lambda x: x[1], reverse=True)
        best_individual = scored_pop[0][0]
        
        # 2. Selection (Top 50%)
        survivors = [x[0] for x in scored_pop[:self.population_size // 2]]
        
        # 3. Crossover & Mutation
        new_pop = survivors.copy()
        while len(new_pop) < self.population_size:
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)
            child = self._crossover(parent1, parent2)
            child = self._mutate(child)
            new_pop.append(child)
            
        self.population = new_pop
        self.generations += 1
        
        logger.info('evolution_generation_complete', 
                   gen=self.generations, 
                   best_score=scored_pop[0][1])
        
        return best_individual

    def _crossover(self, p1: Dict, p2: Dict) -> Dict:
        child = {}
        for k in p1.keys():
            child[k] = p1[k] if random.random() > 0.5 else p2[k]
        return child

    def _mutate(self, ind: Dict) -> Dict:
        for k in ind.keys():
            if isinstance(ind[k], (int, float)) and random.random() < self.mutation_rate:
                ind[k] *= random.uniform(0.9, 1.1)
        return ind
