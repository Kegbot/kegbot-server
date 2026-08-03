import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from pykeg.util.genconstants import genconstants

OUTFILE = os.path.join(settings.BASE_DIR, "web-ui/lib/shared-constants.ts")


class Command(BaseCommand):
    help = f"Writes all Django-managed constants to `{OUTFILE}`."

    def handle(self, *args, **options):
        data = json.dumps(genconstants(), indent=2)
        ts_content = f"export default {data} as const;\n"
        os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)
        with open(OUTFILE, "w+") as fp:
            fp.write(ts_content)
        print(data)
