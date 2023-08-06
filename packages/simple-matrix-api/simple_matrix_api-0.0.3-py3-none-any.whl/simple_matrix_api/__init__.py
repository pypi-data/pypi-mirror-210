# SPDX-FileCopyrightText: 2023-present Filip Strajnar <filip.strajnar@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Union
import requests
from simple_matrix_api.client import Client


def _get_base_url(server_name: str) -> Union[str, None]:
    base_url: str = requests.get(
        f"https://{server_name}/.well-known/matrix/client").json(
        )["m.homeserver"]["base_url"]
    versions: list[str] = requests.get(
        f"{base_url}/_matrix/client/versions").json()["versions"]
    valid_url: bool = len(versions) > 0
    return base_url if valid_url else None


def login(user: str,
          password: str,
          server_url: str = "matrix.org") -> Union[Client, None]:
    """
    Returns None if proper URL was not found.
    
    Returns client object if login was successful
    """
    url = _get_base_url(server_url)
    if (url != None):
        login_body = {
            "type": "m.login.password",
            "identifier": {
                "type": "m.id.user",
                "user": user
            },
            "password": password
        }
        access_token: str = requests.post(
            f"{url}/_matrix/client/v3/login",
            json=login_body).json()["access_token"]
        return Client(url, access_token)
    else:
        return None
