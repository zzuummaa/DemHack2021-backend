import logging
import signal

from timeloop import Timeloop
from datetime import timedelta


timer_loop = Timeloop()
logging.getLogger('timeloop').setLevel(logging.ERROR)


@timer_loop.job(interval=timedelta(seconds=5))
def timer_task():
    # TODO check triggers
    pass


def timer_api_stop():
    timer_loop.stop()


def timer_api_start():
    timer_loop.start()
    signal.signal(signal.SIGTERM, timer_api_stop)
    signal.signal(signal.SIGINT, timer_api_stop)


