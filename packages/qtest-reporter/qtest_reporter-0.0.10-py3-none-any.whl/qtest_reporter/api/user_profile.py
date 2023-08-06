"""This module provides a set of qTest user profile APIs"""
from qtest_reporter.requester import get


class User_Profile:
    """User Profile API"""
    def __init__(self, qtest: object):
        self._host = qtest._host
        self._username = qtest._username
        self._password = qtest._password
        self._token = qtest._token

    @property
    def current_user_admin_profile(self):
        """Retrieves your Admin Profile"""
        response = get(
            url=f"{self._host}/api/v3/admin-profiles/current",
            headers={
                "Authorization": f"Bearer {self._token}"
            })

        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "resopnse": response.json()}
        # If status_code == 200: returns dict: {
        #   'user_id': <user_id>, 
        #   'create_project': False, 
        #   'edit_project': False, 
        #   'archive_project': False, 
        #   'list_project': False, 
        #   'manage_client_user': False, 
        #   'edit_user_profile': False, 
        #   'view_user_profile': False, 
        #   'manage_client_info': False, 
        #   'manage_system_conf': False, 
        #   'site_level_field': False, 
        #   'manage_user_group': False, 
        #   'insight_viewer': False, 
        #   'insight_editor': False, 
        #   'pulse_access': False, 
        #   'launch_access': False, 
        #   'analytics_viewer': True
        # }
