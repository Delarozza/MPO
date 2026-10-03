# Zadanie 1: Analýza a experimentálne riešenie optimalizačnej úlohy (MPO)

Tento projekt implementuje a experimentálne vyhodnocuje algoritmus **NL-SHADE-LBC** (Non-Linear population size reduction Success-History Adaptive Differential Evolution with Linear Bias Change) na medzinárodnom benchmarku **IEEE CEC 2022** podľa článku:

> **Vladimir Stanovov, Shakhnaz Akhmedova, Eugene Semenkin.**  
> *«NL-SHADE-LBC algorithm with linear parameter adaptation bias change for CEC 2022 Numerical Optimization»*  
> IEEE Congress on Evolutionary Computation (CEC 2022), DOI: [10.1109/CEC55065.2022.9870295](https://doi.org/10.1109/CEC55065.2022.9870295).

---

## 📁 Štruktúra projektu

```text
MPO/
├── src/
│   ├── problem.py              # CEC2022Problem: obal funkcií F1-F12 s počítadlom BudgetTracker
│   ├── algorithms/
│   │   ├── nl_shade_lbc.py     # Verná implementácia Algoritmu 1 (NL-SHADE-LBC) zo štúdie
│   │   └── classic_de.py       # Štandardná DE (DE/rand/1/bin) ako porovnávací baseline
│   ├── experiment_runner.py    # Spúšťač sérií experimentov s fixovanými seedmi a výpočtom metrík
│   └── visualize.py            # Generátor publikačných grafov konvergencie a boxplotov
├── results/
│   ├── figures/                # Vygenerované grafy (PNG a PDF)
│   ├── raw_runs.csv            # Kompletné dáta zo všetkých behov
│   ├── summary_table.csv       # Súhrnná štatistická tabuľka (Best, Worst, Mean, Std, atď.)
│   └── summary_table.tex       # Vygenerovaná LaTeX tabuľka pripravená do reportu
├── report/
│   ├── report.tex              # Kompletný akademický report (6–10 strán, 13 sekcií)
│   └── report.pdf              # Skompilovaný PDF report
├── tests/
│   └── test_benchmarks.py      # Automatické jednotkové testy
├── run_experiments.py          # Hlavný CLI skript pre spustenie experimentov
├── requirements.txt            # Zoznam závislostí a ich verzií
└── README.md                   # Tento návod
```

---

## ⚙️ Inštalácia a príprava prostredia

1. **Vytvorenie virtuálneho prostredia (Python 3.10+):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Inštalácia závislostí:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Spustenie overovacích testov:**
   ```bash
   python -m unittest discover tests/
   ```

---

## 🚀 Spustenie experimentov

K dispozícii sú predkonfigurované režimy spúšťania:

* **Rýchly overovací test (cca 3 sekundy):**
  Spustí 1 beh na 2 funkciách na overenie funkčnosti celej pipeline:
  ```bash
  python run_experiments.py --quick-test
  ```

* **Rýchly kompletný beh (cca 1–2 minúty):**
  Spustí všetkých 12 funkcií CEC 2022 na 5 nezávislých seedoch ($NFE_{max} = 50\,000$):
  ```bash
  python run_experiments.py --fast-run
  ```

* **Oficiálna plná replikácia (podľa článku):**
  Spustí všetkých 12 funkcií na 30 nezávislých seedoch s plným rozpočtom $NFE_{max} = 200\,000$:
  ```bash
  python run_experiments.py --full-run
  ```

* **Vlastné nastavenie parametrov:**
  ```bash
  python run_experiments.py --runs 10 --nfe 100000 --dim 10
  ```

Všetky výstupné tabuľky sa ukladajú do priečinka `results/` a grafy do `results/figures/`.

---

## 📑 Kompilácia záverečného reportu (LaTeX)

Pre preklad reportu do PDF:
```bash
cd report
pdflatex report.tex
pdflatex report.tex
```
Výsledný dokument `report.pdf` obsahuje kompletnú 13-bodovú štruktúru požadovanú zadaním, vrátane matematickej formulácie, porovnania s autormi a konvergenčných grafov.
