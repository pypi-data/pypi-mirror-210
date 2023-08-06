from utils import query
from process import nd_credentials
from process import nd_config
from process.nd_token import token_headers


def get():
    """get user apikeys.

    :params: none
    :type:   none
    :returns: json of apikeys.
    :rtype: dict
    :raises: none

    >>> from neurodeploy import apikeys
    >>> apikeys.get()
    """

    conf = nd_config.read_saved_config()
    if "url" not in conf:
        return {
            "status_code": 400,
            "message": "Could not read config file. Plase run configure first.",
        }
    main_url = conf["url"]
    url = main_url + "/api-keys"
    headers = nd_credentials.credentials_headers()
    headers.update(token_headers())

    response_data = query.get(url, headers)

    return response_data


def create(description, model_name=None, expires_after=None):
    """create user apikeys.
    :params: description
    :type:   str
    :params:  model_name
    :type:   str
    :returns: creation message.
    :rtype: dict
    :raises: none

    >>> from neurodeploy import apikeys
    >>> apikeys.create(description,expires_after,model_name)
    """
    conf = nd_config.read_saved_config()
    if "url" not in conf:
        return {
            "status_code": 400,
            "message": "Could not read config file. Plase run configure first.",
        }
    if "status_code" in conf:
        return {
            "message": "Could not create credentials. Please run configure first.",
            "status_code": 400,
        }
    main_url = conf["url"]
    url = main_url + "/api-keys"
    params = {}
    params["model_name"] = model_name
    params["description"] = description
    params["expires_after"] = expires_after

    headers = {}
    headers.update(token_headers())
    data = None
    response_data = query.post(url, data, headers, None, params)
    return response_data


def delete(api_key):
    """delete user apikeys.

    :params: name
    :type:   str
    :returns: message deleted string
    :rtype: dict
    :raises: none

    >>> from neurodeploy import apikeys
    >>> apikeys.delete('api_key')
    """
    conf = nd_config.read_saved_config()
    if "url" not in conf:
        return {
            "status_code": 400,
            "message": "Could not read config file. Plase run configure first.",
        }
    if "status_code" in conf:
        return {
            "message": "Could not delete credentials. Please run configure first.",
            "status_code": 400,
        }

    main_url = conf["url"]
    url = main_url + "/api-keys" + "/" + api_key
    headers = nd_credentials.credentials_headers()
    headers.update(token_headers())
    response_data = query.delete(url, headers)

    return response_data
