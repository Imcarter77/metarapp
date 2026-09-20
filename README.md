# METAR Made Friendly

METAR Made Friendly is a lightweight Flask web application that retrieves a current airport METAR (Meteorological Aerodrome Report) and translates common METAR information into plain English.

Enter a four-letter ICAO airport code, such as `KJFK`, `EGLL`, or `YSSY`, and the application retrieves the latest available METAR from the Aviation Weather Center.

## What the application does

The application:

- Accepts a four-letter ICAO airport code.
- Retrieves the current METAR from the Aviation Weather Center API.
- Parses common METAR fields.
- Converts technical weather information into easier-to-understand language.
- Displays information including:
  - Wind direction and speed
  - Gusts
  - Visibility
  - Weather conditions
  - Cloud coverage and cloud base
  - Temperature
  - Dew point
  - Atmospheric pressure
  - Observation time
- Displays the original/raw METAR alongside the decoded information.

### Example

Enter:

`EGLL`

The application retrieves the latest available METAR for London Heathrow and presents the report in a more readable format.

> **Note:** This application is intended as a learning and readability aid. It is not a replacement for official aviation weather products, NOTAMs, flight briefings, or operational decision-making.

## Technology

- **Python 3.9+**
- **Flask**
- **Requests**
- **HTML/CSS**
- **Aviation Weather Center API**

## Prerequisites

Before installing the application, make sure you have:

- Python 3.9 or newer
- Git
- Internet access

## Installation

Clone the repository:

```bash
git clone https://github.com/Imcarter77/metarapp.git
cd metarapp
```

### Create a virtual environment

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The application currently uses:

- Flask
- Requests

## Start the application

From the project directory, run:

```bash
python app.py
```

You should see Flask start the development server.

Open the application in your browser:

```text
http://127.0.0.1:5000
```

Enter a four-letter ICAO airport code and submit the form to retrieve the latest available METAR.

### Stop the application

Press:

```text
Ctrl + C
```

in the terminal running Flask.

## Project structure

```text
metarapp/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    └── ...
```

## API

The application uses the Aviation Weather Center METAR API:

```text
https://aviationweather.gov/api/data/metar
```

The application requests the latest available METAR for the supplied ICAO airport code and processes the returned report.

## Development

The Flask application currently runs in development mode.

For local development:

```bash
python app.py
```

When making changes, test the application locally and verify that the METAR is retrieved and decoded correctly.

## Built with OpenAI Codex

This application was developed with assistance from **OpenAI Codex**, an AI coding agent used to help write, understand, modify, and troubleshoot code directly within a development environment.

Codex provides a workflow comparable to **Anthropic's Claude Code**, allowing developers to work with an AI coding agent alongside their source code, terminal, and development tools.

The application remains a human-directed project: AI assistance was used during development, while the project requirements, review, testing, and final decisions remain with the developer.

## Licence

This project is provided for learning and development purposes.

## Developer
Frederick Mensah - 20/09/2026
