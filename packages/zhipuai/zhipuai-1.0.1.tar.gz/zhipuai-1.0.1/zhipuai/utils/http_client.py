# -*- coding:utf-8 -*-
import json
import logging

import requests
from requests import exceptions

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=UTF-8",
}


def post(api_url, token, params, timeout=300):
    try:
        headers.update({"Authorization": token})
        resp = requests.post(
            url=api_url, data=json.dumps(params), headers=headers, timeout=timeout
        )
        if requests.codes.ok == resp.status_code:
            return resp.text
    except exceptions.Timeout as e:
        logging.exception("请求超时", e)
    except exceptions.ConnectionError as e:
        logging.exception("请求连接错误", e)
    except exceptions.HTTPError as e:
        logging.exception("http请求错误", e)


def stream(api_url, token, params, timeout=300):
    try:
        resp = requests.post(
            api_url,
            stream=True,
            headers={"Authorization": token},
            json=params,
            timeout=timeout,
        )
        if requests.codes.ok == resp.status_code:
            return resp
    except exceptions.Timeout as e:
        logging.exception("请求超时", e)
    except exceptions.ConnectionError as e:
        logging.exception("请求连接错误", e)
    except exceptions.HTTPError as e:
        logging.exception("http请求错误", e)


def get(api_url, token):
    try:
        headers.update({"Authorization": token})
        resp = requests.get(api_url, headers=headers)
        if requests.codes.ok == resp.status_code:
            return resp.text
    except exceptions.ConnectionError as e:
        logging.exception("请求连接错误", e)
    except exceptions.HTTPError as e:
        logging.exception("http请求错误", e)
