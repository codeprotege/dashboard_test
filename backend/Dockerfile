# Stage 1: Build stage (optional, but good for managing dependencies if build steps were complex)
# For now, a single stage is fine for this Python app.

# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app/backend

# Install system dependencies if any (e.g., for psycopg2 if not using -binary, or other C extensions)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     libpq-dev \
#  && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker cache
# Assuming requirements.txt is in the project root, adjust path if it's specific to backend
COPY ../requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy the backend application code into the container
COPY . /app/backend/
# If .env file needs to be part of the image (NOT RECOMMENDED for production secrets)
# COPY .env /app/backend/.env
# It's better to inject environment variables at runtime via Docker Compose or Kubernetes.

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# The command should be `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
# When WORKDIR is /app/backend, main:app refers to /app/backend/main.py
# If running from /app, it would be backend.main:app
# The --app-dir argument for uvicorn can also manage this.
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# If your main.py is in /app/backend and you run uvicorn from /app:
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app"]
# This assumes the project root (containing backend/, frontend/, requirements.txt) is the Docker build context.
# The COPY ../requirements.txt /app/requirements.txt implies context is project root.
# The COPY . /app/backend/ copies the backend directory contents into /app/backend.
# So, if uvicorn is run with /app as its search path (--app-dir /app), it can find backend.main.
# This structure is common.
