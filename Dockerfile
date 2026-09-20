FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt

COPY src ./src
COPY app ./app
COPY data/raw ./data/raw

RUN python src/parse_midi.py && python src/prepare_data.py && python src/build_index.py && rm -rf data/processed data/prepared

EXPOSE 8501

CMD [
    "streamlit",
    "run",
    "app/app.py",
    "--server.address=0.0.0.0",
    "--server.port=8501",
    "--server.headless=true"
]