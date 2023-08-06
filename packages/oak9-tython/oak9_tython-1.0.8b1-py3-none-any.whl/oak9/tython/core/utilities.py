"""Module providingFunction utilities for the runner."""
import json
from typing import List
from core.types import Finding
from io import StringIO

from core.bp_metadata_utils.blueprint_meta_data import BlueprintMetaData

def verify_config_arguments(args_obj):
    """
    Verifies if the obligatory attributes are available
    """

    if "org_id" not in args_obj or args_obj["org_id"] == "":
        raise Exception("Missing org_id configuration")

    if "project_id" not in args_obj or args_obj["project_id"] == "":
        raise Exception("Missing project_id configuration")

    if "api_key" not in args_obj or args_obj["api_key"] == "":
        raise Exception("Missing api_key configuration")

    if "blueprint_package_path" not in args_obj or args_obj["blueprint_package_path"] == "":
        raise Exception("Missing blueprint_package_path configuration")


def persist_runner_output(args_path: str, runner_stdout: StringIO, blueprint_problems: List[str], blueprint_metadata: List[BlueprintMetaData], findings: List[Finding]) -> None:
    """
    Consolidate and persists runners output data
    """

    if not args_path:
        return

    stdout_text = runner_stdout.getvalue()
    stdout_lines = stdout_text.splitlines()
    findings_json_list = []
    blueprint_metadata_json_list = []

    if findings:
        for finding in findings:
            if finding:
                findings_json_list.append(finding.__json__())
    
    if blueprint_metadata:
        for metadata in blueprint_metadata:
            if metadata:
                blueprint_metadata_json_list.append(metadata.__json__())

    output = {
        "blueprint_metadata": blueprint_metadata_json_list,
        "blueprint_output": stdout_lines,
        "blueprint_problems": blueprint_problems,
        "findings": findings_json_list
    }

    json_string = json.dumps(output)

    file_path = args_path.replace("input", "output")

    with open(file_path, "w") as f:
        f.write(json_string)
