#!/usr/bin/python
import os
import json
import sys
from pathlib import Path

sys.path.append(str(Path(".").absolute()))


def save_token(resp, dir_=".nd", name="token"):
    if "Error" not in resp:
        path = str(Path.home()) + "/" + dir_
        if not os.path.exists(path):
            os.makedirs(path)

        try:
            with open(path + "/" + name, "w") as f:
                json.dump(resp, f)
                return {"message": "credential  saved", "status_code": 200}
        except Exception:
            return {"message": "credential not saved", "status_code": 500}


def read_saved_token(dir_=".nd", name="token"):
    path = str(Path.home()) + "/" + dir_
    try:
        with open(path + "/" + name, "r") as f:
            return json.load(f)["token"]
    except:
        return {"message": "cant read credential ", "status_code": 500}


def token_headers():
    token = read_saved_token()
    if "status_code" not in token:
        headers = {}
        headers["Authorization"] = "Bearer " + str(token)
        return headers
    return {"message": "cant add token to headers", "status_code": 500}
