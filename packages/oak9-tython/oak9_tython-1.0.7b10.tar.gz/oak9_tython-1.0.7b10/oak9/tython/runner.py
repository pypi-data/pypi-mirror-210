import json
import os
import sys
from io import StringIO
from typing import Protocol, runtime_checkable, Set, Optional, List
from core.services.tython_api_service import TythonApiService
from core.bp_metadata_utils.customer_blueprint_repo import CustomerBlueprintRepo
from core.bp_metadata_utils.python_source_file_utils import get_blueprint_classes
from core.types import Finding, Configuration
import core.utilities as Utilities
from core.bp_metadata_utils.blueprint_meta_data import BlueprintMetaData


@runtime_checkable
class SupportsValidation(Protocol):
    def validate(self) -> Set[Finding]:
        """
        Entry point into component's validation logic
        """


class Runner:

    @staticmethod
    def run(validation_target: SupportsValidation):
        return validation_target.validate()


def main(argv):
    stdout = sys.stdout
    sys.stdout = runner_stdout = StringIO()

    args_path = None
    findings = set()
    blueprint_metadata_list = []
    blueprint_problems = []

    try:

        if len(argv) > 0:
            args_path = argv[0]
        else:
            sys.stderr.write("Configuration path was not provided.")
            sys.exit(1)

        config = None
        try:
            args_file = open(args_path)
            args_obj = json.load(args_file)
            args_file.close()
            Utilities.verify_config_arguments(args_obj)
            config = Configuration(**args_obj)
        except:
            raise Exception("Runner arguments not found or could not be understood.")

        runner = Runner()

        blueprint_repo = CustomerBlueprintRepo(config.blueprint_package_path)
        
        try:
            blueprint_metadata_list = blueprint_repo.blueprints
        except:
            blueprint_problems.append("Docstring formatting does not meet specificiation. Update your blueprint docstrings for a more helpful summary of your blueprint")
            blueprint_metadata_list = []

        tython_api_service = TythonApiService(config)
        environment_id = config.environment_id if hasattr(config, "environment_id") and config.environment_id else tython_api_service.get_default_environment()
        request_id = tython_api_service.build_app(environment_id)
        runner_inputs = tython_api_service.fetch_graph_data(environment_id, request_id)

        if len(runner_inputs) == 0:
            raise Exception("No data available for validation")

        # get all blueprint classes
        blueprint_classes = []
        for blueprint_file_path in blueprint_repo.blueprint_file_paths:
            blueprint_classes.extend(get_blueprint_classes(blueprint_file_path))

        # Run each blueprint
        for blueprint in blueprint_classes:
            customer_blueprint = blueprint[1](graph=runner_inputs)
            # TODO: check usage guidelines to see if findings should be reported
            try:
                findings.update(runner.run(customer_blueprint))
            except Exception as e:
                blueprint_problems.append(str(e))
            
        if config.mode == "apply" and findings:
            tython_api_service.apply_findings(list(findings), environment_id, request_id)

        sys.exit(0)

    except Exception as e:
        sys.stderr.write(str(e))
        sys.stderr.flush()
        sys.exit(1)

    finally:
        Utilities.persist_runner_output(args_path, runner_stdout, blueprint_problems, blueprint_metadata_list, list(findings))
        sys.stdout = stdout


if __package__ == "":
    # Resulting path is the name of the wheel itself
    path = os.path.dirname(__file__)
    sys.path.insert(0, path)

if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
