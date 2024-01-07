FROM python:3.11

ENV TZ=Asia/Vladivostok

WORKDIR /app

RUN pip install poetry

COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false && poetry install

CMD python main.py