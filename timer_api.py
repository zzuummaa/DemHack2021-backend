import logging
import signal

from actions_processor import check_trigger_timers

from timeloop import Timeloop
from datetime import timedelta
from database import connect, DatabaseWrapper


timer_loop = Timeloop()
logging.getLogger('timeloop').setLevel(logging.ERROR)

db = DatabaseWrapper(connect())


@timer_loop.job(interval=timedelta(seconds=5))
def timer_task():
    check_trigger_timers(db)
    pass


def timer_api_stop():
    timer_loop.stop()


def timer_api_start():
    timer_loop.start()
    signal.signal(signal.SIGTERM, timer_api_stop)
    signal.signal(signal.SIGINT, timer_api_stop)


