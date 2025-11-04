"""Utility helpers for dispatching outbound webhook events."""

from __future__ import annotations

import asyncio
import inspect
from typing import Any, Dict, Iterable

try:  # pragma: no cover - optional dependency
    import httpx  # type: ignore[import]
except ImportError:  # pragma: no cover - fallback when httpx missing
    httpx = None  # type: ignore[assignment]

from app.core.config import settings


async def dispatch_event(event_name: str, payload: Dict[str, Any]) -> None:
    """Send the given payload to all configured webhook endpoints."""

    endpoints: Iterable[str] = settings.WEBHOOK_ENDPOINTS
    if not endpoints:
        return

    body: Dict[str, Any] = {"event": event_name, "payload": payload}

    async def _post(url: str) -> None:
        if httpx is None:
            return

        async_client_cls = getattr(httpx, "AsyncClient", None)
        if async_client_cls is None:
            return

        try:
            async with async_client_cls(timeout=10.0) as client:  # type: ignore[misc]
                post_method = getattr(client, "post", None)
                if callable(post_method):
                    response = post_method(url, json=body)
                    if inspect.isawaitable(response):
                        await response
        except Exception as exc:  # pragma: no cover - network failures are non-fatal
            print(f"Webhook dispatch failed for {url}: {exc}")

    await asyncio.gather(*(_post(endpoint) for endpoint in endpoints))
