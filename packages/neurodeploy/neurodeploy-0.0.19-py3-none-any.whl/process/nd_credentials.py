#!/usr/bin/python
import os
import json
from pathlib import Path


def save_credentials(data, dir_=".nd", name="credentials"):
    path = str(Path.home()) + "/" + dir_
    if not os.path.exists(path):
        os.makedirs(path)

    try:
        with open(path + "/" + name, "w") as f:
            json.dump(data, f)
            return {"message": "credential saved", "status_code": 200}
    except:
        return {"message": "credential not saved", "status_code": 500}


def read_saved_credentials(dir_=".nd", name="credentials"):
    path = str(Path.home()) + "/" + dir_
    try:
        with open(path + "/" + name, "r") as f:
            return json.load(f)
    except:
        return {"message": "no credential saved", "status_code": 500}


def credentials_headers():
    access = read_saved_credentials(dir_=".nd", name="credentials")
    headers = {}
    if "status_code" not in access:
        headers["access_key"] = access["access_key"]
        headers["secret_key"] = access["secret_key"]
    return headers
