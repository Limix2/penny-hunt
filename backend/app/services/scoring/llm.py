"""LLM score refinement (Claude Opus 4.8). Disabled unless ENABLE_LLM_SCORING=true
and ANTHROPIC_API_KEY is set, so the app stays offline-runnable and free by default."""
import httpx
from app.core.config import settings


async def refine(base_score: float, explanation: str, context: dict) -> tuple[float, str, str]:
    if not (settings.ENABLE_LLM_SCORING and settings.ANTHROPIC_API_KEY):
        return base_score, "rule_v2", explanation
    try:
        prompt = (f"Penny-item likelihood (0-100). Base rule score={base_score}. "
                  f"Context={context}. Reply with only a number then a short reason.")
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": settings.ANTHROPIC_API_KEY,
                         "anthropic-version": "2023-06-01"},
                json={"model": "claude-opus-4-8", "max_tokens": 80,
                      "messages": [{"role": "user", "content": prompt}]},
            )
            r.raise_for_status()
            text = r.json()["content"][0]["text"].strip()
        return max(0.0, min(100.0, float(text.split()[0]))), "rule_v2+llm", text
    except Exception:
        return base_score, "rule_v2", explanation
