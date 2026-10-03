"""
Модуль визуализации результатов экспериментов:
  - Графики сходимости (Convergence curves) в логарифмическом масштабе.
  - Сводный сетчатый график 4x3 для всех 12 функций CEC 2022.
  - Boxplot распределения финальных ошибок.
"""

import os
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Настройка красивого научного стиля графиков
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 15,
})


def plot_single_convergence(
    fid: int,
    nl_runs: List[Dict[str, Any]],
    de_runs: List[Dict[str, Any]],
    output_path: str,
):
    """
    Построение отдельного графика сходимости для функции F_fid.
    """
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    # 1. Интерполяция траекторий NL-SHADE-LBC
    nfe_grid = np.linspace(1000, 200000, 200)

    def extract_interp(runs):
        curves = []
        for r in runs:
            nfe = np.array(r["nfe"])
            err = np.array(r["error"])
            if len(nfe) > 1:
                # логарифм ошибки с защитой от нуля
                log_err = np.log10(np.maximum(err, 1e-16))
                interp = np.interp(nfe_grid, nfe, log_err)
                curves.append(interp)
        return np.array(curves)

    nl_curves = extract_interp(nl_runs)
    de_curves = extract_interp(de_runs)

    if len(nl_curves) > 0:
        nl_mean = np.mean(nl_curves, axis=0)
        nl_std = np.std(nl_curves, axis=0)
        ax.plot(nfe_grid, nl_mean, label="NL-SHADE-LBC (Paper)", color="#1f77b4", lw=2.2)
        ax.fill_between(nfe_grid, nl_mean - nl_std, nl_mean + nl_std, color="#1f77b4", alpha=0.18)

    if len(de_curves) > 0:
        de_mean = np.mean(de_curves, axis=0)
        de_std = np.std(de_curves, axis=0)
        ax.plot(nfe_grid, de_mean, label="Classic DE (Baseline)", color="#d62728", lw=2.0, ls="--")
        ax.fill_between(nfe_grid, de_mean - de_std, de_mean + de_std, color="#d62728", alpha=0.15)

    ax.set_title(f"CEC 2022 - Function F{fid:02d} Convergence (D=10)")
    ax.set_xlabel("Number of Function Evaluations (NFE)")
    ax.set_ylabel(r"$\log_{10}(f(x) - f^*)$")
    ax.legend(loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.6)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def plot_convergence_grid(
    convergence_data: Dict[str, Dict[int, List[Dict[str, Any]]]],
    output_path: str,
):
    """
    Построение общего графика 4x3 для всех 12 функций CEC 2022 (аналог Fig. 2/3 из статьи).
    """
    fig, axes = plt.subplots(4, 3, figsize=(16, 14), dpi=300)
    axes = axes.flatten()

    nfe_grid = np.linspace(1000, 200000, 150)

    for idx, fid in enumerate(range(1, 13)):
        ax = axes[idx]
        nl_runs = convergence_data.get("NL-SHADE-LBC", {}).get(fid, [])
        de_runs = convergence_data.get("ClassicDE", {}).get(fid, [])

        def get_interp(runs):
            curves = []
            for r in runs:
                nfe = np.array(r["nfe"])
                err = np.array(r["error"])
                if len(nfe) > 1:
                    log_err = np.log10(np.maximum(err, 1e-16))
                    interp = np.interp(nfe_grid, nfe, log_err)
                    curves.append(interp)
            return np.array(curves)

        nl_c = get_interp(nl_runs)
        de_c = get_interp(de_runs)

        if len(nl_c) > 0:
            nl_mean = np.mean(nl_c, axis=0)
            ax.plot(nfe_grid, nl_mean, label="NL-SHADE-LBC", color="#1f77b4", lw=1.8)

        if len(de_c) > 0:
            de_mean = np.mean(de_c, axis=0)
            ax.plot(nfe_grid, de_mean, label="Classic DE", color="#d62728", lw=1.5, ls="--")

        ax.set_title(f"F{fid:02d}", fontsize=12, fontweight="bold")
        ax.set_xlabel("NFE", fontsize=9)
        ax.set_ylabel(r"$\log_{10}(f - f^*)$", fontsize=9)
        ax.grid(True, linestyle=":", alpha=0.6)
        if idx == 0:
            ax.legend(loc="upper right", fontsize=8)

    fig.suptitle("Convergence History on CEC 2022 Benchmarks (D=10, 30 Runs)", fontsize=16, y=0.99)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def plot_boxplots(df_raw: pd.DataFrame, output_path: str):
    """
    Построение Boxplot финальных ошибок для сравнения разброса устойчивости.
    """
    fig, ax = plt.subplots(figsize=(14, 6), dpi=300)

    # Логарифмическая ошибка для boxplot
    df_plot = df_raw.copy()
    df_plot["log_error"] = np.log10(np.maximum(df_plot["error"], 1e-16))

    # Сгруппированный boxplot
    funcs = sorted(df_plot["function"].unique())
    positions_nl = np.arange(len(funcs)) * 2.0
    positions_de = positions_nl + 0.7

    data_nl = [df_plot[(df_plot["function"] == f) & (df_plot["algorithm"] == "NL-SHADE-LBC")]["log_error"].values for f in funcs]
    data_de = [df_plot[(df_plot["function"] == f) & (df_plot["algorithm"] == "ClassicDE")]["log_error"].values for f in funcs]

    bp_nl = ax.boxplot(data_nl, positions=positions_nl, widths=0.5, patch_artist=True,
                       boxprops=dict(facecolor="#1f77b4", alpha=0.6),
                       medianprops=dict(color="black", lw=1.5))
    bp_de = ax.boxplot(data_de, positions=positions_de, widths=0.5, patch_artist=True,
                       boxprops=dict(facecolor="#d62728", alpha=0.6),
                       medianprops=dict(color="black", lw=1.5))

    ax.set_xticks(positions_nl + 0.35)
    ax.set_xticklabels(funcs)
    ax.set_title("Distribution of Final Errors (Boxplots across Seeds, D=10)")
    ax.set_xlabel("Test Function")
    ax.set_ylabel(r"$\log_{10}(f(x) - f^*)$")

    ax.legend([bp_nl["boxes"][0], bp_de["boxes"][0]], ["NL-SHADE-LBC", "Classic DE"], loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.5)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
