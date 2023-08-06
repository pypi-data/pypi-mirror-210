#!/usr/bin/python
import os
import json
from pathlib import Path


def save_apikey(data, dir_=".nd", name="apikeys"):
    path = str(Path.home()) + "/" + dir_
    if not os.path.exists(path):
        os.makedirs(path)

    try:
        with open(path + "/" + name, "w") as f:
            json.dump(data, f)
            return {"message": "api keys saved", "status_code": 200}
    except:
        return {"message": "api keys not saved", "status_code": 500}


def read_saved_apikey(dir_=".nd", name="apikeys"):
    path = str(Path.home()) + "/" + dir_
    try:
        with open(path + "/" + name, "r") as f:
            return json.load(f)
    except:
        return {"message": "no api keys saved", "status_code": 500}


def apikeys_headers():
    access = read_saved_apikey(dir_=".nd", name="apikeys")
    headers = {}
    headers["api-key"] = access["api-key"]
    return headers
