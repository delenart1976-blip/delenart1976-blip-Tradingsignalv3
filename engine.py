"""Technical indicators and multi-timeframe signal scoring."""

import numpy as np
import pandas as pd


def add_indicators(data: pd.DataFrame) -> pd.DataFrame:
    required = {"open", "high", "low", "close", "volume"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Colonne mancanti: {', '.join(sorted(missing))}")
    x = data.copy().sort_values("time" if "time" in data else data.index).reset_index(drop=True)
    for column in required:
        x[column] = pd.to_numeric(x[column], errors="coerce")
    x = x.dropna(subset=list(required))
    x["ema20"] = x.close.ewm(span=20, adjust=False).mean()
    x["ema50"] = x.close.ewm(span=50, adjust=False).mean()
    x["ema200"] = x.close.ewm(span=200, adjust=False).mean()
    delta = x.close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    x["rsi"] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    previous = x.close.shift()
    true_range = pd.concat([x.high - x.low, (x.high - previous).abs(), (x.low - previous).abs()], axis=1).max(axis=1)
    x["atr"] = true_range.ewm(alpha=1 / 14, adjust=False).mean()
    macd = x.close.ewm(span=12, adjust=False).mean() - x.close.ewm(span=26, adjust=False).mean()
    x["macd_hist"] = macd - macd.ewm(span=9, adjust=False).mean()
    up, down = x.high.diff(), -x.low.diff()
    plus = pd.Series(np.where((up > down) & (up > 0), up, 0), index=x.index).ewm(alpha=1 / 14, adjust=False).mean()
    minus = pd.Series(np.where((down > up) & (down > 0), down, 0), index=x.index).ewm(alpha=1 / 14, adjust=False).mean()
    pdi, mdi = 100 * plus / x.atr.replace(0, np.nan), 100 * minus / x.atr.replace(0, np.nan)
    x["adx"] = (100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)).ewm(alpha=1 / 14, adjust=False).mean()
    x["res"] = x.high.rolling(20).max().shift(1)
    x["sup"] = x.low.rolling(20).min().shift(1)
    x["vol_ma"] = x.volume.rolling(20).mean()
    return x.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)


def score(data: pd.DataFrame) -> dict:
    try:
        x = add_indicators(data)
    except (ValueError, KeyError) as exc:
        return {"signal": "WAIT", "score": 0, "reason": str(exc)}
    if len(x) < 20:
        return {"signal": "WAIT", "score": 0, "reason": "Dati insufficienti: servono almeno 220 barre valide."}
    row = x.iloc[-1]
    points, reasons = 50, []
    if row.ema20 > row.ema50 > row.ema200:
        points += 25; reasons.append("trend rialzista")
    elif row.ema20 < row.ema50 < row.ema200:
        points -= 25; reasons.append("trend ribassista")
    if row.rsi >= 55 and row.macd_hist > 0:
        points += 15; reasons.append("momentum rialzista")
    elif row.rsi <= 45 and row.macd_hist < 0:
        points -= 15; reasons.append("momentum ribassista")
    if row.close > row.res:
        points += 15; reasons.append("breakout")
    elif row.close < row.sup:
        points -= 15; reasons.append("breakdown")
    if row.adx >= 20: reasons.append("ADX conferma trend")
    if row.volume > row.vol_ma:
        points += 5 if row.close >= row.open else -5; reasons.append("volume sopra media")
    if abs(row.close - row.ema20) > 2 * row.atr:
        points -= 5; reasons.append("prezzo esteso")
    # Keep direction separate from confidence: a bearish score must not be clipped to zero.
    confidence = int(np.clip(abs(points - 50) + 50, 0, 100))
    signal = "BUY" if points >= 85 and row.close > row.ema50 else "SELL" if points <= 15 and row.close < row.ema50 else "WAIT"
    entry = float(row.close) if signal != "WAIT" else None
    if signal == "BUY": sl, tp1, tp2 = entry - 1.5 * row.atr, entry + 1.5 * row.atr, entry + 3 * row.atr
    elif signal == "SELL": sl, tp1, tp2 = entry + 1.5 * row.atr, entry - 1.5 * row.atr, entry - 3 * row.atr
    else: sl = tp1 = tp2 = None
    return {"signal": signal, "score": confidence, "entry": entry, "sl": float(sl) if sl is not None else None, "tp1": float(tp1) if tp1 is not None else None, "tp2": float(tp2) if tp2 is not None else None, "rr": 2.0 if signal != "WAIT" else None, "reason": "; ".join(reasons) or "Nessuna conferma"}


def mtf(frames: dict[str, pd.DataFrame]) -> dict:
    values = {tf: score(frame) for tf, frame in frames.items() if frame is not None and not frame.empty}
    good = [value for value in values.values() if value.get("score", 0) > 0]
    average = round(sum(value["score"] for value in good) / len(good), 1) if good else 0
    buys = sum(value["signal"] == "BUY" for value in good)
    sells = sum(value["signal"] == "SELL" for value in good)
    final = "BUY" if average >= 85 and buys >= 2 else "SELL" if average >= 85 and sells >= 2 else "WAIT"
    return {"signal": final, "score": average, "buy_tf": buys, "sell_tf": sells, "frames": values}
