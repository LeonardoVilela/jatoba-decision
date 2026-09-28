"""TypeSafe Jev (typesafe-ai/jev) through the Vercel AI Gateway System One endpoint. Hosted, not deterministic.

Frozen protocol: one question per request; the identical payload on every attempt; 4 attempts with waits of 1, 2 and
4 s, retrying only connection errors, timeouts, 429 and 5xx. A response counts only if it was served by typesafe-ai/jev
with gateway routing finalProvider == "typesafe-ai" (the gateway can route elsewhere). When the retry budget is exhausted
the run stops: records are never dropped or imputed, which is why the reported Jev coverage is PARTIAL.
The API key is read from AI_GATEWAY_API_KEY and is never logged.
"""

import os
import time

import requests

URL = "https://ai-gateway.vercel.sh/typesafe/v1/systemone"
MODEL = "typesafe-ai/jev"
PROVIDER = "typesafe-ai"
WAITS = (1.0, 2.0, 4.0)


class JevStop(RuntimeError):
    pass


def _retryable(status: int | None) -> bool:
    return status is None or status == 429 or 500 <= status < 600


def ask(state: str, question: dict, timeout: float = 60.0) -> dict:
    headers = {"Authorization": f"Bearer {os.environ['AI_GATEWAY_API_KEY']}", "Content-Type": "application/json"}
    body = {"model": MODEL, "state": state, "questions": {"q": question}}
    for attempt in range(len(WAITS) + 1):
        status = None
        try:
            response = requests.post(URL, json=body, headers=headers, timeout=timeout)
            status = response.status_code
            if status == 200:
                data = response.json()
                routing = ((data.get("provider_metadata") or {}).get("gateway") or {}).get("routing") or {}
                if data.get("model") != MODEL or routing.get("finalProvider") != PROVIDER:
                    raise JevStop(f"response not served by {MODEL}/{PROVIDER}")
                return data["answers"]["q"]
        except (requests.ConnectionError, requests.Timeout):
            pass
        if not _retryable(status):
            raise JevStop(f"non-retryable HTTP {status}")
        if attempt < len(WAITS):
            time.sleep(WAITS[attempt])
    raise JevStop("no valid response after 4 attempts")
