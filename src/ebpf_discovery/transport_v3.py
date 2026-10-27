"""Completed HTTP bytes under a total observation cap, never an application SLO.

A requests-style scalar timeout is an inactivity/connect timeout, not an absolute
whole-body bound. A shared asynchronous loop enforces the remaining attempt
budget through connection, transfer and body receipt without spawning a process
for every request. Adapters keep their original Response/body interpretation.
"""
from __future__ import annotations
import asyncio
import concurrent.futures
import json
import threading
import time

import aiohttp
import requests

_loop = None
_lock = threading.Lock()


def _event_loop():
    global _loop
    with _lock:
        if _loop is None:
            loop = asyncio.new_event_loop()
            ready = threading.Event()
            def run():
                asyncio.set_event_loop(loop)
                ready.set()
                loop.run_forever()
            threading.Thread(target=run, name='bounded-http-observer', daemon=True).start()
            ready.wait()
            _loop = loop
    return _loop


async def _perform(method, url, deadline, kwargs):
    remaining = deadline-time.monotonic()
    if remaining <= 0:
        raise TimeoutError('Observation budget exhausted before HTTP dispatch')
    timeout = aiohttp.ClientTimeout(total=remaining, ceil_threshold=float('inf'))
    headers = requests.utils.default_headers()
    headers.update(kwargs.pop('headers', None) or {})
    async with asyncio.timeout(remaining):
        async with aiohttp.ClientSession(timeout=timeout, headers=headers,
                json_serialize=lambda value: json.dumps(value, allow_nan=False),
                trust_env=True) as session:
            async with session.request(method, url, **kwargs) as incoming:
                content = await incoming.read()
                completed_ns, completed_mono = time.time_ns(), time.monotonic()
                response = requests.Response()
                response.status_code = incoming.status
                response.reason = incoming.reason
                response.url = str(incoming.url)
                response.headers = requests.structures.CaseInsensitiveDict(incoming.headers)
                response._content = content
                response._content_consumed = True
                response.encoding = requests.utils.get_encoding_from_headers(response.headers)
                response._study_body_completed_ns = completed_ns
                response._study_body_completed_monotonic = completed_mono
                return response


def request(method, url, *, timeout, **kwargs):
    """Return a complete requests.Response or a transport exception by the cap."""
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        raise requests.Timeout('Total HTTP observation budget exhausted')
    deadline = time.monotonic()+timeout
    future = asyncio.run_coroutine_threadsafe(_perform(method, url, deadline, dict(kwargs)), _event_loop())
    try:
        # The coroutine enforces the cap. A short outer watchdog prevents a
        # stalled event-loop thread from occupying the load worker indefinitely.
        return future.result(timeout=timeout+0.5)
    except (TimeoutError, concurrent.futures.TimeoutError) as exc:
        future.cancel()
        raise requests.Timeout('Total HTTP observation cap reached') from exc
    except aiohttp.ClientError as exc:
        raise requests.ConnectionError(str(exc)) from exc
