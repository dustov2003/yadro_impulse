FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml ./

COPY dag_service ./dag_service

# Закомментируйте, если нужно захостить сервис
COPY tests ./tests

# Раскомментируйте если нужно захостить сервис, так зависимости для разработчика не будут установлены
# RUN poetry config virtualenvs.create false && poetry install --without dev --no-interaction --no-ansi --no-root
RUN poetry config virtualenvs.create false && poetry install --with dev --no-interaction --no-ansi --no-root

CMD ["uvicorn", "dag_service.__main__:app", "--host", "0.0.0.0", "--port", "8080"]