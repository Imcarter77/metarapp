"""METAR Made Friendly by Freddie — a small Flask METAR reader."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

import requests
from flask import Flask, render_template, request

app = Flask(__name__)

API_URL = "https://aviationweather.gov/api/data/metar"
WEATHER = {
    "-RA": "light rain", "RA": "rain", "+RA": "heavy rain",
    "-SN": "light snow", "SN": "snow", "+SN": "heavy snow",
    "BR": "mist", "FG": "fog", "HZ": "haze", "TS": "thunderstorms",
    "-TSRA": "light thunderstorms with rain", "TSRA": "thunderstorms with rain",
    "DZ": "drizzle", "-DZ": "light drizzle", "GR": "hail",
    "FZFG": "freezing fog", "BLSN": "blowing snow", "SG": "snow grains",
}
CLOUDS = {"SKC": "clear skies", "CLR": "clear skies", "NSC": "no significant clouds",
          "FEW": "a few clouds", "SCT": "scattered clouds", "BKN": "broken clouds",
          "OVC": "overcast skies", "VV": "vertical visibility"}


def celsius_to_fahrenheit(value: int) -> int:
    return round(value * 9 / 5 + 32)


def parse_signed_temperature(value: str) -> int:
    return -int(value[1:]) if value.startswith("M") else int(value)


def visibility_text(token: str) -> str | None:
    if token == "CAVOK":
        return "Visibility is 6 miles or more with no significant weather."
    if token == "9999":
        return "Visibility is 6 miles or more."
    # US METARs may use 10SM, 1 1/2SM, or M1/4SM.
    if token.endswith("SM"):
        value = token[:-2].replace("P", "more than ").replace("M", "less than ")
        return f"Visibility is {value} mile{'s' if value not in ('1', 'less than 1') else ''}."
    if re.fullmatch(r"\d{4}", token):
        metres = int(token)
        return f"Visibility is about {round(metres / 1609, 1)} miles."
    return None


def fetch_metar(airport: str) -> str:
    response = requests.get(API_URL, params={"ids": airport, "format": "json", "hours": 0}, timeout=10)
    response.raise_for_status()
    records: Any = response.json()
    if not records:
        raise ValueError("No current METAR was found for that airport.")
    report = records[0].get("rawOb") or records[0].get("raw_text")
    if not report:
        raise ValueError("The weather service returned a report with no raw METAR.")
    return report


def decode_metar(raw: str) -> dict[str, Any]:
    """Decode common operational METAR fields into reader-friendly pieces."""
    clean = raw.replace("=", "").strip()
    tokens = clean.split()
    if tokens and tokens[0] in {"METAR", "SPECI"}:
        tokens.pop(0)
    station = tokens[0] if tokens else "Unknown"
    facts: list[str] = []
    conditions: list[str] = []
    details: list[tuple[str, str]] = [("Station", station)]
    temperature: str | None = None
    dew_point: str | None = None
    pressure: str | None = None
    wind_summary: str | None = None
    cloud_summary: str | None = None

    for index, token in enumerate(tokens[1:], start=1):
        if re.fullmatch(r"\d{6}Z", token):
            details.append(("Observed", f"day {token[:2]} at {token[2:4]}:{token[4:6]} UTC"))
        elif match := re.fullmatch(r"(\d{3}|VRB)(\d{2,3})(?:G(\d{2,3}))?KT", token):
            direction, knots, gusts = match.groups()
            mph = round(int(knots) * 1.15078)
            direction_text = "variable directions" if direction == "VRB" else f"{direction}°"
            wind_summary = f"Wind {direction_text} at {mph} mph"
            if gusts:
                wind_summary += f", gusting to {round(int(gusts) * 1.15078)} mph"
            wind_summary += "."
            details.append(("Wind", wind_summary[:-1]))
        elif token == "00000KT":
            wind_summary = "Calm winds."
            details.append(("Wind", "Calm"))
        elif token == "CAVOK" or token == "9999" or token.endswith("SM") or re.fullmatch(r"\d{4}", token):
            # In reports such as "1 1/2SM", the preceding whole number belongs
            # to the fractional visibility group.
            combined = token
            if token.endswith("SM") and index > 1 and re.fullmatch(r"\d+", tokens[index - 1]):
                combined = f"{tokens[index - 1]} {token}"
            visibility = visibility_text(combined)
            if visibility:
                facts.append(visibility)
                details.append(("Visibility", visibility.replace("Visibility is ", "").rstrip(".")))
        elif token in WEATHER:
            conditions.append(WEATHER[token])
        elif match := re.fullmatch(r"(SKC|CLR|NSC|FEW|SCT|BKN|OVC|VV)(\d{3})?", token):
            kind, height = match.groups()
            description = CLOUDS[kind]
            if height:
                description += f" at {int(height) * 100:,} ft"
            cloud_summary = description + "."
            details.append(("Clouds", description.capitalize()))
        elif match := re.fullmatch(r"(M?\d{2})/(M?\d{2})", token):
            temp_c, dew_c = map(parse_signed_temperature, match.groups())
            temp_f, dew_f = celsius_to_fahrenheit(temp_c), celsius_to_fahrenheit(dew_c)
            temperature = f"{temp_f}°F ({temp_c}°C)"
            dew_point = f"{dew_f}°F ({dew_c}°C)"
            details.extend([("Temperature", temperature), ("Dew point", dew_point)])
        elif match := re.fullmatch(r"A(\d{4})", token):
            pressure = f"{int(match.group(1)) / 100:.2f} inHg"
            details.append(("Pressure", pressure))
        elif match := re.fullmatch(r"Q(\d{4})", token):
            pressure = f"{match.group(1)} hPa"
            details.append(("Pressure", pressure))

    headline_parts = []
    if conditions:
        headline_parts.append("Conditions include " + ", ".join(conditions) + ".")
    if cloud_summary:
        headline_parts.append(cloud_summary.capitalize())
    else:
        headline_parts.append("No cloud layer was reported.")
    if temperature:
        headline_parts.append(f"It is {temperature}.")
    if wind_summary:
        headline_parts.append(wind_summary)
    headline_parts.extend(facts)
    if pressure:
        headline_parts.append(f"Pressure is {pressure}.")

    return {"station": station, "summary": " ".join(headline_parts), "details": details, "raw": clean,
            "decoded_at": datetime.now(timezone.utc).strftime("%H:%M UTC")}


@app.route("/", methods=["GET", "POST"])
def index():
    airport = request.values.get("airport", "KJFK").strip().upper()
    result = error = None
    if request.method == "POST" or request.args.get("airport"):
        if not re.fullmatch(r"[A-Z]{4}", airport):
            error = "Enter a four-letter ICAO airport code, such as KJFK, EGLL, or YSSY."
        else:
            try:
                result = decode_metar(fetch_metar(airport))
            except requests.RequestException:
                error = "The weather service could not be reached. Please try again shortly."
            except ValueError as exc:
                error = str(exc)
    return render_template("index.html", airport=airport, result=result, error=error)


if __name__ == "__main__":
    app.run(debug=True)

