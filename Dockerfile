FROM python:2.7-alpine

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
      openjpeg && \
   pip install pipenv

ADD Pipfile Pipfile.lock ./
RUN apk add --no-cache mariadb-connector-c-dev && \
   apk add --no-cache --virtual _build-deps \
     build-base mariadb-dev libjpeg-turbo-dev zlib-dev && \
   pipenv install --deploy && \
   apk del _build-deps

ADD bin ./bin
ADD pykeg ./pykeg
ADD setup.py ./
RUN pipenv run python setup.py develop
RUN pipenv run kegbot collectstatic -v 0 --noinput

VOLUME  ["/kegbot-data"]

EXPOSE 8000
CMD ["/usr/local/bin/pipenv", "run", "gunicorn", "pykeg.web.wsgi:application", "-b", "0.0.0.0:8000"]
