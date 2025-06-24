## Agent Instructions for Financial Dashboard

This file provides guidance for AI agents working on this project.

### General Guidelines
1.  **Follow the plan:** Adhere to the established project plan and phases.
2.  **Modular Code:** Write modular and reusable code.
3.  **Testing:** Implement unit and integration tests for all new features.
4.  **Documentation:** Keep documentation (code comments, API docs, user guides) up-to-date.
5.  **Commit Messages:** Write clear and descriptive commit messages (e.g., Conventional Commits).
6.  **Dependencies:** Add new dependencies to `requirements.txt` using `pip freeze > requirements.txt` after installation in the active virtual environment.

### Backend (FastAPI)
-   Organize code into routers (e.g., in a `backend/routers` directory).
-   Use Pydantic models for request/response validation (`backend/schemas.py`).
-   Implement proper error handling and logging.
-   Follow RESTful API design principles.
-   Database models go into `backend/models.py`.
-   Database connection and session management in `backend/database.py`.
-   Configuration using `.env` and Pydantic settings in `backend/config.py`.

### Frontend (Streamlit)
-   Keep the UI clean and intuitive (`frontend/app.py` and `frontend/pages/`).
-   Ensure responsiveness across different screen sizes.
-   Optimize for performance, especially with large datasets.
-   Store session state variables using `st.session_state`.

### Data
-   Handle data securely, especially API keys and user data. Store API keys in `.env`.
-   Implement efficient data caching strategies (e.g., Streamlit's caching, database caching).

### Forecasting
-   Clearly document the forecasting models used and their assumptions.
-   Provide metrics for forecast accuracy if possible.

### Specific Tasks
-   **API Integration:** When integrating with external financial APIs, store API keys securely using environment variables loaded via `backend/config.py` from the `.env` file. Do not commit API keys to the repository. The `.env` file is in `.gitignore`.
-   **Database:** Use SQLAlchemy for database interactions. Define models in `backend/models.py` and Pydantic schemas in `backend/schemas.py`. Initialize database tables from `backend/main.py` (on startup for dev) or using Alembic for migrations in production.
-   **Authentication:** Implement JWT-based authentication. Store `SECRET_KEY` in `.env`.
-   **WebSockets:** Ensure WebSocket connections are handled robustly and efficiently for real-time updates.
