# Kegbot Server

This is Kegbot Server, a backend and web interface for monitoring
and managing kegged beverages.

**Official repository:** https://github.com/Kegbot/kegbot-server/


## Quick start

Super quick start instructions:

```
$ docker-compose up
$ open http://localhost:8000/
```

For much more detail, see the complete [Kegbot Server documentation](https://docs.kegbot.org/projects/kegbot-server/en/latest/).


## Development

The web interface is a React single-page app (in `web-ui/`) served by the
Django backend (in `pykeg/`). For development, run both servers and browse
the vite dev server, which proxies API requests to Django:

```
$ uv sync                  # python dependencies
$ bun install              # frontend dependencies
$ kegbot runserver         # django, on port 8001
$ bun run dev              # vite, on http://localhost:8000  <-- browse here
```

Other useful commands:

```
$ uv run pytest                  # backend tests
$ bun run test                   # frontend tests
$ bun run check                  # frontend lint + typecheck
$ bun run build                  # production frontend build (web-ui/dist)
$ bun run generate-api           # regenerate the API client from the schema
$ bun run generate-constants     # regenerate web-ui/lib/shared-constants.ts
```


## Documentation and Help

* Main project page: https://kegbot.org/
* Docs: https://docs.kegbot.org/
* Discussion forum: https://forum.kegbot.org/
* Discusion Slack group: [Slack link](https://join.slack.com/t/kegbot/shared_invite/zt-3t6rpu9t-AXLNNmL0vPelsbcU6afvjQ)
* [@kegbot](http://twitter.com/kegbot) on Twitter


## Related Projects

* [Kegboard](https://github.com/Kegbot/kegboard): Firmware and schematics
  for the Kegbot controller board.
* [Kegbot Android app](https://github.com/Kegbot/kegbot-android): Kegtap,
  the Kegbot manager app for Android.


## License

All code is offered under the **MIT** license, unless otherwise noted.  Please
see `LICENSE.txt` for the full license.

