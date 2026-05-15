from __future__ import annotations

import os
import httpx

DEFAULT_BASE_URL = "https://treasuremap.space/api/v1"

_token: str = ""
_base_url: str = DEFAULT_BASE_URL


def configure(api_token: str = None, base_url: str = None) -> None:
    global _token, _base_url
    _token = api_token or os.getenv("GWTM_API_TOKEN", "")
    _base_url = (base_url or os.getenv("GWTM_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")


def _headers() -> dict:
    return {"api_token": _token}


def _clean(params: dict) -> dict:
    return {k: v for k, v in params.items() if v is not None}


def get(path: str, params: dict = None) -> list | dict:
    response = httpx.get(
        f"{_base_url}{path}", headers=_headers(), params=_clean(params or {}))
    response.raise_for_status()
    return response.json()


def post(path: str, json: dict = None) -> dict:
    response = httpx.post(f"{_base_url}{path}", headers=_headers(), json=json)
    response.raise_for_status()
    return response.json()


def put(path: str, json: dict = None) -> dict:
    response = httpx.put(f"{_base_url}{path}", headers=_headers(), json=json)
    response.raise_for_status()
    return response.json()


def delete(path: str, json: dict = None) -> dict:
    response = httpx.delete(f"{_base_url}{path}", headers=_headers(), json=json)
    response.raise_for_status()
    return response.json()


def get_raw(path: str, params: dict = None) -> httpx.Response:
    return httpx.get(
        f"{_base_url}{path}", headers=_headers(), params=_clean(params or {}))
