from pykeg.core.management.commands.common import RunnerCommand


class Command(RunnerCommand):
    help = "Performs `run_server` and `run_workers`"
    pidfile_name = "kegbot_run_all.pid"

    def get_commands(self, options):
        ret = []
        logs_dir = options.get("logs_dir")

        server_command = "kegbot run_server"
        if logs_dir:
            server_command += " --logs_dir={}".format(logs_dir)
        ret.append(("server", server_command))

        workers_command = "kegbot run_workers"
        if logs_dir:
            workers_command += " --logs_dir={}".format(logs_dir)
        ret.append(("workers", workers_command))

        return ret
