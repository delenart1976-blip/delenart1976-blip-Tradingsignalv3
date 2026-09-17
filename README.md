# TradingSignalAI

Dashboard Streamlit per segnali multi-timeframe su forex e crypto, in modalità esclusivamente paper trading.

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

Inserisci la tua chiave in `.env`:

```env
MASSIVE_API_KEY=la_tua_chiave
```

Su Streamlit Cloud, inserisci la stessa variabile in **Settings → Secrets**.

L'app legge i dati su 15m, 1H e 4H, calcola indicatori tecnici e salva i segnali confermati in `signals.csv`. Non effettua ordini reali. I segnali non sono consulenza finanziaria: verifica sempre dati, spread, liquidità e rischio prima di operare.
