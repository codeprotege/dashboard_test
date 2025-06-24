# Stage 1: Build stage (optional)

# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app/frontend

# Install system dependencies if any
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first (assuming it's in the project root)
COPY ../requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy the frontend application code into the container
COPY . /app/frontend/

# Expose the port Streamlit runs on (default is 8501)
EXPOSE 8501

# Command to run the Streamlit application
# The command `streamlit run frontend/app.py` assumes being in the project root.
# If WORKDIR is /app/frontend, then app.py is directly accessible.
# Streamlit also needs a server address to bind to for Docker.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
# --server.headless=true is important for running in environments without a browser to auto-open.
# It also helps Streamlit understand it's in a non-interactive (server) mode.
# The Docker build context should be the project root.
# COPY ../requirements.txt implies this.
# COPY . /app/frontend/ copies the frontend directory contents into /app/frontend.
