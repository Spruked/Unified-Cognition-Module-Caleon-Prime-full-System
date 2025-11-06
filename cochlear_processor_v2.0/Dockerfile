FROM python:3.11-slim

# Canonical project name: cochlear_processor_v2.0
WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y libsndfile1 && \
    pip install --no-cache-dir -r config/requirements.txt && \
    rm -rf /var/lib/apt/lists/*

CMD ["python", "cochlear_processor.py"]
