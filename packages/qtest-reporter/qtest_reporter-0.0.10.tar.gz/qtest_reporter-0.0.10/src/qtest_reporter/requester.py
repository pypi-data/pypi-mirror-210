"""This module provides a set of APIs for integration with qTest test case management tool."""
import requests

def get(url: str, headers: str = None, params: dict = None):
    return requests.get(url=url, headers=headers, params=params)

def post(url: str, headers: dict, params: dict = None, data: dict = None, json: dict = None):
    return requests.post(url=url, headers=headers, params=params, data=data, json=json)
