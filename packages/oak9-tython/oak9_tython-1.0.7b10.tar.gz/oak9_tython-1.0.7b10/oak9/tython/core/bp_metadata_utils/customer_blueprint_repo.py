import ast
import os
from typing import Iterator, AnyStr, List

from core.bp_metadata_utils.blueprint_docstring import BlueprintDocstring
from core.bp_metadata_utils.blueprint_meta_data import BlueprintMetaData
from core.bp_metadata_utils.multiple_policies_per_file_repo import MultiplePoliciesPerFileRepo
from core.bp_metadata_utils.policy import Policy, Validation
from core.bp_metadata_utils.policy_implementation_docstring import PolicyImplementationDocstring
from core.bp_metadata_utils.python_source_file_utils import is_customer_blueprint


class CustomerBlueprintRepo(MultiplePoliciesPerFileRepo):
    """Represents Customer SaC repo."""

    def __init__(self, local_path, url="", token: str = "", skip_sync=True) -> None:
        """
        Constructs a repo for Azure Policies.
        """
        if not url and not local_path:
            raise Exception("Local Path must be provided")

        super(CustomerBlueprintRepo, self).__init__(
            url=url,
            local_path=local_path,
            skip_sync=skip_sync,
        )

    @property
    def glob_pattern(self) -> str:
        return os.path.join(
            self._local_path,
            '*.py')

    def filter(self, policy: Policy) -> bool:
        return False

    def pre_filter(self, blueprint_file_path: str) -> bool:
        return False

    def parse_policy_file(self, blueprint_path: str) -> Iterator[Policy]:
        for func in self.get_functions(blueprint_path=blueprint_path):
            docstring = ast.get_docstring(func)
            if not docstring:
                continue

            implementation_docstring = PolicyImplementationDocstring(docstring_raw=docstring)
            for implementation in implementation_docstring.implementations:
                yield implementation

    def parse_blueprint_file(self, blueprint_path: str) -> Iterator[Validation]:
        for func in self.get_functions(blueprint_path=blueprint_path):
            docstring = ast.get_docstring(func)
            if not docstring:
                continue

            implementations = []
            references = []

            func_docstring = PolicyImplementationDocstring(docstring_raw=docstring)
            for implementation in func_docstring.implementations:
                implementations.append(implementation)

            for reference in func_docstring.references:
                references.append(reference)

            yield Validation(
                references=references,
                description=func_docstring.desc,
                coverage=func_docstring.coverage,
                implements=implementations,
                name=''
            )

    @staticmethod
    def get_functions(blueprint_path: str) -> Iterator[ast.FunctionDef]:
        with open(blueprint_path) as fd:
            source = fd.read()

        module = ast.parse(source)
        implementing_class = [node for node in module.body if isinstance(node, ast.ClassDef)][0]
        # TODO: Assert that we got exactly one Class.
        return (node for node in implementing_class.body if isinstance(node, ast.FunctionDef))

    def get_blueprint_metadata(self, blueprint_path: str) -> Iterator[BlueprintMetaData]:
        with open(blueprint_path) as fd:
            source = fd.read()

        module = ast.parse(source)
        for node in module.body:
            if isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                if not docstring:
                    continue

                # blueprint_docstring = BlueprintDocstring(docstring_raw=docstring)
                validations_result = []

                validations = self.parse_blueprint_file(blueprint_path)
                for validation in validations:
                    validations_result.append(validation)

                blueprint_meta_data = BlueprintMetaData(
                    # name=blueprint_docstring.name,
                    # desc=blueprint_docstring.desc,
                    # author=blueprint_docstring.author,
                    validations=validations_result
                )

                yield blueprint_meta_data

    @property
    def blueprint_file_paths(self) -> Iterator[AnyStr]:
        paths = self.policy_file_paths
        result = []
        for path in paths:
            if is_customer_blueprint(path):
                result.append(path)
        return result

    @property
    def blueprints(self) -> List[BlueprintMetaData]:
        """
        Iterate over the blueprints and provide a summary of the blueprints
        return: A list of policies
        """
        result = []
        for blueprint_path in self.blueprint_file_paths:
            if self.pre_filter(blueprint_path):
                continue
            blueprints = self.get_blueprint_metadata(blueprint_path)
            result.extend(blueprints)

        return result

