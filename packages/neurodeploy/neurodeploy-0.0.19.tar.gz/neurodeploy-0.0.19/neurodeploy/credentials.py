from utils import query
from process import nd_credentials
from process import nd_config
from process.nd_token import token_headers


def get():
    """get user credentials.

    :params: none
    :type:   none
    :returns: json of credentials.
    :rtype: dict
    :raises: none

    >>> from neurodeploy import credentials
    >>> credentials.get()
    """

    conf = nd_config.read_saved_config()
    if "url" not in conf:
        return {
            "status_code": 400,
            "message": "Could not read config file. Plase run configure first.",
        }
    main_url = conf["url"]
    url = main_url + "/credentials"
    headers = nd_credentials.credentials_headers()
    headers.update(token_headers())

    response_data = query.get(url, headers)

    return response_data


def create(name, description):
    """create user credentials.
    :params: name
    :type:   str
    :params: description
    :type:   str
    :returns: creation message.
    :rtype: dict
    :raises: none

    >>> from neurodeploy import credentials
    >>> credentials.create(name,description)
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
    url = main_url + "/credentials"
    headers = {}
    headers.update(token_headers())
    headers["credentials_name"] = name
    headers["description"] = description
    data = None
    response_data = query.post(url, data, headers)
    return response_data


def delete(name):
    """delete user credentials.

    :params: name
    :type:   str
    :returns: message deleted string
    :rtype: dict
    :raises: none

    >>> from neurodeploy import credentials
    >>> credentials.delete('model_name')
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
    url = main_url + "/credentials" + "/" + name
    headers = nd_credentials.credentials_headers()
    headers.update(token_headers())
    response_data = query.delete(url, headers)

    return response_data
