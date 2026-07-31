FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .

RUN uv sync --no-dev

COPY main.py agent.py schema.py ./

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
