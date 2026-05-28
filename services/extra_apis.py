import os
import httpx
from urllib.parse import quote

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

async def get_youtube_videos(location_name: str, max_results: int = 3):
    if not YOUTUBE_API_KEY:
        return [{"error": "YOUTUBE_API_KEY not configured on the server."}]

    query = quote(f"Travel {location_name}")
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults={max_results}&order=date&key={YOUTUBE_API_KEY}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        
    if response.status_code != 200:
        return []
        
    data = response.json()
    videos = []
    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        videos.append({
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "embed_url": f"https://www.youtube.com/embed/{video_id}"
        })
    return videos

def get_google_maps_data(lat: float, lon: float, location_name: str):
    embed_url = f"https://maps.google.com/maps?q={lat},{lon}&hl=en&z=14&output=embed"
    
    return {
        "google_maps_url": embed_url
    }

async def get_wikipedia_summary(location_name: str):
    city = location_name.split(",")[0].strip()
    
    formatted_city = quote(city.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_city}"
    
    headers = {
        "User-Agent": "WeatherApp_Assessment/1.0 (https://www.cruzeirotech.com; daniellimas2000@gmail.com)"
    }
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        
    if response.status_code == 200:
        data = response.json()
        
        if data.get("type") == "disambiguation":
            return f"The search for '{city}' returned multiple results on Wikipedia. Please be more specific."
            
        return data.get("extract", "Summary not available for this location.")
        
    return f"Summary not available. (Wikipedia error code: {response.status_code})"