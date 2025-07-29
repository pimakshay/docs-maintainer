FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install curl (required for uv installation)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better Docker layer caching
COPY uv.lock .
COPY pyproject.toml .
COPY main.py .

# Install uv and add to PATH
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure uv is available
ENV PATH="/root/.local/bin/:$PATH"

# Install Python dependencies
RUN uv sync --frozen

# Set HOME and working directory
ENV HOME=/app
WORKDIR $HOME

# Copy application code
COPY fastapi_backend ./fastapi_backend
COPY data ./data

# Set PYTHONPATH so Python can find the `fastapi_backend` package
ENV PYTHONPATH=/app

# Expose FastAPI port
EXPOSE 8000

# Start the FastAPI app using uvicorn via uv
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
