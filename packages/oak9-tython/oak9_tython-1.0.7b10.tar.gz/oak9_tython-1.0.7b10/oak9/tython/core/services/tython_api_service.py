import core.sdk.helper as Helper
import requests
import time
from core.types import Finding, Configuration
from models.shared.shared_pb2 import RunnerInput
from http import HTTPStatus


class TythonApiService:
    """
    Provides access to the tython api
    """

    def __init__(self, config: Configuration):
        self.config = config

    def get_default_environment(self):
        """
        Gets the default environment_id
        """
        url = f"{self.config.data_endpoint}{self.config.org_id}/projectEnvironment/{self.config.project_id}/default"
        response = requests.get(url, auth=(self.config.org_id, self.config.api_key))

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise Exception("Unable to connect to your oak9 tenant, please verify your credentials.")

        if response.status_code != HTTPStatus.OK:
            raise Exception("Unable to connect to your oak9 tenant, check your internet connection or please try again in a few moments.")

        environment_result = response.json()
        environment_id = "" if "projectId" not in environment_result else environment_result["projectId"]

        if not environment_id:
            raise Exception("Unable to connect to your oak9 tenant, please verify your credentials.")

        return environment_id


    def build_app(self, environment_id: str):
        """
        Triggers build app endpoint
        """
        if not environment_id:
            raise Exception("Please verify your environment_id.")

        url = f"{self.config.data_endpoint}{self.config.org_id}/sac/{self.config.project_id}/build/{environment_id}"
        response = requests.post(url, auth=(self.config.org_id, self.config.api_key))

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise Exception("Unable to connect to your oak9 tenant, please verify your credentials.")
        
        if response.status_code != HTTPStatus.OK:
            raise Exception("Unable to trigger build app, please try again in a few moments.")

        build_app_result = response.json()
        request_id = "" if "requestId" not in build_app_result else build_app_result["requestId"]

        if not request_id:
            raise Exception("Unable to trigger build app, please try again in a few moments.")

        return request_id


    def fetch_graph_data(self, environment_id: str, request_id: str):
        """
        Fetch projects graph data
        """
        if not environment_id:
            raise Exception("Please verify your environment_id.")
        
        if not request_id:
            raise Exception("Please verify the request_id.")

        url = f"{self.config.data_endpoint}{self.config.org_id}/sac/{self.config.project_id}/resourcegraph/{environment_id}/{request_id}"
        timeout = 600
        poll_interval = 15
        start_time = time.time()

        while True:
            response = requests.get(url, auth=(self.config.org_id, self.config.api_key))
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise Exception("Unable to connect to your oak9 tenant, please verify your credentials.")
            
            if response.status_code == HTTPStatus.OK:
                break
            elif time.time() - start_time > timeout:
                raise Exception(f"Unable to fetch {self.config.project_id} data, please try again in a few moments.")
            time.sleep(poll_interval)

        runner_inputs = []
        raw_snake_case_input = Helper.snake_case_json(response.json())

        for raw_item in raw_snake_case_input:
            item = raw_item['item1']
            for root_node in item['graph']['root_nodes']:
                root_node['node']['resource']['data']['value'] = bytes(root_node['node']['resource']['data']['value'])
            Helper.remove_attributes(item, "has_")
            runner_inputs.append(RunnerInput(**item))

        return runner_inputs


    def apply_findings(self, findings: list[Finding], environment_id: str, request_id: str):
        """
        Apply a findings list to the oak9 project
        """
        if not environment_id:
            raise Exception("Please verify your environment_id.")
        
        if not request_id:
            raise Exception("Please verify the request_id.")
        
        design_gaps = []
        capability_number = 1

        for finding in findings:
            if finding:
                violation = finding.to_violation()
                design_gaps.append(
                    {
                        "capabilityId": finding.req_id if finding.req_id else f"CustomReq.{capability_number}",
                        "capabilityName": finding.req_name if finding.req_name else f"Custom Req {capability_number}",
                        "source": "",
                        "resourceName": finding.resource_metadata.resource_name,
                        "resourceId": finding.resource_metadata.resource_id,
                        "resourceType": finding.resource_metadata.resource_type,
                        "resourceImpact": "",
                        "resourceGap": "",
                        "violations": [violation.__json__()],
                        "oak9Guidance": "",
                        "mappedIndustryFrameworks": []
                    }
                )
                capability_number += 1

        payload = {
            "runtime": "Python",
            "author": "",
            "designGaps": design_gaps
        }

        url = f"{self.config.data_endpoint}{self.config.org_id}/sac/{self.config.project_id}/apply/{environment_id}/{request_id}"
        response = requests.post(url, auth=(self.config.org_id, self.config.api_key), json=payload)

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise Exception("Unable to connect to your oak9 tenant, please verify your credentials.")

        if response.status_code != HTTPStatus.OK:
            raise Exception(f"Unable to apply {self.config.project_id} findings, please try again in a few moments.")
