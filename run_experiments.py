#!/usr/bin/env python3
"""
Главная точка входа для проведения экспериментов по Заданию 1 (MPO).
Позволяет запустить эксперименты одной командой, собрать метрики и сгенерировать графики.

Использование:
  python run_experiments.py --quick-test   (быстрый тест за 3 секунды)
  python run_experiments.py --fast-run     (быстрый прогон всех 12 функций на 5 сидов)
  python run_experiments.py --full-run     (полная репликация: 12 функций, 30 сидов, 200k NFE)
"""

import os
import argparse
from src.experiment_runner import ExperimentRunner
from src.visualize import plot_single_convergence, plot_convergence_grid, plot_boxplots
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Запуск экспериментов NL-SHADE-LBC vs Classic DE на CEC 2022")
    parser.add_argument("--quick-test", action="store_true", help="Быстрый смоук-тест на 2 функциях и 1 сиде")
    parser.add_argument("--fast-run", action="store_true", help="Быстрый прогон: 12 функций, 5 сидов, 50k NFE")
    parser.add_argument("--full-run", action="store_true", help="Полный официальный прогон: 12 функций, 30 сидов, 200k NFE")
    parser.add_argument("--runs", type=int, default=None, help="Количество независимых прогонов (сидов)")
    parser.add_argument("--nfe", type=int, default=None, help="Максимальное число вызовов целевой функции")
    parser.add_argument("--dim", type=int, default=10, help="Размерность задачи (по умолчанию 10)")
    parser.add_argument("--results-dir", type=str, default="results", help="Папка для сохранения результатов")

    args = parser.parse_args()

    # Определение параметров запуска
    if args.quick_test:
        func_ids = [1, 2]
        runs = 1
        nfe_max = 20_000
    elif args.fast_run:
        func_ids = list(range(1, 13))
        runs = 5
        nfe_max = 50_000
    elif args.full_run:
        func_ids = list(range(1, 13))
        runs = 30
        nfe_max = 200_000
    else:
        # По умолчанию если флаги не переданы
        func_ids = list(range(1, 13))
        runs = args.runs if args.runs is not None else 5
        nfe_max = args.nfe if args.nfe is not None else 50_000

    if args.runs is not None:
        runs = args.runs
    if args.nfe is not None:
        nfe_max = args.nfe

    runner = ExperimentRunner(
        func_ids=func_ids,
        num_runs=runs,
        dim=args.dim,
        nfe_max=nfe_max,
        results_dir=args.results_dir,
    )

    # Запуск вычислений
    df_summary = runner.run_all()

    # Генерация графиков
    print("\nГенерация научных графиков...")
    figures_dir = os.path.join(args.results_dir, "figures")

    # 1. Индивидуальные графики сходимости для каждой функции
    for fid in func_ids:
        plot_single_convergence(
            fid=fid,
            nl_runs=runner.convergence_data["NL-SHADE-LBC"].get(fid, []),
            de_runs=runner.convergence_data["ClassicDE"].get(fid, []),
            output_path=os.path.join(figures_dir, f"convergence_F{fid:02d}.png"),
        )

    # 2. Сетка графиков (если функций несколько)
    if len(func_ids) == 12:
        plot_convergence_grid(
            convergence_data=runner.convergence_data,
            output_path=os.path.join(figures_dir, "all_functions_grid.png"),
        )

    # 3. Boxplot
    df_raw = pd.read_csv(os.path.join(args.results_dir, "raw_runs.csv"))
    plot_boxplots(df_raw, os.path.join(figures_dir, "error_boxplots.png"))

    print(f"Все графики сохранены в {figures_dir}/")
    print("\n=== Сводная таблица результатов ===")
    print(df_summary[["Function", "NL_Best", "NL_Mean", "Paper_Mean", "DE_Mean", "NL_Time_s"]].to_string())


if __name__ == "__main__":
    main()
