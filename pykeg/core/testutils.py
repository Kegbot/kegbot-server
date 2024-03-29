"""Utilities for use in tests."""

import datetime
import os

import vcr
from django.conf import settings
from django.utils import timezone

TESTDATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../testdata/"))
CASSETTE_DIR = os.path.join(TESTDATA_DIR, "request_fixtures")


def get_filename(f):
    return os.path.join(TESTDATA_DIR, f)


def make_datetime(*args):
    if settings.USE_TZ:
        return datetime.datetime(*args, tzinfo=timezone.utc)
    else:
        return datetime.datetime(*args)


def get_vcr(test_name):
    cassette_dir = os.path.join(CASSETTE_DIR, test_name)
    return vcr.VCR(
        serializer="yaml",
        cassette_library_dir=cassette_dir,
        record_mode="none",
        match_on=["uri", "method"],
    )
