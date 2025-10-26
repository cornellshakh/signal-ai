FROM python:3.13-slim-buster

RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && poetry install --no-dev --user

COPY . .

USER appuser

CMD ["poetry", "run", "python", "src/bot.py"]