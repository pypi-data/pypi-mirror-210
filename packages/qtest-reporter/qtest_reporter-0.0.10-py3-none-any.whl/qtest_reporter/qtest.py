"""This module provides a set of APIs for integration with qTest test case management tool"""
from .api.login import Login


class Qtest:
    """Main qTest class"""
    def __init__(self, host: str, username: str, password: str):
        self._host = host
        self._username = username
        self._password = password
        self._token = Login(self).token['resopnse']
