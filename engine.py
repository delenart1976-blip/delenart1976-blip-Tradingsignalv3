
import numpy as np, pandas as pd

def add_indicators(d):
    x=d.copy()
    x["ema20"]=x.close.ewm(span=20,adjust=False).mean()
    x["ema50"]=x.close.ewm(span=50,adjust=False).mean()
    x["ema200"]=x.close.ewm(span=200,adjust=False).mean()
    delta=x.close.diff()
    gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False).mean()
    loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean()
    x["rsi"]=100-100/(1+gain/loss.replace(0,np.nan))
    prev=x.close.shift()
    tr=pd.concat([x.high-x.low,(x.high-prev).abs(),(x.low-prev).abs()],axis=1).max(axis=1)
    x["atr"]=tr.ewm(alpha=1/14,adjust=False).mean()
    macd=x.close.ewm(span=12,adjust=False).mean()-x.close.ewm(span=26,adjust=False).mean()
    x["macd_hist"]=macd-macd.ewm(span=9,adjust=False).mean()
    up=x.high.diff(); dn=-x.low.diff()
    plus=np.where((up>dn)&(up>0),up,0)
    minus=np.where((dn>up)&(dn>0),dn,0)
    p=pd.Series(plus,index=x.index).ewm(alpha=1/14,adjust=False).mean()
    m=pd.Series(minus,index=x.index).ewm(alpha=1/14,adjust=False).mean()
    pdi=100*p/x.atr.replace(0,np.nan); mdi=100*m/x.atr.replace(0,np.nan)
    dx=100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)
    x["adx"]=dx.ewm(alpha=1/14,adjust=False).mean()
    x["res"]=x.high.rolling(20).max().shift(1)
    x["sup"]=x.low.rolling(20).min().shift(1)
    x["vol_ma"]=x.volume.rolling(20).mean()
    return x.dropna().reset_index(drop=True)

def score(d):
    x=add_indicators(d)
    if len(x)<20: return {"signal":"WAIT","score":0,"reason":"Dati insufficienti"}
    r=x.iloc[-1]; s=50; reasons=[]
    if r.ema20>r.ema50>r.ema200: s+=25; reasons.append("trend rialzista")
    elif r.ema20<r.ema50<r.ema200: s-=25; reasons.append("trend ribassista")
    if r.rsi>=55 and r.macd_hist>0: s+=15; reasons.append("momentum rialzista")
    elif r.rsi<=45 and r.macd_hist<0: s-=15; reasons.append("momentum ribassista")
    if r.close>r.res: s+=15; reasons.append("breakout")
    elif r.close<r.sup: s-=15; reasons.append("breakdown")
    if r.adx>=20: reasons.append("ADX conferma trend")
    if r.volume>r.vol_ma: s += 5 if r.close>=r.open else -5; reasons.append("volume sopra media")
    if abs(r.close-r.ema20)>2*r.atr: s-=5; reasons.append("prezzo esteso")
    s=int(np.clip(s,0,100))
    side="BUY" if s>=85 and r.close>r.ema50 else "SELL" if s>=85 and r.close<r.ema50 else "WAIT"
    if side=="BUY":
        entry=float(r.close); sl=entry-1.5*r.atr; tp1=entry+1.5*r.atr; tp2=entry+3*r.atr
    elif side=="SELL":
        entry=float(r.close); sl=entry+1.5*r.atr; tp1=entry-1.5*r.atr; tp2=entry-3*r.atr
    else: entry=sl=tp1=tp2=None
    return {"signal":side,"score":s,"entry":entry,"sl":sl,"tp1":tp1,"tp2":tp2,
            "rr":2.0 if side!="WAIT" else None,"reason":"; ".join(reasons)}

def mtf(frames):
    vals={tf:score(df) for tf,df in frames.items()}
    good=[v for v in vals.values() if v.get("score",0)>0]
    avg=round(sum(v["score"] for v in good)/len(good),1) if good else 0
    buys=sum(v["signal"]=="BUY" for v in good); sells=sum(v["signal"]=="SELL" for v in good)
    final="BUY" if avg>=85 and buys>=2 else "SELL" if avg>=85 and sells>=2 else "WAIT"
    return {"signal":final,"score":avg,"buy_tf":buys,"sell_tf":sells,"frames":vals}
