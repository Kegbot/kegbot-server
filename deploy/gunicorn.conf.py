import os

bind = "127.0.0.1:8000"
workers = (os.sysconf("SC_NPROCESSORS_ONLN") * 2) + 1
loglevel = "error"
proc_name = "kegbot"
