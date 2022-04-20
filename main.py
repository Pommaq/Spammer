import random
import time
import threading
import typing

import requests

domain = "hjalposs47.shop"
path = "/verification/"

emails = ("gmail.com", "outlook.com", "yahoo.com", "protonmail.com",)
"""
email=MinEnormaSnopp@gmail.com
pass=Storpenis1234
get=Logga+in
"""


def format_bytes(size) -> typing.Tuple[int, str]:
    """
    :param: size given in bytes
    :return (Number of units, postfix):
    """
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'kilo', 2: 'mega', 3: 'giga', 4: 'tera'}
    while size > power:
        size /= power
        n += 1
    return size, power_labels[n]+'bytes'


class sender:
    def __init__(self):
        self.cntr = 0
        self.mtx  = threading.Lock()
        self.sent = 0


    def send(self, email, password: str, domain: str) -> requests.Response:
        x = requests.post(domain, data={"email": email, "pass": password, "get": "Logga in"})
        self.mtx.acquire()
        self.cntr += 1
        self.sent += len(email) + len(password)
        sz, postfix = format_bytes(self.sent)
        print(f"Sent request no: {self.cntr}. Sent total of {sz} {postfix}")

        self.mtx.release()
        return x



with open("firstnames.txt", "r") as file_h:
    firstnames = [x.strip().lower() for x in file_h.readlines()]

with open("lastnames.txt", "r") as file_h:
    lastnames = [x.strip().lower() for x in file_h.readlines()]



fullpath = f"http://{domain}{path}"


exiting = False
with open("passlist.txt", "r") as file_h:
    passwords = [x.strip() for x in file_h.readlines()]


reqhandle = sender()

def runner():
    #massivedata = b"A" * (15 * 1024 ** 2)  # 1MB
    while not exiting:
        indx = random.randint(0, len(emails) - 1)
        email = f"{firstnames[random.randint(0, len(firstnames) - 1)]}.{lastnames[random.randint(0, len(lastnames) - 1)]}@{emails[indx]}"
        password = passwords[random.randint(0, len(passwords) - 1)] #massivedata
        x = reqhandle.send(email, password, fullpath)
        if 400 <= x.status_code <= 600:
            break

        time.sleep(0.3)







threads = 4
handles = []
for _ in range(threads):
    handle = threading.Thread(target=runner)
    handle.start()
    handles.append(handle)


for handle in handles:
    handle.join()
