from fastapi import FastAPI
from database import engine, Base
from routers import weather, export

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Weather API - PM Accelerator",
    description="Backend API for Weather Application",
    version="1.0.0"
)

app.include_router(weather.router)
app.include_router(export.router)

@app.get("/")
def read_root():
    return {
        "developer": "Daniel Lima de Sousa",
        "app_name": "Weather App API",
        "about_pm_accelerator": "PM Accelerator is a US based company with a global reach premiering in AI learning and as a development hub, featuring award-winning AI products and mentors from top-tier companies such as Google, Meta, Apple, and Nvidia."
    }