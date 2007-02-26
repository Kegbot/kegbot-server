#!/bin/bash

export PYTHONPATH="$PYTHONPATH:$(dirname `pwd`)"
export DJANGO_SETTINGS_MODULE="pykeg.db_settings"

