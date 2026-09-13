
import os, requests, pandas as pd
from dotenv import load_dotenv
load_dotenv()
KEY=os.getenv("MASSIVE_API_KEY","")
if not KEY:
    try:
        import streamlit as st
        KEY=st.secrets.get("MASSIVE_API_KEY","")
    except Exception:
        pass
BASE="https://api.massive.com"

def _get(url, params=None):
    if not KEY: raise RuntimeError("MASSIVE_API_KEY mancante.")
    p=dict(params or {}); p["apiKey"]=KEY
    r=requests.get(url,params=p,timeout=30)
    r.raise_for_status()
    return r.json()

def forex_crypto_bars(ticker,mult,timespan,start,end,limit=50000):
    data=_get(f"{BASE}/v2/aggs/ticker/{ticker}/range/{mult}/{timespan}/{start}/{end}",
              {"adjusted":"true","sort":"asc","limit":limit})
    rows=data.get("results",[])
    if not rows: return pd.DataFrame()
    d=pd.DataFrame(rows).rename(columns={"t":"time","o":"open","h":"high","l":"low","c":"close","v":"volume"})
    d["time"]=pd.to_datetime(d["time"],unit="ms",utc=True)
    return d[["time","open","high","low","close","volume"]].sort_values("time").reset_index(drop=True)

def active_futures(product_code=None):
    params={"active":"true","limit":1000}
    data=_get(f"{BASE}/futures/v1/contracts",params)
    d=pd.DataFrame(data.get("results",[]))
    if product_code and not d.empty:
        d=d[d.product_code.astype(str).str.upper()==product_code.upper()]
    return d

def futures_bars(contract,resolution,start=None,limit=50000):
    params={"resolution":resolution,"limit":limit,"sort":"window_start.asc"}
    if start: params["window_start.gte"]=start
    data=_get(f"{BASE}/futures/v1/aggs/{contract}",params)
    rows=data.get("results",[])
    if not rows: return pd.DataFrame()
    d=pd.DataFrame(rows).rename(columns={"window_start":"time"})
    d["time"]=pd.to_datetime(d["time"],unit="ns",utc=True)
    if "volume" not in d: d["volume"]=0
    return d[["time","open","high","low","close","volume"]].sort_values("time").reset_index(drop=True)
