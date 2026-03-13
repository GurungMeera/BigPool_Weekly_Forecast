from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

API_KEY = "cdc38a132c5afd324c6eb6da1e75875b"
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"


def get_weekly_forecast(location: str):

    # Determine if location is zip code or city/state
    if location.isdigit():
        params = {
            "zip": f"{location},US",
            "appid": API_KEY,
            "units": "imperial"
        }
    else:
        params = {
            "q": f"{location},US",
            "appid": API_KEY,
            "units": "imperial"
        }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        return None

    data = response.json()
    forecast_list = data["list"]

    weekly = []

    # OpenWeather returns data every 3 hours
    # 8 entries ≈ 1 day
    for i in range(0, len(forecast_list), 8):

        day = forecast_list[i]

        weekly.append({
            "date": day["dt_txt"],
            "temperature": day["main"]["temp"],
            "weather": day["weather"][0]["description"]
        })

        if len(weekly) == 7:
            break

    return weekly


@app.get("/weekly-forecast")
def weekly_forecast(location: str):
    forecast = get_weekly_forecast(location)

    if not forecast:
        raise HTTPException(
            status_code=400,
            detail="Invalid location or forecast data unavailable"
        )

    return {
        "location": location,
        "forecast": forecast
    }


@app.get("/weekly-summary")
def weekly_summary(location: str):

    forecast = get_weekly_forecast(location)

    if not forecast:
        raise HTTPException(
            status_code=400,
            detail="Unable to generate weekly summary due to missing forecast data"
        )

    summary = []

    for day in forecast:
        summary.append(
            f"{day['date']}: {day['weather']} with temperature {day['temperature']}°F"
        )

    return {
        "location": location,
        "weekly_summary": summary
    }
