FROM python:3.13-slim-bookworm

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy only the dependency files first
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Install Node.js and open-websearch
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g open-websearch

# Copy the rest of the application code
COPY . .

CMD ["python", "src/bot.py"]
