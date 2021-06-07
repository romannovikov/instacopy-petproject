# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.1.6

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml ./

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy other files for a project:
COPY instacopy .
