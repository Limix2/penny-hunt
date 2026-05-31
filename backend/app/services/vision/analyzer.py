"""AI Vision with a model switcher + daily cost limiter.
- local   : free heuristic, no network (default).
- deepseek: DeepSeek Vision (cheap) -- needs DEEPSEEK_API_KEY.
- claude  : Claude Opus 4.8 Vision (premium) -- needs ANTHROPIC_API_KEY.
If a paid model would exceed VISION_DAILY_COST_LIMIT_USD it falls back to local.
"""
import base64
import hashlib
from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, func
from app.core.config import settings
from app.models import VisionLog

MODEL_COST = {"local": 0.0, "deepseek": 0.002, "claude": 0.03}


def _today_spend(db) -> float:
    since = datetime.utcnow() - timedelta(days=1)
    return db.execute(select(func.coalesce(func.sum(VisionLog.cost_usd), 0.0))
                      .where(VisionLog.created_at >= since)).scalar() or 0.0


def _local(image: bytes) -> dict:
    h = int(hashlib.sha256(image).hexdigest(), 16)
    penny = round((h % 100) / 100, 2)
    return {
        "product_guess": "Unrecognized retail item (local heuristic)",
        "penny_likelihood": penny,
        "clearance_likelihood": round(min(1.0, penny + 0.15), 2),
        "confidence": 0.35,
        "explanation": "Free on-device heuristic. Enable DeepSeek/Claude for real recognition.",
    }


async def _remote(url: str, headers: dict, payload: dict) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()
    except Exception:
        return None


async def analyze(image: bytes, model: str, db) -> dict:
    model = model if model in MODEL_COST else "local"
    spent = _today_spend(db)
    cost = MODEL_COST[model]
    if model != "local" and spent + cost > settings.VISION_DAILY_COST_LIMIT_USD:
        model, cost = "local", 0.0
    b64 = base64.b64encode(image).decode()
    result = None
    if model == "deepseek" and settings.DEEPSEEK_API_KEY:
        result = await _remote("https://api.deepseek.com/v1/vision",
                               {"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
                               {"image": b64})
    elif model == "claude" and settings.ANTHROPIC_API_KEY:
        result = await _remote(
            "https://api.anthropic.com/v1/messages",
            {"x-api-key": settings.ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01"},
            {"model": "claude-opus-4-8", "max_tokens": 200, "messages": [
                {"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64",
                     "media_type": "image/jpeg", "data": b64}},
                    {"type": "text", "text": "Identify product, penny & clearance likelihood (0-1), confidence, explanation."}]}]})
    parsed = _local(image) if not result else {
        "product_guess": str(result.get("product_guess", "See provider response")),
        "penny_likelihood": float(result.get("penny_likelihood", 0.5)),
        "clearance_likelihood": float(result.get("clearance_likelihood", 0.5)),
        "confidence": float(result.get("confidence", 0.6)),
        "explanation": str(result.get("explanation", "Provider analysis")),
    }
    if not result and model != "local":
        cost = 0.0
    db.add(VisionLog(model=model, cost_usd=cost, result_json=parsed))
    db.commit()
    return {**parsed, "model": model, "cost_usd": cost, "daily_spent_usd": round(spent + cost, 4)}

