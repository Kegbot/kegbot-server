# Frontend build stage: compiles the web-ui bundle with bun + vite.
FROM oven/bun:1-slim AS frontend
WORKDIR /build
COPY package.json bun.lockb bunfig.toml ./
RUN bun install --frozen-lockfile
COPY vite.config.ts tsconfig.json openapi-ts.config.ts ./
COPY web-ui ./web-ui
RUN bun run build


FROM python:3.14-slim

RUN mkdir /app
WORKDIR /app

ENV SHELL=/bin/sh \
   KEGBOT_DATA_DIR=/kegbot-data \
   KEGBOT_IN_DOCKER=True \
   KEGBOT_ENV=debug

# Build/runtime libraries: MySQL + Postgres client headers (mysqlclient,
# psycopg2 build from source), client tools (`kegbot backup`/`restore`
# shell out to mysqldump/mysql/pg_dump/psql), and the image libraries
# Pillow needs.
RUN apt-get -qq update \
   && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
      build-essential \
      pkg-config \
      default-libmysqlclient-dev \
      default-mysql-client \
      libpq-dev \
      postgresql-client \
      libjpeg-dev \
      libfreetype6-dev \
      liblcms2-dev \
      libopenjp2-7-dev \
      libtiff-dev \
      libwebp-dev \
      zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

# uv, configured to install into the system Python (no venv).
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/usr/local

# Install dependencies first (cached) using only the lockfile + manifest.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Install the app itself.
COPY bin /usr/local/sbin/
COPY pykeg ./pykeg
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Bring in the built frontend, then collect static files. Use fake
# versions of required env variables since they're not relevant here.
COPY --from=frontend /build/web-ui/dist ./web-ui/dist
RUN DATABASE_URL=mysql:// \
   REDIS_URL=redis:// \
   KEGBOT_SECRET_KEY=changeme \
   kegbot collectstatic --noinput -v 0

# Tag the build with build information.
ARG GIT_SHORT_SHA="unknown"
ARG VERSION="unknown"
ARG BUILD_DATE="unknown"
RUN printf "GIT_SHORT_SHA=%s\nVERSION=%s\nBUILD_DATE=%s\n" "${GIT_SHORT_SHA}" "${VERSION}" "${BUILD_DATE}" > /etc/kegbot-version

VOLUME  ["/kegbot-data"]

EXPOSE 8000
ENTRYPOINT ["/usr/local/sbin/kegbot"]
CMD ["run_server"]
