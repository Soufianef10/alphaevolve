# AlphaEvolve

> **Inspired by [DeepMind’s AlphaEvolve coding agent](https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)**—this project applies the same evolutionary-LLM principles to financial markets.

**Autonomously discovers and back‑tests high‑performing algorithmic‑trading strategies** using evolutionary LLM prompts, Backtrader, and daily market data via yfinance.

![CI](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## ✨ Key Features

| Layer      | Highlights                                                                                  |
| ---------- | ------------------------------------------------------------------------------------------- |
| Data       | Daily OHLC loader via `yfinance` with caching to Feather |
| Strategies | Seed templates with **EVOLVE‑BLOCK** markers that the LLM mutates                           |
| Evaluator  | Deterministic Backtrader walk‑forward, JSON KPIs (Sharpe, CAGR, Calmar, DD)                 |
| LLM Engine | OpenAI o3 structured‑output chat → JSON diff/patch system                                   |
| Evolution  | Async controller, SQLite hall‑of‑fame, optional MAP‑Elites niches                           |
| Dashboard  | (optional) Streamlit live view of metrics & equity curves                                   |

---

## 🚀 Quickstart

```bash
# clone and install in editable mode
$ git clone https://github.com/paperswithbacktest/pwb-alphaevolve.git
$ cd pwb-alphaevolve
$ pip install -e .

# set your OpenAI key (model "o3" required)
$ export OPENAI_API_KEY=sk-...
# data is automatically downloaded via yfinance

# launch the evolution controller (infinite loop)
$ python scripts/run_controller.py
$ streamlit run scripts/dashboard.py
```

The dashboard uses Streamlit to visualize the evolution process and back‑test results.

---

## 📂 Project structure (high‑level)

```
alpha_trader/
├── data/          # loaders & helpers using yfinance
├── strategies/    # seed strategies (EVOLVE‑BLOCK markers)
├── evaluator/     # Backtrader KPIs & walk‑forward
├── llm_engine/    # prompt builder + OpenAI client
├── evolution/     # controller, patching, islands
└── store/         # SQLite persistence
scripts/           # CLI entry‑points
```

---

## ⚙️  Installation

> **Python ≥ 3.10** required.

```bash
pip install pwb-alphaevolve
```

Or install the bleeding‑edge version:

```bash
pip install git+https://github.com/your‑org/pwb-alphaevolve.git
```

### Core Dependencies

* [yfinance](https://github.com/ranaroussi/yfinance)
* [pwb-backtrader](https://github.com/paperswithbacktest/pwb-backtrader)
* backtrader ≥ 1.9
* openai ≥ 1.0 (structured output)
* tqdm, pandas, numpy, pydantic

(See `pyproject.toml` for the full list.)

---


## 🤝 Contributing

1. Fork the repo & create your feature branch (`git checkout -b feat/new-feature`).
2. Commit your changes (`git commit -m 'feat: add something'`).
3. Push to the branch (`git push origin feat/new-feature`).
4. Open a Pull Request.

Please run `black` + `ruff` before submitting.

---

## 📄 License

MIT © 2025 Contributors
