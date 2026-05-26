from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import weather, export

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Weather API - PM Accelerator",
    description="Backend API for Weather Application",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather.router)
app.include_router(export.router)

@app.get("/")
def read_root():
    return {
        "developer": "Daniel Lima de Sousa",
        "app_name": "Weather App API",
        "about_pm_accelerator": "The Product Manager Accelerator Program is designed to support PM professionals through every stage of their careers. From students looking for entry-level jobs to Directors looking to take on a leadership role, our program has helped over hundreds of students fulfill their career aspirations."
    }