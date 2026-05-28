from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from services.weather_api import validate_location, fetch_temperature_data
from services.extra_apis import get_youtube_videos, get_google_maps_data, get_wikipedia_summary

router = APIRouter(
    prefix="/weather",
    tags=["Weather CRUD"]
)

@router.post("/", response_model=schemas.WeatherResponse)
async def create_weather_record(record: schemas.WeatherCreate, db: Session = Depends(get_db)):
    official_location, lat, lon = await validate_location(record.location)
    
    avg_max, avg_min, primary_code, primary_uv, current_humidity, forecast_list = await fetch_temperature_data(lat, lon, record.start_date, record.end_date)
    
    db_record = models.WeatherRecord(
        location=official_location, 
        start_date=record.start_date,
        end_date=record.end_date,
        temperature_max=avg_max,
        temperature_min=avg_min,
        weather_code=primary_code,
        uv_index=primary_uv,
        humidity=current_humidity,
        daily_forecast=forecast_list
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.get("/", response_model=list[schemas.WeatherResponse])
def read_all_weather_records(db: Session = Depends(get_db)):
    records = db.query(models.WeatherRecord).all()
    return records

@router.put("/{record_id}", response_model=schemas.WeatherResponse)
async def update_weather_record(record_id: int, update_data: schemas.WeatherUpdate, db: Session = Depends(get_db)):
    db_record = db.query(models.WeatherRecord).filter(models.WeatherRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    
    loc_to_search = update_dict.get("location", db_record.location)
    new_start = update_dict.get("start_date", db_record.start_date)
    new_end = update_dict.get("end_date", db_record.end_date)
    
    if new_start > new_end:
        raise HTTPException(status_code=400, detail="Incoerência de datas.")

    official_location, lat, lon = await validate_location(loc_to_search)
    update_dict["location"] = official_location
    
    avg_max, avg_min, primary_code, primary_uv, current_humidity, forecast_list = await fetch_temperature_data(lat, lon, new_start, new_end)
    update_dict["temperature_max"] = avg_max
    update_dict["temperature_min"] = avg_min
    update_dict["weather_code"] = primary_code
    update_dict["uv_index"] = primary_uv
    update_dict["humidity"] = current_humidity
    update_dict["daily_forecast"] = forecast_list

    for key, value in update_dict.items():
        setattr(db_record, key, value)
        
    db.commit()
    db.refresh(db_record)
    return db_record

@router.delete("/{record_id}")
def delete_weather_record(record_id: int, db: Session = Depends(get_db)):
    db_record = db.query(models.WeatherRecord).filter(models.WeatherRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db.delete(db_record)
    db.commit()
    return {"message": "Record deleted successfully"}

@router.get("/{record_id}", response_model=schemas.WeatherDetailResponse)
async def read_single_weather_record(record_id: int, db: Session = Depends(get_db)):
    db_record = db.query(models.WeatherRecord).filter(models.WeatherRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    
    from services.weather_api import validate_location
    _, lat, lon = await validate_location(db_record.location)
    
    from services.extra_apis import get_youtube_videos, get_google_maps_data, get_wikipedia_summary
    maps_data = get_google_maps_data(lat, lon, db_record.location)
    wiki_summary = await get_wikipedia_summary(db_record.location)
    yt_videos = await get_youtube_videos(db_record.location)
    
    response_data = {
        "id": db_record.id,
        "location": db_record.location,
        "start_date": db_record.start_date,
        "end_date": db_record.end_date,
        "temperature_max": db_record.temperature_max,
        "temperature_min": db_record.temperature_min,
        "weather_code": db_record.weather_code,
        "uv_index": db_record.uv_index,
        "humidity": db_record.humidity,
        "daily_forecast": db_record.daily_forecast,
        "wikipedia_summary": wiki_summary,
        "google_maps_url": maps_data["google_maps_url"],
        "youtube_videos": yt_videos
    }
    
    return response_data