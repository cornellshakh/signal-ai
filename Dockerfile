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

# Create the data directory and the database file
RUN mkdir -p /app/data && touch /app/data/signal_ai.db

CMD ["python", "-m", "src.signal_ai.bot"]
