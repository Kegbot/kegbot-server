FROM python:3-alpine

RUN mkdir /app
WORKDIR /app

ENV SHELL=/bin/sh \
   PIP_NO_CACHE_DIR=1 \
   KEGBOT_DATA_DIR=/kegbot-data \
   KEGBOT_IN_DOCKER=True \
   KEGBOT_ENV=debug

RUN apk update && \
    apk add --no-cache \
      bash \
      curl \
      libjpeg \
      libjpeg-turbo \
      openjpeg \
      mariadb-connector-c-dev \
      libpq && \
   apk add --no-cache --virtual _build-deps \
     build-base \
     mariadb-dev \
     postgresql-dev \
     libjpeg-turbo-dev \
     zlib-dev \
     py-gevent \
     libffi-dev \
     musl-dev \
     python3-dev \
     openssl-dev \
     cargo

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
ADD pykeg/__init__.py ./pykeg/
RUN poetry config virtualenvs.create false && poetry install -n

ADD bin ./bin
ADD pykeg ./pykeg
RUN poetry run python bin/kegbot collectstatic --noinput -v 0

ARG GIT_SHORT_SHA="unknown"
ARG VERSION="unknown"
ARG BUILD_DATE="unknown"
RUN echo "GIT_SHORT_SHA=${GIT_SHORT_SHA}" > /etc/kegbot-version
RUN echo "VERSION=${VERSION}" >> /etc/kegbot-version
RUN echo "BUILD_DATE=${BUILD_DATE}" >> /etc/kegbot-version

VOLUME  ["/kegbot-data"]

EXPOSE 8000
CMD [ \
   "gunicorn", \
   "pykeg.web.wsgi:application", \
   "--config=python:pykeg.web.gunicorn_conf" \
]
