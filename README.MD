# Weather App (Backend)
**PM Accelerator - Tech Assessment**

A robust, asynchronous RESTful API built with **Python** and **FastAPI**. This backend serves as the core engine for the Weather App, handling data validation, external API integrations (Open-Meteo and OpenStreetMap), and persistent data storage using **SQLite**.

---

## ⚠️ Important Architecture Note (Rate Limiting)

This API fetches real-time meteorological data from the free tier of the **Open-Meteo API**. 
Because free cloud hosting platforms (like Render.com) share outgoing IP addresses among thousands of applications, the Open-Meteo daily limit (10,000 requests per IP) can occasionally be exhausted by other users on the same server node.

To ensure resilience, this backend is explicitly engineered to handle this edge case. If the third-party limit is reached, the API safely catches the failure and returns a structured `429 Too Many Requests` HTTP error to the frontend, preventing system crashes and demonstrating proper API error handling.

**To evaluate the full functionality without shared-IP restrictions, running this backend locally is highly recommended.**

---

## ✨ Features

- **Forward & Reverse Geocoding:** Converts city names to coordinates and vice-versa using the Nominatim (OpenStreetMap) API.
- **Weather Data Aggregation:** Fetches and processes N-day forecasts (X start date to Y end date), UV indices, and current humidity asynchronously.
- **Full CRUD Operations:** Endpoints to Create, Read, Update, and Delete weather search records.
- **Dynamic Updates:** Updating a record's location or date automatically triggers a recalculation of the weather data.
- **Export Engine:** Generates downloadable files of the database history in multiple formats (JSON, CSV, XML, PDF, Markdown).

---

## 🛠️ Tech Stack

- **Language:** Python 3.9+
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Server:** Uvicorn
- **Database:** SQLite & SQLAlchemy (ORM)
- **HTTP Client:** HTTPX (for asynchronous third-party requests)

---

## 🚀 Local Deploy

Follow these steps to run the backend API on your local machine.

### Prerequisites
Make sure you have **Python (3.9 or higher)** and **Git** installed.

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DanielLS2000/Weather-App-Backend
   cd Weather-App-Backend

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv

3. **Activate the Virtual Environment (Windows):**
   ```bash
   venv\Scripts\activate
(Note: If you are using Git Bash on Windows, use source venv/Scripts/activate)

4. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt

5. **Run the API server:**
   ```bash
   uvicorn main:app --reload

The server will start running at http://127.0.0.1:8000.

## 📖 API Documentation (Swagger UI)
FastAPI automatically generates interactive API documentation.
Once the server is running, you can explore all endpoints, test requests, and view the data schemas by navigating to:

Interactive Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

You can also access the docs via the render deployment: [https://weather-app-backend-8n5a.onrender.com/docs](https://weather-app-backend-8n5a.onrender.com/docs)
