import os
import sys

from django.conf import settings

from pykeg.core.management.commands.common import RunnerCommand


class Command(RunnerCommand):
    help = "Runs background task queue workers."
    pidfile_name = "kegbot_run_workers.pid"

    def get_commands(self, options):
        default_log = ""
        logs_dir = options.get("logs_dir")
        if logs_dir:
            default_log = ' --logfile="{}"'.format(os.path.join(logs_dir, "workers.log"))

        queue_names = " ".join(settings.RQ_QUEUES.keys())
        ret = [
            ("rq", f"{sys.argv[0]} rqworker {queue_names}{default_log} -v 3"),
        ]
        return ret
