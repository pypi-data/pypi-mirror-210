"""This module provides a set of Test Run qTest APIs"""
from qtest_reporter.api.test_case import Test_Case
from qtest_reporter.api.test_suite import Test_Suite
from qtest_reporter.logger import Logger
from qtest_reporter.requester import get, post


class Test_Run:
    """Test Run API"""
    def __init__(self, qtest: object):
        self._host = qtest._host
        self._token = qtest._token
        self._logger = Logger()._logger

    def get_test_runs(
            self,
            projectId: int,         # ID of the project
            parentSuiteId: int = 0, # The ID of the parent test suite
            ):
        """To retrieve all Test Runs under root or under a container (Release, Test Cycle or Test Suite)"""
        response = get(
            url=f"{self._host}/api/v3/projects/{projectId}/test-runs?parentId={parentSuiteId}&parentType=test-suite",
            headers={
                "Authorization": f"Bearer {self._token}"
            })

        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "resopnse": response.json()}
        # If status_code == 200: returns dict with a list of test runs dicts: {'links': [], 'page': 1, 'page_size': 100, 'total': 3, 'items': [

        # {'parentId': <parent_suite_ID_1>, 'parentType': 'test-suite', 'automation': 'No', 'testCaseId': <test_case_id>, 'links': [
        #   {'rel': 'test-case', 
        #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<test_case_id>?versionId=<version_id>&showParamIdentifier=false'}, 
        #   {'rel': 'test-cycle', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<test_cycle_id>'}, 
        #   {'rel': 'test-suite', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites/<parent_suite_ID_1>'}, 
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs/<test_run_id>'}], 
        #       'id': <test_run_id>, 
        #       'name': '<Test Run Name 1>', 
        #       'order': 1, 
        #       'pid': 'TR-<Test Run Number>', 
        #       'created_date': '2023-04-03T14:34:18+00:00', 
        #       'last_modified_date': '2023-04-03T14:34:18+00:00', 
        # 'properties': [
        #   {'field_id': 2623, 'field_name': 'Run Order', 'field_value': '1'}, 
        #   {'field_id': 168, 'field_name': 'Execution Type', 'field_value': '503', 'field_value_name': 'Smoke'}, 
        #   {'field_id': 175, 'field_name': 'Planned Start Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
        #   {'field_id': 172, 'field_name': 'Environment', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': 171, 'field_name': 'Planned End Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
        #   {'field_id': 176, 'field_name': 'Target Release/Build', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': 164, 'field_name': 'Assigned To', 'field_value': '<Assignee_ID>', 'field_value_name': '<Assignee_Name>'}, 
        #   {'field_id': 180, 'field_name': 'Status', 'field_value': '605', 'field_value_name': 'Unexecuted'}, 
        #   {'field_id': 167, 'field_name': 'Priority', 'field_value': '723', 'field_value_name': 'Medium'}], '
        # test_case': {'links': [], 'id': <test_case_id>}, 'test_case_version_id': <tc_version_id>, 'test_case_version': '0.7', 'creator_id': <User ID>}]}, 

        # ...

        # {'parentId': <parent_suite_ID_2>, 'parentType': 'test-suite', 'automation': 'No', 'testCaseId': <test_case_id>, 'links': [
        #   {'rel': 'test-case', 
        #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<test_case_id>?versionId=<version_id>&showParamIdentifier=false'}, 
        #   {'rel': 'test-cycle', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<test_cycle_id>'}, 
        #   {'rel': 'test-suite', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites/<parent_suite_ID_3>'}, 
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs/<test_run_id>'}], 
        #       'id': <test_run_id>, 
        #       'name': '<Test Run Name 2>', 
        #       'order': 3, 
        #       'pid': 'TR-<Test Run Number>', 
        #       'created_date': '2023-04-04T21:09:54+00:00', 
        #       'last_modified_date': '2023-04-04T21:09:54+00:00', 
        # 'properties': [
        #   {'field_id': 2623, 'field_name': 'Run Order', 'field_value': '3'}, 
        #   {'field_id': 168, 'field_name': 'Execution Type', 'field_value': '501', 'field_value_name': 'Functional'}, 
        #   {'field_id': 175, 'field_name': 'Planned Start Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
        #   {'field_id': 172, 'field_name': 'Environment', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': 171, 'field_name': 'Planned End Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
        #   {'field_id': 176, 'field_name': 'Target Release/Build', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': 164, 'field_name': 'Assigned To', 'field_value': '<Assignee_ID>', 'field_value_name': '<Assignee_Name>'}, 
        #   {'field_id': 180, 'field_name': 'Status', 'field_value': '605', 'field_value_name': 'Unexecuted'}, 
        #   {'field_id': 167, 'field_name': 'Priority', 'field_value': '723', 'field_value_name': 'Medium'}], 
        # 'test_case': {'links': [], 'id': <test_case_id>}, 'test_case_version_id': <tc_version_id>, 'test_case_version': '0.3', 'creator_id': <User ID>}
        # ]}

    def get_test_run_by_id(
            self,
            projectId: int, # ID of the project
            testRunId: int, # ID of the test run
            ):
        """To retrieve a Test Run. You can optionally retrieve the associated Test Case and its Test Steps"""
        response = get(
            url=f"{self._host}/api/v3/projects/{projectId}/test-runs/{testRunId}",
            headers={
                "Authorization": f"Bearer {self._token}"
            })

        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "resopnse": response.json()}
        # If status_code == 200: returns test run dict: {'links': [], 'page': 1, 'page_size': 100, 'total': 1, 
        #   'items': [{'parentId': <parent_suite_ID>, 'parentType': 'test-suite', 'automation': 'No', 'testCaseId': <test_case_id>, 'links': [
        #       {'rel': 'test-case', 
        #        'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<test_case_id>?versionId=<version_id>&showParamIdentifier=false'}, 
        #       {'rel': 'test-cycle', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<test_cycle_id>'}, 
        #       {'rel': 'test-suite', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites/<test_suite_id>'}, 
        #       {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs/<test_run_id>'}], 
        #   'id': <test_run_id>, 
        #   'name': '<Test Run Name>', 
        #   'order': 1, 
        #   'pid': 'TR-<Test Run Number>', 
        #   'created_date': '2023-04-03T14:34:18+00:00', 
        #   'last_modified_date': '2023-04-03T14:34:18+00:00', 
        # 'properties': [
        #   {'field_id': 2623, 'field_name': 'Run Order', 'field_value': '1'}, 
        #   {'field_id': 168, 'field_name': 'Execution Type', 'field_value': '503', 'field_value_name': 'Smoke'}, 
        #   {'field_id': 175, 'field_name': 'Planned Start Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
        #   {'field_id': 172, 'field_name': 'Environment', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': 171, 'field_name': 'Planned End Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
        #   {'field_id': 176, 'field_name': 'Target Release/Build', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': 164, 'field_name': 'Assigned To', 'field_value': '<Assignee_ID>', 'field_value_name': '<Assignee_Name>'}, 
        #   {'field_id': 180, 'field_name': 'Status', 'field_value': '605', 'field_value_name': 'Unexecuted'}, 
        #   {'field_id': 167, 'field_name': 'Priority', 'field_value': '723', 'field_value_name': 'Medium'}], '
        # test_case': {'links': [], 'id': <test_case_id>}, 'test_case_version_id': <tc_version_id>, 'test_case_version': '0.7', 'creator_id': <User ID>}]}

    def post_add_new_test_run(
            self,
            projectId: int,     # ID of the project
            parentSuiteId: int, # The ID of the parent test suite
            testCaseId: int,    # Test Case ID
            ):
        """To create a Test Run under root or a container (Release, Test Cycle or Test Suite)"""
        test_case_name = Test_Case(self).get_test_case_by_id(
            projectId=projectId,
            testCaseId=testCaseId
        )['resopnse']['name']
        tstr_data = self.get_test_runs(
            projectId=projectId,
            parentSuiteId=parentSuiteId,
        )
        test_suite_name = Test_Suite(self).get_a_test_suite_by_id(
                projectId=projectId,
                testSuiteId=parentSuiteId
                )['resopnse']['name']
        test_runs = []
        for test_run in tstr_data['resopnse']['items']:
            test_runs += [test_run['name']]
        availability = False
        if not test_case_name in test_runs:
            response = post(
                url=f"{self._host}/api/v3/projects/{projectId}/test-runs?parentId={parentSuiteId}&parentType=test-suite",
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": test_case_name,
                    "test_case": {"id": testCaseId}
                })
        else:
            availability = True

        if availability:
            self._logger.warning(
                "\n[%s] test run already present in [%s] test suite."
                "\nHere is a list of all existing test runs: %s!"
                "\nExisted [%s] test run will be used.", test_case_name, test_suite_name, test_runs, test_case_name)
            return {
                "status_code": 200,
                "headers": {},
                "resopnse": tstr_data['resopnse']['items'][0]}
            # If Test Run already exist - returns just it's object as dict (to get it's ID, for example).
            # That's why status_code and headres are hardcoded, because there was no creation request.
        elif response.status_code == 201:
            self._logger.info("[%s] test run was successfully added to [%s] test suite!", test_case_name, test_suite_name)
            return {
                "status_code": response.status_code,
                "headers": response.headers,
                "resopnse": response.json()}
            # If status_code == 201: returns dict: {
            #   'testCaseId': <test_case_id>, 
            #   'links': [
            #       {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs/<test_run_id>'}], 
            #   'id': <test_run_id>, 
            #   'name': '<Test Run Name>', 
            #   'order': 6, 
            #   'pid': 'TR-<Test Run Number>', 
            #   'created_date': '2023-05-03T17:22:04+00:00', 
            #   'last_modified_date': '2023-05-03T17:22:04+00:00', 
            # 'properties': [
            #   {'field_id': 2623, 'field_name': 'Run Order', 'field_value': '6'}, 
            #   {'field_id': 168, 'field_name': 'Execution Type', 'field_value': '501', 'field_value_name': 'Functional'}, 
            #   {'field_id': 175, 'field_name': 'Planned Start Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
            #   {'field_id': 172, 'field_name': 'Environment', 'field_value': '', 'field_value_name': ''}, 
            #   {'field_id': 171, 'field_name': 'Planned End Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
            #   {'field_id': 176, 'field_name': 'Target Release/Build', 'field_value': '', 'field_value_name': ''}, 
            #   {'field_id': 164, 'field_name': 'Assigned To', 'field_value': '<Assignee_ID>', 'field_value_name': '<Assignee_Name>'}, 
            #   {'field_id': 180, 'field_name': 'Status', 'field_value': '605', 'field_value_name': 'Unexecuted'}, 
            #   {'field_id': 167, 'field_name': 'Priority', 'field_value': '723', 'field_value_name': 'Medium'}], 
            # 'test_case': {'links': [], 'id': <test_case_id>}, 'test_case_version_id': <tc_version_id>, 'creator_id': <User ID>}
        else:
            return {
                "status_code": response.status_code,
                "headers": response.headers,
                "resopnse": response.json()}
