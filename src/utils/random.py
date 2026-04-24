"""
Deterministic Random - 确定性随机数生成器

Provides reproducible random number generation for the simulation.
This is critical for scientific reproducibility of the ABM.
"""

import random as _random


class DeterministicRandom:
    """
    确定性随机数生成器 - Deterministic random number generator.

    Wraps Python's random module with seed control for reproducibility.
    """

    def __init__(self, seed: int = None):
        self._rng = _random.Random(seed)
        self._seed = seed

    def random(self) -> float:
        return self._rng.random()

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def choice(self, seq):
        return self._rng.choice(seq)

    def choices(self, population, weights=None, k=1):
        return self._rng.choices(population, weights=weights, k=k)

    def shuffle(self, x):
        self._rng.shuffle(x)

    def seed(self, seed: int):
        self._rng = _random.Random(seed)
        self._seed = seed
