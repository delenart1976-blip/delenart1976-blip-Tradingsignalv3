# TradingSignalAI

Dashboard Streamlit per segnali basati su dati live da API esterna. Le informazioni usano prezzi reali del mercato, non dati mock o locali.

## Requisiti

- Python 3.10+
- Una chiave valida `MASSIVE_API_KEY`

## Avvio rapido

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Inserisci la chiave in `.env`:

```env
MASSIVE_API_KEY=la_tua_chiave
MASSIVE_BASE_URL=https://api.massive.com
```

Su Streamlit Cloud, inserisci le stesse variabili in **Settings → Secrets**.

L'app recupera dati live per 15m, 1H e 4H, calcola indicatori tecnici, e salva i segnali in `signals.csv` senza inviare ordini reali.

Attenzione: i segnali non sono consulenza finanziaria e non devono essere trattati come raccomandazioni di trading.
