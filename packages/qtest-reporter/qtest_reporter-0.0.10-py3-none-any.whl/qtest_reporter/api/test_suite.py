"""This module provides a set of Test Suite qTest APIs"""
from qtest_reporter.api.test_cycle import Test_Cycle
from qtest_reporter.logger import Logger
from qtest_reporter.requester import get, post


class Test_Suite:
    """Test Suite API"""
    def __init__(self, qtest: object):
        self._host = qtest._host
        self._token = qtest._token
        self._logger = Logger()._logger

    def get_test_suites(
            self,
            projectId: int,         # ID of the project
            parentCycleId: int = 0, # ID of the Release or Test Cycle which directly contains the Test Suites you are retrieving.
                                    # Input 0 (zero) to get Test Cycles directly under root
            parentType: str = None, # The artifact type of the parent folder. Valid values include release, test-cycle or root
            ):
        """Retrieves Test Suites which are located directly under root or a Release/Test Cycle"""
        response = get(
            url=f"{self._host}/api/v3/projects/{projectId}/test-suites?parentId={parentCycleId}&parentType=test-cycle",
            headers={
                "Authorization": f"Bearer {self._token}"
            },
            params={
                "parentCycleId": parentCycleId,
                "parentType": parentType,
            })

        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "resopnse": response.json()}
        # If status_code == 200: returns list of test suites dicts: [
        # {'links': [
        #   {'rel': 'parent-test-cycle', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<test_cycle_id>'}, 
        #   {'rel': 'test-runs', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs?parentId=<test_suite_id>&parentType=test-suite&includeToscaProperties=false'}, 
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites/<test_suite_id>'}], 
        # 'id': <test_suite_id>, 'name': '<Test Suite Name 1>', 'order': 1, 'pid': 'TS-1', 'created_date': '2023-03-31T10:35:04+00:00', 'last_modified_date': '2023-03-31T16:29:23+00:00', 
        # 'properties': [
        #   {'field_id': -194, 'field_name': 'Planned Start Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
        #   {'field_id': -193, 'field_name': 'Planned End Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
        #   {'field_id': -197, 'field_name': 'Target Release/Build', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': -185, 'field_name': 'Environment', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': -181, 'field_name': 'Assigned To', 'field_value': '[<Assignee_ID>]', 'field_value_name': '[<Assignee_Name>]'}, 
        #   {'field_id': -186, 'field_name': 'Execution Type', 'field_value': '501', 'field_value_name': 'Functional'}, 
        #   {'field_id': -184, 'field_name': 'Description', 'field_value': ''}], 'web_url': 'https://<qtest_url>/p/<project_id>/portal/project#tab=testexecution&object=2&id=<test_suite_id>'}, 

        # {'links': [
        #   {'rel': 'parent-test-cycle', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<test_cycle_id>'}, 
        #   {'rel': 'test-runs', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs?parentId=<test_suite_id>&parentType=test-suite&includeToscaProperties=false'}, 
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites/<test_suite_id>'}], 
        # 'id': <test_suite_id>, 'name': '<Test Suite Name 2>', 'order': 2, 'pid': 'TS-9', 'created_date': '2023-03-31T22:01:07+00:00', 'last_modified_date': '2023-03-31T22:01:07+00:00', 
        # 'properties': [
        #   {'field_id': -194, 'field_name': 'Planned Start Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
        #   {'field_id': -193, 'field_name': 'Planned End Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
        #   {'field_id': -197, 'field_name': 'Target Release/Build', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': -185, 'field_name': 'Environment', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': -181, 'field_name': 'Assigned To', 'field_value': '[<Assignee_ID>]', 'field_value_name': '[<Assignee_Name>]'}, 
        #   {'field_id': -186, 'field_name': 'Execution Type', 'field_value': '503', 'field_value_name': 'Smoke'}, 
        #   {'field_id': -184, 'field_name': 'Description', 'field_value': 'Test Description'}], 'web_url': 'https://<qtest_url>/p/<project_id>/portal/project#tab=testexecution&object=2&id=<test_suite_id>'}]

    def get_a_test_suite_by_id(
            self,
            projectId: int,   # ID of the project
            testSuiteId: int, # ID of the test suite which you want to retrieve
            ):
        """To retrieve a test suite's details using its ID"""
        response = get(
            url=f"{self._host}/api/v3/projects/{projectId}/test-suites/{testSuiteId}",
            headers={
                "Authorization": f"Bearer {self._token}"
            })

        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "resopnse": response.json()}
        # If status_code == 200: returns test suite dict: {'links': [
        #   {'rel': 'parent-test-cycle', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<test_cycle_id>'}, 
        #   {'rel': 'test-runs', 
        #   'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs?parentId=<test_suite_id>&parentType=test-suite&includeToscaProperties=false'}, 
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites/<test_suite_id>'}], 
        # 'id': <test_suite_id>, 'name': '<Test Suite Name>', 'order': 1, 'pid': 'TS-1', 'created_date': '2023-03-31T10:35:04+00:00', 'last_modified_date': '2023-03-31T10:35:29+00:00', 
        # 'properties': [
        #   {'field_id': -194, 'field_name': 'Planned Start Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
        #   {'field_id': -193, 'field_name': 'Planned End Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
        #   {'field_id': -197, 'field_name': 'Target Release/Build', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': -185, 'field_name': 'Environment', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': -181, 'field_name': 'Assigned To', 'field_value': '[<Assignee_ID>]', 'field_value_name': '[<Assignee_Name>]'}, 
        #   {'field_id': -186, 'field_name': 'Execution Type', 'field_value': '503', 'field_value_name': 'Smoke'}, 
        #   {'field_id': -184, 'field_name': 'Description', 'field_value': ''}], 
        #     'web_url': 'https://<qtest_url>/p/<project_id>/portal/project#tab=testexecution&object=2&id=<test_suite_id>'}

    def post_create_test_suite(
            self,
            projectId: int,                 # ID of the project
            testCycleId: int,               # ID of the Release or Test Cycle under which the newly created Test Cycle will be located.
                                            # Use 0 (zero) to create the Test Cycle under the root
            name: str,                      # ID of the Test Cycle which you want to retrieve.
            description: str,               # Description
            execution_type: int = 503,      # Type of test execution (e.g. `Functional`=501, `Regression`=502, `Smoke`=503 etc.)
            parentType: str = "test-cycle", # The artifact type of the parent folder. Valid values include release, test-cycle or root
            ):
        """Verify Test Suite is not present and create it"""
        sts_data = self.get_test_suites(
            projectId=projectId,
            parentCycleId=testCycleId,
        )['resopnse']
        test_suites = []
        for test_suite in sts_data:
            test_suites += [test_suite['name']]
        availability = False
        if not name in test_suites:
            response = post(
                url=f"{self._host}/api/v3/projects/{projectId}/test-suites?parentId={testCycleId}&parentType={parentType}",
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": name,
                    "properties": [ 
                        { "field_id": -184, "field_value": description },
                        { "field_id": -186, "field_name": "Execution Type", "field_value": execution_type}
                     ]
                })
        else:
            root_cycle_name = Test_Cycle(self).get_test_cycle_by_id(
                projectId=projectId,
                testCycleId=testCycleId
                )['resopnse']['name']
            availability = True

        if availability:
            self._logger.warning(
                "\n[%s] test suite already present in root [%s] test cycle."
                "\nHere is a list of all existing test suites: %s!"
                "\nExisted [%s] test suite will be used.", name, root_cycle_name, test_suites, name)
            return {
                "status_code": 200,
                "headers": {},
                "resopnse": sts_data[-1]}
            # If Test Suite already exist - returns just it's object as dict (to get it's ID, for example).
            # That's why status_code and headres are hardcoded, because there was no creation request.
        elif response.status_code == 200:
            self._logger.info("[%s] test suite created!", name)
            return {
                "status_code": response.status_code,
                "headers": response.headers,
                "resopnse": response.json()}
            # If status_code == 200: returns dict: {'links': [
            #   {'rel': 'parent-test-cycle', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<test_cycle_id>'}, 
            #   {'rel': 'test-runs', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs?parentId=<test_suite_id>&parentType=test-suite&includeToscaProperties=false'}, 
            #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites/<test_suite_id>'}], 
            # 'id': <test_suite_id>, 'name': '<Test Suite Name>', 'order': 2, 'pid': 'TS-6', 'created_date': '2023-03-31T17:02:37+00:00', 'last_modified_date': '2023-03-31T17:02:37+00:00', 
            # 'properties': [
            #   {'field_id': -194, 'field_name': 'Planned Start Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
            #   {'field_id': -193, 'field_name': 'Planned End Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
            #   {'field_id': -197, 'field_name': 'Target Release/Build', 'field_value': '', 'field_value_name': ''}, 
            #   {'field_id': -185, 'field_name': 'Environment', 'field_value': '', 'field_value_name': ''}, 
            #   {'field_id': -181, 'field_name': 'Assigned To', 'field_value': '[<User ID>]', 'field_value_name': '[qTest Bot]'}, 
            #   {'field_id': -186, 'field_name': 'Execution Type', 'field_value': '502', 'field_value_name': 'Regression'}, 
            #   {'field_id': -184, 'field_name': 'Description', 'field_value': '<Test Description>'}], 'web_url': 'https://<qtest_url>/p/<project_id>/portal/project#tab=testexecution&object=2&id=<test_suite_id>'}
        else:
            return {
                "status_code": response.status_code,
                "headers": response.headers,
                "resopnse": response.json()}
