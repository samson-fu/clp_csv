# syntax = docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/
# https://medium.com/vantageai/how-to-make-your-python-docker-images-secure-fast-small-b3a6870373a0

ARG PYTHON_VERSION=3.12
# FROM python:${PYTHON_VERSION}-slim as base
# Use slim when there is pandas or numpy in the project!
# 1. FROM python:3.11.5-alpine3.18
# 2. FROM python:3.12-alpine
FROM python:${PYTHON_VERSION}-slim AS base

ENV PIP_DEFAULT_TIMEOUT=100 \
    # Allow statements and log messages to immediately appear
    PYTHONUNBUFFERED=1 \
    # disable a pip version check to reduce run-time & log-spam
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # cache is useless in docker image, so disable to reduce image size
    PIP_NO_CACHE_DIR=1 \
    # Prevents Python from writing pyc files.
    PYTHONDONTWRITEBYTECODE=1 \
    # Keeps Python from buffering stdout and stderr to avoid situations where
    # the application crashes without emitting any logs due to buffering.
    PYTHONUNBUFFERED=1 \
    # Set the time zone environment variable to Asia/Hong_Kong.
    TZ=Asia/Hong_Kong

# Update the package list and install the latest version of the tzdata package.
# Install the tzdata package without cache, copy the Hong Kong time zone info to localtime,
# and set the time zone to Asia/Hong_Kong.
# RUN apk update && \
#     apk add --no-cache tzdata && \
#     cp /usr/share/zoneinfo/Asia/Hong_Kong /etc/localtime && \
#     echo "Asia/Hong_Kong" > /etc/timezone

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

RUN apt-get update \
    && apt-get upgrade -y
# RUN apk update
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port that the application listens on.
# EXPOSE 8000

# Run the application.
# RUN apt-get install -y crontab
# RUN crontab crontab

# Start the cron daemon in the foreground.
CMD ["crond", "-f"]

# Now it is time to build the docker image as below cmd:
# $ docker image rm hkclp-powermeter:latest
# $ docker build -t hkclp-powermeter:latest .
# Save the docker image to tar file:
# $ del hkclp-powermeter.tar
# $ docker image save -o hkclp-powermeter.tar hkclp-powermeter
