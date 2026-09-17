import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from data_engine import forex_crypto_bars
from engine import mtf
from journal import history, log

ASSETS = {"EUR/USD": "C:EURUSD", "GBP/USD": "C:GBPUSD", "USD/JPY": "C:USDJPY", "BTC/USD": "X:BTCUSD", "ETH/USD": "X:ETHUSD"}
TIMEFRAMES = [("15m", 15, "minute"), ("1H", 1, "hour"), ("4H", 4, "hour")]

st.set_page_config(page_title="TradingSignalAI", page_icon="📈", layout="wide")
st.title("TradingSignalAI")
st.caption("Analisi multi-timeframe · PAPER TRADING · nessun ordine reale viene inviato")

with st.sidebar:
    st.header("Impostazioni")
    asset = st.selectbox("Mercato", list(ASSETS))
    days = st.slider("Giorni di storico", 30, 90, 45)
    scan = st.button("🔎 SCANSIONA ORA", type="primary", use_container_width=True)
    key_present = bool(os.getenv("MASSIVE_API_KEY", "").strip())
    if not key_present:
        try: key_present = bool(st.secrets.get("MASSIVE_API_KEY", "").strip())
        except Exception: pass
    st.caption("API: configurata ✅" if key_present else "API: manca MASSIVE_API_KEY ⚠️")

if scan:
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)
    frames, errors = {}, {}
    progress = st.progress(0, text="Recupero dati...")
    for index, (tf, multiplier, timespan) in enumerate(TIMEFRAMES, 1):
        try:
            frame = forex_crypto_bars(ASSETS[asset], multiplier, timespan, start, end)
            if frame.empty: errors[tf] = "Nessun dato restituito"
            else: frames[tf] = frame
        except Exception as exc:
            errors[tf] = str(exc)
        progress.progress(index / len(TIMEFRAMES), text=f"Elaborazione {tf}...")
    progress.empty()
    if errors:
        st.warning(" · ".join(f"{tf}: {error}" for tf, error in errors.items()))
    if frames:
        result = mtf(frames)
        a, b, c, d = st.columns(4)
        a.metric("SEGNALE", result["signal"])
        b.metric("CONFIDENCE", result["score"])
        c.metric("TF BUY", result["buy_tf"])
        d.metric("TF SELL", result["sell_tf"])
        rows = [{"TF": tf, **value} for tf, value in result["frames"].items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        if result["signal"] != "WAIT" and "15m" in result["frames"]:
            value = result["frames"]["15m"]
            log({"timestamp": datetime.now(timezone.utc).isoformat(), "asset": asset, "signal": result["signal"], "score": result["score"], "entry": value.get("entry"), "sl": value.get("sl"), "tp1": value.get("tp1"), "tp2": value.get("tp2"), "rr": value.get("rr"), "reason": value.get("reason")})
            st.success("Segnale registrato nello storico paper-trading.")
else:
    st.info("Configura MASSIVE_API_KEY e premi SCANSIONA ORA.")

st.divider()
st.subheader("Storico segnali")
records = history()
st.dataframe(pd.DataFrame(records) if records else pd.DataFrame(columns=["timestamp", "asset", "signal", "score", "entry", "sl", "tp1", "tp2", "rr", "reason"]), use_container_width=True, hide_index=True)
