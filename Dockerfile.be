FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for sentence-transformers, SQLAlchemy, and others)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./SCIML/requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire backend app
COPY ./SCIML /app

# Expose port
EXPOSE 8000

# Run the FastAPI server with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
