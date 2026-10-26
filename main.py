
import os
#it is bharath filedd .

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

# Load settings from the .env file
load_dotenv()

app = FastAPI(
    title="Weather API",
    description="Fetch weather data and calculate average temperature",
    version="1.0.0",
)

API_URL = os.getenv(
    "OPEN_METEO_API_URL",
    "https://api.open-meteo.com/v1/forecast"
)

API_URL = "https://api.open-meteo.com/v1/forecast"

DEFAULT_LATITUDE = float(os.getenv("LATITUDE", "13.0827"))
DEFAULT_LONGITUDE = float(os.getenv("LONGITUDE", "80.2707"))


@app.get("/")
def home():
    return {
        "message": "Welcome to the Weather API",
        "docs": "/docs",
    }


@app.get("/weather")
def get_weather(
    latitude: float = DEFAULT_LATITUDE,
    longitude: float = DEFAULT_LONGITUDE,
):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
        "forecast_days": 1,
        "timezone": "auto",
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        temperatures = data.get("hourly", {}).get(
            "temperature_2m", []
        )

        # Remove missing temperature values
        valid_temperatures = [
            temp for temp in temperatures if temp is not None
        ]

        if not valid_temperatures:
            raise HTTPException(
                status_code=502,
                detail="No temperature data available",
            )

        average_temperature = round(
            sum(valid_temperatures) / len(valid_temperatures),
            2,
        )

        return {
            "location": {
                "latitude": data["latitude"],
                "longitude": data["longitude"],
            },
            "temperature_unit": data["hourly_units"][
                "temperature_2m"
            ],
            "number_of_readings": len(valid_temperatures),
            "average_temperature": average_temperature,
            "minimum_temperature": min(valid_temperatures),
            "maximum_temperature": max(valid_temperatures),
            "summary": (
                f"The average temperature for the forecast "
                f"day is {average_temperature}°"
                f"{data['hourly_units']['temperature_2m']}."
            ),
        }

    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch weather data. Try again later.",
        )
