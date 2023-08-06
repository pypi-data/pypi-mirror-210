#!/usr/bin/python
import os
import json
from pathlib import Path


def save_config(
    username,
    url="https://user-api.neurodeploy.com",
    #    url="https://user-api.playingwithml.com",
    dir_=".nd",
    name="config",
    url_api="https://api.neurodeploy.com",
    #  url_api="https://api.playingwithml.com",
):
    path = str(Path.home()) + "/" + dir_
    if not os.path.exists(path):
        os.makedirs(path)

    config = {}
    config["username"] = username
    config["url"] = url
    config["url_api"] = url_api

    try:
        with open(path + "/" + name, "w") as f:
            json.dump(config, f)
            return {"message": "config saved", "status_code": 200}
    except:
        return {"message": "config not saved", "status_code": 400}


def read_saved_config(dir_=".nd", name="config"):
    path = str(Path.home()) + "/" + dir_
    try:
        with open(path + "/" + name, "r") as f:
            return json.load(f)
    except:
        return {
            "message": "Could not read config file. Please run configure first.",
            "status_code": 400,
        }


def read_env_config():
    env = {}
    env["secret_key"] = os.getenv(
        "ND_SECRET_KEY"
    )  # user acces key value to auth to api
    env["access_key"] = os.getenv(
        "ND_ACCESS_KEY"
    )  # usr secret key value to auth to api
    env["default_lib"] = os.getenv("ND_DEFAULT_LIB")  # Default ml library used
    env["default_filetype"] = os.getenv(
        "ND_DEFAULT_FILETYPE"
    )  # Default ml model file extention
    env["default_confdir"] = os.getenv(
        "ND_DEFAULT_CONFDIR"
    )  # Default cli configuration path to store username / token / credentials
    env["default_endpoint"] = os.getenv(
        "ND_DEFAULT_ENDPOINT"
    )  # Default neurodeploy endpoint domain name
    return env
