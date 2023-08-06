import os
import json


from utils import query
from utils import files

from process import nd_config
from process import nd_credentials
from process.nd_token import token_headers
from process import nd_apikeys


def push(name, file=None, lib="tensorflow", filetype="h5", is_public="false"):
    """create a model and upload model file or update modelmeta data.

    :params: name
    :type:   str
    :params: filepath
    :type:   str
    :params: type
    :type:   str
    :params: persistance_type
    :type:   str
    :returns: ok.
    :rtype: dict
    :raises: none

    >>> from neurodeploy import model
    >>> model.push(name, file, lib, filetype)
    """
    conf = nd_config.read_saved_config()
    if "url" not in conf:
        return {
            "status_code": 400,
            "message": "Could not read config file. Plase run configure first.",
        }
    if "status_code" in conf:
        return {
            "message": "Could not push model. Please run configure first.",
            "status_code": 400,
        }

    main_url = conf["url"]
    url = main_url + "/" + "ml-models/" + name
    params = {}
    params["lib"] = lib
    params["filetype"] = filetype
    params["is_public"] = is_public
    headers = nd_credentials.credentials_headers()
    headers.update(token_headers())

    response_data = query.put(url, headers, params)
    if "errors" in response_data:
        return response_data
    if file:
        resp = files.upload_file(response_data, file)
        return resp
    return {"message": "Your model params has been updated", "status_code": 200}


def deploy(name, model, lib="tensorflow"):
    if lib != "tensorflow":
        print("Error: we currently only support this command for tensorflow.")
        raise NotImplementedError

    if lib == "tensorflow":
        file_path = "/tmp/model.h5"
        model.save(file_path)
        resp = push(name, file=file_path, lib="tensorflow", filetype="h5")
        os.remove(file_path)
    return resp


def delete(name):
    """delete the model with the given model name for the user associated with the credentials/jwt token..

    :params: name
    :type:   str
    :returns: ok.
    :rtype: dict
    :raises: none

    >>> from neurodeploy import model
    >>> model.delete(name)
    """
    conf = nd_config.read_saved_config()
    if "url" not in conf:
        return {
            "status_code": 400,
            "message": "Could not read config file. Plase run configure first.",
        }
    if "status_code" in conf:
        return {
            "message": "Could not delete model. Please run configure first.",
            "status_code": 400,
        }
    main_url = conf["url"]

    url = main_url + "/ml-models" + "/" + name
    headers = nd_credentials.credentials_headers()
    headers.update(token_headers())

    response_data = query.delete(url, headers)
    print(response_data["message"])
    return {"message": response_data["message"], "status_code": 200}


def list_logs(name):
    """list model logs  for logged user.

    :params: name
    :type:   str
    :returns: reponse_data
    :rtype: dict
    :raises: none

    >>> from neurodeploy import model
    >>> model.list_logs()
    """
    conf = nd_config.read_saved_config()
    if "url" not in conf:
        return {
            "status_code": 400,
            "message": "Could not read config file. Plase run configure first.",
        }
    if "status_code" in conf:
        return {
            "message": "Could not list models. Please run configure first.",
            "status_code": 400,
        }
    main_url = conf["url"]

    url = main_url + "/ml-models/" + name + "/logs"
    headers = nd_credentials.credentials_headers()
    headers.update(token_headers())

    response_data = query.get(url, headers)
    return response_data


def get_logs(name, timestamp):
    """list model logs of a spesific timestamp  for logged user.

    :params: name
    :type:   str
    :params: timestamp
    :type:   str
    :returns:  response_data
    :rtype: dict
    :raises: none

    >>> from neurodeploy import model
    >>> model.get_logs()
    """
    conf = nd_config.read_saved_config()
    if "url" not in conf:
        return {
            "status_code": 400,
            "message": "Could not read config file. Plase run configure first.",
        }
    if "status_code" in conf:
        return {
            "message": "Could not list models. Please run configure first.",
            "status_code": 400,
        }
    main_url = conf["url"]

    url = main_url + "/ml-models/" + name + "/logs" + timestamp
    headers = nd_credentials.credentials_headers()
    headers.update(token_headers())

    response_data = query.get(url, headers)
    return response_data


def list():
    """list models  for logged user.

    :params: none
    :type:   str
    :returns: ok.
    :rtype: dict
    :raises: none

    >>> from neurodeploy import model
    >>> model.list()
    """
    conf = nd_config.read_saved_config()
    if "url" not in conf:
        return {
            "status_code": 400,
            "message": "Could not read config file. Plase run configure first.",
        }
    if "status_code" in conf:
        return {
            "message": "Could not list models. Please run configure first.",
            "status_code": 400,
        }
    main_url = conf["url"]

    url = main_url + "/ml-models"
    headers = nd_credentials.credentials_headers()
    headers.update(token_headers())

    response_data = query.get(url, headers)
    return response_data


def get(name):
    """get metadata (and download link) for model with the given model name for the user associated with the credentials/jwt token.

    :params: name
    :type:   str
    :returns: ok.
    :rtype: dict
    :raises: none

    >>> from neurodeploy import model
    >>> model.list()
    """
    conf = nd_config.read_saved_config()
    if "url" not in conf:
        return {
            "status_code": 400,
            "message": "Could not read config file. Plase run configure first.",
        }
    if "status_code" in conf:
        return {
            "message": "Could not get model. Please run configure first.",
            "status_code": 400,
        }
    main_url = conf["url"]

    url = main_url + "/ml-models" + "/" + name
    headers = nd_credentials.credentials_headers()
    headers.update(token_headers())

    response_data = query.get(url, headers)
    return response_data


def predict(name, data):
    """delete model name for logged user.

    :params: model
    :type:   str
    :params: data
    :type:   list[list]
    :returns: ok.
    :rtype: dict
    :raises: none

    >>> from neurodeploy import model
    >>> model.predict(name,data)
    """
    access = nd_config.read_saved_config()
    if "status_code" in access:
        return {
            "message": "Could not predict model. Please run configure first.",
            "status_code": 400,
        }
    user_name = access["username"]
    conf = nd_config.read_saved_config()
    if "url" not in conf:
        return {
            "status_code": 400,
            "message": "Could not read config file. Plase run configure first.",
        }
    main_url = conf["url_api"]
    url = main_url + "/" + user_name + "/" + name
    headers = nd_apikeys.apikeys_headers()
    j = {}
    j["payload"] = data
    response_data = query.post(url, json.dumps(j), headers)
    return response_data
