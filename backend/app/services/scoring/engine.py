"""Scoring Engine v2: rules + price history + markdown cycles + spike + reliability,
with optional LLM refinement."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

MODEL_VERSION = "rule_v2"


@dataclass
class ScoreResult:
    score: float
    model_version: str
    explanation: str


def detect_markdown_cycle(prices: list[float]) -> bool:
    streak = 0
    for a, b in zip(prices, prices[1:]):
        streak = streak + 1 if b < a else 0
        if streak >= 2:
            return True
    return False


def score_store_item(store_item, prices: list[float], signals, reliability: float = 0.8) -> ScoreResult:
    score, reasons = 0.0, []
    cur, reg = store_item.current_price, store_item.regular_price
    if cur is not None and cur <= 0.05:
        score += 40
        reasons.append(f"near-zero ${cur:.2f}")
    if cur is not None and cur <= 0.01:
        score += 10
        reasons.append("penny price")
    if cur is not None and reg and reg > 0 and (reg - cur) / reg >= 0.5:
        score += 20
        reasons.append(f"down {(reg - cur) / reg * 100:.0f}%")
    if store_item.clearance_flag:
        score += 30
        reasons.append("clearance flag")
    if detect_markdown_cycle(prices):
        score += 10
        reasons.append("markdown cycle")
    if {s.signal_type for s in signals} & {"penny_spike"}:
        score += 10
        reasons.append("store penny spike")
    if store_item.first_seen_at and (datetime.utcnow() - store_item.first_seen_at).days > 30:
        score -= 10
        reasons.append("stale clearance")
    score *= 0.9 + 0.1 * max(0.0, min(1.0, reliability))
    score = max(0.0, min(100.0, score))
    return ScoreResult(score, MODEL_VERSION, "; ".join(reasons) or "no strong penny signals")
