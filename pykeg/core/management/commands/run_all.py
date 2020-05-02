from pykeg.core.management.commands.common import RunnerCommand


class Command(RunnerCommand):
    help = "Runs background task queue workers."
    pidfile_name = "kegbot_run_all.pid"

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
        logs_dir = options.get("logs_dir")

        workers_command = "kegbot run_workers"
        if logs_dir:
            workers_command += " --logs_dir={}".format(logs_dir)
        ret.append(("workers", workers_command))

        extra_options = options.get("gunicorn_options", "")
        ret.append(("guincorn", "gunicorn pykeg.web.wsgi:application " + extra_options))
        return ret
