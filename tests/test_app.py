import pytest
from unittest.mock import Mock, patch

import app


def test_decode_metar_interprets_common_fields():
    raw = "METAR EGLL 201220Z 24012G22KT 9999 -RA SCT020 BKN035 18/15 Q1013="

    result = app.decode_metar(raw)

    assert result["station"] == "EGLL"
    assert "Wind 240° at 14 mph, gusting to 25 mph." in result["summary"]
    assert "light rain" in result["summary"]
    assert "scattered clouds at 2,000 ft." in result["summary"]
    assert "broken clouds at 3,500 ft." in result["summary"]
    assert "It is 64°F (18°C)." in result["summary"]
    assert "Visibility is 6 miles or more." in result["summary"]
    assert "Pressure is 1013 hPa." in result["summary"]


def test_decode_metar_interprets_negative_temperature_and_dew_point():
    raw = "METAR KJFK 201251Z 18008KT 10SM CLR M03/M06 A2992="

    result = app.decode_metar(raw)

    assert result["station"] == "KJFK"
    assert "It is 27°F (-3°C)." in result["summary"]
    assert any(label == "Dew point" and value == "21°F (-6°C)" for label, value in result["details"])
    assert "Pressure is 29.92 inHg." in result["summary"]


def test_decode_metar_interprets_cavok_and_calm_wind():
    raw = "METAR EGCC 201250Z 00000KT CAVOK 12/08 Q1020="

    result = app.decode_metar(raw)

    assert "Calm winds." in result["summary"]
    assert "Visibility is 6 miles or more with no significant weather." in result["summary"]
    assert "It is 54°F (12°C)." in result["summary"]
    assert "Pressure is 1020 hPa." in result["summary"]


def test_decode_metar_handles_us_fractional_visibility():
    raw = "METAR KDEN 201253Z 27015KT 1 1/2SM -SN OVC010 M05/M08 A3010="

    result = app.decode_metar(raw)

    assert "Visibility is 1 1/2 miles." in result["summary"]
    assert "light snow" in result["summary"]
    assert "overcast skies at 1,000 ft." in result["summary"]


def test_fetch_metar_uses_mocked_weather_service():
    mocked_response = Mock()
    mocked_response.json.return_value = [{"rawOb": "METAR EGLL 201220Z 24012KT 9999 SCT020 18/15 Q1013="}]
    mocked_response.raise_for_status.return_value = None

    with patch("app.requests.get", return_value=mocked_response) as mock_get:
        result = app.fetch_metar("EGLL")

    assert result.startswith("METAR EGLL")
    mock_get.assert_called_once_with(
        app.API_URL,
        params={"ids": "EGLL", "format": "json", "hours": 0},
        timeout=10,
    )


def test_index_rejects_invalid_icao_code():
    client = app.app.test_client()

    response = client.post("/", data={"airport": "LHR"})

    assert response.status_code == 200
    assert b"Enter a four-letter ICAO airport code" in response.data
