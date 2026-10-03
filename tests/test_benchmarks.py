"""
Модульные тесты для проверки корректности задач и алгоритмов.
"""

import unittest
import numpy as np
from src.problem import CEC2022Problem
from src.algorithms.nl_shade_lbc import NLSHADELBC
from src.algorithms.classic_de import ClassicDE


class TestCEC2022(unittest.TestCase):

    def test_functions_initialization(self):
        """Проверка инициализации всех 12 функций CEC 2022."""
        for fid in range(1, 13):
            prob = CEC2022Problem(func_id=fid, dim=10, nfe_max=100)
            self.assertEqual(prob.dim, 10)
            self.assertEqual(prob.evaluations, 0)
            self.assertTrue(prob.has_budget)

    def test_budget_enforcement(self):
        """Проверка строгого соблюдения вычислительного бюджета."""
        budget = 500
        prob = CEC2022Problem(func_id=1, dim=10, nfe_max=budget)
        solver = ClassicDE(prob, pop_size=20, seed=1)
        solver.solve()
        self.assertLessEqual(prob.evaluations, budget)
        self.assertFalse(prob.has_budget)

    def test_nl_shade_convergence_f1(self):
        """Проверка сходимости NL-SHADE-LBC на унимодальной функции F1."""
        prob = CEC2022Problem(func_id=1, dim=10, nfe_max=30000)
        solver = NLSHADELBC(prob, seed=42)
        _, err = solver.solve()
        # Ошибка на F1 должна быть пренебрежимо мала (< 1e-4)
        self.assertLess(err, 1e-4)


if __name__ == "__main__":
    unittest.main()
