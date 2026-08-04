#!/usr/bin/env python
"""Verifies a site restored from a v1.3 backup and upgraded to this version.

Run after `kegbot restore <legacy zip>` + `kegbot upgrade`. Compares the
database against testdata/demo-site.json (the data the legacy backups were
built from) and smoke-tests key API endpoints. Exits nonzero on any failure.
"""

import json
import os
import sys
from collections import Counter

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pykeg.settings")
django.setup()

from django.apps import apps  # noqa: E402
from django.test import Client  # noqa: E402

from pykeg.core import models  # noqa: E402
from pykeg.core.util import get_version  # noqa: E402

failures = []


def check(label, expected, actual):
    if expected == actual:
        print(f"ok: {label}: {actual}")
    else:
        print(f"FAIL: {label}: expected {expected}, got {actual}")
        failures.append(label)


with open("testdata/demo-site.json") as f:
    fixture_counts = Counter(row["model"] for row in json.load(f))

for label, expected in sorted(fixture_counts.items()):
    check(f"count {label}", expected, apps.get_model(label).objects.count())

site = models.KegbotSite.get()
check("server_version", get_version(), site.server_version)
check("site is_setup", True, site.is_setup)
check("kegs on tap", 2, models.Keg.objects.filter(status=models.Keg.STATUS_ON_TAP).count())

client = Client()
for url in [
    "/api/users/me",
    "/api/status",
    "/api/kegs",
    "/api/sessions",
    "/api/stats/system",
]:
    response = client.get(url)
    check(f"GET {url}", 200, response.status_code)

api_key = models.ApiKey.objects.first()
if api_key:
    response = client.get(f"/api/v1/status/?api_key={api_key.key}")
    check("GET /api/v1/status (restored api key)", 200, response.status_code)

if failures:
    print(f"\n{len(failures)} check(s) failed")
    sys.exit(1)
print("\nAll checks passed.")
