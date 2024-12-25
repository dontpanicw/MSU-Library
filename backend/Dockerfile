FROM python:3.12-slim AS base

ENV TZ="Europe/Moscow"

RUN pip install --upgrade pip

FROM base AS base_with_req

WORKDIR /app

COPY backend/requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r /app/requirements.txt

RUN apt-get purge -y --auto-remove build-essential libpq-dev

FROM base_with_req AS app

RUN cd / && mkdir .conf

COPY .conf/.env /.conf
COPY backend/ .

CMD ["python", "-m", "app.main"]