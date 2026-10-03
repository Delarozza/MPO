"""
Реализация алгоритма NL-SHADE-LBC (Non-Linear population size reduction Success-History
Adaptive Differential Evolution with Linear Bias Change) по статье:
Stanovov, Akhmedova, Semenkin — IEEE CEC 2022 (Algorithm 1).
"""

from typing import Tuple, List, Dict
import numpy as np
from src.problem import CEC2022Problem


def generalized_weighted_lehmer(vals: np.ndarray, weights: np.ndarray, p: float, m: float = 1.5) -> float:
    """Обобщённое среднее Лемера: sum(w * x^p) / sum(w * x^(p-m))."""
    if len(vals) == 0:
        return 0.5
    # Защита от деления на ноль и отрицательных чисел
    vals_clean = np.clip(vals, 1e-6, 1.0)
    w_clean = np.clip(weights, 1e-12, None)
    w_clean /= np.sum(w_clean)

    num = np.sum(w_clean * (vals_clean ** p))
    den = np.sum(w_clean * (vals_clean ** (p - m)))
    if den <= 1e-12 or np.isnan(den) or np.isinf(den):
        return float(np.mean(vals_clean))
    res = float(num / den)
    return float(np.clip(res, 0.0, 1.0))


def sample_cauchy(location: float, scale: float = 0.1) -> float:
    """Генерация положительного числа из распределения Коши."""
    while True:
        val = location + scale * np.tan(np.pi * (np.random.rand() - 0.5))
        if val > 0.0:
            return float(min(1.0, val))


def sample_normal(mean: float, std: float = 0.1) -> float:
    """Генерация числа из усеченного нормального распределения [0, 1]."""
    val = np.random.normal(mean, std)
    return float(np.clip(val, 0.0, 1.0))


class NLSHADELBC:
    """
    Алгоритм NL-SHADE-LBC (Stanovov et al., IEEE CEC 2022).
    """

    def __init__(self, problem: CEC2022Problem, seed: int = 42):
        self.problem = problem
        self.seed = seed
        self.dim = problem.dim
        self.nfe_max = problem.nfe_max
        self.lb = problem.lower_bound
        self.ub = problem.upper_bound

        # Параметры из статьи:
        self.np_max = 23 * self.dim      # Для D=10: 230
        self.np_min = 4                  # Минимальный размер популяции
        self.h = 20 * self.dim           # Размер памяти H (для D=10: 200)

        # LBC параметры
        self.m = 1.5
        self.p_ini_f = 3.5
        self.p_fin_f = 1.5
        self.p_ini_cr = 1.0
        self.p_fin_cr = 1.5

    def solve(self) -> Tuple[np.ndarray, float]:
        """
        Запуск оптимизации согласно Algorithm 1.
        """
        np.random.seed(self.seed)
        self.problem.reset()

        np_current = self.np_max
        pop = np.random.uniform(self.lb, self.ub, (np_current, self.dim))
        fitness = np.array([self.problem.evaluate(ind) for ind in pop])

        # Память исторических значений
        m_f = np.full(self.h, 0.5)
        m_cr = np.full(self.h, 0.9)
        k_mem = 0

        # Внешний архив вытесненных решений
        archive: List[np.ndarray] = []
        archive_fitness: List[float] = []

        g = 0

        while self.problem.has_budget:
            # 1. Ранжирование популяции (лучшие сначала)
            order = np.argsort(fitness)
            pop = pop[order]
            fitness = fitness[order]

            n = len(pop)
            progress = self.problem.evaluations / float(self.nfe_max)

            # 2. Выбор pbest границы (динамически растет)
            # pbest = max(2, NP * (0.2 + 0.1 * NFE / NFE_max))
            p_val = 0.2 + 0.1 * progress
            pbest_count = max(2, int(np.round(n * p_val)))

            # 3. Генерация Cr и сортировка
            mem_indices = np.random.randint(0, self.h, size=n)
            raw_cr = np.array([sample_normal(m_cr[idx], 0.1) for idx in mem_indices])

            # Crossover-rate sorting: лучшие особи получают меньший Cr (локальный поиск),
            # худшие — больший Cr (исследование)
            sorted_cr = np.sort(raw_cr)
            cr_rates = sorted_cr  # популяция уже отсортирована: индекс 0 — лучшая особь

            # Ранговые вероятности для выбора r2 из популяции: Ri = exp(-4*i / NP)
            rank_positions = np.arange(1, n + 1)
            rank_probs = np.exp(-4.0 * rank_positions / float(n))
            rank_probs /= np.sum(rank_probs)

            # Списки успешных параметров за поколение
            s_f: List[float] = []
            s_cr: List[float] = []
            delta_f: List[float] = []

            trials = np.empty_like(pop)
            f_values = np.empty(n)

            # 4. Основной цикл генерации мутантов и скрещивания
            for i in range(n):
                if not self.problem.has_budget:
                    break

                target_f = 0.5
                trial_found = False

                # До 100 попыток ресэмплинга при выходе за границы
                for attempt in range(100):
                    F_i = sample_cauchy(m_f[mem_indices[i]], 0.1)
                    target_f = F_i

                    # Выбор pbest из top pbest_count
                    pbest_idx = np.random.randint(0, pbest_count)
                    while pbest_idx == i:
                        pbest_idx = np.random.randint(0, pbest_count)

                    # Выбор r1 != i != pbest
                    r1_candidates = [idx for idx in range(n) if idx != i and idx != pbest_idx]
                    r1 = np.random.choice(r1_candidates)

                    # Выбор r2: с вероятностью 0.5 из архива (если архив не пуст), иначе из популяции
                    if len(archive) > 0 and np.random.rand() < 0.5:
                        r2_vec = archive[np.random.randint(0, len(archive))]
                    else:
                        # Селективное давление на r2
                        r2_candidates = [idx for idx in range(n) if idx != i and idx != pbest_idx and idx != r1]
                        probs = rank_probs[r2_candidates]
                        probs /= np.sum(probs)
                        r2_idx = np.random.choice(r2_candidates, p=probs)
                        r2_vec = pop[r2_idx]

                    # Мутация current-to-pbest/1
                    donor = pop[i] + F_i * (pop[pbest_idx] - pop[i]) + F_i * (pop[r1] - r2_vec)

                    # Биномиальное скрещивание
                    cross = np.random.rand(self.dim) < cr_rates[i]
                    cross[np.random.randint(self.dim)] = True  # гарантируем минимум одну координату
                    trial = np.where(cross, donor, pop[i])

                    # Проверка границ
                    if np.all((trial >= self.lb) & (trial <= self.ub)):
                        trials[i] = trial
                        trial_found = True
                        break

                if not trial_found:
                    # Midpoint target BCHM при превышении 100 попыток
                    repaired = trial.copy()
                    below = repaired < self.lb
                    above = repaired > self.ub
                    repaired[below] = 0.5 * (self.lb + pop[i][below])
                    repaired[above] = 0.5 * (self.ub + pop[i][above])
                    trials[i] = np.clip(repaired, self.lb, self.ub)

                f_values[i] = target_f

            # 5. Оценка кандидатов и селекция
            for i in range(len(trials)):
                if not self.problem.has_budget:
                    break

                trial_fit = self.problem.evaluate(trials[i])
                if trial_fit < fitness[i]:
                    # Улучшение!
                    # Добавление старого родителя в архив
                    archive_capacity = max(1, n)
                    if len(archive) < archive_capacity:
                        archive.append(pop[i].copy())
                        archive_fitness.append(fitness[i])
                    else:
                        # Замена в архиве по стратегии авторов
                        replaced = False
                        for _ in range(len(archive)):
                            ra = np.random.randint(0, len(archive))
                            if archive_fitness[ra] > fitness[i]:
                                archive[ra] = pop[i].copy()
                                archive_fitness[ra] = fitness[i]
                                replaced = True
                                break
                        if not replaced:
                            ra = np.random.randint(0, len(archive))
                            archive[ra] = pop[i].copy()
                            archive_fitness[ra] = fitness[i]

                    # Сохранение успеха для обновления памяти
                    s_f.append(f_values[i])
                    s_cr.append(cr_rates[i])
                    delta_f.append(abs(fitness[i] - trial_fit))

                    pop[i] = trials[i]
                    fitness[i] = trial_fit

            # 6. Обновление памяти с механизмом Linear Bias Change (LBC)
            if len(s_f) > 0:
                weights = np.array(delta_f, dtype=float)
                weights /= (np.sum(weights) + 1e-12)

                # Вычисление текущих степеней p по формуле (13)
                p_f = (1.0 - progress) * (self.p_ini_f - self.p_fin_f) + self.p_fin_f
                p_cr = (1.0 - progress) * (self.p_ini_cr - self.p_fin_cr) + self.p_fin_cr

                m_f[k_mem] = generalized_weighted_lehmer(np.array(s_f), weights, p_f, self.m)
                if np.max(s_cr) <= 0.0:
                    m_cr[k_mem] = 0.0
                else:
                    m_cr[k_mem] = generalized_weighted_lehmer(np.array(s_cr), weights, p_cr, self.m)

                k_mem = (k_mem + 1) % self.h

            # 7. Нелинейное уменьшение популяции (NLPSR)
            curr_progress = self.problem.evaluations / float(self.nfe_max)
            target_np = int(np.round(
                (self.np_min - self.np_max) * (curr_progress ** (1.0 - curr_progress)) + self.np_max
            ))
            target_np = max(self.np_min, target_np)

            if len(pop) > target_np:
                survivor_order = np.argsort(fitness)[:target_np]
                pop = pop[survivor_order]
                fitness = fitness[survivor_order]

            # Трассировка размера архива
            max_archive = len(pop)
            if len(archive) > max_archive:
                keep_idx = np.random.choice(len(archive), size=max_archive, replace=False)
                archive = [archive[idx] for idx in keep_idx]
                archive_fitness = [archive_fitness[idx] for idx in keep_idx]

            g += 1

        best_idx = np.argmin(fitness)
        return pop[best_idx], float(fitness[best_idx])
