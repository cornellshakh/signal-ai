FROM python:3.13-slim-bookworm

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Set the Poetry cache directory
ENV POETRY_CACHE_DIR=/app/.cache

# Copy only the dependency files first
COPY pyproject.toml poetry.lock* ./
COPY ./vendor /app/vendor

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --no-root


# Copy the rest of the application code
COPY ./src /app/src

# Add src to PYTHONPATH
ENV PYTHONPATH "${PYTHONPATH}:/app/src"

CMD ["poetry", "run", "python", "-m", "src.signal_ai.app.main"]
