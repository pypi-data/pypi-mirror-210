"""This module provides a set of qTest user profile APIs"""
from qtest_reporter.requester import get


class Project:
    """Project API"""
    def __init__(self, qtest: object):
        self._host = qtest._host
        self._token = qtest._token

    def get_projects(self, user_id: str, assigned: bool = True, page: int = None, pageSize: int = 100):
        """Retrieves all Projects which the requested qTest Manager account can access to"""
        response = get(
            url=f"{self._host}/api/v3/projects",
            headers={
                "Authorization": f"Bearer {self._token}"
            },
            params={
                "expand": user_id,
                "assigned": assigned,
                "page": page,
                "pageSize": pageSize
            })

        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "resopnse": response.json()}
        # If status_code == 200: returns list of user projects dicts: [
        # {'links': [
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>'}, 
        #   {'rel': 'releases', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/releases'}, 
        #   {'rel': 'test-cycles', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles'}, 
        #   {'rel': 'test-suites', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites'}, 
        #   {'rel': 'test-runs', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs?includeToscaProperties=false'}, 
        #   {'rel': 'test-cases', 
        #   'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases?page=0&size=0&expandProps=false&expandSteps=false&showParamIdentifier=false'}], 
        # 'id': <project_id>, 'name': '<Project name>', 'description': '', 'status_id': <status_id>, 'start_date': '2016-05-12T00:00:00+00:00', 'sample': False, 'defect_tracking_systems': [], 'x_explorer_access_level': <access_level_number>, 'date_format': 'MM/dd/yyyy', 'automation': True, 'uuid': ''}, 

        # ...

        # {'links': [
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>'}, 
        #   {'rel': 'releases', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/releases'}, 
        #   {'rel': 'test-cycles', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles'}, 
        #   {'rel': 'test-suites', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites'}, 
        #   {'rel': 'test-runs', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs?includeToscaProperties=false'}, 
        #   {'rel': 'test-cases', 
        #   'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases?page=0&size=0&expandProps=false&expandSteps=false&showParamIdentifier=false'}], 
        # 'id': <project_id>, 'name': '<Project name>', 'description': '', 'status_id': <status_id>, 'start_date': '2016-05-12T00:00:00+00:00', 'sample': False, 'defect_tracking_systems': [], 'x_explorer_access_level': <access_level_number>, 'date_format': 'MM/dd/yyyy', 'automation': True, 'uuid': ''}]
