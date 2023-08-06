#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"
__version__ = "1.0.8"


import sys
import time

from datetime import datetime, timedelta
from itertools import cycle
from io import TextIOWrapper
from typing import Iterable, Callable


def str_timedelta(td: timedelta) -> str:
    """
    Returns a string description of the datetime.timedelta object

    """

    td = str(td)

    # Remove ms
    # 0:01:40.123000 -> 0:01:40
    if "." in td:
        td = td[: td.rindex(".")]

    # 0:01:40 -> 00:01:40
    if td.startswith("0:"):
        td = "00:" + td[2:]

    return td


def get_timeout_date(
    date: datetime = None,
    days: int = 0,
    seconds: int = 0,
    microseconds: int = 0,
    milliseconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    weeks: int = 0,
) -> datetime:
    """
    Returns a new datetime.datetime object with the modified date

    """

    if date is None:
        date = datetime.today()

    return date + timedelta(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
    )


def wait(
    days: int = 0,
    seconds: int = 0,
    microseconds: int = 0,
    milliseconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    weeks: int = 0,
    progress_bar: Iterable[str] = ("|", "/", "-", "\\"),
    delay_seconds: float = 1,
    log_pattern_progress: str = "[{progress_bar}] Time left to wait: {left}",
    log_pattern_cancel: str = "\nWaiting canceled\n",
    log_pattern_clear_line: str = "\r" + " " * 100 + "\r",
    log: TextIOWrapper = sys.stdout,
    is_need_stop: Callable[[], bool] = lambda: False,
):
    """
    The function calls the wait for the specified period.

    """
    try:
        progress_bar = cycle(progress_bar)

        today = datetime.today()
        timeout_date = get_timeout_date(
            date=today,
            days=days,
            seconds=seconds,
            microseconds=microseconds,
            milliseconds=milliseconds,
            minutes=minutes,
            hours=hours,
            weeks=weeks,
        )

        while today <= timeout_date and not is_need_stop():
            left = timeout_date - today
            left = str_timedelta(left)

            log.write(log_pattern_clear_line)
            log.write(
                log_pattern_progress.format(
                    progress_bar=next(progress_bar),
                    left=left,
                )
            )
            log.flush()

            time.sleep(delay_seconds)
            today = datetime.today()

        log.write(log_pattern_clear_line)

    except KeyboardInterrupt:
        log.write(log_pattern_cancel)


if __name__ == "__main__":
    wait(seconds=1)
    wait(seconds=3)
    wait(seconds=5)

    print("Start wait")
    wait(seconds=1)
    print("Finish wait")

    while True:
        print()
        print("Current datetime:", datetime.now())
        print()
        wait(minutes=1, seconds=30)
