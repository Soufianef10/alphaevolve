"""
Seed strategies with EVOLVE-BLOCK markers so the LLM can mutate only the
relevant sections.  These act as the initial population for the evolution
controller.
"""

import backtrader as bt

from .base import BaseLoggingStrategy


# ---------------------------------------------------------------------
# ☀️  Template 1 – 10-month SMA cross on multiple assets
# ---------------------------------------------------------------------
class SMAMomentum(BaseLoggingStrategy):
    params = {"leverage": 0.9, "sma_period": 210}

    def __init__(self):
        super().__init__()
        self.sma = {
            d._name: bt.indicators.SMA(d.close, period=self.p.sma_period) for d in self.datas
        }
        self.last_month = -1

    # === EVOLVE-BLOCK: decision_logic =================================
    def next(self):
        super().next()  # keeps equity log

        today = self.datas[0].datetime.date(0)
        if today.month == self.last_month:
            return  # rebalance monthly
        self.last_month = today.month

        tradable = [d for d in self.datas if len(self.sma[d._name]) >= self.p.sma_period]
        longs = [d for d in tradable if d.close[0] > self.sma[d._name][0]]

        weight = self.p.leverage / len(longs) if longs else 0.0
        for d in self.datas:
            self.order_target_percent(d, target=weight if d in longs else 0.0)

    # === END EVOLVE-BLOCK =============================================


# ---------------------------------------------------------------------
# ☀️  Template 2 – Volatility-adjusted momentum (placeholder)
# ---------------------------------------------------------------------
class VolAdjMomentum(BaseLoggingStrategy):
    params = {"leverage": 0.95, "lookback": 63}

    def __init__(self):
        super().__init__()
        self.roc = {
            d._name: bt.indicators.RateOfChange(d.close, period=self.p.lookback) for d in self.datas
        }
        self.std = {
            d._name: bt.indicators.StandardDeviation(d.close, period=self.p.lookback)
            for d in self.datas
        }

    # === EVOLVE-BLOCK: decision_logic =================================
    def next(self):
        super().next()
        scores = {}
        for d in self.datas:
            if len(self.roc[d._name]) < self.p.lookback:
                continue
            momentum = self.roc[d._name][0]
            vol = self.std[d._name][0] or 1e-9  # avoid div-zero
            scores[d] = momentum / vol

        top = [d for d, s in scores.items() if s > 0]
        n = len(top)
        w = self.p.leverage / n if n else 0
        for d in self.datas:
            self.order_target_percent(d, target=w if d in top else 0)

    # === END EVOLVE-BLOCK =============================================
