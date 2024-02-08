FROM python:3.11

WORKDIR /app

RUN pip install poetry

COPY poetry.lock pyproject.toml /app/

COPY . /app

WORKDIR /app/api

RUN poetry config virtualenvs.create false && poetry install

CMD uvicorn main:app --reload --host 0.0.0.0 --port 4000