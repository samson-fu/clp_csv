# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.12
# FROM python:${PYTHON_VERSION}-slim as base
# 1. FROM python:3.11.5-alpine3.18
# 2. FROM python:3.12-alpine
FROM python:${PYTHON_VERSION}-alpine AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

RUN apk update && \
    apk add -U tzdata

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
# ARG UID=10001
# RUN adduser \
#     --disabled-password \
#     --gecos "" \
#     --home "/nonexistent" \
#     --shell "/sbin/nologin" \
#     --no-create-home \
#     --uid "${UID}" \
#     appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
# RUN --mount=type=cache,target=/root/.cache/pip \
#     --mount=type=bind,source=requirements.txt,target=requirements.txt \
#     python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
# USER appuser
RUN mkdir history

# Copy the source code into the container.
COPY . .
COPY ./crontab /var/spool/cron/crontabs/root

# RUN apk update
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

# Expose the port that the application listens on.
# EXPOSE 8000

# Run the application.
# RUN apt-get install -y crontab
RUN crontab crontab

CMD ["crond", "-f"]

# Now it is time to build the docker image as below cmd:
# $ docker image rm hkclp-powermeter:latest
# $ docker build -t hkclp-powermeter:latest .
# Save the docker image to tar file:
# $ del hkclp-powermeter.tar
# $ docker image save -o hkclp-powermeter.tar hkclp-powermeter
