import multiprocessing
import os

if os.getenv("KEGBOT_IN_HEROKU") and os.getenv("PORT"):
    # Necessary on Heroku, which doesn't respect EXPOSE :-\
    bind = "0.0.0.0:{}".format(int(os.getenv("PORT")))
else:
    bind = "0.0.0.0:8000"

worker_class = "gevent"
workers = multiprocessing.cpu_count() * 2 + 1
