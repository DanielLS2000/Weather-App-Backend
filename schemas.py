from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import datetime

def validate_date_format(date_str: str) -> str:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

class WeatherBase(BaseModel):
    location: str
    start_date: str
    end_date: str

    @model_validator(mode='after')
    def check_date_range(self) -> 'WeatherBase':
        validate_date_format(self.start_date)
        validate_date_format(self.end_date)
        if self.start_date > self.end_date:
            raise ValueError("The start date (start_date) cannot be later than the end date (end_date).")
        return self

class WeatherCreate(WeatherBase):
    pass

class WeatherUpdate(BaseModel):
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    @model_validator(mode='after')
    def check_date_range_update(self) -> 'WeatherUpdate':
        if self.start_date: validate_date_format(self.start_date)
        if self.end_date: validate_date_format(self.end_date)
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("start_date cannot be greater than end_date.")
        return self

class WeatherResponse(WeatherBase):
    id: int
    temperature_max: Optional[float] = None
    temperature_min: Optional[float] = None
    daily_forecast: Optional[list[dict]] = None

    class Config:
        from_attributes = True

class WeatherDetailResponse(WeatherResponse):
    wikipedia_summary: Optional[str] = None
    google_maps_url: Optional[str] = None
    youtube_videos: Optional[list[dict]] = []

class ExtraInfoResponse(BaseModel):
    location: str
    wikipedia_summary: str
    google_maps_url: str
    youtube_videos: list[dict]