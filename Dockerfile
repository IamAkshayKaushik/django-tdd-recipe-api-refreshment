# FROM python:3.11-slim-buster
FROM python:3.11-alpine3.19

LABEL maintainer="github.com/IamAkshayKaushik"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt

COPY ./app /app
WORKDIR /app
EXPOSE 8000


RUN python -m venv .venv && \
    /bin/sh -c "source .venv/bin/activate" && \
    pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    adduser --disabled-password --no-create-home  django-user

ENV PATH /.venv/bin:$PATH

USER django-user