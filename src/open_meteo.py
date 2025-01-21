from loguru import logger
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

def fetch_weather_data(latitude, longitude, timezone="Europe/Berlin", forecast_days=1):
    """
    Fetch hourly weather data from Open-Meteo API and return it as a Pandas DataFrame.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        timezone (str): Timezone for the weather data. Default is "Europe/Berlin".
        forecast_days (int): Number of days to forecast. Default is 1.

    Returns:
        pd.DataFrame: DataFrame containing hourly weather data.
    """
    
    
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Define API request parameters
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "rain", "showers", "snowfall", "uv_index"],
        "timezone": timezone,
        "forecast_days": forecast_days
    }

    # Fetch weather data
    responses = openmeteo.weather_api(url, params=params)

    # Process first location (extendable to handle multiple locations)
    response = responses[0]
    logger.info(f"Coordinates: {response.Latitude()}\u00b0N {response.Longitude()}\u00b0E")
    logger.info(f"Elevation: {response.Elevation()} m asl")
    logger.info(f"Timezone: {response.Timezone()} {response.TimezoneAbbreviation()}")
    logger.info(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()} s")

    # Process hourly data
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_rain = hourly.Variables(1).ValuesAsNumpy()
    hourly_showers = hourly.Variables(2).ValuesAsNumpy()
    hourly_snowfall = hourly.Variables(3).ValuesAsNumpy()
    hourly_uv_index = hourly.Variables(4).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "temperature_2m": hourly_temperature_2m,
        "rain": hourly_rain,
        "showers": hourly_showers,
        "snowfall": hourly_snowfall,
        "uv_index": hourly_uv_index
    }

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    logger.info("Hourly weather data fetched successfully.")
    return hourly_dataframe

    


