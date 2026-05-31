# Race Engineer Dashboard

Formula 1 race engineer style dashboard built with Streamlit and the OpenF1 API. It gives you a live-command-center feel with session selection, lap pace analysis, weather, race control messages, driver telemetry, track trace, stint summaries, and optional team radio clips.

## Why Streamlit

I chose Streamlit over Flask for the first version because it lets me ship a polished analytics dashboard faster, which is ideal for a GitHub standout project. It also deploys cleanly on Streamlit Community Cloud and can still run on Render if I want more control later.

## Features

- Grand Prix weekend and session selector
- Lap pace chart by driver
- Weather trend panel
- Fastest lap summary and session overview cards
- Driver drilldown with sector summary, telemetry traces, and track map
- Position or interval history view
- Stint table and optional team radio playback
- Race control feed table
- Auto refresh for active sessions

## Project structure

```text
Race-Engineer-Dashboard/
├── app.py
├── requirements.txt
└── README.md
```

## Local setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push these files to GitHub.
2. Go to https://share.streamlit.io/
3. Click **New app**
4. Select your repo and `app.py`
5. Deploy

## Deploy to Render

- Environment: Python 3
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Future extensions

- Add tire compound strategy overlays
- Add teammate delta comparisons
- Add alerts for yellow flag, safety car, and rain changes
- Add historical session comparison mode
- Add export buttons for lap analysis CSV files
