
import os
from datetime import datetime,timedelta,timezone
import pandas as pd, streamlit as st
from data_engine import forex_crypto_bars, active_futures, futures_bars
from engine import mtf
from journal import log

ASSETS={"EUR/USD":"C:EURUSD","GBP/USD":"C:GBPUSD","USD/JPY":"C:USDJPY","BTC/USD":"X:BTCUSD","ETH/USD":"X:ETHUSD"}
st.set_page_config(page_title="TradingSignalAI REAL v3",layout="wide")
st.title("TradingSignalAI — REAL v3")
st.caption("Analisi automatica multi-timeframe. Modalità PAPER TRADING.")

asset=st.selectbox("Mercato",list(ASSETS))
if st.button("SCANSIONA ORA"):
    end=datetime.now(timezone.utc).date(); start=end-timedelta(days=45)
    frames={}
    errors={}
    for tf,m,u in [("15m",15,"minute"),("1H",1,"hour"),("4H",4,"hour")]:
        try: frames[tf]=forex_crypto_bars(ASSETS[asset],m,u,str(start),str(end))
        except Exception as e: errors[tf]=str(e)
    if errors: st.error(" | ".join(f"{k}: {v}" for k,v in errors.items()))
    if frames:
        r=mtf(frames)
        a,b,c=st.columns(3); a.metric("SEGNALE",r["signal"]); b.metric("SCORE",r["score"]); c.metric("TF BUY",r["buy_tf"])
        rows=[]
        for tf,v in r["frames"].items():
            rows.append({"TF":tf,**v})
        st.dataframe(pd.DataFrame(rows),use_container_width=True)
        if r["signal"]!="WAIT":
            v=r["frames"]["15m"]
            log({"timestamp":datetime.now(timezone.utc).isoformat(),"asset":asset,"signal":r["signal"],"score":r["score"],
                 "entry":v.get("entry"),"sl":v.get("sl"),"tp1":v.get("tp1"),"tp2":v.get("tp2"),"rr":v.get("rr"),"reason":v.get("reason")})
            st.success("Segnale registrato nello storico.")
else:
    st.info("Inserisci MASSIVE_API_KEY nel file .env e premi SCANSIONA ORA.")

st.divider()
st.subheader("Futures: Gold / WTI")
st.write("Il motore può usare i contratti futures Massive; il contratto va scelto dinamicamente in base a scadenza/liquidità. Non vengono inviati ordini.")
