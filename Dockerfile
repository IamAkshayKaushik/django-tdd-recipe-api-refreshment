# FROM python:3.11-slim-bullseye
FROM python:3.11-alpine3.19

LABEL maintainer="github.com/IamAkshayKaushik"

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt

COPY ./app /app
WORKDIR /app
EXPOSE 8000

## Alpine
RUN python -m venv /.venv && \
    /bin/sh -c "source /.venv/bin/activate" && \
    /.venv/bin/pip install --upgrade pip setuptools && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev zlib zlib-dev && \
    /.venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser --disabled-password --no-create-home django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

## slim-buster
# RUN python -m venv /.venv && \
#     /bin/bash -c "source /.venv/bin/activate" && \
#     /.venv/bin/pip install --upgrade --no-cache-dir pip setuptools && \
#     apt-get update && \
#     apt-get install -y --no-install-recommends build-essential postgresql-client libpq-dev && \
#     /.venv/bin/pip install --no-cache-dir psycopg2 && \
#     /.venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt && \
#     rm -rf /var/lib/apt/lists/* && \
#     adduser --disabled-password \
#     #  --no-create-home \
#     django-user
#     mkdir -p /vol/web/media && \
#     mkdir -p /vol/web/static && \
#     chown -R django-user:django-user /vol && \
#     chmod -R 755 /vol

ENV PATH="/.venv/bin:$PATH"

USER django-user