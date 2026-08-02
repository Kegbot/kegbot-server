import os

from pykeg.core.management.commands.common import RunnerCommand


class Command(RunnerCommand):
    help = "Runs the web server."
    pidfile_name = "kegbot_run_server.pid"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--waitress_options",
            action="store",
            dest="waitress_options",
            default="--threads=4",
            help="Specifies extra options to pass to waitress-serve.",
        )

    def get_commands(self, options):
        # Honor $PORT (e.g. Heroku) but default to 8000.
        port = os.getenv("PORT") or "8000"
        extra_options = options.get("waitress_options", "")
        command_line = (
            f"waitress-serve --host=0.0.0.0 --port={port} "
            f"{extra_options} pykeg.web.wsgi:application"
        ).strip()
        return [("waitress", command_line)]
