FROM python:3.10-slim

WORKDIR /app

# Environment setup
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY src/requirement.txt /app/requirements-backend.txt
COPY src/front-end/requirements.txt /app/requirements-frontend.txt

# Install dependencies with pinned versions
RUN pip install --no-cache-dir -r requirements-backend.txt && \
    pip install --no-cache-dir -r requirements-frontend.txt

# Copy application code
COPY . /app/

# Create required directories
RUN mkdir -p /app/uploads /app/qdrant_db

# Starting script
RUN echo '#!/bin/bash\n\
cd /app/src && python main.py &\n\
cd /app/src/front-end && python main.py\n' > /app/start.sh && \
chmod +x /app/start.sh

# Expose ports for front and backend
EXPOSE 8000 5001

# Start both servers
CMD ["/app/start.sh"]