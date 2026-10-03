"""
Модуль задачи оптимизации для бенчмарка IEEE CEC 2022.
Содержит строгий контроль бюджета вычислений (BudgetTracker)
и запись истории сходимости.
"""

from typing import Tuple, List, Dict, Optional
import numpy as np
import opfunu


class CEC2022Problem:
    """
    Обёртка тестовых функций IEEE CEC 2022 (F1 - F12) с контролем бюджета вычислений.
    По правилам CEC 2022:
      - Область поиска: [-100, 100]^D
      - Значение ошибки: e = max(0.0, f(x) - f_bias)
      - Если e < 1e-8, ошибка считается равной 0.0.
    """

    def __init__(self, func_id: int, dim: int = 10, nfe_max: Optional[int] = None):
        if not (1 <= func_id <= 12):
            raise ValueError(f"func_id должен быть от 1 до 12, получено: {func_id}")
        if dim not in (10, 20):
            raise ValueError(f"dim должен быть 10 или 20, получено: {dim}")

        self.func_id = func_id
        self.dim = dim
        self.nfe_max = nfe_max if nfe_max is not None else (200_000 if dim == 10 else 1_000_000)

        # Загрузка функции из opfunu
        cls_name = f"F{func_id}2022"
        if not hasattr(opfunu.cec_based, cls_name):
            raise AttributeError(f"Функция {cls_name} не найдена в opfunu.cec_based")
        self.fn_obj = getattr(opfunu.cec_based, cls_name)(ndim=dim)

        self.f_bias = float(self.fn_obj.f_bias)
        self.name = self.fn_obj.name
        self.lower_bound = -100.0
        self.upper_bound = 100.0

        # Состояние текущего прогона
        self.evaluations = 0
        self.best_error = float("inf")
        self.best_x = None

        # Запись контрольных точек CEC 2022: (D/5)^(k/5 - 3) * NFE_max, k = 0..15
        self.cec_checkpoints = self._calc_cec_checkpoints()
        self.cec_records: Dict[int, float] = {}

        # История для построения графиков сходимости
        self.history_nfe: List[int] = []
        self.history_error: List[float] = []
        self._last_logged_nfe = 0
        self.log_interval = 1000  # логируем каждые 1000 вычислений для плавных графиков

    def _calc_cec_checkpoints(self) -> List[int]:
        """Расчет контрольных точек согласно регламенту IEEE CEC 2022."""
        pts = []
        base = self.dim / 5.0
        for k in range(16):
            val = int(np.round((base ** (k / 5.0 - 3.0)) * self.nfe_max))
            if 1 <= val <= self.nfe_max:
                pts.append(val)
        return sorted(list(set(pts)))

    def reset(self):
        """Сброс состояния перед новым независимым прогоном."""
        self.evaluations = 0
        self.best_error = float("inf")
        self.best_x = None
        self.cec_records.clear()
        self.history_nfe.clear()
        self.history_error.clear()
        self._last_logged_nfe = 0

    @property
    def has_budget(self) -> bool:
        """Проверка, остался ли вычислительный бюджет."""
        return self.evaluations < self.nfe_max

    def evaluate(self, x: np.ndarray) -> float:
        """
        Вычисление значения функции с контролем бюджета.
        Возвращает значение ошибки: error = max(0.0, f(x) - f_bias).
        """
        if self.evaluations >= self.nfe_max:
            # Бюджет исчерпан, возвращаем текущее лучшее
            return self.best_error

        # Оценка исходной функции
        raw_val = float(self.fn_obj.evaluate(x))
        error = raw_val - self.f_bias
        if error < 1e-8:
            error = 0.0

        self.evaluations += 1

        if error < self.best_error:
            self.best_error = error
            self.best_x = x.copy()

        # Проверка чекпоинтов CEC
        if self.evaluations in self.cec_checkpoints:
            self.cec_records[self.evaluations] = self.best_error

        # Логирование для графиков
        if (self.evaluations - self._last_logged_nfe >= self.log_interval) or (self.evaluations == self.nfe_max):
            self.history_nfe.append(self.evaluations)
            self.history_error.append(self.best_error)
            self._last_logged_nfe = self.evaluations

        return error
