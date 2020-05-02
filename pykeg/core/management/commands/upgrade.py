from __future__ import print_function

from builtins import str
from distutils.version import StrictVersion
import sys

from pykeg.core.util import get_version_object

from django.core.management.base import BaseCommand

from django.contrib.staticfiles.management.commands import collectstatic
from django.core.management.commands import migrate
from pykeg.core.management.commands import regen_stats

from pykeg.core import models
from pykeg.core import checkin


# Versions earlier than this cannot be upgraded. History:
#  v0.9.35 - migrations rebased to 0001
#  v1.1.1  - last release with South-based migrations
#  v1.2.0  - first Django 1.7 migrations
MINIMUM_INSTALLED_VERSION = StrictVersion("1.1.1")


def run(cmd, args=[]):
    cmdname = cmd.__module__.split(".")[-1]
    arg_str = " ".join("%s" % a for a in args)
    print("--- Running command: %s %s" % (cmdname, arg_str))
    cmd.run_from_argv([sys.argv[0], cmdname] + args)


class Command(BaseCommand):
    help = "Perform post-upgrade tasks."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            dest="force",
            default=False,
            help="Run even if installed version is up-to-date.",
        )
        parser.add_argument(
            "--skip_static",
            action="store_true",
            dest="skip_static",
            default=False,
            help="Skip `kegbot collectstatic` during upgrade. (Not recommended.)",
        )
        parser.add_argument(
            "--skip_stats",
            action="store_true",
            dest="skip_stats",
            default=False,
            help="Skip `kegbot regen_stats` during upgrade. (Not recommended.)",
        )

    def handle(self, *args, **options):
        installed_version = models.KegbotSite.get_installed_version()
        app_version = get_version_object()
        force = options.get("force")

        if installed_version is None:
            print("Kegbot is not installed; run setup-kegbot.py first.")
            sys.exit(1)

        if installed_version == app_version and not force:
            print("Version {} already installed.".format(installed_version))
            return

        if installed_version > app_version:
            print(
                "Installed version {} is newer than app version {}".format(
                    installed_version, app_version
                )
            )
            sys.exit(1)

        if installed_version < MINIMUM_INSTALLED_VERSION:
            print("")
            print("ERROR: This version of Kegbot can only upgrade systems running on version")
            print(
                "v{} or newer.  Please install Kegbot v{} and run `kegbot upgrade` again.".format(
                    MINIMUM_INSTALLED_VERSION, MINIMUM_INSTALLED_VERSION
                )
            )
            print("(Existing version: {})".format(installed_version))
            print("")
            print("More help: https://github.com/Kegbot/kegbot-server/wiki/Upgrading-Old-Versions")
            print("")
            sys.exit(1)

        print("Upgrading from {} to {}".format(installed_version, app_version))
        self.do_version_upgrades(installed_version)

        run(migrate.Command(), args=["--noinput", "-v", "0"])

        if not options.get("skip_stats"):
            run(regen_stats.Command())

        if not options.get("skip_static"):
            run(collectstatic.Command(), args=["--noinput"])

        site = models.KegbotSite.get()
        site.server_version = str(app_version)
        site.save()

        # Refresh any news (since we have a new version).
        try:
            checkin.checkin(timeout=5.0, quiet=True)
        except (checkin.CheckinError, Exception):
            pass

        print("")
        print("Upgrade complete!")

    def do_version_upgrades(self, installed_version):
        if installed_version.version < (1, 2, 0):
            print("Upgrading from v1.1.x")
