# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-08 11:07:25
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Request methods.
"""


from typing import List, Tuple, Dict, Literal, Optional, Union
from os.path import abspath as os_abspath, basename as os_basename
from urllib.parse import urlsplit as urllib_urlsplit
from requests.api import request as requests_request
from requests.models import Response
from filetype import guess as filetype_guess

from .rfile import read_file
from .rregular import re_search


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
    split_result = urllib_urlsplit(url)
    params_str = split_result.query
    url = split_result.scheme + "://" + split_result.netloc + split_result.path

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
    Guess HTTP `content type` of file.

    Parameters
    ----------
    file : File path or bytes data.

    Returns
    -------
    HTTP content type.
    """

    # Guess.
    file_type_obj = filetype_guess(file)
    if not file_type_obj is None:
        return file_type_obj.MIME


def request(
    url: str,
    params: Optional[Dict] = None,
    data: Optional[Union[Dict, str, bytes]] = None,
    json: Optional[Dict] = None,
    files: Optional[Dict[str, Union[str, bytes, Tuple[Union[str, bytes], dict]]]] = None,
    headers: Dict = {},
    timeout: Optional[float] = None,
    proxies: Dict[str, str] = {},
    method: Optional[Literal["get", "post", "put", "patch", "delete"]] = None,
    throw_e: bool = False
    ) -> Response:
    """
    `Send` request.

    Parameters
    ----------
    url : Request URL.
    params : Request URL add parameters.
    data : Request body data.
        - `Dict` : Convert to `key=value&...` format bytes.
            Auto set `Content-Type` to `application/x-www-form-urlencoded`.
        - `str` : File path to read file bytes data.
            Auto set `Content-Type` to file media type, and `filename` to file name.
        - `bytes` : File bytes data.
            Auto set `Content-Type` to file media type.

    json : Request body data, convert to `JSON` format.
        Auto set `Content-Type` to `application/json`.
    files : Request body data, convert to `multi form` format.
        Auto set `Content-Type` to `multipart/form-data`.
        - `Dict[str, str]` : Parameter name and File path to read file bytes data.
            Auto set `Content-Type` to file media type, and `filename` to file name.
        - `Dict[str, bytes]` : Parameter name and file bytes data.
        - `Dict[str, Tuple[str, dict]` : Parameter name and File path to read file bytes data and other parameters.
            Auto set `Content-Type` to file media type, and `filename` to file name.
        - `Dict[str, Tuple[bytes, dict]` : Parameter name and file bytes data and other parameters.

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
    if files is None:
        if data.__class__ == str:
            if "Content-Disposition" not in headers:
                file_name = os_basename(data)
                headers["Content-Disposition"] = "attachment; filename=%s" % file_name
            data = read_file(data)
        if data.__class__ == bytes:
            if "Content-Type" not in headers:
                headers["Content-Type"] = content_type(data)
    else:
        for key, val in files.items():
            if val.__class__ == tuple:
                item_data, item_headers = val
            else:
                item_data, item_headers = val, {}
            if item_data.__class__ == str:
                if "filename" not in item_headers:
                    item_headers["filename"] = os_basename(item_data)
                item_data = read_file(item_data)
            if item_data.__class__ == bytes:
                if "Content-Type" not in item_headers:
                    item_headers["Content-Type"] = content_type(item_data)
            files[key] = item_headers.get("filename", key), item_data, item_headers.get("Content-Type"), item_headers

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
        Content_disposition = response.headers.get("Content-Disposition", "")
        if "filename" in Content_disposition:
            file_name = re_search(
                "filename=['\"]?([^\s'\"]+)",
                Content_disposition
            )
        else:
            file_name = None
        if file_name is None:
            file_type_obj = filetype_guess(content)
            if not file_type_obj is None:
                file_name = "download." + file_type_obj.EXTENSION
        if file_name is None:
            file_name = "download"
        path = os_abspath(file_name)

    # Save.
    with open(path, "wb") as file:
        file.write(content)

    return path