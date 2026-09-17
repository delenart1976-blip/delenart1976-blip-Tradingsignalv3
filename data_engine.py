"""Market data access layer for Massive/Polygon-compatible endpoints."""

import os
from datetime import date
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("MASSIVE_BASE_URL", "https://api.massive.com").rstrip("/")


def _api_key() -> str:
    key = os.getenv("MASSIVE_API_KEY", "").strip()
    if not key:
        try:
            import streamlit as st
            key = str(st.secrets.get("MASSIVE_API_KEY", "")).strip()
        except Exception:
            pass
    if not key or key == "your_key_here":
        raise RuntimeError("MASSIVE_API_KEY mancante. Configurala in .env o nei secrets di Streamlit.")
    return key


def _get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    query = dict(params or {})
    query["apiKey"] = _api_key()
    try:
        response = requests.get(f"{BASE}{path}", params=query, timeout=30)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Errore API ({getattr(exc.response, 'status_code', 'rete')}): {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("La risposta API non è JSON valida.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Risposta API non valida.")
    return payload


def _bars(rows: list[dict[str, Any]], timestamp_unit: str = "ms") -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["time", "open", "high", "low", "close", "volume"])
    data = pd.DataFrame(rows).rename(columns={"t": "time", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "window_start": "time"})
    required = ["time", "open", "high", "low", "close"]
    missing = [column for column in required if column not in data]
    if missing:
        raise RuntimeError(f"Dati OHLC incompleti: mancano {', '.join(missing)}")
    if "volume" not in data:
        data["volume"] = 0.0
    data["time"] = pd.to_datetime(data["time"], unit=timestamp_unit, utc=True, errors="coerce")
    for column in ["open", "high", "low", "close", "volume"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    return data[["time", "open", "high", "low", "close", "volume"]].dropna().sort_values("time").drop_duplicates("time").reset_index(drop=True)


def forex_crypto_bars(ticker: str, mult: int, timespan: str, start: str | date, end: str | date, limit: int = 50000) -> pd.DataFrame:
    payload = _get(f"/v2/aggs/ticker/{ticker}/range/{mult}/{timespan}/{start}/{end}", {"adjusted": "true", "sort": "asc", "limit": limit})
    return _bars(payload.get("results", []))


def active_futures(product_code: str | None = None) -> pd.DataFrame:
    payload = _get("/futures/v1/contracts", {"active": "true", "limit": 1000})
    data = pd.DataFrame(payload.get("results", []))
    if product_code and not data.empty and "product_code" in data:
        data = data[data["product_code"].astype(str).str.upper() == product_code.upper()]
    return data.reset_index(drop=True)


def futures_bars(contract: str, resolution: str, start: str | None = None, limit: int = 50000) -> pd.DataFrame:
    params: dict[str, Any] = {"resolution": resolution, "limit": limit, "sort": "window_start.asc"}
    if start:
        params["window_start.gte"] = start
    payload = _get(f"/futures/v1/aggs/{contract}", params)
    return _bars(payload.get("results", []), timestamp_unit="ns")
