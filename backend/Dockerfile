FROM python:3.13-slim
WORKDIR /app

# Install build dependencies for compiling native extensions (e.g., mgrs)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optionally remove build dependencies to slim down the image
RUN apt-get purge -y --auto-remove build-essential gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
