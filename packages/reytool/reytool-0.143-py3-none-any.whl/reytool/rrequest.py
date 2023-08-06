# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-08 11:07:25
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Request methods.
"""


from typing import List, Tuple, Dict, Literal, Optional, Union
from os.path import abspath as os_path_abspath
from requests.api import request as requests_request
from requests.models import Response
from filetype import guess as filetype_guess

from .rfile import read_file
from .rregular import re_searches


def url_join(url: str, params: Dict) -> str:
    """
    Join `URL` and `parameters`.

    Parameters
    ----------
    url : URL.
    params : Parameters of URL.

    Returns
    -------
    Joined URL.
    """

    # Join parameters.
    params_str = "&".join(
        [
            "%s=%s" % (key, val)
            for key, val in params.items()
        ]
    )

    # Join URL.
    if "?" not in url:
        url += "?"
    elif url[-1] != "?":
        url += "&"
    url += params_str

    return url


def url_split(url: str) -> Tuple[str, Dict[str, str]]:
    """
    Split `URL` and `parameters`.

    Parameters
    ----------
    url : URL.

    Returns
    -------
    Split URL and parameters.
    """

    # Split URL.
    url, params_str = url.rsplit("?", 1)

    # Split parameters.
    params = {
        key: val
        for key, val in map(
            lambda item: item.split("=", 1),
            params_str.split("&")
        )
    }

    return url, params


def cookie_join(params: Dict[str, str]) -> str:
    """
    Join parameters of `Cookie`.

    Parameters
    ----------
    params : Parameters.

    Returns
    -------
    Joined cookie.
    """

    # Join.
    cookie = "; ".join(
        [
            "%s=%s" % (key, val)
            for key, val in params.items()
        ]
    )

    return cookie


def cookie_split(cookie: str) -> Dict[str, str]:
    """
    Split parameters of `Cookie`.

    Parameters
    ----------
    cookie : Cookie.

    Returns
    -------
    Split parameters
    """

    # Split parameters.
    params = {
        key: val
        for key, val in map(
            lambda item: item.split("=", 1),
            cookie.split("; ")
        )
    }

    return params


def content_type(file: Union[str, bytes]) -> str:
    """
    Guess HTTP content type of file.

    Parameters
    ----------
    file : File path or bytes data.

    Returns
    -------
    HTTP content type.
    """

    # Guess.
    file_obj = filetype_guess(file)
    if not file_obj is None:
        return file_obj.MIME


def request(
    url: str,
    params: Optional[Dict] = None,
    data: Optional[Dict] = None,
    json: Optional[Dict] = None,
    files: Optional[Dict[str, Union[str, bytes]]] = None,
    headers: Optional[Dict] = None,
    timeout: Optional[Union[int, float]] = None,
    proxies: Optional[Dict[str, str]] = None,
    method: Optional[Literal["get", "post", "put", "patch", "delete"]] = None,
    throw_e: bool = False
    ) -> Response:
    """
    `Send` request.

    Parameters
    ----------
    url : Request URL.
    params : Request parameters.
    data : Request body data, in `application/x-www-form-urlencoded` format.
    json : Request body data, in `application/json` format.
    files : Request body data, in `multipart/form-data; boundary=random code` format.
        Key is parameter name and file name, value is file path or bytes data.

    headers : Request header data.
    timeout : Request maximun waiting time.
        - `None` : No limit.
        - `Union[int, float]` : Use this value.

    proxies : Proxy IP setup.
        - `None` : No setup.
        - `Dict[str, str]` : Name and use IP of each protocol.

    method : Request method.
        - `None` : Automatic judge.
            * When parameter `data` or `json` or `files` not has value, then request method is `get`.
            * When parameter `data` or `json` or `files` has value, then request method is `post`.
        - `Literal['get', 'post', 'put', 'patch', 'delete']` : Use this request method.

    throw_e : Whether throw `exception`, when response code is not `200`.

    Returns
    -------
    Response object of requests package.
    """

    # Handle parameters.
    if method is None:
        if data is None and json is None and files is None:
            method = "get"
        else:
            method = "post"
    if not files is None:
        for key, val in files.items():
            file_type = content_type(val)
            if val.__class__ == str:
                file_data = read_file(val)
            else:
                file_data = val
            if file_type is None:
                info = (key, file_data)
            else:
                info = (key, file_data, file_type)
            files[key] = info

    # Request.
    response = requests_request(
        method,
        url,
        params=params,
        data=data,
        json=json,
        files=files,
        headers=headers,
        timeout=timeout,
        proxies=proxies,
        )

    # Set encod type.
    if response.encoding == "ISO-8859-1":
        response.encoding = "utf-8"

    # Throw exception.
    assert not (throw_e and response.status_code != 200), "response code is not 200"

    return response


def download(url: str, path: Optional[str] = None) -> str:
    """
    `Download` file from URL.

    Parameters
    ----------
    url : Download URL.
    path : Save path.
        - `None` : File name is `download` and auto judge file type.

    Returns
    -------
    File absolute path.
    """

    # Download.
    response = request(url)
    content = response.content

    # Judge file type and path.
    if path is None:
        headers = response.headers
        content_type = headers["Content-Type"]
        pattern = "^[^/]*/([^;\s]+).*$"
        result = re_searches(content_type, pattern)
        if not result is None:
            path = "download." + result[0]
        else:
            path = "download"
        path = os_path_abspath(path)

    # Save.
    with open(path, "wb") as file:
        file.write(content)

    return path