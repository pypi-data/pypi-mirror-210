"""This module provides a set of Test Log qTest APIs"""
from datetime import datetime
from qtest_reporter.api.test_case import Test_Case
from qtest_reporter.api.test_run import Test_Run
from qtest_reporter.logger import Logger
from qtest_reporter.requester import post


class Test_Log:
    """Test Log API"""
    def __init__(self, qtest: object):
        self._host = qtest._host
        self._token = qtest._token
        self._current_date_to_unit = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        self._logger = Logger()._logger

    def post_submit_test_run_result(
            self,
            projectId: int,  # ID of the project
            testRunId: int,  # ID of the Test Run
            status: str,     # Status, as in qTest project's Field Settings, of test log. 601 => Passed, 602 => Failed, 603 => Skipped
            note: str = None # Execution note included with the test log
            ):
        """To submit test result of a manual Test Run"""
        status_id = 601 if status == "passed" else 602 if status == "failed" else 603 if status == "skipped" else 603
        parentSuiteId = Test_Run(self).get_test_run_by_id(projectId=projectId, testRunId=testRunId)['resopnse']['parentId']
        test_runs = Test_Run(self).get_test_runs(projectId=projectId, parentSuiteId=parentSuiteId)['resopnse']['items']

        for test_run in test_runs:
            if test_run['id'] == testRunId: testCaseId = test_run['testCaseId']
            for _ in test_run['properties']:
                if test_run['id'] == testRunId: test_run_name = test_run['name']

        test_case = Test_Case(self).get_test_case_by_id(projectId=projectId, testCaseId=testCaseId)['resopnse']

        response = post(
                url=f"{self._host}/api/v3/projects/{projectId}/test-runs/{testRunId}/test-logs",
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json"
                },
                json={
                    "exe_start_date": self._current_date_to_unit,
                    "exe_end_date": self._current_date_to_unit,
                    "test_case_version_id": test_case['test_case_version_id'],
                    "status": { "id": status_id },
                    "test_step_logs": [{ "test_step_id": test_step['id'], "status": { "id": status_id } } for test_step in test_case['test_steps']],
                    "note": note
                    }
                )

        if response.status_code == 201:
            self._logger.info("[%s] test run status was successfully changed to [%s]!", test_run_name, status)
            return {
                "status_code": response.status_code,
                "headers": response.headers,
                "resopnse": response.json()}
            # If status_code == 201: returns dict with an updated test run status: {
            # 'links': [
            #   {'rel': 'self', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs/<test_run_id>/test-logs/<test_log_id>'}, 
            #   {'rel': 'test-case', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<test_case_id>?versionId=<version_id>&showParamIdentifier=false'}, 
            #   {'rel': 'attachments', 'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-logs/<test_log_id>/attachments'}], 

            # 'id': <test_log_id>, 
            # 'test_case_version_id': <version_id>, 
            # 'exe_start_date': '2023-04-25T14:00:54+00:00', 
            # 'exe_end_date': '2023-04-25T14:00:54+00:00', 
            # 'user_id': <Assignee_ID>, 
            # 'planned_exe_time': 0, 
            # 'actual_exe_time': 0, 
            # 'automation': False, 

            # 'properties': [
            #   {'field_id': 165, 'field_name': 'Tester', 'field_value': '<Assignee_ID>', 'field_value_name': '<Assignee_Name>'}, 
            #   {'field_id': 168, 'field_name': 'Execution Type', 'field_value': '503', 'field_value_name': 'Smoke'}, 
            #   {'field_id': 175, 'field_name': 'Planned Start Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
            #   {'field_id': 171, 'field_name': 'Planned End Date', 'field_value': '2016-05-12T00:00:00+00:00'}, 
            #   {'field_id': 174, 'field_name': 'Test Case Version', 'field_value': '1.0'}, 
            #   {'field_id': 176, 'field_name': 'Target Release/Build', 'field_value': '', 'field_value_name': ''}, 
            #   {'field_id': 180, 'field_name': 'Status', 'field_value': '601', 'field_value_name': 'Passed'}, 
            #   {'field_id': -183, 'field_name': 'Test Data Source', 'field_value': '', 'field_value_name': ''}], 

            # 'status': {'links': [], 'id': 601, 'name': 'Passed'}, 'result_number': 1, 
            # 'test_step_logs': [

            # {'links': [
            #   {'rel': 'self', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs/<test_run_id>/test-logs/<test_log_id>/test-steps/<test_step_log_id1>'}, 
            #   {'rel': 'test-step', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<test_case_id>/test-steps/<test_step_id>?showParamIdentifier=false'}, 
            #   {'rel': 'defects', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs/<test_run_id>/test-logs/<test_log_id>/test-steps/<test_step_log_id1>/defects'}], 
            # 'test_step_id': <test_step_id>, 
            # 'test_step_log_id': <test_step_log_id1>, 
            # 'user_id': <Assignee_ID>, 
            # 'status': {'links': [], 'id': 601, 'name': 'Passed'}, 
            # 'description': '[ SETUP ] Create ... for data collection.', 
            # 'expected_result': '... created', 
            # 'order': 1, 
            # 'group': 0, 
            # 'defects': [], 
            # 'exe_date': '2023-04-25T14:00:54+00:00', 
            # 'tester_id': <Assignee_ID>}, 

            # {'links': [
            #   {'rel': 'self', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs/<test_run_id>/test-logs/<test_log_id>/test-steps/<test_step_log_id2>'}, 
            #   {'rel': 'test-step', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<test_case_id>/test-steps/<test_step_id>?showParamIdentifier=false'}, 
            #   {'rel': 'defects', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs/<test_run_id>/test-logs/<test_log_id>/test-steps/<test_step_log_id2>/defects'}],
            # 'test_step_id': <test_step_id>, 
            # 'test_step_log_id': <test_step_log_id2>, 
            # 'user_id': <Assignee_ID>, 
            # 'status': {'links': [], 'id': 601, 'name': 'Passed'}, 
            # 'description': 'Log in via ... as ... to the ... and prepare ...', 
            # 'expected_result': 'File ... exist in folder ... and ... is stopped', 
            # 'order': 2, 
            # 'group': 0, 
            # 'defects': [], 
            # 'exe_date': '2023-04-25T14:00:54+00:00', 
            # 'tester_id': <Assignee_ID>}, 

            # {'links': [
            #   {'rel': 'self', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs/<test_run_id>/test-logs/<test_log_id>/test-steps/<test_step_log_id3>'}, 
            #   {'rel': 'test-step', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<test_case_id>/test-steps/<test_step_id>?showParamIdentifier=false'}, 
            #   {'rel': 'defects', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs/<test_run_id>/test-logs/<test_log_id>/test-steps/<test_step_log_id3>/defects'}],
            # 'test_step_id': <test_step_id>, 
            # 'test_step_log_id': <test_step_log_id3>, 
            # 'user_id': <Assignee_ID>, 
            # 'status': {'links': [], 'id': 601, 'name': 'Passed'}, 
            # 'description': 'Log in via ... as ... to the ... and save general static data to ...stats.xlsx', 
            # 'expected_result': 'The user ... has successfully logged in and data is collected', 
            # 'order': 3, 
            # 'group': 0, 
            # 'defects': [], 
            # 'exe_date': '2023-04-25T14:00:54+00:00', 
            # 'tester_id': <Assignee_ID>}, 

            #   ...
 
            # {'links': [
            #   {'rel': 'self', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs/<test_run_id>/test-logs/<test_log_id>/test-steps/<test_step_log_idn>'}, 
            #   {'rel': 'test-step', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-cases/<test_case_id>/test-steps/<test_step_id>?showParamIdentifier=false'}, 
            #   {'rel': 'defects', 
            #    'href': 'https://<qtest_url>/api/v3/projects/<project_id>/test-runs/<test_run_id>/test-logs/<test_log_id>/test-steps/<test_step_log_idn>/defects'}],
            # 'test_step_id': <test_step_id>, 
            # 'test_step_log_id': <test_step_log_idn>, 
            # 'user_id': <Assignee_ID>, 
            # 'status': {'links': [], 'id': 601, 'name': 'Passed'}, 
            # 'description': 'Compress ...'s logs to an logs.zip file and download it. Be patient! Compressing these logs will take a few minutes', 
            # 'expected_result': 'All log files were collected', 
            # 'order': n, 
            # 'group': 0, 
            # 'defects': [], 
            # 'exe_date': '2023-04-25T14:00:54+00:00', 
            # 'tester_id': <Assignee_ID>}]}
        else:
            return {
                "status_code": response.status_code,
                "headers": response.headers,
                "resopnse": response.json()}
