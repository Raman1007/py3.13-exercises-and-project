
"""Canonical token counting for the retail_context project.

Methodology:
1. SDK path — Anthropic messages.count_tokens endpoint.
2. Heuristic path — len(text) / 3.8 when using CLI or no API key.
"""
from __future__ import annotations

import os
from functools import lru_cache

from retail_context.client import get_client, get_model

_CHARS_PER_TOKEN = 3.8


def _use_sdk() -> bool:
    """Use SDK token counting only when the SDK backend is configured."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def methodology() -> str:
    if _use_sdk():
        return "Anthropic messages.count_tokens endpoint (model-authoritative)"
    return f"len(text) / {_CHARS_PER_TOKEN} heuristic (CLI or no API key)"


@lru_cache(maxsize=4096)
def count(text: str) -> int:
    if not text:
        return 0

    if _use_sdk():
        client = get_client()

        # Check SDK compatibility before using the endpoint.
        if hasattr(client.messages, "count_tokens"):
            resp = client.messages.count_tokens(
                model=get_model(),
                messages=[{"role": "user", "content": text}],
            )
            return int(resp.input_tokens)

    return max(1, int(len(text) / _CHARS_PER_TOKEN))


def count_many(texts: list[str]) -> int:
    return sum(count(t) for t in texts)
