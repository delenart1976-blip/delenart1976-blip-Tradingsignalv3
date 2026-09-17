# TradingSignalAI

TradingSignalAI is a multi-timeframe market signal dashboard built with Streamlit.

It analyzes forex and crypto assets using moving averages, RSI, MACD, ADX, support/resistance, and volume filters.

## Features
- Multi-timeframe scan: 15m, 1H, 4H
- Signals: BUY / SELL / WAIT
- Score and risk plan (entry, SL, TP1, TP2)
- Automatic logging in `signals.csv`
- Paper-trading oriented UI

## Requirements
- Python 3.10+
- pip
- A valid `MASSIVE_API_KEY`

## Quick start

1. Clone the repository
2. Create and activate a virtual environment

On Linux/Mac:
```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure API key
Create a `.env` file in the project root using the example:
```bash
cp .env.example .env
```
Then edit `.env` and set:
```env
MASSIVE_API_KEY=your_key_here
```

Alternative for Streamlit Cloud / local secrets:
```toml
# .streamlit/secrets.toml
MASSIVE_API_KEY = "your_key_here"
```

5. Start the app
```bash
streamlit run app.py
```

Then open the URL shown in the terminal, usually:
```text
http://localhost:8501
```

## Notes
- The app does not send real orders; it is in paper-trading mode.
- If no API key is provided, the app will show a warning instead of running the scan.
- The journal writes trade records to `signals.csv` in the project root.
