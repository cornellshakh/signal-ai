FROM python:3.13-slim-bookworm

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy only the dependency files first
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root


# Copy the rest of the application code
COPY ./src /app/src

CMD ["python", "-m", "src.signal_ai.bot"]
