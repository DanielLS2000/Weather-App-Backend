import re
import httpx
from fastapi import HTTPException

async def validate_location(location: str):
    clean_location = location.replace("GPS:", "").strip()
    
    coord_pattern = r"^([-+]?\d{1,2}(?:\.\d+)?)\s*,\s*([-+]?\d{1,3}(?:\.\d+)?)$"
    match = re.match(coord_pattern, clean_location)
    
    # 1. For GPS coordinates, we attempt to parse them directly
    if match:
        lat = float(match.group(1))
        lon = float(match.group(2))
        
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 10,
            "accept-language": "en"
        }
        headers = {
            "User-Agent": "WeatherApp_Assessment/1.0 (https://www.cruzeirotech.com; daniellimas2000@gmail.com)"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    address = data.get("address", {})
                    
                    city = address.get("city") or address.get("town") or address.get("village") or address.get("county")
                    country = address.get("country", "")
                    
                    if city:
                        return f"{city}, {country}" if country else city, lat, lon
            except Exception:
                pass 
        
        return f"{lat}, {lon}", lat, lon

    # 2. For city names, we use the geocoding API to get the official name and coordinates
    search_query = clean_location.split(',')[0].strip()
    
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": search_query,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        
    if response.status_code != 200:
        print(f"ERRO OPEN-METEO (GEO): Status {response.status_code} - Body: {response.text}")
        raise HTTPException(status_code=400, detail=f"API Error ({response.status_code}). Check server logs.")
        
    data = response.json()
    if not data.get("results"):
        raise HTTPException(status_code=404, detail=f"The location '{clean_location}' was not found.")
        
    result = data["results"][0]
    name = result.get("name")
    country = result.get("country", "")
    
    official_name = f"{name}, {country}" if country else name
    
    return official_name, result["latitude"], result["longitude"]

async def fetch_temperature_data(lat: float, lon: float, start_date: str, end_date: str):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,temperature_2m_min,weather_code,uv_index_max&current=relative_humidity_2m&timezone=auto"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error fetching weather data.")
        
    data = response.json()
    
    current_data = data.get("current", {})
    current_humidity = current_data.get("relative_humidity_2m", 0.0)
    
    daily_data = data.get("daily", {})
    times = daily_data.get("time", [])
    temps_max = daily_data.get("temperature_2m_max", [])
    temps_min = daily_data.get("temperature_2m_min", [])
    codes = daily_data.get("weather_code", [])
    uv_indices = daily_data.get("uv_index_max", [])
    
    if not times or not temps_max or not temps_min or not codes:
        return 0.0, 0.0, 0, 0.0, 0.0, []
        
    forecast_list = [
        {"date": t, "temp_max": t_max, "temp_min": t_min, "weather_code": code} 
        for t, t_max, t_min, code in zip(times, temps_max, temps_min, codes)
    ]
    
    avg_max = round(sum(temps_max) / len(temps_max), 2)
    avg_min = round(sum(temps_min) / len(temps_min), 2)
    
    primary_code = codes[0] if codes else 0
    primary_uv = uv_indices[0] if uv_indices and uv_indices[0] is not None else 0.0
    
    return avg_max, avg_min, primary_code, primary_uv, current_humidity, forecast_list