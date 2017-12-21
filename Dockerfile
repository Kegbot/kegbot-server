FROM python:2.7-alpine

RUN mkdir /app
WORKDIR /app

RUN apk update && apk add \
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
   zlib-dev

ADD requirements.txt /app/
RUN pip install -r requirements.txt

ADD setup.py .
ADD bin ./bin
ADD pykeg ./pykeg
RUN python setup.py install

RUN apk del musl-dev gcc
RUN kegbot collectstatic -v 0 --noinput

ENV KEGBOT_DATA_DIR=/kegbot-data
ENV KEGBOT_IN_DOCKER=True
ENV KEGBOT_DEBUG=True

VOLUME  ["/kegbot-data"]

EXPOSE 8000
CMD ["/usr/local/bin/gunicorn", "pykeg.web.wsgi:application", "-b", "0.0.0.0:8000"]
