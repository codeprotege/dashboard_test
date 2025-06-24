# Financial Dashboard Application

This application provides an interactive dashboard for financial data analysis, including stock market tracking, currency exchange rate monitoring, and forecasting.

## Project Structure
- `backend/`: Contains the FastAPI application.
  - `main.py`: Main FastAPI application instance, router inclusions, DB table creation.
  - `config.py`: Pydantic settings for configuration management (loads from `.env`).
  - `database.py`: SQLAlchemy setup and database session management.
  - `models.py`: SQLAlchemy ORM models (e.g., User).
  - `schemas.py`: Pydantic schemas for data validation and serialization.
  - `crud.py`: CRUD (Create, Read, Update, Delete) operations for database interaction.
  - `auth.py`: Authentication logic (JWT generation/validation, password hashing, user dependency).
  - `routers/`: Directory for API route modules (e.g., `auth_router.py`, `users_router.py`).
- `frontend/`: Contains the Streamlit application.
  - `app.py`: Main Streamlit application script (homepage).
  - `pages/`: Directory for additional Streamlit pages (multi-page app).
  - `utils.py`: Utility functions for the frontend.
- `data/`: For local data files, SQLite database, etc. (ensure this dir exists if using local SQLite).
- `tests/`: For test scripts (e.g., PyTest).
- `docs/`: For project documentation.
- `.env`: Environment variables (API keys, database URL, secrets - **NOT COMMITTED TO GIT**).
- `requirements.txt`: Python dependencies.
- `AGENTS.md`: Instructions for AI development agents.
- `README.md`: This file.

## Features (Planned)
-   Real-time and historical data visualization.
-   Stock price candlestick charts, line charts for trends, heatmaps, bar charts, gauge charts.
-   Forecasting for 2025 period.
-   User authentication and customizable dashboard layouts.
-   Data export and alert system for price movements.
-   File upload, external API integration, and manual data entry.

## Technologies
-   **Backend:** FastAPI
-   **Frontend:** Streamlit
-   **Visualization:** Plotly
-   **Database:** SQLite (for development), PostgreSQL (recommended for production)
-   **Deployment:** Docker (planned)

## Local Development Setup
1.  **Prerequisites:** Python 3.8+
2.  **Clone Repository:** `git clone <repository_url>`
3.  **Navigate to Project:** `cd financial-dashboard` (or your chosen directory name)
4.  **Create Virtual Environment:**
    `python -m venv venv`
5.  **Activate Virtual Environment:**
    -   macOS/Linux: `source venv/bin/activate`
    -   Windows: `venv\Scripts\activate`
6.  **Install Dependencies:**
    `pip install -r requirements.txt`
7.  **Create `.env` File:**
    Copy `.env.example` (if provided, otherwise create manually) to `.env` in the project root.
    Update `.env` with your actual API keys and settings:
    ```env
    # Example .env content:
    ALPHA_VANTAGE_API_KEY="YOUR_ALPHA_VANTAGE_KEY"
    DATABASE_URL="sqlite:///./data/financial_dashboard.db" # Ensure 'data' dir exists
    SECRET_KEY="your_very_strong_and_secret_key_for_jwt_here"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```
8.  **Ensure `data` directory exists** if using SQLite as per default `DATABASE_URL`:
    `mkdir data` (if it doesn't exist and wasn't created by script)

## Running the Application
-   **Backend (FastAPI):**
    Open a terminal, activate venv, and run from project root:
    `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`
    (FastAPI will be at http://localhost:8000)
-   **Frontend (Streamlit):**
    Open another terminal, activate venv, and run from project root:
    `streamlit run frontend/app.py`
    (Streamlit will usually open in your browser at http://localhost:8501)

Access the API documentation at http://localhost:8000/docs.
