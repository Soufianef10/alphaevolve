"""Thin async wrapper around the OpenAI Chat Completions API.

* Transparent exponential back‑off with `backoff` package
* Enforces structured‑output (`{"type": "json_object"}`)
* Centralised settings via `pwb_alphaevolve.config.settings`
"""

from typing import Any

import backoff
import openai

from pwb_alphaevolve.config import settings

# Configure global client key
_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)


@backoff.on_exception(backoff.expo, openai.OpenAIError, max_tries=5, jitter=backoff.full_jitter)
async def chat(messages: list[dict[str, str]], **kw) -> Any:
    """Call OpenAI chat completion returning the ``message`` object of the first choice."""
    # ensure response_format enforced
    response_format = {"type": "json_object"}
    params = {
        "model": settings.openai_model,
        "messages": messages,
        "max_tokens": settings.max_tokens,
        "response_format": response_format,
    }
    params.update(kw)
    completion = await _client.chat.completions.create(**params)
    return completion.choices[0].message
