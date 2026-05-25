import httpx
from fastapi import HTTPException

def parse_coordinates(location_str: str):
    """
    Tries to parse latitude and longitude from a string in the format 'latitude, longitude' (ex: '-23.5505, -46.6333').
    """
    try:
        parts = [p.strip() for p in location_str.split(',')]
        if len(parts) == 2:
            lat = float(parts[0])
            lon = float(parts[1])
            return lat, lon
    except ValueError:
        pass # If not parsable, it means its a city name
    return None, None

async def validate_location(location_name: str):
    lat, lon = parse_coordinates(location_name)
    if lat is not None and lon is not None:
        return f"GPS: {lat}, {lon}", lat, lon

    # If not a coord string, treat it as a city name and call the geocoding API
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={location_name}&count=1&language=en&format=json"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        
    if response.status_code != 200:
        raise HTTPException(status_code=503, detail="Error occurred while communicating with the external geocoding service.")
        
    data = response.json()
    
    if not data.get("results"):
        raise HTTPException(status_code=400, detail=f"The location '{location_name}' was not found.")
        
    result = data["results"][0]
    official_name = result.get("name")
    country = result.get("country", "")
    
    full_name = f"{official_name}, {country}" if country else official_name
    
    return full_name, result.get("latitude"), result.get("longitude")

async def fetch_temperature_data(lat: float, lon: float, start_date: str, end_date: str):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error fetching weather data. Please ensure the date range is recent.")
        
    data = response.json()
    daily_data = data.get("daily", {})
    
    times = daily_data.get("time", [])
    temps_max = daily_data.get("temperature_2m_max", [])
    temps_min = daily_data.get("temperature_2m_min", [])
    
    if not times or not temps_max or not temps_min:
        return 0.0, 0.0, []
        
    forecast_list = [
        {"date": t, "temp_max": t_max, "temp_min": t_min} 
        for t, t_max, t_min in zip(times, temps_max, temps_min)
    ]
    
    avg_max = round(sum(temps_max) / len(temps_max), 2)
    avg_min = round(sum(temps_min) / len(temps_min), 2)
    
    return avg_max, avg_min, forecast_list