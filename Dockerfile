FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml ./

COPY dag_service ./dag_service

RUN poetry config virtualenvs.create false && poetry install --without dev --no-interaction --no-ansi --no-root

CMD ["uvicorn", "dag_service.__main__:app", "--host", "0.0.0.0", "--port", "8080"]