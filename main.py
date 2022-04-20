import random
import time

import requests

domain = "hjalposs47.shop"
path = "/verification/"

emails = ("gmail.com", "outlook.com", "yahoo.com", "protonmail.com",)
"""
email=MinEnormaSnopp@gmail.com
pass=Storpenis1234
get=Logga+in


"""
with open("firstnames.txt", "r") as file_h:
    firstnames = file_h.readlines()

with open("lastnames.txt", "r") as file_h:
    lastnames = file_h.readlines()


fullpath = f"http://{domain}{path}"
cntr = 0
with open("passlist.txt", "r") as file_h:
    for passw in file_h:
        indx = random.randint(0, len(emails) - 1)
        email = f"{firstnames[random.randint(0, len(firstnames)- 1)].strip().lower()}.{lastnames[random.randint(0, len(lastnames)- 1)].strip().lower()}@{emails[indx]}"
        x = requests.post(fullpath, data={"email": email, "pass": passw.strip(), "get": "Logga in"})
        print(f"Sent request no: {cntr}")
        cntr += 1
        time.sleep(0.3)
