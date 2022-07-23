from pykeg.core.management.commands.common import RunnerCommand


class Command(RunnerCommand):
    help = "Runs the web server."
    pidfile_name = "kegbot_run_server.pid"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--gunicorn_options",
            action="store",
            dest="gunicorn_options",
            default="-w 3",
            help="Specifies extra options to pass to gunicorn.",
        )

    def get_commands(self, options):
        ret = []
        extra_options = options.get("gunicorn_options", "")
        ret.append(("guincorn", "gunicorn pykeg.web.wsgi:application " + extra_options))
        return ret
