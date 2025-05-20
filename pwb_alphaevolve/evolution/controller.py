"""Async evolution controller.

High‑level loop:
1. Choose a *parent* strategy (elite or random) from `ProgramStore`.
2. Build prompt, call OpenAI → JSON diff/full code.
3. Apply patch ⇒ child code.
4. Evaluate back‑test KPIs.
5. Insert child into store (which updates MAP‑Elites grid).
"""

import asyncio
import inspect
import json
import logging
import textwrap

from pwb_alphaevolve.evaluator.backtest import evaluate
from pwb_alphaevolve.evolution.patching import apply_patch
from pwb_alphaevolve.llm_engine import openai_client, prompts
from pwb_alphaevolve.store.sqlite import ProgramStore
from pwb_alphaevolve.strategies import templates  # seed strategies
from pwb_alphaevolve.strategies.base import BaseLoggingStrategy

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, store: ProgramStore, *, max_concurrency: int = 4):
        self.store = store
        self.sem = asyncio.Semaphore(max_concurrency)
        self._ensure_seed_population()

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------
    def _ensure_seed_population(self):
        """If DB empty, insert seed strategies w/out metrics (lazy eval)."""
        if self.store.top_k(k=1):
            return  # already seeded
        seeds = [templates.SMAMomentum, templates.VolAdjMomentum]
        for cls in seeds:
            code = textwrap.dedent(inspect.getsource(cls))
            self.store.insert(code, metrics=None, parent_id=None)
        logger.info("Seed strategies inserted into store.")

    async def _spawn(self, parent_id: str | None):
        """Generate, evaluate & store one child strategy."""
        async with self.sem:
            # 1) Select parent
            parent = self.store.sample(parent_id)
            if parent is None:
                logger.warning("No parent found; skipping spawn.")
                return

            # 2) Build prompt & call OpenAI
            messages = prompts.build(parent, self.store)
            try:
                msg = await openai_client.chat(messages)
            except Exception as e:
                logger.error(f"OpenAI call failed: {e}")
                return

            # 3) Apply patch
            try:
                diff_json = json.loads(msg.content)
            except json.JSONDecodeError as e:
                logger.error(f"Model did not return valid JSON: {e}\n{msg.content[:500]}")
                return

            child_strategy = apply_patch(parent["code"], diff_json)

            imports = "from collections import deque\nimport backtrader as bt"
            base_cls = inspect.getsource(BaseLoggingStrategy)
            child_code = textwrap.dedent(imports + "\n\n" + base_cls + "\n\n" + child_strategy)

            # 4) Evaluate
            try:
                kpis = await evaluate(child_code)
                print(kpis)
            except Exception as e:
                logger.error(f"Evaluation failed: {e}")
                return

            # 5) Persist
            self.store.insert(child_code, kpis, parent_id=parent["id"])
            logger.info("Child stored – Sharpe %.2f", kpis.get("sharpe", 0))

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    async def run_forever(self):
        """Continuous evolution loop (no termination)."""
        while True:
            await self._spawn(None)
            # Optional: back‑off to be polite to API limits when concurrency=1
            await asyncio.sleep(0.01)
