import os

from pykeg.core.management.commands.common import RunnerCommand


class Command(RunnerCommand):
    help = "Runs background task queue workers."
    pidfile_name = "kegbot_run_workers.pid"

    def get_commands(self, options):
        default_log = stats_log = beat_log = ""
        logs_dir = options.get("logs_dir")

        if logs_dir:
            default_log = ' --logfile="{}"'.format(os.path.join(logs_dir, "celery_default.log"))
            stats_log = ' --logfile="{}"'.format(os.path.join(logs_dir, "celery_stats.log"))
            beat_log = ' --logfile="{}"'.format(os.path.join(logs_dir, "celery_beat.log"))
        ret = []

        base_cmd = "celery -A pykeg worker -l info "

        ret.append(
            ("celery_default", base_cmd + '-Q default --hostname="default@%h"' + default_log)
        )
        ret.append(
            (
                "celery_stats",
                base_cmd + '-Q stats --concurrency=1 --hostname="stats@%h"' + stats_log,
            )
        )

        ret.append(("celery_beat", "celery -A pykeg beat --pidfile= -l info{}".format(beat_log)))

        return ret
