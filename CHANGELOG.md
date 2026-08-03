# Changelog

You can [view the published changelog here](https://docs.kegbot.org/projects/kegbot-server/en/latest/releases/changelog.html).

## Current version (unreleased)

A modernization release. The runtime, framework, and toolchain were all brought
up to date.

### Highlights

- **Python 3.14** is now required (was 3.10).
- **Django 5.2 LTS** (was 3.2).
- Web server switched from **gunicorn/gevent** to **waitress**.
- Packaging moved from **Poetry** to **uv**; linting/formatting moved to **ruff**;
  pre-flight checks run via **pre-commit**.
- protobuf upgraded to the 6.x series.
- Docker image rebuilt on `python:3.14-slim` with uv.
- **Very old backups can now be restored directly.** `kegbot restore` accepts
  legacy format-1 backups (created by Kegbot v1.1.x) and upgrades their data in
  one step; no intermediate 1.2/1.3 install is needed.

### Upgrade notes (for existing installs)

- **Everyone is logged out once.** Sessions now use the JSON serializer (Django
  removed the pickle serializer), so existing session cookies are invalidated on
  upgrade. Users simply log in again.
- **Background jobs enqueue on database commit.** Stats/notification jobs are now
  handed to the worker only after the surrounding DB transaction commits. Ensure
  `run_workers` is running (unchanged) to process them.
- **`run_gunicorn` was removed.** Use `kegbot run_server` (now waitress). Tune
  with `--waitress_options` (e.g. `--threads=8`); `$PORT` is still honored.
- The Docker image no longer publishes a `linux/arm/v7` variant (amd64 + arm64
  only).
- The legacy gflags-based Python API client was removed from the server package;
  it lives in the separate kegbot-api project.
