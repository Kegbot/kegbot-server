from builtins import object
import copy
import logging
import os
import pwd
import signal
import sys
import subprocess
import time

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 1.0


class Runner(object):
    """Runs several commands together as a process group, acting as a watchdog
    while running.

    Limitations:
      * All subprocesses will run in the *same* process group as the parent
        process.
      * All subprocesses will have stdin, stdout, and stderr redirected to
        the OS's /dev/null fd.
      * A Runner cannot be be reused.
    """

    def __init__(self):
        self.commands = {}
        self.watched_procs = {}
        self.running = False
        self.logger = logger

    def is_running(self):
        return self.running

    def add_command(self, command_name, command):
        logger.debug('Adding command "{}": {}'.format(command_name, command))
        if command_name in self.commands:
            raise ValueError("Command already installed")
        self.commands[command_name] = command

    def run(self):
        """Launches all commands, watching their pids."""
        assert not self.is_running(), "Already running!"
        self.running = True

        self.logger.info("Starting commands from pid={}".format(os.getpid()))
        dev_null_name = getattr(os, "devnull", "/dev/null")
        dev_null = os.open(dev_null_name, os.O_RDWR)

        # Set sensible env defaults, since supervisor won't.
        path = os.environ.get("PATH", "")
        if sys.argv[0]:
            d = os.path.dirname(sys.argv[0])
            if d not in path.split(":"):
                path = "{}:{}".format(d, path)

        user = os.environ.get("USER", "")
        if not user:
            try:
                user = pwd.getpwuid(os.getuid()).pw_name
            except KeyError:
                pass

        env = copy.copy(os.environ)
        env["PATH"] = path
        env["USER"] = user

        self.logger.debug("env={}".format(repr(env)))

        for command_name, command in list(self.commands.items()):
            proc = self._launch_command(command_name, command, dev_null, env)
            self.logger.info("Started {} (pid={})".format(command_name, proc.pid))
            self.watched_procs[command_name] = proc

        self.watch_commands()

    def watch_commands(self):
        self.logger.info("Watching {} processes.".format(len(self.commands)))
        while True:
            abort = False
            for command_name, proc in list(self.watched_procs.items()):
                self.logger.debug("Pinging {} (pid={})".format(command_name, proc.pid))
                proc.poll()
                if proc.returncode is not None:
                    self.logger.info(
                        'Process "{}" exited with returncode {}'.format(
                            command_name, proc.returncode
                        )
                    )
                    abort = True
            if abort:
                self.abort()
                return
            time.sleep(POLL_INTERVAL_SECONDS)

    def abort(self):
        self.logger.info("Abort called, killing remaining processes ...")
        for command_name, proc in list(self.watched_procs.items()):
            if proc.returncode is None:
                self.logger.info("Killing {} (pid={})".format(command_name, proc.pid))
                os.killpg(proc.pid, signal.SIGTERM)
        for command_name, proc in list(self.watched_procs.items()):
            self.logger.info("Waiting for {} to exit (pid={}) ...".format(command_name, proc.pid))
            proc.wait()
            self.logger.info("... done.")
        self.logger.info("All processes exited.")

    def _launch_command(self, command_name, command, dev_null, env=None):
        self.logger.info("Launching command: {}: {}".format(command_name, command))

        def preexec():
            # Set session id.
            os.setsid()
            # Set umask to default to safe file permissions for root.
            os.umask(0o27)
            # Switch to a "safe" directory.
            os.chdir("/")

        proc = subprocess.Popen(
            command,
            stdin=dev_null,
            stdout=dev_null,
            stderr=dev_null,
            close_fds=True,
            shell=True,
            preexec_fn=preexec,
            env=env,
        )

        return proc


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    r = Runner()
    r.add_command("listen1", "nc -l 8081")
    r.add_command("listen2", "nc -l 8082")
    r.run()
