"""
WSGI config for pykeg project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from pykeg.core.util import get_version

BANNER = """
██╗  ██╗███████╗ ██████╗ ██████╗  ██████╗ ████████╗
██║ ██╔╝██╔════╝██╔════╝ ██╔══██╗██╔═══██╗╚══██╔══╝
█████╔╝ █████╗  ██║  ███╗██████╔╝██║   ██║   ██║   
██╔═██╗ ██╔══╝  ██║   ██║██╔══██╗██║   ██║   ██║   
██║  ██╗███████╗╚██████╔╝██████╔╝╚██████╔╝   ██║   
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝   
""".strip()

print(BANNER)
print('kegbot-server - version {}'.format(get_version()))
print('  homepage: https://kegbot.org')
print('   discuss: https://forum.kegbot.org')
print('-' * 80)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pykeg.settings")
application = get_wsgi_application()
