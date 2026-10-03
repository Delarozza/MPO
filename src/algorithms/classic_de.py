"""
Классическая дифференциальная эволюция (Standard DE/rand/1/bin)
в качестве сравнительного эталона (baseline) для Варианта B.
"""

from typing import Tuple
import numpy as np
from src.problem import CEC2022Problem


class ClassicDE:
    """
    Стандартная дифференциальная эволюция со статическими параметрами:
      - Стратегия: DE/rand/1/bin
      - Размер популяции: NP = 50
      - Фактор масштабирования: F = 0.5
      - Вероятность скрещивания: Cr = 0.9
    """

    def __init__(
        self,
        problem: CEC2022Problem,
        pop_size: int = 50,
        f: float = 0.5,
        cr: float = 0.9,
        seed: int = 42,
    ):
        self.problem = problem
        self.pop_size = pop_size
        self.f = f
        self.cr = cr
        self.seed = seed
        self.dim = problem.dim
        self.lb = problem.lower_bound
        self.ub = problem.upper_bound

    def solve(self) -> Tuple[np.ndarray, float]:
        """
        Запуск оптимизации стандартной DE.
        """
        np.random.seed(self.seed)
        self.problem.reset()

        pop = np.random.uniform(self.lb, self.ub, (self.pop_size, self.dim))
        fitness = np.array([self.problem.evaluate(ind) for ind in pop])

        while self.problem.has_budget:
            for i in range(self.pop_size):
                if not self.problem.has_budget:
                    break

                # Выбор трёх различных случайных индексов != i
                idxs = [idx for idx in range(self.pop_size) if idx != i]
                r1, r2, r3 = np.random.choice(idxs, size=3, replace=False)

                # Мутация rand/1
                mutant = pop[r1] + self.f * (pop[r2] - pop[r3])

                # Биномиальное скрещивание
                cross = np.random.rand(self.dim) < self.cr
                cross[np.random.randint(self.dim)] = True
                trial = np.where(cross, mutant, pop[i])

                # Ограничение границами
                trial = np.clip(trial, self.lb, self.ub)

                # Вычисление ошибки
                trial_fit = self.problem.evaluate(trial)

                # Жадная селекция
                if trial_fit <= fitness[i]:
                    pop[i] = trial
                    fitness[i] = trial_fit

        best_idx = np.argmin(fitness)
        return pop[best_idx], float(fitness[best_idx])
