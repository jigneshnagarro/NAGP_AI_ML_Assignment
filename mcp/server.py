from mcp.server import MCPServer
import requests


mcp = MCPServer("Singapore Travel MCP Server")


# Singapore coordinates
SINGAPORE_LATITUDE = 1.3521
SINGAPORE_LONGITUDE = 103.8198

@mcp.tool()
def get_weather(
    city: str,
    start_date: str = "",
    end_date: str = ""
) -> dict:
    """
    Get current or forecast weather for Singapore.

    Dates must be in YYYY-MM-DD format.

    If no dates are supplied, current weather and the
    available forecast are returned.
    """

    if city.lower() != "singapore":
        return {
            "error": "Weather is currently supported only for Singapore."
        }

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": SINGAPORE_LATITUDE,
        "longitude": SINGAPORE_LONGITUDE,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code"
        ],
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "precipitation_sum"
        ],
        "timezone": "Asia/Singapore"
    }
    
    if start_date:
        params["start_date"] = start_date

    if end_date:
        params["end_date"] = end_date

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return {
            "city": city,
            "source": "Open-Meteo",
            "timezone": data.get("timezone"),
            "current": data.get("current"),
            "daily": data.get("daily")
        }

    except requests.RequestException as e:
        return {
            "error": f"Weather service unavailable: {str(e)}"
        }
        
@mcp.tool()
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> dict:
    """
    Convert an amount using the latest available exchange rate.
    """

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "exchange_rate": 1,
            "converted_amount": amount,
            "source": "Frankfurter"
        }

    url = (
        f"https://api.frankfurter.dev/v2/rate/"
        f"{from_currency}/{to_currency}"
    )

    try:
        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        rate = data["rate"]

        return {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "exchange_rate": rate,
            "converted_amount": round(amount * rate, 2),
            "date": data.get("date"),
            "source": "Frankfurter"
        }

    except requests.RequestException as e:
        return {
            "error": f"Currency service unavailable: {str(e)}"
        }

    except KeyError:
        return {
            "error": (
                f"Exchange rate not available for "
                f"{from_currency} → {to_currency}"
            )
        }


if __name__ == "__main__":
    mcp.run()