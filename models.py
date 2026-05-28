from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from database import Base
from datetime import datetime

class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True, nullable=False)
    start_date = Column(String, nullable=False) 
    end_date = Column(String, nullable=False)
    temperature_max = Column(Float, nullable=True)
    temperature_min = Column(Float, nullable=True)
    weather_code = Column(Integer, nullable=True)
    uv_index = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    daily_forecast = Column(JSON, nullable=True) 
    created_at = Column(DateTime, default=datetime.utcnow)