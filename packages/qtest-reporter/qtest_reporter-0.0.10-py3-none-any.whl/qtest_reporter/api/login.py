"""This module provides a set of APIs to login into qTest"""
from qtest_reporter.requester import get, post
import base64


class Login:
    """Login API"""
    def __init__(self, qtest: object):
        self._host = qtest._host
        self._username = qtest._username
        self._password = qtest._password

    @property
    def token(self):
        """Authenticate the API client against qTest Manager and acquire authorized access token"""
        response = post(
            url=f"{self._host}/oauth/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {str(base64.b64encode(f'{self._username}:'.encode('utf-8')), 'utf-8')}"
            },
            data={
                "grant_type": "password",
                "username": self._username,
                "password": self._password
            })

        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "resopnse": response.json().get('access_token')}
        # If status_code == 200: returns Bearer token string: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

    @property
    def status(self):
        """Gets status of access token"""
        response = get(
            url=f"{self._host}/oauth/status",
            headers={
                "Authorization": f"Bearer {self.token['resopnse']}"
            })

        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "resopnse": response.json()}
        # If status_code == 200: returns dict: "{'expiration': 0, 'validityInMilliseconds': 0}"
