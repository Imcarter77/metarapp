# METAR Made Friendly

A Flask web app that retrieves a current airport METAR and translates common report fields into plain English.

## Run it

Install Python 3.9 or newer, then from this folder run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` and enter a four-letter ICAO code, such as `KJFK`, `EGLL`, or `YSSY`.

The app retrieves live reports from the Aviation Weather Center. It is a readable aid, not a replacement for official weather products or flight briefings.

