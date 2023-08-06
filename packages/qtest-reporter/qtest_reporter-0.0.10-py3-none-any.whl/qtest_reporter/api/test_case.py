"""This module provides a set of Test Case qTest APIs"""
from qtest_reporter.requester import get


class Test_Case:
    """Test Case API"""
    def __init__(self, qtest: object):
        self._host = qtest._host
        self._token = qtest._token

    def get_all_test_cases(
        self,
        projectId: int,       # ID of the project
        parentId: int = None, # Specify ID of the parent module to retrieve all of its test cases.
        page: int = None,     # 20 Test Cases are included in a page. By default, the first page is returned.
                                # However, you can specify any page number to retrieve test cases.
        size: int = None,     # The result is paginated. By the default, the number of requirements in each age is 20. 
                                # You can specify your custom number in this parameter.
        expandProps = None,   # By default, Test Case properties are included in the response body.
                                # If you want to exclude them, specify false for this parameter.
        expandSteps = None    # By default, Test Steps are excluded from the response body. 
                                # If you want to include them, specify true for this parameter.
        ):
        """
        To retrieve all Test Cases or Test Cases which are located directly under a Module. 
        You can optionally specify a module to retrieve its test cases.
        """
        response = get(
            url=f"{self._host}/api/v3/projects/{projectId}/test-cases",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json"
            },
            params={
                "parentId": parentId,
                "page": page,
                "size": size,
                "expandProps": expandProps,
                "expandSteps": expandSteps
            })

        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "resopnse": response.json()}
        # If status_code == 200: returns list of test cases dicts: [
        # {'links': [
        #   {'rel': 'self', 
        #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<Test_Case_ID>?versionId=<Version_ID>&showParamIdentifier=false'}, 
        #   {'rel': 'test-steps', 
        #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<Test_Case_ID>/versions/<Version_ID>/test-steps?expand=&showParamIdentifier=false'}, 
        #   {'rel': 'attachments', 
        #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<Test_Case_ID>/attachments'}], 
        #       'id': <Test_Case_ID>, 
        #       'name': '<Test Case Name>', 
        #       'order': 2, 
        #       'pid': 'TC-<Test Case Number>', 
        #       'created_date': '2023-04-03T16:24:38+00:00', 
        #       'last_modified_date': '2023-04-03T16:37:01+00:00', 
        # 'properties': [
        #   {'field_id': 396, 'field_name': 'Automation', 'field_value': '712', 'field_value_name': 'No'}, 
        #   {'field_id': 397, 'field_name': 'Automation Content', 'field_value': ''}, 
        #   {'field_id': 152, 'field_name': 'Status', 'field_value': '201', 'field_value_name': 'New'}, 
        #   {'field_id': 150, 'field_name': 'Type', 'field_value': '701', 'field_value_name': 'Manual'}, 
        #   {'field_id': 148, 'field_name': 'Assigned To', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': 153, 'field_name': 'Precondition', 'field_value': ''}, 
        #   {'field_id': 158, 'field_name': 'Description', 'field_value': '...'}, 
        #   {'field_id': 155, 'field_name': 'Priority', 'field_value': '723', 'field_value_name': 'Medium'}, 
        #   {'field_id': 161, 'field_name': 'Notes', 'field_value': ''}, 
        #   {'field_id': 162, 'field_name': 'Review Status', 'field_value': '1', 'field_value_name': 'Ready for Review'}, 
        #   {'field_id': 163, 'field_name': 'Regression Test', 'field_value': '', 'field_value_name': ''}], 
        #       'web_url': 'https://<qtest_url>/p/<project_id>/portal/project#tab=testdesign&object=1&id=<Test_Case_ID>', 
        #       'parent_id': <Root_Module_ID>, 
        #       'test_case_version_id': <Version_ID>, 
        #       'version': '0.3', 
        #       'description': '...', 
        #       'precondition': '', 
        #       'creator_id': <User ID>}, 

        # {'links': [
        #   {'rel': 'self', 
        #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<Test_Case_ID>?versionId=<Version_ID>&showParamIdentifier=false'}, 
        #   {'rel': 'test-steps', 
        #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<Test_Case_ID>/versions/<Version_ID>/test-steps?expand=&showParamIdentifier=false'}, 
        #   {'rel': 'attachments', 
        #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<Test_Case_ID>/attachments'}], 
        #       'id': <Test_Case_ID>, 
        #       'name': '<Test Case Name>', 
        #       'order': 1, 
        #       'pid': 'TC-<Test Case Number>', 
        #       'created_date': '2023-04-03T10:38:21+00:00', 
        #       'last_modified_date': '2023-04-03T15:48:46+00:00', 
        # 'properties': [
        #   {'field_id': 396, 'field_name': 'Automation', 'field_value': '712', 'field_value_name': 'No'}, 
        #   {'field_id': 397, 'field_name': 'Automation Content', 'field_value': ''}, 
        #   {'field_id': 152, 'field_name': 'Status', 'field_value': '201', 'field_value_name': 'New'}, 
        #   {'field_id': 150, 'field_name': 'Type', 'field_value': '701', 'field_value_name': 'Manual'}, 
        #   {'field_id': 148, 'field_name': 'Assigned To', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': 153, 'field_name': 'Precondition', 'field_value': ''}, 
        #   {'field_id': 158, 'field_name': 'Description', 'field_value': '...'}, 
        #   {'field_id': 155, 'field_name': 'Priority', 'field_value': '723', 'field_value_name': 'Medium'}, 
        #   {'field_id': 161, 'field_name': 'Notes', 'field_value': ''}, 
        #   {'field_id': 162, 'field_name': 'Review Status', 'field_value': '1', 'field_value_name': 'Ready for Review'}, 
        #   {'field_id': 163, 'field_name': 'Regression Test', 'field_value': '', 'field_value_name': ''}], 
        #       'web_url': 'https://<qtest_url>/p/<project_id>/portal/project#tab=testdesign&object=1&id=<Test_Case_ID>', 
        #       'parent_id': <Root_Module_ID>, 
        #       'test_case_version_id': <Version_ID>, 
        #       'version': '0.10', 
        #       'description': '...', 
        #       'precondition': '', 
        #       'creator_id': <User ID>}]

    def get_test_case_by_id(
            self,
            projectId: int,    # ID of the project
            testCaseId: int,   # ID of the test case which you want to retrieve
            expand: str = None # If specify expand=teststep, test steps will be included in the test case.
            ):
        """To retrieve a Test Case by ID"""
        response = get(
            url=f"{self._host}/api/v3/projects/{projectId}/test-cases/{testCaseId}",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json"
            },
            params={
                "expand": expand
            })

        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "resopnse": response.json()}
        # If status_code == 200: returns list of test cases dicts {
        # 'links': [
        #   {'rel': 'attachments', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<Test_Case_ID>/attachments'}, 
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<Test_Case_ID>'}, 
        #   {'rel': 'test-steps', 
        #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<Test_Case_ID>/versions/<Version_ID>/test-steps?expand=&showParamIdentifier=false'}, 
        #   {'rel': 'attachments', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<Test_Case_ID>/attachments'}], 
        #       'id': <Test_Case_ID>, 
        #       'name': '<Test Case Name>', 
        #       'order': 1, 
        #       'pid': 'TC-<Test Case Number>', 
        #       'created_date': '2023-04-03T10:38:21+00:00', 
        #       'last_modified_date': '2023-04-03T15:48:46+00:00', 
        #   'properties': [
        #   {'field_id': 396, 'field_name': 'Automation', 'field_value': '712', 'field_value_name': 'No'}, 
        #   {'field_id': 397, 'field_name': 'Automation Content', 'field_value': ''}, 
        #   {'field_id': 152, 'field_name': 'Status', 'field_value': '201', 'field_value_name': 'New'}, 
        #   {'field_id': 150, 'field_name': 'Type', 'field_value': '701', 'field_value_name': 'Manual'}, 
        #   {'field_id': 148, 'field_name': 'Assigned To', 'field_value': '', 'field_value_name': ''}, 
        #   {'field_id': 153, 'field_name': 'Precondition', 'field_value': ''}, 
        #   {'field_id': 158, 'field_name': 'Description', 'field_value': 'This test case verifies that performance of ... is in the range of ... ±1%.'}, 
        #   {'field_id': 155, 'field_name': 'Priority', 'field_value': '723', 'field_value_name': 'Medium'}, 
        #   {'field_id': 161, 'field_name': 'Notes', 'field_value': ''}, 
        #   {'field_id': 162, 'field_name': 'Review Status', 'field_value': '1', 'field_value_name': 'Ready for Review'}, 
        #   {'field_id': 163, 'field_name': 'Regression Test', 'field_value': '', 'field_value_name': ''}], 
        #       'web_url': 'https://<qtest_url>/p/<project_id>/portal/project#tab=testdesign&object=1&id=<Test_Case_ID>', 

        #       'test_steps': [
        # {'links': [
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<Test_Case_ID>/test-steps/<Test_Step_1>'}, 
        #   {'rel': 'attachments', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-steps/<Test_Step_1>/attachments'}], 
        #       'id': <Test_Step_1>, 
        #       'description': '[ SETUP ] Create spreadsheet for data collection', 
        #       'expected': 'Spreadsheet created', 
        #       'order': 1, 
        #       'attachments': [], 
        #       'plain_value_text': '[ SETUP ] Create spreadsheet for data collection'}, 
        # # {'links': [
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<Test_Case_ID>/test-steps/<Test_Step_2>'}, 
        #   {'rel': 'attachments', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-steps/<Test_Step_2>/attachments'}], 
        #       'id': <Test_Step_2>, 
        #       'description': 'Log in via SSH as ... to the ... and prepare ...', 
        #       'expected': '... file downloaded and saved successfully', 
        #       'order': 2, 
        #       'attachments': [], 
        #       'plain_value_text': 'Log in via SSH as ... to the ... and prepare ...'}, 

        # ...

        # {'links': [
        #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<Test_Case_ID>/test-steps/<Test_Step_n>'}, 
        #   {'rel': 'attachments', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-steps/<Test_Step_n>/attachments'}], 
        #       'id': <Test_Step_n>, 
        #       'description': 'Compress logs.zip Be patient! Compressing these logs will take a few minutes.', 
        #       'expected': 'All log files colleccted', 
        #       'order': 8, 
        #       'attachments': [], 
        #       'plain_value_text': 'Compress ... logs to logs.zip file and download it. Compressing these logs will take a few minutes.'}], 

        #   'parent_id': <Module_ID>, 
        #   'test_case_version_id': <Version_ID>, 
        #   'version': '0.10', 
        #   'description': 'This test case verifies that performance of ... is in the range of ... ±1%.', 
        #   'precondition': '', 
        #   'creator_id': <User ID>, 
        #   'agent_ids': []}
