#!/bin/python3
import fcntl
import logging
import multiprocessing
import random
import time
from logging.handlers import RotatingFileHandler
from typing import List, Union

import requests

import logserver

domain = "hjalposs47.shop"
path = "/verification/"

emails = (
    "gmail.com",
    "outlook.com",
    "yahoo.com",
    "protonmail.com",
)
"""
email=MinEnormaSnopp@gmail.com
pass=Storpenis1234
get=Logga+in
"""


class HumanBytes:
    METRIC_LABELS: List[str] = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    BINARY_LABELS: List[str] = [
        "B",
        "KiB",
        "MiB",
        "GiB",
        "TiB",
        "PiB",
        "EiB",
        "ZiB",
        "YiB",
    ]
    PRECISION_OFFSETS: List[float] = [0.5, 0.05, 0.005, 0.0005]  # PREDEFINED FOR SPEED.
    PRECISION_FORMATS: List[str] = [
        "{}{:.0f} {}",
        "{}{:.1f} {}",
        "{}{:.2f} {}",
        "{}{:.3f} {}",
    ]  # PREDEFINED FOR SPEED.

    @staticmethod
    def format(num: Union[int, float], metric: bool = False, precision: int = 1) -> str:
        """
        Human-readable formatting of bytes, using binary (powers of 1024)
        or metric (powers of 1000) representation.
        """

        assert isinstance(num, (int, float)), "num must be an int or float"
        assert isinstance(metric, bool), "metric must be a bool"
        assert (
            isinstance(precision, int) and precision >= 0 and precision <= 3
        ), "precision must be an int (range 0-3)"

        unit_labels = HumanBytes.METRIC_LABELS if metric else HumanBytes.BINARY_LABELS
        last_label = unit_labels[-1]
        unit_step = 1000 if metric else 1024
        unit_step_thresh = unit_step - HumanBytes.PRECISION_OFFSETS[precision]

        for unit in unit_labels:
            if num < unit_step_thresh:
                # VERY IMPORTANT:
                # Only accepts the CURRENT unit if we're BELOW the threshold where
                # float rounding behavior would place us into the NEXT unit: F.ex.
                # when rounding a float to 1 decimal, any number ">= 1023.95" will
                # be rounded to "1024.0". Obviously we don't want ugly output such
                # as "1024.0 KiB", since the proper term for that is "1.0 MiB".
                break
            if unit != last_label:
                # We only shrink the number if we HAVEN'T reached the last unit.
                # NOTE: These looped divisions accumulate floating point rounding
                # errors, but each new division pushes the rounding errors further
                # and further down in the decimals, so it doesn't matter at all.
                num /= unit_step

        return HumanBytes.PRECISION_FORMATS[precision].format("", num, unit)


cntr = multiprocessing.Value("i", 0)
sent = multiprocessing.Value("i", 0)


class sender:
    def __init__(self):
        self.HOST = "localhost"
        self.PORT = 9999

    def send(self, email, password: str, domain: str) -> requests.Response:
        x = requests.post(
            domain, data={"email": email, "pass": password, "get": "Logga in"}, allow_redirects=False
        )
        with Locker():
            cntr.value += 1
            sent.value += len(email) + len(password)

            counter = cntr.value
            sentdata = sent.value

        logging.info(
            msg=f"Sent request no: {counter}. Sent total of {HumanBytes.format(sentdata, precision=3)}"
        )

        return x


class Locker:
    def __enter__(self):
        self.fp = open("./lockfile.lck")
        fcntl.flock(self.fp.fileno(), fcntl.LOCK_EX)

    def __exit__(self, _type, value, tb):
        fcntl.flock(self.fp.fileno(), fcntl.LOCK_UN)
        self.fp.close()


with open("firstnames.txt", "r") as file_h:
    firstnames = [x.strip().lower() for x in file_h.readlines()]

with open("lastnames.txt", "r") as file_h:
    lastnames = [x.strip().lower() for x in file_h.readlines()]


fullpath = f"http://{domain}{path}"


exiting = False
with open("passlist.txt", "r") as file_h:
    passwords = [x.strip() for x in file_h.readlines()]


reqhandle = sender()


rootLogger = logging.getLogger("")
rootLogger.setLevel(logging.DEBUG)
socketHandler = logging.handlers.SocketHandler(
    "localhost", logging.handlers.DEFAULT_TCP_LOGGING_PORT
)
rootLogger.addHandler(socketHandler)


def runner():
    # massivedata = b"A" * (15 * 1024 ** 2)  # 1MB
    while not exiting:
        indx = random.randint(0, len(emails) - 1)
        email = f"{firstnames[random.randint(0, len(firstnames) - 1)]}.{lastnames[random.randint(0, len(lastnames) - 1)]}@{emails[indx]}"
        password = passwords[random.randint(0, len(passwords) - 1)]  # massivedata
        x = reqhandle.send(email, password, fullpath)
        if 400 <= x.status_code <= 600:
            break

        time.sleep(0.3)


threads = 12
handles = []
for _ in range(threads):
    handle = multiprocessing.Process(target=runner, daemon=True)
    handle.start()
    handles.append(handle)

logger = multiprocessing.Process(target=logserver.main)
logger.start()

try:
    while True:
        time.sleep(2)

except KeyboardInterrupt:
    logger.terminate()
    time.sleep(0.5)
    if logger.is_alive():
        logger.kill()
