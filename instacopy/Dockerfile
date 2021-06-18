# syntax=docker/dockerfile:1

# Pull official base image
FROM python:3.8-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_VERSION=1.1.6

# Set work directory
WORKDIR /usr/src/app

# Install netcat
RUN apt-get update \
  && apt-get install -y netcat

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Copy poetry files to cache them in docker layer
COPY poetry.lock pyproject.toml ./

# Install dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy entrypoint.sh
COPY entrypoint.sh .

# Copy other files for a project:
COPY . .

# Run entrypoint.sh
RUN ls
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]



