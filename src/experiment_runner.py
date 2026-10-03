"""
Модуль проведения масштабных экспериментов.
Запускает NL-SHADE-LBC и Classic DE на функциях CEC 2022 с фиксацией сидов,
собирает статистику и генерирует сравнительные таблицы с результатами статьи.
"""

import os
import time
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from tqdm import tqdm

from src.problem import CEC2022Problem
from src.algorithms.nl_shade_lbc import NLSHADELBC
from src.algorithms.classic_de import ClassicDE

# Эталонные результаты авторов статьи из Table VI (CEC 2022, 10D, 30 runs, 200k evals)
PAPER_RESULTS_10D = {
    1:  {"best": 0.0,      "worst": 0.0,      "median": 0.0,      "mean": 0.0,      "std": 0.0},
    2:  {"best": 0.0,      "worst": 0.0,      "median": 0.0,      "mean": 1.33e-01, "std": 7.16e-01},
    3:  {"best": 0.0,      "worst": 0.0,      "median": 0.0,      "mean": 0.0,      "std": 0.0},
    4:  {"best": 2.16e-05, "worst": 2.99e+00, "median": 9.95e-01, "mean": 1.30e+00, "std": 7.78e-01},
    5:  {"best": 0.0,      "worst": 0.0,      "median": 0.0,      "mean": 0.0,      "std": 0.0},
    6:  {"best": 4.31e-03, "worst": 4.40e-01, "median": 7.21e-02, "mean": 1.24e-01, "std": 1.25e-01},
    7:  {"best": 0.0,      "worst": 0.0,      "median": 0.0,      "mean": 0.0,      "std": 0.0},
    8:  {"best": 2.96e-04, "worst": 1.79e-01, "median": 3.29e-02, "mean": 4.60e-02, "std": 3.80e-02},
    9:  {"best": 2.29e+02, "worst": 2.29e+02, "median": 2.29e+02, "mean": 2.29e+02, "std": 5.68e-14},
    10: {"best": 1.00e+02, "worst": 1.00e+02, "median": 1.00e+02, "mean": 1.00e+02, "std": 2.95e-02},
    11: {"best": 0.0,      "worst": 0.0,      "median": 0.0,      "mean": 0.0,      "std": 0.0},
    12: {"best": 1.63e+02, "worst": 1.65e+02, "median": 1.65e+02, "mean": 1.65e+02, "std": 4.04e-01},
}


class ExperimentRunner:
    """
    Координатор экспериментов над набором тестовых функций.
    """

    def __init__(
        self,
        func_ids: List[int],
        num_runs: int = 30,
        dim: int = 10,
        nfe_max: int = 200_000,
        results_dir: str = "results",
    ):
        self.func_ids = func_ids
        self.num_runs = num_runs
        self.dim = dim
        self.nfe_max = nfe_max
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        os.makedirs(os.path.join(results_dir, "figures"), exist_ok=True)

        self.raw_records: List[Dict[str, Any]] = []
        self.convergence_data: Dict[str, Dict[int, List[Dict[str, Any]]]] = {
            "NL-SHADE-LBC": {},
            "ClassicDE": {},
        }

    def run_all(self) -> pd.DataFrame:
        """
        Запуск полного цикла экспериментов для обоих алгоритмов.
        """
        print(f"=== Запуск экспериментов: {len(self.func_ids)} функций, {self.num_runs} сидов, NFE_max={self.nfe_max} ===")

        for fid in self.func_ids:
            self.convergence_data["NL-SHADE-LBC"][fid] = []
            self.convergence_data["ClassicDE"][fid] = []

            for run_idx in tqdm(range(1, self.num_runs + 1), desc=f"Функция F{fid:02d}"):
                seed = run_idx * 100 + fid  # детерминированный сид

                # 1. Запуск NL-SHADE-LBC
                prob_nl = CEC2022Problem(func_id=fid, dim=self.dim, nfe_max=self.nfe_max)
                solver_nl = NLSHADELBC(prob_nl, seed=seed)
                t0 = time.time()
                _, err_nl = solver_nl.solve()
                t1 = time.time()

                self.raw_records.append({
                    "function": f"F{fid:02d}",
                    "func_id": fid,
                    "algorithm": "NL-SHADE-LBC",
                    "run": run_idx,
                    "seed": seed,
                    "error": err_nl,
                    "evaluations": prob_nl.evaluations,
                    "time_sec": t1 - t0,
                })
                self.convergence_data["NL-SHADE-LBC"][fid].append({
                    "nfe": list(prob_nl.history_nfe),
                    "error": list(prob_nl.history_error),
                })

                # 2. Запуск Classic DE
                prob_de = CEC2022Problem(func_id=fid, dim=self.dim, nfe_max=self.nfe_max)
                solver_de = ClassicDE(prob_de, seed=seed)
                t0 = time.time()
                _, err_de = solver_de.solve()
                t1 = time.time()

                self.raw_records.append({
                    "function": f"F{fid:02d}",
                    "func_id": fid,
                    "algorithm": "ClassicDE",
                    "run": run_idx,
                    "seed": seed,
                    "error": err_de,
                    "evaluations": prob_de.evaluations,
                    "time_sec": t1 - t0,
                })
                self.convergence_data["ClassicDE"][fid].append({
                    "nfe": list(prob_de.history_nfe),
                    "error": list(prob_de.history_error),
                })

        # Сохранение сырых данных
        df_raw = pd.DataFrame(self.raw_records)
        df_raw.to_csv(os.path.join(self.results_dir, "raw_runs.csv"), index=False)

        # Вычисление сводной статистики
        df_summary = self.compute_summary(df_raw)
        df_summary.to_csv(os.path.join(self.results_dir, "summary_table.csv"), index=False)

        # Сохранение сводной таблицы в LaTeX
        latex_str = df_summary.to_latex(index=False, float_format="%.2e")
        with open(os.path.join(self.results_dir, "summary_table.tex"), "w") as f:
            f.write(latex_str)

        print(f"\nЭксперименты завершены. Результаты сохранены в папку: {self.results_dir}/")
        return df_summary

    def compute_summary(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Расчет статистических метрик (Best, Worst, Median, Mean, Std)
        и объединение с данными статьи.
        """
        summary_rows = []
        for fid in self.func_ids:
            fname = f"F{fid:02d}"
            sub_nl = df_raw[(df_raw["function"] == fname) & (df_raw["algorithm"] == "NL-SHADE-LBC")]
            sub_de = df_raw[(df_raw["function"] == fname) & (df_raw["algorithm"] == "ClassicDE")]

            paper = PAPER_RESULTS_10D.get(fid, {})

            # Статистика NL-SHADE-LBC
            nl_errs = sub_nl["error"].values
            nl_best = float(np.min(nl_errs))
            nl_worst = float(np.max(nl_errs))
            nl_median = float(np.median(nl_errs))
            nl_mean = float(np.mean(nl_errs))
            nl_std = float(np.std(nl_errs))
            nl_time = float(np.mean(sub_nl["time_sec"].values))

            # Статистика Classic DE
            de_errs = sub_de["error"].values
            de_best = float(np.min(de_errs))
            de_worst = float(np.max(de_errs))
            de_median = float(np.median(de_errs))
            de_mean = float(np.mean(de_errs))
            de_std = float(np.std(de_errs))
            de_time = float(np.mean(sub_de["time_sec"].values))

            summary_rows.append({
                "Function": fname,
                "NL_Best": nl_best,
                "NL_Worst": nl_worst,
                "NL_Median": nl_median,
                "NL_Mean": nl_mean,
                "NL_Std": nl_std,
                "NL_Time_s": nl_time,
                "Paper_Best": paper.get("best", np.nan),
                "Paper_Mean": paper.get("mean", np.nan),
                "Paper_Std": paper.get("std", np.nan),
                "DE_Best": de_best,
                "DE_Mean": de_mean,
                "DE_Std": de_std,
                "DE_Time_s": de_time,
            })

        return pd.DataFrame(summary_rows)
