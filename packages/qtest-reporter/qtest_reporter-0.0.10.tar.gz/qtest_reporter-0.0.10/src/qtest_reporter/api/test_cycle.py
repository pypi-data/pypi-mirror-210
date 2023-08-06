"""This module provides a set of Test Cycle qTest APIs"""
from qtest_reporter.logger import Logger
from qtest_reporter.requester import get, post


class Test_Cycle:
    """Test Cycle API"""
    def __init__(self, qtest: object):
        self._host = qtest._host
        self._token = qtest._token
        self._logger = Logger()._logger

    def get_project_test_cycles(
            self,
            projectId: int,         # ID of the project
            parentId: int = 0,      # ID of the Release or Test Cycle which directly contains the Test Cycles you are retrieving.
                                    # Input 0 (zero) to get Test Cycles directly under root
            parentType: str = None, # The artifact type of the parent folder. Valid values include release, test-cycle or root
            expand: str = None,     # Specify expand=descendants to retrieve the Test Cycles’ sub and grand-sub Cycles/Suites
            tosca: bool = False,
            page: int = None,
            pageSize: int = 100
            ):
        """Retrieves Test Cycles which are located directly under project root"""
        response = get(
            url=f"{self._host}/api/v3/projects/{projectId}/test-cycles",
            headers={
                "Authorization": f"Bearer {self._token}"
            },
            params={
                "parentId": parentId,
                "parentType": parentType,
                "expand": expand,
                "tosca": tosca,
                "page": page,
                "pageSize": pageSize,
            })

        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "resopnse": response.json()}
        # If status_code == 200: returns list: [{'links': [
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<test_cycle_id>'}, 
        #   {'rel': 'test-suites', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites?parentId=<test_cycle_id>&parentType=test-cycle'}, 
        #   {'rel': 'test-runs', 
        #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs?parentId=<test_cycle_id>&parentType=test-cycle&includeToscaProperties=false'}], 
        # 'id': <test_cycle_id>, 
        # 'name': '<Test Cycle Name>', 
        # 'order': 1, 
        # 'pid': 'CL-1', 
        # 'created_date': '2020-07-28T12:15:10+00:00', 
        # 'last_modified_date': '2020-07-28T12:15:17+00:00', 
        # 'web_url': 'https://<qtest_url>/p/<project_id>/portal/project#tab=testexecution&object=<project_id>&id=<test_cycle_id>', 
        # 'test-cycles': []}]

    def get_test_cycle_by_id(
            self,
            projectId: int,     # ID of the project
            testCycleId: int,   # ID of the Test Cycle which you want to retrieve.
            expand: str = None, # Specify expand=descendants to retrieve the Test Cycles’ sub and grand-sub Cycles/Suites
            ):
        """Retrieves a Test Cycle by ID"""
        response = get(
            url=f"{self._host}/api/v3/projects/{projectId}/test-cycles/{testCycleId}",
            headers={
                "Authorization": f"Bearer {self._token}"
            },
            params={
                "expand": expand
            })

        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "resopnse": response.json()}
        # If status_code == 200: returns dict: {'links': [
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<test_cycle_id>'}, 
        #   {'rel': 'test-suites', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites?parentId=<test_cycle_id>&parentType=test-cycle'}, 
        #   {'rel': 'test-runs', 
        #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs?parentId=<test_cycle_id>&parentType=test-cycle&includeToscaProperties=false'}], 
        # 'id': <test_cycle_id>, 
        # 'name': '<Test Cycle Name>', 
        # 'order': 1, 
        # 'pid': 'CL-1', 
        # 'created_date': '2020-07-28T12:15:10+00:00', 
        # 'last_modified_date': '2020-07-28T12:15:17+00:00', 
        # 'web_url': 'https://<qtest_url>/p/<project_id>/portal/project#tab=testexecution&object=<project_id>&id=<test_cycle_id>', 
        # 'test-cycles': []}

    def get_sub_test_cycles(
            self,
            projectId: int,                 # ID of the project
            parentCycleId: int,             # ID of the Test Cycle which you want to retrieve.
            parentType: str = "test-cycle", # Input test-cycle
            expand: str = None,             # Specify expand=descendants to retrieve the Test Cycles’ sub and grand-sub Cycles/Suites
            ):
        """Retrieves all test cycles under a specific parent test cycle"""
        response = get(
            url=f"{self._host}/api/v3/projects/{projectId}/test-cycles?parentId={parentCycleId}",
            headers={
                "Authorization": f"Bearer {self._token}"
            },
            params={
                "parentType": parentType,
                "expand": expand
            })

        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "resopnse": response.json()}
        # If status_code == 200: returns list: [
        # {'links': [
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<sub_test_cycle_1>'}, 
        #   {'rel': 'parent-test-cycle', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<test_cycle_id>'}, 
        #   {'rel': 'test-suites', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites?parentId=<sub_test_cycle_1>&parentType=test-cycle'}, 
        #   {'rel': 'test-runs', 
        #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs?parentId=<sub_test_cycle_1>&parentType=test-cycle&includeToscaProperties=false'}], 
        # 'id': <sub_test_cycle_1>, 
        # 'name': '<Sub Test Cycle Name>', 
        # 'order': 3, 
        # 'pid': 'CL-12', 
        # 'created_date': '2021-07-11T16:57:17+00:00', 
        # 'last_modified_date': '2021-07-12T16:01:38+00:00', 
        # 'web_url': 'https://<qtest_url>/p/<project_id>/portal/project#tab=testexecution&object=<project_id>&id=<sub_test_cycle_1>', 
        # 'test-cycles': []}, 

        # {'links': [
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<sub_test_cycle_2>'}, 
        #   {'rel': 'parent-test-cycle', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<test_cycle_id>'}, 
        #   {'rel': 'test-suites', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites?parentId=<sub_test_cycle_2>&parentType=test-cycle'}, 
        #   {'rel': 'test-runs', 
        #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs?parentId=<sub_test_cycle_2>&parentType=test-cycle&includeToscaProperties=false'}], 
        # 'id': <sub_test_cycle_2>, 
        # 'name': '<Sub Test Cycle Name>', 
        # 'order': 7, 
        # 'pid': 'CL-4', 
        # 'created_date': '2020-07-28T13:00:19+00:00', 
        # 'last_modified_date': '2020-07-28T13:00:19+00:00', 
        # 'web_url': 'https://<qtest_url>/p/<project_id>/portal/project#tab=testexecution&object=<project_id>&id=<sub_test_cycle_2>', 
        # 'test-cycles': []}]

    def post_create_test_cycle(
            self,
            projectId: int,                 # ID of the project
            testCycleId: int,               # ID of the Release or Test Cycle under which the newly created Test Cycle will be located.
                                            # Use 0 (zero) to create the Test Cycle under the root
            name: str,                      # ID of the Test Cycle which you want to retrieve.
            description: str = None,        # Test Cycle Description
            parentType: str = "test-cycle", # The artifact type of the parent folder. Valid values include release, test-cycle or root
            ):
        """Verify Test Case is not present and create it"""
        stc_data = self.get_sub_test_cycles(
            projectId=projectId,
            parentCycleId=testCycleId,
        )['resopnse']
        sub_test_cycles = []
        for test_cycle in stc_data:
            sub_test_cycles += [test_cycle['name']]
        availability = False
        if not name in sub_test_cycles:
            response = post(
                url=f"{self._host}/api/v3/projects/{projectId}/test-cycles",
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json"
                },
                params={
                    "parentType": parentType,
                    "parentId": testCycleId
                },
                json={
                    "name": name,
                    "description": description
                })
        else:
            root_cycle_name = self.get_test_cycle_by_id(
                projectId=projectId,
                testCycleId=testCycleId
                )['resopnse']['name']
            availability = True

        if availability:
            self._logger.warning(
                "\n[%s] test cycle already present in root [%s] test cycle."
                "\nHere is a list of all existing sub test cycles: %s!"
                "\nExisted [%s] test cycle will be used.", name, root_cycle_name, sub_test_cycles, name)
            return {
                "status_code": 200,
                "headers": {},
                "resopnse": stc_data[0]}
            # If Test Cycle already exist - returns just it's object as dict (to get it's ID, for example).
            # That's why status_code and headres are hardcoded, because there was no creation request.
        elif response.status_code == 200:
            self._logger.info("[%s] test cycle created!", name)
            return {
                "status_code": response.status_code,
                "headers": response.headers,
                "resopnse": response.json()}
            # If status_code == 200: returns dict: {'links': [
            #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<new_sub_test_cycle_id>'}, 
            #   {'rel': 'parent-test-cycle', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cycles/<test_cycle_id>'}, 
            #   {'rel': 'test-suites', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-suites?parentId=<new_sub_test_cycle_id>&parentType=test-cycle'}, 
            #   {'rel': 'test-runs', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs?parentId=<new_sub_test_cycle_id>&parentType=test-cycle&includeToscaProperties=false'}], 
            # 'id': <new_sub_test_cycle_id>, 
            # 'name': '<Sub Test Cycle Name>', 
            # 'order': 15, 'pid': 'CL-25', 
            # 'created_date': '2023-03-23T09:32:37+00:00', 
            # 'last_modified_date': '2023-03-23T09:32:37+00:00', 
            # 'web_url': 'https://<qtest_url>/p/<project_id>/portal/project#tab=testexecution&object=<project_id>&id=<new_sub_test_cycle_id>', 
            # 'description': 'Test test-cycle', 
            # 'test-cycles': []}
        else:
            return {
                "status_code": response.status_code,
                "headers": response.headers,
                "resopnse": response.json()}
