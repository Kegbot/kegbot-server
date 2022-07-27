FROM python:3.10.5-bullseye

RUN mkdir /app
WORKDIR /app

ENV SHELL=/bin/sh \
   PIP_NO_CACHE_DIR=1 \
   KEGBOT_DATA_DIR=/kegbot-data \
   KEGBOT_IN_DOCKER=True \
   KEGBOT_ENV=debug

# Install toolchains. Mostly, image libraries that Python PIL/Pillow will require.
RUN apt-get -qq update \
   && DEBIAN_FRONTEND=noninteractive apt-get -y install \
      curl \
      libffi-dev \
      libfreetype6-dev \
      libfribidi-dev \
      libharfbuzz-dev \
      libjpeg-turbo-progs \
      libjpeg62-turbo-dev \
      liblcms2-dev \
      libopenjp2-7-dev \
      libtiff5-dev \
      libwebp-dev \
      libssl-dev \
      zlib1g-dev \
  && rm -rf /var/lib/apt/lists/* \
  && python -m pip install -U pip \
  # The cryptography build requires rust, which adds >1GB to the image. \
  # Install it only to install cryptography, then remove it. \
  && curl https://sh.rustup.rs -sSf | sh -s -- -y \
  && PATH=/root/.cargo/bin:$PATH pip install cryptography \
  && rm -rf /root/.rustup /root/.cargo \
  && pip install poetry \
  && rm -rf /root/.cache

# Install python dependencies.
COPY pyproject.toml poetry.lock ./
ADD pykeg/__init__.py ./pykeg/
RUN poetry config virtualenvs.create false && poetry install -n

# Install the app itself.
ADD bin /usr/local/sbin/
ADD pykeg ./pykeg

# Collect static files. Use fake versions of required env variables
# since they're not relevant at this step.
RUN DATABASE_URL=mysql:// \
   REDIS_URL=redis:// \
   KEGBOT_SECRET_KEY=changeme \
   kegbot collectstatic --noinput -v 0

# Tag the build with build information.
ARG GIT_SHORT_SHA="unknown"
ARG VERSION="unknown"
ARG BUILD_DATE="unknown"
RUN echo "GIT_SHORT_SHA=${GIT_SHORT_SHA}\nVERSION=${VERSION}\nBUILD_DATE=${BUILD_DATE}" > /etc/kegbot-version

VOLUME  ["/kegbot-data"]

EXPOSE 8000
ENTRYPOINT ["/usr/local/sbin/kegbot"]
CMD ["run_server"]
