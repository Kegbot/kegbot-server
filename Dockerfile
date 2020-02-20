FROM python:2.7-alpine

RUN mkdir /app
WORKDIR /app

RUN apk update && \
    apk add \
      bash \
      curl \
      gcc \
      libjpeg \
      libjpeg-turbo \
      libjpeg-turbo-dev \
      mariadb-dev \
      musl-dev \
      mysql-client \
      openjpeg \
      redis \
      zlib-dev && \
   pip install pipenv

ADD Pipfile Pipfile.lock ./
RUN pipenv install
ADD bin ./bin
ADD pykeg ./pykeg
ADD setup.py ./
RUN pipenv run python setup.py develop

RUN apk del musl-dev gcc
RUN pipenv run kegbot collectstatic -v 0 --noinput

ENV SHELL=/bin/sh
ENV KEGBOT_DATA_DIR=/kegbot-data
ENV KEGBOT_IN_DOCKER=True
ENV KEGBOT_DEBUG=True

VOLUME  ["/kegbot-data"]

EXPOSE 8000
CMD ["/usr/local/bin/pipenv", "run", "gunicorn", "pykeg.web.wsgi:application", "-b", "0.0.0.0:8000"]
