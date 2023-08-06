#!/usr/bin/python
from typing import Union
import requests


def post(
    url: str,
    data: Union[str, dict],
    headers: dict = None,
    files: str = None,
    params: dict = None,
) -> dict:
    try:
        response = requests.post(
            url, data=data, files=files, headers=headers, params=params
        )
    except requests.exceptions.RequestException as e:
        return {"message": "Cant post data", "status_code": 400}
    except Exception as err:
        raise err

    if response.status_code in [200, 201]:
        return {"status_code": 200, **response.json()}
    elif response.status_code in [204]:
        return {"status_code": 200, "message": "post ok"}
    elif not response.ok:
        return {"status_code": 400, **response.json()}
    else:
        return {"status_code": 200, **response.json()}


def get(url, headers=None, params=None):
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code in [200, 201]:
            return {"status_code": 200, **response.json()}
        else:
            return {"status_code": response.status_code, **response.json()}
    except requests.exceptions.RequestException as e:
        return {
            "message": "cant get URL please check config and auth",
            "status_code": 400,
        }


def put(url, headers, params=None, data=None):
    try:
        response = requests.put(url, data=data, headers=headers, params=params)
        if response.status_code in [200, 201]:
            return {"status_code": 200, **response.json()}
        else:
            return {"status_code": response.status_code, **response.json()}
    except requests.exceptions.RequestException as e:
        return {
            "message": "cant put URL please check config and auth",
            "status_code": 400,
        }


def delete(url, headers, params=None):
    try:
        response = requests.delete(url, headers=headers, params=params)
        if response.status_code in [200, 201]:
            return {"status_code": 200, **response.json()}
        else:
            return {"status_code": response.status_code, **response.json()}
    except requests.exceptions.RequestException as e:
        return {
            "message": "cant delete on  URL please check config and auth",
            "status_code": 400,
        }
